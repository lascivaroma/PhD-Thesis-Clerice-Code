from helpers.reader.curated import get_graph, get_texts, text_length
from pandas import Series

PERIODS = 25
START, END = -300, 750


def texts_between(graph, start, end):
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


def time_analysis(graph, texts):
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
    figure.savefig('results/analysis/corpus_analysis/time_tokens.png')


def run():
    # We get the graph
    graph = get_graph()

    # And the list of texts as a dictionary of text: text_length
    texts = get_texts()

    # And the list of texts as a dictionary of text: text_length
    texts_dicts = {text_id: [] for path, text_id in texts}
    for text, text_id in texts:
        texts_dicts[text_id].append(text_length(text))

    # Run time analysis
    time_ana = time_analysis(graph, texts_dicts)


if __name__ == "__main__":
    run()

