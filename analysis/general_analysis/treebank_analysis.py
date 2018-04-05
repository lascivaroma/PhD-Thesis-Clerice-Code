from .corpus_analysis import time_analysis

from helpers.reader.curated import get_graph, get_texts, get_text_length_dict
from helpers.metadata import wordcounts
import matplotlib.pyplot as plt


def draw_tokens_representation(series, fname, template="{corpus} ({words} mots)"):
    """ Draw the series in one fig"""
    fig = plt.figure()
    for name, totalWord, serie in series:
        ax = serie.plot(
            kind="area",
            title="Mots écrits par auteur vivant à une période donnée",
            legend=True,
            label=template.format(corpus=name, words=totalWord)
        )
        fig.add_axes(ax)
    plt.savefig(fname)


def run(corpora):
    """ Run a generic analysis"""
    graph = get_graph()

    # And the list of texts as a dictionary of text: text_length
    texts = get_texts()

    # And the list of texts as a dictionary of text: text_length
    texts_dict = get_text_length_dict(texts)

    wc = wordcounts.build()

    data = [
        (
            "Catalogue Latin d'après le Perseus Catalog",
            sum([v for li in wc.values() for v in li]),
            *time_analysis(graph, wc, False, False)
        ),
        (
            "Corpus global latin ouvert Capitains",
            sum([v for li in texts_dict.values() for v in li]),
            *time_analysis(graph, texts_dict)
        )
    ]
    for corpus in corpora:
        corpus.parse()
        data.append((
            corpus.name,
            sum([len(li) for li in corpus.words.values()]),
            *time_analysis(graph, corpus.tokens_by_document, False, False))
        )
    # MEME CHOSE AVEC LES POURCENTAGES PAR RAPPORT a TEXTS_DICT

    draw_tokens_representation(
        series=[
            (name, words, tokens_per_year)
            for name, words, accumulated_tokens, tokens_per_year, text_per_year in data
        ],
        fname="results/analysis/corpus_analysis/treebank_representativite.png"
    )
    draw_tokens_representation(
        series=[
            (name, words, text_per_year)
            for name, words, accumulated_tokens, tokens_per_year, text_per_year in data
        ],
        fname="results/analysis/corpus_analysis/treebank_representativite_texts.png"
    )
    draw_tokens_representation(
        series=[
            (name, words, tokens_per_year/data[0][3])
            for name, words, accumulated_tokens, tokens_per_year, text_per_year in data[1:]
        ],
        fname="results/analysis/corpus_analysis/treebank_representativite_relatif.png",
        template="{corpus} ({words} mots)"
    )

    template = "| {:<64} | {:<10} |\n"
    for corpus in corpora:
        with open("results/analysis/corpus_analysis/treebank_"+corpus.name+".md", "w") as f:
            f.write(template.format('Documents', 'Tokens'))
            f.write(template.format("--", "--"))
            for word, tokens in corpus.words.items():
                f.write(template.format(word, len(tokens)))
