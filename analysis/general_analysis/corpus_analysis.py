from helpers.reader.curated import get_graph, get_texts, get_text_length_dict
from pandas import Series
from operator import itemgetter
import matplotlib.pyplot as matplot_plot

PERIODS = 25
START, END = -300, 750


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


def texts_date(graph):
    """ Get text using a range

    :param graph: Graph to use to retrieve date
    :return: {TextID : [StartDate, EndDate]}
    """
    results = graph.query("""SELECT DISTINCT ?s ?sdate ?edate
        WHERE {
            ?s lr:EndDate ?edate .
            ?s lr:StartDate ?sdate .
            ?s lr:Ignore false
        }""")
    return {str(r): (int(s), int(e)) for r, s, e in results}


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


def time_analysis(graph, texts):
    """ Analysis the repartition of text size

    :param graph: RDF Graph of metadata
    :param texts: Dictionary of texts length {text_id : [TokenCount, ...]}
    :return:
    """
    # Get dates for each text
    dates = {k: range(values[0], values[1]+1) for k, values in texts_date(graph).items()}

    # Create tokens year dict
    tokens_per_year = {year: 0 for year in range(START, END+1)}
    accumulated_tokens = {year: 0 for year in range(START, END + 1)}
    text_per_year = {year: 0 for year in range(START, END+1)}

    # Generate an helper for accumulated tokens
    first_year_tokens = []

    # Feed the tokens !
    for text_id, daterange in dates.items():
        temp_text_count, temp_token = 0, []
        try:
            temp_token = texts[text_id]
            temp_text_count = 1
        except KeyError:
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

    serie = Series(data=accumulated_tokens)
    plot = serie.plot(kind="line", title="Mots accumulés par année")
    figure = plot.get_figure()
    figure.savefig('results/analysis/corpus_analysis/accumulated_tokens.png')

    matplot_plot.figure()
    serie = Series(data=tokens_per_year)
    plot = serie.plot(kind="line", title="Mots écrits par auteur vivant à une période donnée")
    figure = plot.get_figure()
    figure.savefig('results/analysis/corpus_analysis/tokens_per_year.png')
    del plot, figure

    matplot_plot.figure()
    serie = Series(data=text_per_year)
    plot = serie.plot(kind="line", title="Textes écrits par un auteur vivant à une période donnée")
    figure = plot.get_figure()
    figure.savefig('results/analysis/corpus_analysis/texts_per_year.png')
    del plot, figure

    return accumulated_tokens, tokens_per_year, text_per_year


def passage_size_analysis(graph, texts_dict):
    fre_name = authors_name(graph)

    # Get the violin representation
    flatten_length = [x for lengths in texts_dict.values() for x in lengths]
    fig = matplot_plot.figure()
    axes = fig.add_subplot(111)
    axes.violinplot(flatten_length)
    matplot_plot.show()


def run():
    # We get the graph
    graph = get_graph()

    # And the list of texts as a dictionary of text: text_length
    texts = get_texts()

    # And the list of texts as a dictionary of text: text_length
    texts_dict = get_text_length_dict(texts)

    # Run time analysis
    #accumulated_tokens, tokens_per_year, text_per_year = time_analysis(graph, texts_dict)

    # Passage Size Analysis
    passages_repartition = passage_size_analysis(graph, texts_dict)


if __name__ == "__main__":
    run()

