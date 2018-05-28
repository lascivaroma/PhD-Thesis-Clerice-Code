from helpers.reader.curated import get_graph, get_texts, get_text_length_dict, texts_date, tg_dates, ignored
from pandas import Series
from operator import itemgetter
import matplotlib.pyplot as matplot_plot
from MyCapytain.common.reference import URN
from numpy import mean, median

PERIODS = 25
START, END = -300, 750
PRINT = False

def texts_between(graph, start, end):
    """ Get text using a range

    :param graph:
    :param start:
    :param end:
    :return:
    """
    filters = """?s lr:EndDate ?edate .
    ?s lr:StartDate ?sdate .
    FILTER (( {start} <= ?sdate  &&  ?sdate < {end} ) || ( {start} <= ?edate  &&  ?edate < {end} )) .""".format(
        start=start, end=end
    )
    results = graph.query("""SELECT DISTINCT ?s
        WHERE {
    """ + filters + """
        }""")
    return [str(r) for r, *_ in results]


def authors_name(graph):
    """ Get texts names

    :param graph: Graph to use to retrieve date
    :return: {TextID : [StartDate, EndDate]}
    """
    results = graph.query("""SELECT ?s ?aname
        WHERE {
            ?s dc:author ?aname .
            ?s lr:Ignore false
        }""")
    return {str(r): n for r, n in results}


def time_analysis_range(graph, texts):
    """ Analysis the repartition of text size

    :param graph: RDF Graph of metadata
    :param texts: Dictionary of texts length {text_id : [TokenCount, ...]}
    :return:
    """
    # Assigned Period
    splitted_texts = [
        (dateStart, texts_between(graph, dateStart, dateStart+PERIODS))
        for dateStart in range(START, END, PERIODS)
    ]
    range_length = []
    text_count = []

    for _, text_group in splitted_texts:
        temp_token, temp_text_count = [], 0
        for text in text_group:
            try:
                temp_token += texts[text]
                temp_text_count += 1
            except KeyError:
                print(text + " was not found in text length dictionary")

        range_length.append(sum(temp_token))
    # Realign the dict with length
    serie = Series(
        data=range_length,
        index=[dateStart for dateStart, _ in splitted_texts]
    )
    plot = serie.plot(kind="bar", alpha=0.5)
    figure = plot.get_figure()
    figure.savefig('results/analysis/corpus_analysis/time_tokens_range.png')


def time_analysis(graph, texts, draw=True, print_missing=True):
    """ Analysis the repartition of text size

    :param graph: RDF Graph of metadata
    :param texts: Dictionary of texts length {text_id : [TokenCount, ...]}
    :param draw: Draw the figure
    :param print_missing: Print if the text is in the graph but is missing
    :return:
    :rtype: (Series, Series, Series)
    """
    # Get dates for each text
    dates = {k: range(values[0], values[1]+1) for k, values in texts_date(graph).items()}
    to_ignore = ignored(graph)

    # Create tokens year dict
    tokens_per_year = {year: 0 for year in range(START, END+1)}
    accumulated_tokens = {year: 0 for year in range(START, END + 1)}
    text_per_year = {year: 0 for year in range(START, END+1)}

    # Generate an helper for accumulated tokens
    first_year_tokens = []

    # Check that all texts are in the date informations
    # If they do not have date, check that we have Textgroup information
    textgroups = {}
    for text_id in texts:
        if text_id not in dates and text_id not in to_ignore:
            tg = URN(text_id)
            tg = str(tg.upTo(URN.TEXTGROUP))
            _dates = tg_dates(graph, tg)
            if _dates:
                textgroups[text_id] = _dates
                if PRINT:
                    print("Dates for {} comes from textgroup data".format(text_id))
            else:
                print(text_id + " has no dates informations")
    if len(textgroups):
        dates.update({
            k: range(values[0], values[1] + 1)
            for k, values in textgroups.items()
        })

    # Feed the tokens !
    for text_id, daterange in dates.items():
        temp_text_count, temp_token = 0, []
        try:
            temp_token = texts[text_id]
            temp_text_count = 1
        except KeyError:
            if print_missing:
                print(text_id + " was not found in text length dictionary")

        _start = True
        if temp_text_count == 1:
            for year in daterange:
                tokens_per_year[year] += sum(temp_token)
                text_per_year[year] += temp_text_count
                if _start is True:
                    first_year_tokens.append((year, sum(temp_token)))
                    _start = False

    first_year_tokens = sorted(first_year_tokens, key=itemgetter(0))
    for year in range(START, END + 1):
        # Get the previous year + all texts where the first year match
        accumulated_tokens[year] = accumulated_tokens.get(year-1, 0) + \
                                   sum([tokens for year_tokens, tokens in first_year_tokens if year_tokens == year])

    accumulated_tokens = Series(data=accumulated_tokens)
    if draw:
        plot = accumulated_tokens.plot(kind="line", title="Mots accumulés par année")
        figure = plot.get_figure()
        figure.savefig('results/analysis/corpus_analysis/accumulated_tokens.png')

    tokens_per_year = Series(data=tokens_per_year)
    if draw:
        matplot_plot.figure()
        plot = tokens_per_year.plot(kind="line", title="Mots écrits par auteur vivant à une période donnée")
        figure = plot.get_figure()
        figure.savefig('results/analysis/corpus_analysis/tokens_per_year.png')
        del plot, figure

    text_per_year = Series(data=text_per_year)
    if draw:
        matplot_plot.figure()
        plot = text_per_year.plot(kind="line", title="Textes écrits par un auteur vivant à une période donnée")
        figure = plot.get_figure()
        figure.savefig('results/analysis/corpus_analysis/texts_per_year.png')
        del plot, figure
        matplot_plot.figure()

    return accumulated_tokens, tokens_per_year, text_per_year


def passage_size_analysis(texts_dict):
    # Get the violin representation
    flatten_length = [x for lengths in texts_dict.values() for x in lengths]

    fig, axes = matplot_plot.subplots(1, 1)
    series = Series(data=flatten_length)
    series.hist(ax=axes, log=True, bins=200, histtype="bar")
    axes.set_xlabel("Taille (en mots) des passages")
    axes.set_ylabel("Nombre de passages")
    fig.tight_layout()
    fig.savefig('results/analysis/corpus_analysis/passage_size_distribution.png')


def authors_annex(graph, texts_dict):
    """ Creates a CSV file for annexes of the thesis with name of the author, number of tokens

    :param graph: Graph that needs to be used for metadata
    :param texts_dict:
    :return:
    """
    authors = authors_name(graph)
    reversed_authors = {}
    for ed_id, author in authors.items():
        _id = URN(ed_id)
        tg = str(_id.upTo(URN.TEXTGROUP))
        if author not in reversed_authors:
            reversed_authors[author] = {
                "name": author,
                "ids": [],
                "texts": [],
                "passages": [],
                "tokens": [],
                "tokens_notflat": []
            }
        reversed_authors[author]["ids"].append(tg)
        reversed_authors[author]["texts"].append(ed_id)
        if ed_id in texts_dict:
            reversed_authors[author]["passages"].append(len(texts_dict[ed_id]))
            reversed_authors[author]["tokens"].append(sum(texts_dict[ed_id]))
            reversed_authors[author]["tokens_notflat"] += texts_dict[ed_id]
        else:
            reversed_authors[author]["passages"].append(0)
            reversed_authors[author]["tokens"].append(0)
            reversed_authors[author]["tokens_notflat"] += [0]

    with open("results/analysis/corpus_analysis/authors.tsv", "w") as f:
        f.write("\t".join(["Auteur", "Nombre de textes", "Nombre de passages", "Nombre de mots", "Médiane de taille de passage", "Moyenne de taille de passage"])+"\n")
        for aname in sorted(list(reversed_authors.keys())):
            f.write(
                "\t".join([
                    str(lmb(reversed_authors[aname][key]))
                    for key, lmb in
                    [
                        ("name", lambda x: x),
                        ("texts", lambda x: len(x)),
                        ("passages", lambda x: sum(x)),
                        ("tokens", lambda x: sum(x)),
                        ("tokens_notflat", lambda x: median(x)),
                        ("tokens_notflat", lambda x: mean(x)),
                    ]
                ])+"\n"
            )


def run():
    # We get the graph
    graph = get_graph()

    # And the list of texts as a dictionary of text: text_length
    texts = get_texts()
    print("Texts retrieved")
    # And the list of texts as a dictionary of text: text_length
    texts_dict = get_text_length_dict(texts)
    print("Texts lengths retrieved")

    # Run time analysis
    accumulated_tokens, tokens_per_year, text_per_year = time_analysis(graph, texts_dict)
    print("Texts time analysis done")

    # Passage Size Analysis
    passages_repartition = passage_size_analysis(texts_dict)
    print("Passage repartition analysis done")

    # Generation of annexes
    authors_annexes = authors_annex(graph, texts_dict)
    print("Annexes d'auteur construites")


if __name__ == "__main__":
    run()

