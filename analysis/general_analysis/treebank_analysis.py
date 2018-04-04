from .corpus_analysis import get_graph, get_texts, get_text_length_dict, time_analysis
import matplotlib.pyplot as plt


def draw_tokens_representation(series, names):
    """ Draw the series in one fig"""
    fig = plt.figure()
    for name, totalWord, accumulated_tokens, tokens_per_year, text_per_year in series:
        ax = tokens_per_year.plot(
            kind="area",
            title="Mots écrits par auteur vivant à une période donnée",
            legend=True,
            label="{corpus} ({words} mots)".format(corpus=name, words=totalWord)
        )
        fig.add_axes(ax)
    plt.savefig("results/analysis/corpus_analysis/treebank_representativite.png")


def run(corpora):
    """ Run a generic analysis"""
    graph = get_graph()

    # And the list of texts as a dictionary of text: text_length
    texts = get_texts()

    # And the list of texts as a dictionary of text: text_length
    texts_dict = get_text_length_dict(texts)

    data = [("Corpus global latin ouvert Capitains", sum([v for li in texts_dict.values() for v in li]), *time_analysis(graph, texts_dict))]
    for corpus in corpora:
        corpus.parse()
        data.append((
            corpus.name,
            sum([len(li) for li in corpus.words.values()]),
            *time_analysis(graph, corpus.tokens_by_document, False, False))
        )

    # MEME CHOSE AVEC LES POURCENTAGES PAR RAPPORT a TEXTS_DICT

    draw_tokens_representation(data, ("x.png", "y.png", "z.png"))

    template = "| {:<64} | {:<10} |\n"
    for corpus in corpora:
        with open("results/analysis/corpus_analysis/treebank_"+corpus.name+".md", "w") as f:
            f.write(template.format('Documents', 'Tokens'))
            f.write(template.format("--", "--"))
            for word, tokens in corpus.words.items():
                f.write(template.format(word, len(tokens)))
