from .corpus_analysis import time_analysis
import collections
from helpers.reader.curated import get_graph, get_texts, get_text_length_dict
from helpers.metadata import wordcounts
import matplotlib.pyplot as plt


_Serie = collections.namedtuple("Serie",
                                ["name", "text_count", "word_count",
                                 "accumulated_tokens", "tokens_per_year", "text_per_year"])


def draw_tokens_representation(
        series, fname,
        title="Mots écrits par auteur vivant à une période donnée", template="{corpus} ({words} mots)",
        kind="line",
        colors_index_offset=0):

    """ Draw the series in one fig"""

    # These are the "Tableau 20" colors as RGB.
    COLORS = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
                 (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
                 (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
                 (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
                 (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)][colors_index_offset:]

    # Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.
    for i in range(len(COLORS)):
        r, g, b = COLORS[i]
        COLORS[i] = r / 255., g / 255., b / 255.

    fig = plt.figure(figsize=(12, 14))

    index = 0
    for name, totalWord, serie in series:
        ax = serie.plot(
            kind=kind,
            title=title,
            legend=True,
            label=template.format(corpus=name, words=totalWord),
            color=COLORS[index]
        )
        index += 1
        fig.add_axes(ax)

    # Put a legend below current axis
    fig.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)

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
        _Serie(
            "Catalogue Latin d'après le Perseus Catalog",
            len(wc),
            sum([v for li in wc.values() for v in li]),
            *time_analysis(graph, wc, False, False)
        ),
        _Serie(
            "Corpus global latin ouvert Capitains",
            len(texts_dict),
            sum([v for li in texts_dict.values() for v in li]),
            *time_analysis(graph, texts_dict)
        )
    ]
    for corpus in corpora:
        corpus.parse()
        data.append(_Serie(
            corpus.name,
            len(corpus.words),
            sum([len(li) for li in corpus.words.values()]),
            *time_analysis(graph, corpus.tokens_by_document, False, False))
        )
    # MEME CHOSE AVEC LES POURCENTAGES PAR RAPPORT a TEXTS_DICT

    draw_tokens_representation(
        series=[
            (serie.name, serie.word_count, serie.tokens_per_year)
            for serie in data
        ],
        fname="results/analysis/corpus_analysis/treebank_representativite.png"
    )
    draw_tokens_representation(
        series=[
            (serie.name, serie.word_count, serie.accumulated_tokens)
            for serie in data
        ],
        title="Mot accumulés",
        fname="results/analysis/corpus_analysis/treebank_accumulation.png"
    )
    draw_tokens_representation(
        series=[
            (serie.name, serie.text_count, serie.text_per_year)
            for serie in data
        ],
        fname="results/analysis/corpus_analysis/treebank_representativite_texts.png",
        kind="bar",
        template="{corpus} ({words} textes)",
        title="Textes écrits par auteur vivant à une période donnée"
    )
    draw_tokens_representation(
        series=[
            (serie.name, serie.word_count, serie.accumulated_tokens/data[0].accumulated_tokens)
            for serie in data[2:]
        ],
        fname="results/analysis/corpus_analysis/treebank_representativite_relatif.png",
        template="{corpus} ({words} mots)",
        title="Représentativité du corpus vis-à-vis des décompte du catalogue de Perseus (en mots accumulés)",
        colors_index_offset=2
    )

    template = "| {:<64} | {:<10} |\n"
    for corpus in corpora:
        with open("results/analysis/corpus_analysis/treebank_"+corpus.name+".md", "w") as f:
            f.write(template.format('Documents', 'Tokens'))
            f.write(template.format("--", "--"))
            for word, tokens in corpus.words.items():
                f.write(template.format(word, len(tokens)))
