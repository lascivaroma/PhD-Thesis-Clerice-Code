from collections import namedtuple
from csv import DictReader
import rdflib
import rdflib.namespace
import MyCapytain.common.constants
from .ns import SemanticCut, StartDate, EndDate, Ignore
from ..printing import SUBTASK_SEPARATOR, TASK_SEPARATOR, SUBSUBTASK_SEPARATOR


additional_infos = namedtuple("AdditionalInfo", ["CutAt", "StartDate", "EndDate", "Ignore", "Author"])


def read_datation_spreadsheet(src="data/raw/datation.tsv"):
    """ Read the datation spreadsheet
    """
    print(TASK_SEPARATOR+"Parsing original csv file")
    urns = {}
    with open(src) as src_file:
        reader = DictReader(src_file, delimiter="\t")
        for row in reader:
            try:
                urns[row["URN"]] = additional_infos(
                    CutAt=int(row["Citation level"]),
                    Ignore=row["Ignore"] == 'x',
                    StartDate=row["Birth"],
                    EndDate=row["Death"],
                    Author=row["Nom FR"]
                )
            except Exception:
                print(SUBTASK_SEPARATOR+"Text {} has an error".format(row["URN"]))
    return urns


def feed_resolver(metadata_urn, resolver):
    """ Feed the resolver with additional metadata

    :param metadata_urn:
    :param resolver: Resolver
    :type resolver: capitains_nautilus.cts.resolver.NautilusCTSResolver
    :return:
    """
    print(TASK_SEPARATOR+"Feeding the resolver with data")
    texts = [str(text.id) for text in resolver.getMetadata().readableDescendants]
    for urn, informations in metadata_urn.items():
        try:
            obj = resolver.getMetadata(urn)

            node, graph = obj.asNode(), obj.graph
            graph.add((node, StartDate, rdflib.Literal(informations.StartDate, datatype=rdflib.namespace.XSD.integer)))
            graph.add((node, EndDate, rdflib.Literal(informations.EndDate, datatype=rdflib.namespace.XSD.integer)))
            graph.add((node, Ignore, rdflib.Literal(informations.Ignore, datatype=rdflib.namespace.XSD.boolean)))
            graph.add((node, SemanticCut, rdflib.Literal(informations.CutAt, datatype=rdflib.namespace.XSD.integer)))
            graph.add((node, rdflib.namespace.DC.term("author"), rdflib.Literal(informations.Author, lang="fre")))
            texts.pop(texts.index(urn))
        except :
            print(SUBTASK_SEPARATOR+"{} was not found in the corpus but is annotated".format(urn))
    print(SUBTASK_SEPARATOR+"Texts having no enhanced metadata : "+", ".join(texts))
    return resolver


def write_inventory(resolver, tgt="./data/curated/inventory.xml"):
    print(TASK_SEPARATOR+"Exporting the annotated inventory")
    data = resolver.getMetadata()

    inventory = data.export(MyCapytain.common.constants.Mimetypes.XML.CTS)
    with open(tgt, "w") as target_file:
        target_file.write(inventory)
    with open(tgt+".turtle", "w") as target_file:
        target_file.write(data.graph.serialize(format='turtle').decode())

