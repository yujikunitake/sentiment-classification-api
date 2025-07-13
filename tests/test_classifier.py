import pytest
from app.services.classifier import classify_sentiment, sentiment_classifier

CASOS = [
    # POSITIVAS
    ("Lucas Mendes", "O suporte foi impecável! Resolveram tudo em menos de 10 minutos e ainda me explicaram como evitar o problema no futuro.", "positive"),  # noqa: E501
    ("Mariana Castro", "Fiquei impressionada com a agilidade e clareza do atendimento. Me senti muito bem acompanhada durante todo o processo.", "positive"),  # noqa: E501
    ("Priscila Nogueira", "Atendimento nota 10! Técnicos muito bem preparados e atenciosos, recomendo sem pensar duas vezes.", "positive"),  # noqa: E501
    ("Thiago Lopes", "Foi o melhor atendimento técnico que já tive com qualquer fornecedor. Profissionais muito competentes.", "positive"),  # noqa: E501
    ("Camila Ferreira", "Me surpreendi com a velocidade da resposta e a gentileza do atendente. Super eficiente!", "positive"),  # noqa: E501
    ("Vinícius Ramos", "Equipe muito prestativa. Me explicaram tudo com paciência e resolveram mesmo uma questão complexa.", "positive"),  # noqa: E501
    ("Letícia Gomes", "Resolveram meu chamado rapidamente e ainda me deram dicas extras de segurança. Muito bom!", "positive"),  # noqa: E501
    ("Rodrigo Santana", "Suporte excelente. Já sou cliente há anos e sempre que preciso, o atendimento é de primeira.", "positive"),  # noqa: E501
    ("Andréa Lima", "Atendimento rápido e eficaz. Consegui voltar ao trabalho em poucos minutos graças à ajuda do suporte.", "positive"),  # noqa: E501

    # NEUTRAS
    ("Beatriz Rocha", "O atendimento foi educado, mas não consegui entender completamente a explicação técnica fornecida.", "neutral"),  # noqa: E501
    ("Fábio Matos", "Demorou um pouco para me responderem, mas depois que começou o atendimento, fluiu bem.", "neutral"),  # noqa: E501
    ("Tatiane Souza", "Não foi ruim, mas também não senti muita segurança nas respostas. Acabei resolvendo por conta própria.", "neutral"),  # noqa: E501
    ("Gustavo Pires", "O atendente tentou ajudar, mas parecia inseguro em alguns pontos. No final deu certo, mas podia ser melhor.", "neutral"),  # noqa: E501
    ("Larissa Campos", "A resposta foi ok, mas esperava uma solução mais completa. Consegui contornar com uma gambiarra.", "neutral"),  # noqa: E501
    ("Felipe Teixeira", "Achei a solução meio incompleta. Resolvi pela metade e ainda estou aguardando uma confirmação final.", "neutral"),  # noqa: E501
    ("Juliana Ribeiro", "A comunicação foi boa, mas a resolução demorou mais do que o necessário.", "neutral"),  # noqa: E501
    ("Renato Barros", "Foi resolvido, mas precisei insistir bastante e mandar várias mensagens. Poderia ter sido mais direto.", "neutral"),  # noqa: E501
    ("Danilo Tavares", "Recebi suporte, mas não senti muita confiança nas instruções. Precisei testar algumas alternativas por conta própria.", "neutral"),  # noqa: E501

    # NEGATIVAS
    ("Paulo Andrade", "Foi uma experiência péssima. Além da demora absurda, ninguém soube resolver o meu problema.", "negative"),  # noqa: E501
    ("Aline Neves", "O atendimento foi confuso, contraditório e terminou sem nenhuma solução. Decepcionante.", "negative"),  # noqa: E501
    ("Diego Silveira", "Fiquei completamente insatisfeito. Nada foi resolvido e ninguém me deu retorno depois.", "negative"),  # noqa: E501
    ("Simone Braga", "Não obtive ajuda alguma. Parecia que o atendente nem sabia do que estava falando.", "negative"),  # noqa: E501
    ("Leonardo Costa", "Perdi mais de uma hora tentando resolver algo simples e saí com mais dúvidas do que entrei.", "negative"),  # noqa: E501
    ("Eduardo Bezerra", "O suporte simplesmente me ignorou por horas. Inaceitável para um serviço profissional.", "negative"),  # noqa: E501
    ("Fernanda Silva", "Problema recorrente, nunca resolvem de forma definitiva. Já perdi a paciência com essa empresa.", "negative"),  # noqa: E501
    ("Marcelo Cunha", "Total despreparo. A equipe não entendeu o problema e ainda sugeriu uma solução errada.", "negative"),  # noqa: E501
    ("Sabrina Dias", "Serviço horrível. Me deixaram sem resposta em um momento crítico para minha operação.", "negative")  # noqa: E501
]


@pytest.mark.parametrize("nome,texto,esperado", CASOS)
def test_classificacao_sentimento(nome: str, texto: str, esperado: str):
    """
    Testa se o classificador de sentimento retorna o resultado esperado
    para vários casos.

    Args:
        nome (str): Nome do caso de teste (para referência).
        texto (str): Texto da avaliação.
        esperado (str): Sentimento esperado ('positive', 'neutral'
        ou 'negative').

    Asserts:
        O resultado da classificação deve ser igual ao esperado.
    """
    resultado = classify_sentiment(texto)
    assert resultado == esperado, (
        f"Classificação incorreta para {nome}: esperado '{esperado}', "
        f"obtido '{resultado}'. Detalhes: {sentiment_classifier.analyze_sentiment_strength(texto)}"  # noqa: E501
    )


def test_acuracia_geral_e_por_categoria():
    """
    Testa a acurácia geral e por categoria, garantindo mínimos aceitáveis.

    Acurácia mínima geral: 90%
    Acurácia mínima por categoria: 80%

    Asserts:
        As acurácias devem atender os mínimos definidos.
    """
    total_casos = len(CASOS)
    acertos = 0
    acertos_categoria = {"positive": 0, "neutral": 0, "negative": 0}
    totais_categoria = {"positive": 0, "neutral": 0, "negative": 0}

    for nome, texto, esperado in CASOS:
        totais_categoria[esperado] += 1
        resultado = classify_sentiment(texto)
        if resultado == esperado:
            acertos += 1
            acertos_categoria[esperado] += 1

    acuracia_geral = acertos / total_casos
    assert acuracia_geral >= 0.9, f"Acurácia geral de {acuracia_geral:.1%} está abaixo do mínimo de 90%"  # noqa: E501

    for categoria in totais_categoria:
        if totais_categoria[categoria] > 0:
            acuracia_cat = acertos_categoria[categoria] / totais_categoria[categoria]  # noqa: E501
            assert acuracia_cat >= 0.8, (
                f"Acurácia da categoria '{categoria}' de {acuracia_cat:.1%} está abaixo do mínimo de 80%"  # noqa: E501
            )


ORIGINAIS = [
    ("Ana Silva", "O atendimento foi rápido e eficiente, mas senti que poderia ser mais detalhado em alguns pontos técnicos. Por exemplo, ao explicar a falha que ocorreu, o atendente não conseguiu detalhar a causa raiz do problema, o que me deixou com dúvidas sobre o que realmente aconteceu. No geral, foi uma experiência satisfatória, mas acredito que poderia ser mais completa.", "neutral"),  # noqa: E501
    ("Bruno Souza", "Estou extremamente satisfeito com o suporte! Resolveram meu problema de forma ágil e com clareza nas explicações. Além de resolverem o erro no sistema que estava impedindo a execução de uma função crítica para o meu negócio, eles ainda sugeriram melhorias para evitar que o problema ocorresse novamente. O atendimento foi muito acima do esperado!", "positive"),  # noqa: E501
    ("Carlos Pereira", "O serviço foi muito demorado e o atendente parecia completamente despreparado. Precisei repetir meu problema várias vezes, e mesmo assim senti que ele não estava entendendo o que eu estava dizendo. Perdi muito tempo, e o pior de tudo é que o problema não foi resolvido ao final. Vou reconsiderar continuar usando esse serviço.", "negative"),  # noqa: E501
    ("Daniela Rocha", "A equipe de suporte foi extremamente atenciosa e dedicada. Adorei o atendimento, pois desde o início até a resolução do meu problema fui informado de cada etapa do processo. Eles fizeram de tudo para que eu entendesse o que estava acontecendo e até me ofereceram um acompanhamento extra para garantir que tudo estivesse funcionando corretamente após a solução.", "positive"),  # noqa: E501
    ("Eduardo Lima", "Infelizmente, não conseguiram resolver meu problema, e fiquei muito decepcionado. Além da demora para obter uma resposta clara, não houve um acompanhamento adequado após o primeiro contato, o que deixou a sensação de que meu problema não era uma prioridade. Esperava mais de uma empresa com uma reputação tão boa no mercado.", "negative"),  # noqa: E501
    ("Fernanda Carvalho", "O sistema que utilizo tem funcionado bem, mas o suporte não foi tão eficiente quanto eu esperava. Tive que esperar bastante tempo por uma resposta e, quando ela finalmente veio, não era clara o suficiente para que eu pudesse seguir as instruções por conta própria. A experiência foi mediana, espero que melhorem essa parte do serviço.", "neutral"),  # noqa: E501
    ("Gabriel Costa", "Ótimo serviço! A equipe de suporte foi muito prestativa e realmente se dedicou a resolver o meu problema. Além de solucionarem a questão com rapidez, eles ainda se certificaram de que eu entendesse o que havia causado o erro e como evitar que ele ocorresse novamente no futuro. Superou completamente as minhas expectativas.", "positive"),  # noqa: E501
    ("Helena Ribeiro", "O atendente foi educado e respeitoso durante todo o processo, mas infelizmente não conseguiu solucionar o problema técnico que eu estava enfrentando. Ele tentou várias abordagens, mas ao final, ainda fiquei sem uma solução definitiva. Agradeço pelo esforço, mas o resultado final me deixou frustrado.", "neutral"),  # noqa: E501
    ("Igor Almeida", "Não tive uma boa experiência. Precisei contatar o suporte diversas vezes até que uma solução adequada fosse finalmente apresentada. A falta de consistência nas respostas e a demora entre os contatos me deixaram bastante insatisfeito. Era um problema simples de configuração, mas o processo todo acabou tomando muito mais tempo do que o necessário.", "negative"),  # noqa: E501
    ("Julia Martins", "Fui muito bem atendido desde o início, e o problema foi resolvido sem nenhuma complicação. O serviço foi prático, eficiente e me surpreendeu pela rapidez com que conseguiram resolver tudo. A comunicação também foi excelente, me mantendo informado a cada passo. Um atendimento realmente de qualidade.", "positive"),  # noqa: E501
]


@pytest.mark.parametrize("nome,texto,esperado", ORIGINAIS)
def test_casos_originais(nome: str, texto: str, esperado: str):
    """
    Testa o classificador com os casos originais fornecidos.

    Args:
        nome (str): Nome do caso.
        texto (str): Texto da avaliação.
        esperado (str): Sentimento esperado.

    Asserts:
        A acurácia total deve ser pelo menos 90%.
    """
    total = len(ORIGINAIS)
    acertos = 0
    erros = []

    for n, t, e in ORIGINAIS:
        r = classify_sentiment(t)
        if r == e:
            acertos += 1
        else:
            erros.append((n, e, r))

    acuracia = acertos / total
    assert acuracia >= 0.9, f"Acurácia dos casos originais ({acuracia:.1%}) abaixo do mínimo de 90%"  # noqa: E501

    if erros:
        detalhes = "\n".join(f"{n}: esperado={exp}, obtido={res}" for n, exp, res in erros)  # noqa: E501
        pytest.fail(f"Erros de classificação:\n{detalhes}")
