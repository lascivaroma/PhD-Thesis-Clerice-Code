from lxml import etree
from ..reader.curated import get_graph, tg_dates, ignored
from MyCapytain.common.reference import URN
import os
import glob

NS = {
    "mods": "http://www.loc.gov/mods/v3"
}
MISSING = []
FOUND = []


def parse_namespace(graph, path, ns="latinLit", ignore=[]):
    """ Parses a namespace and produce a time analysis compatible dictionary of {textId: [tokenCount]}

    :param graph: RDF Graph
    :param path: Path where the function should look for MODS
    :param ns: Namespace to look in
    :return: {textId : [tokenCount]}
    """
    token_count = {}

    for textgroup_dir in glob.glob(os.path.join(path, ns, "**")):
        textgroup = "urn:cts:{ns}:{tg}".format(
            ns=ns,
            tg=textgroup_dir.split("/")[-1]
        )

        if textgroup in ignore:
            continue

        dates = tg_dates(graph, textgroup)
        if not dates and ns == "latinLit":
            MISSING.append(textgroup)
            continue

        for work_dir in glob.glob(os.path.join(textgroup_dir, "**")):
            max_count = 0
            urn = textgroup+"."+work_dir.split("/")[-1]

            for edition_mods_file in glob.glob(os.path.join(work_dir, "**", "*.xml")):
                basename = os.path.basename(edition_mods_file)
                urn = "urn:cts:{ns}:{version}".format(
                    ns=ns,
                    version=basename.replace("mods1.xml", "")
                )
                try:
                    with open(edition_mods_file) as mods_io_wrapper:
                        mods_xml = etree.parse(mods_io_wrapper)
                        word_count = mods_xml.xpath("//mods:extent[@unit='words']/mods:total/text()", namespaces=NS)
                        if word_count:
                            word_count = int(word_count[0])
                            if max_count < word_count:
                                max_count = word_count
                except:
                    continue
            token_count[urn] = [max_count]
    return token_count


def build(path="data/raw/metadatas/PerseusDL_catalog_data/catalog_data-*/mods"):
    """ Build a {textId: [tokenCount]} of all known texts of annotated authors

    :param path: Path where the function should look for MODS
    :return: {textId : [tokenCount]}
    """
    graph = get_graph()

    TG_IGNORE = [str((URN(text)).upTo(URN.TEXTGROUP)) for text in ignored(graph)]

    texts = parse_namespace(graph, path, ignore=TG_IGNORE)
    texts.update(parse_namespace(graph, path, ns="greekLit", ignore=TG_IGNORE))

    print("{} are missing dates".format(len(MISSING)))
    return texts
