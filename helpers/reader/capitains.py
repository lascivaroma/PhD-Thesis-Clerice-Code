from capitains_nautilus.cts.resolver import NautilusCTSResolver
from MyCapytain.common.constants import Mimetypes
import glob
from ..metadata.ns import THESE_NS, THESE_NS_PREFIX, SemanticCut
from ..printing import TASK_SEPARATOR, SUBTASK_SEPARATOR
import logging
import os
import shutil
import re
import rdflib.namespace
from lxml import etree
from unidecode import unidecode


with open("./helpers/reader/passage.transform.xsl") as f:
    xml = etree.parse(f)
_transformer = etree.XSLT(xml)
_hyphen = re.compile("-[\s\n]+")
_number = re.compile("\d+")

IGNORED = [
    "urn:cts:phi0474.phi045.perseus-lat1:praef",
    "urn:cts:phi0474.phi045.perseus-lat1:index",
    "urn:cts:phi0474.phi048.perseus-lat1:praef",
    "urn:cts:phi0474.phi048.perseus-lat1:index",
    "urn:cts:phi0474.phi049.perseus-lat1:praef",
    "urn:cts:phi0474.phi049.perseus-lat1:index"
]

def transform(resource):
    return unidecode(
        _number.sub(
            "", 
            _hyphen.sub(
                "",
                str(_transformer(resource))
            ).
            replace("AUG ", "Augustus").
            replace("/", "")
        )
    )


def make_resolver(directories=None, additional_metadata=None):
    """ Generate the CapiTainS Resolver and add metadata to it
    """
    if directories is None:
        directories = glob.glob("data/raw/corpora/**/**")
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.CRITICAL)

    resolver = NautilusCTSResolver(resource=directories, logger=logger)
    resolver.inventory.graph.namespace_manager.bind(THESE_NS_PREFIX, THESE_NS)
    resolver.inventory.graph.namespace_manager.bind("dc", rdflib.namespace.DC)
    return resolver


def create_raw_text(resolver, tgt="data/curated/corpus/generic", step=20):
    regex = re.compile('[^\w\s\.\;]')
    ponctu = re.compile("\.\;")
    normalize = re.compile('\s+')
    print(TASK_SEPARATOR+"Creating the corpus raw texts")
    if os.path.isdir(tgt):
        print(SUBTASK_SEPARATOR+"Cleaning up old text")
        shutil.rmtree(tgt)
    print(SUBTASK_SEPARATOR+"Generating folder")
    i, y = 1, 1
    for text in resolver.getMetadata().readableDescendants:
        if (i % 20) == 0:
            print(SUBTASK_SEPARATOR+"{} texts done".format(i))
        subtarget = tgt+"/"+str(text.id)

        annotations = list(text.graph.objects(text.asNode(), SemanticCut))
        if len(annotations) == 0:
            y += 1
            print(SUBTASK_SEPARATOR+"{} text has no SemanticCut".format(str(text.id)))
        else:
            level = int(annotations[0])
            os.makedirs(subtarget)
            excludes = [
                "tei:orig", "tei:abbr", "tei:head", "tei:title", "tei:teiHeader", "tei:del"
            ]
            if level == 0:
                contents = {
                    "": "\n".join([

                        transform(
                            resolver.getTextualNode(textId=text.id, subreference=node).export(Mimetypes.PYTHON.ETREE)#,exclude=excludes)
                        )
                        for node in resolver.getReffs(textId=text.id, level=0)
                    ])
                }
            else:
                reffs = resolver.getReffs(textId=text.id, level=level)
                contents = {
                    str(reff): transform(
                        resolver.getTextualNode(textId=text.id, subreference=reff).export(Mimetypes.PYTHON.ETREE)#, exclude=excludes)
                    )
                    for reff in reffs
                    if str(text.id)+":"+str(reff) not in IGNORED
                }
            for file, content in contents.items():
                with open(subtarget+"/"+file+".txt", "w") as f:
                    f.write(normalize.sub(" ", regex.sub(" ", ponctu.sub(" . ", content.strip()))))
        i += 1
    print(SUBTASK_SEPARATOR+"{}/{} texts done".format(i, i))
    print(SUBTASK_SEPARATOR+"{}/{} texts not converted because they lacked SemanticCut information".format(y, i))
