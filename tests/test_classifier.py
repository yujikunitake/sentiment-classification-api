from app.services.classifier import classify_sentiment, sentiment_classifier

casos = [
    # POSITIVAS
    ("Lucas Mendes", "O suporte foi impecável! Resolveram tudo em menos de 10 minutos e ainda me explicaram como evitar o problema no futuro.", "positive"),  # noqa:E501
    ("Mariana Castro", "Fiquei impressionada com a agilidade e clareza do atendimento. Me senti muito bem acompanhada durante todo o processo.", "positive"),  # noqa:E501
    ("Rafael Dias", "Tudo correu perfeitamente. Resolveram meu problema e ainda melhoraram a configuração do sistema.", "positive"),  # noqa:E501
    ("Priscila Nogueira", "Atendimento nota 10! Técnicos muito bem preparados e atenciosos, recomendo sem pensar duas vezes.", "positive"),  # noqa:E501
    ("Thiago Lopes", "Foi o melhor atendimento técnico que já tive com qualquer fornecedor. Profissionais muito competentes.", "positive"),  # noqa:E501
    ("Camila Ferreira", "Me surpreendi com a velocidade da resposta e a gentileza do atendente. Super eficiente!", "positive"),  # noqa:E501
    ("Vinícius Ramos", "Equipe muito prestativa. Me explicaram tudo com paciência e resolveram mesmo uma questão complexa.", "positive"),  # noqa:E501
    ("Letícia Gomes", "Resolveram meu chamado rapidamente e ainda me deram dicas extras de segurança. Muito bom!", "positive"),  # noqa:E501
    ("Rodrigo Santana", "Suporte excelente. Já sou cliente há anos e sempre que preciso, o atendimento é de primeira.", "positive"),  # noqa:E501
    ("Andréa Lima", "Atendimento rápido e eficaz. Consegui voltar ao trabalho em poucos minutos graças à ajuda do suporte.", "positive"),  # noqa:E501

    # NEUTRAS
    ("Beatriz Rocha", "O atendimento foi educado, mas não consegui entender completamente a explicação técnica fornecida.", "neutral"),  # noqa:E501
    ("Fábio Matos", "Demorou um pouco para me responderem, mas depois que começou o atendimento, fluiu bem.", "neutral"),  # noqa:E501
    ("Tatiane Souza", "Não foi ruim, mas também não senti muita segurança nas respostas. Acabei resolvendo por conta própria.", "neutral"),  # noqa:E501
    ("Gustavo Pires", "O atendente tentou ajudar, mas parecia inseguro em alguns pontos. No final deu certo, mas podia ser melhor.", "neutral"),  # noqa:E501
    ("Larissa Campos", "A resposta foi ok, mas esperava uma solução mais completa. Consegui contornar com uma gambiarra.", "neutral"),  # noqa:E501
    ("Felipe Teixeira", "Achei a solução meio incompleta. Resolvi pela metade e ainda estou aguardando uma confirmação final.", "neutral"),  # noqa:E501
    ("Juliana Ribeiro", "A comunicação foi boa, mas a resolução demorou mais do que o necessário.", "neutral"),  # noqa:E501
    ("Renato Barros", "Foi resolvido, mas precisei insistir bastante e mandar várias mensagens. Poderia ter sido mais direto.", "neutral"),  # noqa:E501
    ("Carolina Faria", "A equipe foi educada e prestativa, porém o problema se resolveu mais por insistência minha do que por iniciativa deles.", "neutral"),  # noqa:E501
    ("Danilo Tavares", "Recebi suporte, mas não senti muita confiança nas instruções. Precisei testar algumas alternativas por conta própria.", "neutral"),  # noqa:E501

    # NEGATIVAS
    ("Paulo Andrade", "Foi uma experiência péssima. Além da demora absurda, ninguém soube resolver o meu problema.", "negative"),  # noqa:E501
    ("Aline Neves", "O atendimento foi confuso, contraditório e terminou sem nenhuma solução. Decepcionante.", "negative"),  # noqa:E501
    ("Diego Silveira", "Fiquei completamente insatisfeito. Nada foi resolvido e ninguém me deu retorno depois.", "negative"),  # noqa:E501
    ("Simone Braga", "Não obtive ajuda alguma. Parecia que o atendente nem sabia do que estava falando.", "negative"),  # noqa:E501
    ("Leonardo Costa", "Perdi mais de uma hora tentando resolver algo simples e saí com mais dúvidas do que entrei.", "negative"),  # noqa:E501
    ("Viviane Melo", "Atendimento muito fraco. Tive que buscar ajuda em outro lugar para conseguir trabalhar.", "negative"),  # noqa:E501
    ("Eduardo Bezerra", "O suporte simplesmente me ignorou por horas. Inaceitável para um serviço profissional.", "negative"),  # noqa:E501
    ("Fernanda Silva", "Problema recorrente, nunca resolvem de forma definitiva. Já perdi a paciência com essa empresa.", "negative"),  # noqa:E501
    ("Marcelo Cunha", "Total despreparo. A equipe não entendeu o problema e ainda sugeriu uma solução errada.", "negative"),  # noqa:E501
    ("Sabrina Dias", "Serviço horrível. Me deixaram sem resposta em um momento crítico para minha operação.", "negative")  # noqa:E501
]


def test_generalizacao_detalhado():
    total = len(casos)
    acertos = 0
    erros = []

    # Contadores por categoria
    stats = {
        'positive': {'total': 0, 'acertos': 0},
        'neutral': {'total': 0, 'acertos': 0},
        'negative': {'total': 0, 'acertos': 0}
    }

    print("=== ANÁLISE DETALHADA ===\n")

    for nome, texto, esperado in casos:
        resultado = classify_sentiment(texto)

        # Análise detalhada
        analysis = sentiment_classifier.analyze_sentiment_strength(texto)

        stats[esperado]['total'] += 1

        if resultado == esperado:
            print(f"✓ {nome}: esperado={esperado}, resultado={resultado}")
            acertos += 1
            stats[esperado]['acertos'] += 1
        else:
            print(f"✗ {nome}: esperado={esperado}, resultado={resultado}")
            print(f"   Análise: pos={analysis['very_positive']}, neg={analysis['very_negative']}, "  # noqa:E501
                  f"neu={analysis['neutral_indicators']}, weak={analysis['weakening_words']}, "  # noqa:E501
                  f"contr={analysis['has_contradiction']}, pattern={analysis['matches_neutral_pattern']}, "  # noqa:E501
                  f"flair={analysis['flair_label']}({analysis['flair_confidence']:.2f})")  # noqa:E501
            erros.append((nome, esperado, resultado))

        print()

    acuracia = acertos / total

    print("\n*===* RELATÓRIO FINAL *===*")
    print(f"Total de casos: {total}")
    print(f"Acertos: {acertos}")
    print(f"Erros: {len(erros)}")
    print(f"Acurácia Geral: {acuracia*100:.2f}%")

    print("\n*===* PERFORMANCE POR CATEGORIA *===*")
    for categoria, data in stats.items():
        if data['total'] > 0:
            acc = (data['acertos'] / data['total']) * 100
            print(f"{categoria.upper()}: {data['acertos']}/{data['total']} ({acc:.1f}%)")  # noqa:E501

    print("\n*===* ERROS DETALHADOS *===*")
    for nome, esperado, resultado in erros:
        print(f"• {nome}: {esperado} → {resultado}")

    print("\n*===* RESUMO *===*")
    if acuracia >= 0.9:
        print(f"SUCESSO! Acurácia de {acuracia:.1%} atingiu o objetivo (90%)")
    else:
        print(f"Meta não atingida. Acurácia de {acuracia:.1%} abaixo dos 90% esperados")  # noqa:E501

    # ASSERTIONS
    assert acuracia >= 0.9, f"Acurácia geral de {acuracia:.1%} está abaixo do mínimo exigido de 90%"  # noqa:E501

    # Assertinons por categoria)
    for categoria, data in stats.items():
        if data['total'] > 0:
            categoria_acuracia = data['acertos'] / data['total']
            assert categoria_acuracia >= 0.8, f"Acurácia da categoria {categoria} de {categoria_acuracia:.1%} está abaixo do mínimo de 80%"   # noqa:E501

    return True


def test_casos_originais():
    """Testa com os casos originais que você forneceu"""
    casos_originais = [
        ("Ana Silva", "O atendimento foi rápido e eficiente, mas senti que poderia ser mais detalhado em alguns pontos técnicos. Por exemplo, ao explicar a falha que ocorreu, o atendente não conseguiu detalhar a causa raiz do problema, o que me deixou com dúvidas sobre o que realmente aconteceu. No geral, foi uma experiência satisfatória, mas acredito que poderia ser mais completa.", "neutral"),  # noqa:E501
        ("Bruno Souza", "Estou extremamente satisfeito com o suporte! Resolveram meu problema de forma ágil e com clareza nas explicações. Além de resolverem o erro no sistema que estava impedindo a execução de uma função crítica para o meu negócio, eles ainda sugeriram melhorias para evitar que o problema ocorresse novamente. O atendimento foi muito acima do esperado!", "positive"),  # noqa:E501
        ("Carlos Pereira", "O serviço foi muito demorado e o atendente parecia completamente despreparado. Precisei repetir meu problema várias vezes, e mesmo assim senti que ele não estava entendendo o que eu estava dizendo. Perdi muito tempo, e o pior de tudo é que o problema não foi resolvido ao final. Vou reconsiderar continuar usando esse serviço.", "negative"),  # noqa:E501
        ("Daniela Rocha", "A equipe de suporte foi extremamente atenciosa e dedicada. Adorei o atendimento, pois desde o início até a resolução do meu problema fui informado de cada etapa do processo. Eles fizeram de tudo para que eu entendesse o que estava acontecendo e até me ofereceram um acompanhamento extra para garantir que tudo estivesse funcionando corretamente após a solução.", "positive"),  # noqa:E501
        ("Eduardo Lima", "Infelizmente, não conseguiram resolver meu problema, e fiquei muito decepcionado. Além da demora para obter uma resposta clara, não houve um acompanhamento adequado após o primeiro contato, o que deixou a sensação de que meu problema não era uma prioridade. Esperava mais de uma empresa com uma reputação tão boa no mercado.", "negative"),  # noqa:E501
        ("Fernanda Carvalho", "O sistema que utilizo tem funcionado bem, mas o suporte não foi tão eficiente quanto eu esperava. Tive que esperar bastante tempo por uma resposta e, quando ela finalmente veio, não era clara o suficiente para que eu pudesse seguir as instruções por conta própria. A experiência foi mediana, espero que melhorem essa parte do serviço.", "neutral"),  # noqa:E501
        ("Gabriel Costa", "Ótimo serviço! A equipe de suporte foi muito prestativa e realmente se dedicou a resolver o meu problema. Além de solucionarem a questão com rapidez, eles ainda se certificaram de que eu entendesse o que havia causado o erro e como evitar que ele ocorresse novamente no futuro. Superou completamente as minhas expectativas.", "positive"),  # noqa:E501
        ("Helena Ribeiro", "O atendente foi educado e respeitoso durante todo o processo, mas infelizmente não conseguiu solucionar o problema técnico que eu estava enfrentando. Ele tentou várias abordagens, mas ao final, ainda fiquei sem uma solução definitiva. Agradeço pelo esforço, mas o resultado final me deixou frustrado.", "neutral"),  # noqa:E501
        ("Igor Almeida", "Não tive uma boa experiência. Precisei contatar o suporte diversas vezes até que uma solução adequada fosse finalmente apresentada. A falta de consistência nas respostas e a demora entre os contatos me deixaram bastante insatisfeito. Era um problema simples de configuração, mas o processo todo acabou tomando muito mais tempo do que o necessário.", "negative"),  # noqa:E501
        ("Julia Martins", "Fui muito bem atendido desde o início, e o problema foi resolvido sem nenhuma complicação. O serviço foi prático, eficiente e me surpreendeu pela rapidez com que conseguiram resolver tudo. A comunicação também foi excelente, me mantendo informado a cada passo. Um atendimento realmente de qualidade.", "positive")  # noqa:E501
    ]

    print("=== TESTE COM CASOS ORIGINAIS ===\n")

    acertos = 0
    total = len(casos_originais)
    erros = []

    for nome, texto, esperado in casos_originais:
        resultado = classify_sentiment(texto)

        if resultado == esperado:
            print(f"✓ {nome}: {esperado}")
            acertos += 1
        else:
            print(f"✗ {nome}: esperado={esperado}, resultado={resultado}")
            erros.append((nome, esperado, resultado))

    acuracia = acertos / total
    print(f"\nCasos originais: {acertos}/{total} ({acuracia:.1%})")

    # ASSERTIONS
    assert acuracia >= 0.9, f"Acurácia dos casos originais de {acuracia:.1%} está abaixo do mínimo exigido de 90%"  # noqa:E501

    if erros:
        print("\nErros encontrados:")
        for nome, esperado, resultado in erros:
            print(f"• {nome}: {esperado} → {resultado}")

    return True


def test_acuracia_completa():
    """Executa todos os testes e verifica se a acurácia geral está
    acima de 90%"""
    print("=== TESTE COMPLETO DE ACURÁCIA ===\n")

    # Executa teste detalhado
    print("1. Executando teste detalhado...")
    test_generalizacao_detalhado()

    print("\n" + "="*50 + "\n")

    # Executa teste com casos originais
    print("2. Executando teste com casos originais...")
    test_casos_originais()

    print("\n" + "="*50)
    print("TODOS OS TESTES PASSARAM!")
    print("ACURÁCIA ACIMA DE 90% CONFIRMADA!")

    return True


if __name__ == "__main__":
    test_acuracia_completa()
