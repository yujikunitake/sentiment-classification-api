from app.services.classifier import classify_sentiment, sentiment_classifier

casos = [
    # POSITIVAS
    ("Lucas Mendes", "O suporte foi impecável! Resolveram tudo em menos de 10 minutos e ainda me explicaram como evitar o problema no futuro.", "positiva"),  # noqa:E501
    ("Mariana Castro", "Fiquei impressionada com a agilidade e clareza do atendimento. Me senti muito bem acompanhada durante todo o processo.", "positiva"),  # noqa:E501
    ("Rafael Dias", "Tudo correu perfeitamente. Resolveram meu problema e ainda melhoraram a configuração do sistema.", "positiva"),  # noqa:E501
    ("Priscila Nogueira", "Atendimento nota 10! Técnicos muito bem preparados e atenciosos, recomendo sem pensar duas vezes.", "positiva"),  # noqa:E501
    ("Thiago Lopes", "Foi o melhor atendimento técnico que já tive com qualquer fornecedor. Profissionais muito competentes.", "positiva"),  # noqa:E501
    ("Camila Ferreira", "Me surpreendi com a velocidade da resposta e a gentileza do atendente. Super eficiente!", "positiva"),  # noqa:E501
    ("Vinícius Ramos", "Equipe muito prestativa. Me explicaram tudo com paciência e resolveram mesmo uma questão complexa.", "positiva"),  # noqa:E501
    ("Letícia Gomes", "Resolveram meu chamado rapidamente e ainda me deram dicas extras de segurança. Muito bom!", "positiva"),  # noqa:E501
    ("Rodrigo Santana", "Suporte excelente. Já sou cliente há anos e sempre que preciso, o atendimento é de primeira.", "positiva"),  # noqa:E501
    ("Andréa Lima", "Atendimento rápido e eficaz. Consegui voltar ao trabalho em poucos minutos graças à ajuda do suporte.", "positiva"),  # noqa:E501

    # NEUTRAS
    ("Beatriz Rocha", "O atendimento foi educado, mas não consegui entender completamente a explicação técnica fornecida.", "neutra"),  # noqa:E501
    ("Fábio Matos", "Demorou um pouco para me responderem, mas depois que começou o atendimento, fluiu bem.", "neutra"),  # noqa:E501
    ("Tatiane Souza", "Não foi ruim, mas também não senti muita segurança nas respostas. Acabei resolvendo por conta própria.", "neutra"),  # noqa:E501
    ("Gustavo Pires", "O atendente tentou ajudar, mas parecia inseguro em alguns pontos. No final deu certo, mas podia ser melhor.", "neutra"),  # noqa:E501
    ("Larissa Campos", "A resposta foi ok, mas esperava uma solução mais completa. Consegui contornar com uma gambiarra.", "neutra"),  # noqa:E501
    ("Felipe Teixeira", "Achei a solução meio incompleta. Resolvi pela metade e ainda estou aguardando uma confirmação final.", "neutra"),  # noqa:E501
    ("Juliana Ribeiro", "A comunicação foi boa, mas a resolução demorou mais do que o necessário.", "neutra"),  # noqa:E501
    ("Renato Barros", "Foi resolvido, mas precisei insistir bastante e mandar várias mensagens. Poderia ter sido mais direto.", "neutra"),  # noqa:E501
    ("Carolina Faria", "A equipe foi educada e prestativa, porém o problema se resolveu mais por insistência minha do que por iniciativa deles.", "neutra"),  # noqa:E501
    ("Danilo Tavares", "Recebi suporte, mas não senti muita confiança nas instruções. Precisei testar algumas alternativas por conta própria.", "neutra"),  # noqa:E501

    # NEGATIVAS
    ("Paulo Andrade", "Foi uma experiência péssima. Além da demora absurda, ninguém soube resolver o meu problema.", "negativa"),  # noqa:E501
    ("Aline Neves", "O atendimento foi confuso, contraditório e terminou sem nenhuma solução. Decepcionante.", "negativa"),  # noqa:E501
    ("Diego Silveira", "Fiquei completamente insatisfeito. Nada foi resolvido e ninguém me deu retorno depois.", "negativa"),  # noqa:E501
    ("Simone Braga", "Não obtive ajuda alguma. Parecia que o atendente nem sabia do que estava falando.", "negativa"),  # noqa:E501
    ("Leonardo Costa", "Perdi mais de uma hora tentando resolver algo simples e saí com mais dúvidas do que entrei.", "negativa"),  # noqa:E501
    ("Viviane Melo", "Atendimento muito fraco. Tive que buscar ajuda em outro lugar para conseguir trabalhar.", "negativa"),  # noqa:E501
    ("Eduardo Bezerra", "O suporte simplesmente me ignorou por horas. Inaceitável para um serviço profissional.", "negativa"),  # noqa:E501
    ("Fernanda Silva", "Problema recorrente, nunca resolvem de forma definitiva. Já perdi a paciência com essa empresa.", "negativa"),  # noqa:E501
    ("Marcelo Cunha", "Total despreparo. A equipe não entendeu o problema e ainda sugeriu uma solução errada.", "negativa"),  # noqa:E501
    ("Sabrina Dias", "Serviço horrível. Me deixaram sem resposta em um momento crítico para minha operação.", "negativa")  # noqa:E501
]


def test_generalizacao_detalhado():
    total = len(casos)
    acertos = 0
    erros = []

    # Contadores por categoria
    stats = {
        'positiva': {'total': 0, 'acertos': 0},
        'neutra': {'total': 0, 'acertos': 0},
        'negativa': {'total': 0, 'acertos': 0}
    }

    print("=== ANÁLISE DETALHADA ===\n")

    for nome, texto, esperado in casos:
        resultado = classify_sentiment(texto)

        # Análise detalhada
        analysis = sentiment_classifier.analyze_sentiment_strength(texto)

        stats[esperado]['total'] += 1

        if resultado == esperado:
            print(f"{nome}: esperado={esperado}, resultado={resultado}")
            acertos += 1
            stats[esperado]['acertos'] += 1
        else:
            print(f"{nome}: esperado={esperado}, resultado={resultado}")
            print(f"   Análise: pos={analysis['very_positive']}, neg={analysis[
                'very_negative']}, "
                  f"neu={analysis['neutral_indicators']}, weak={analysis[
                      'weakening_words']}, "
                  f"contr={analysis['has_contradiction']}, flair={analysis[
                      'flair_label']}({analysis['flair_confidence']:.2f})")
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
            print(f"{categoria.upper()}: {data['acertos']}/{data['total']} ({acc:.1f}%)")  # noqa: E501

    print("\n*===* ERROS DETALHADOS *===*")
    for nome, esperado, resultado in erros:
        print(f"• {nome}: {esperado} → {resultado}")

    assert acuracia >= 0.9, f"Acurácia abaixo do esperado: {acuracia:.2%}"
