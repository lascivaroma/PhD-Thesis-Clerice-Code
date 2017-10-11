from capitains_nautilus.cts.resolver import NautilusCTSResolver
from MyCapytain.common.constants import Mimetypes
import glob
from ..metadata.ns import THESE_NS, THESE_NS_PREFIX, SemanticCut
from ..printing import TASK_SEPARATOR, SUBTASK_SEPARATOR
import logging
import os
import shutil
import re


def make_resolver(directories=None, additional_metadata=None):
    """ Generate the CapiTainS Resolver and add metadata to it
    """
    if directories is None:
        directories = glob.glob("data/raw/corpora/**/**")
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.CRITICAL)

    resolver = NautilusCTSResolver(resource=directories, logger=logger)
    resolver.inventory.graph.namespace_manager.bind(THESE_NS_PREFIX, THESE_NS)
    return resolver


def create_raw_text(resolver, tgt="data/curated/corpus/generic", step=20):
    regex = re.compile('[^a-zA-Z ]')
    normalize = re.compile('\s+')
    print(TASK_SEPARATOR+"Creating the corpus raw texts")
    if os.path.isdir(tgt):
        print(SUBTASK_SEPARATOR+"Cleaning up old text")
        shutil.rmtree(tgt)
    print(SUBTASK_SEPARATOR+"Generating folder")
    i, y  = 1, 1
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
                "tei:note", "tei:orig", "tei:abbr", "tei:head", "tei:title", "tei:teiHeader"
            ]
            if level == 0:
                contents = {
                    "": "\n".join([
                        resolver.getTextualNode(textId=text.id, subreference=node).export(Mimetypes.PLAINTEXT, exclude=excludes)
                        for node in resolver.getReffs(textId=text.id, level=0)
                    ])
                }
            else:
                reffs = resolver.getReffs(textId=text.id, level=level)
                contents = {
                    str(reff): resolver.
                        getTextualNode(textId=text.id, subreference=reff).
                        export(Mimetypes.PLAINTEXT, exclude=excludes)
                    for reff in reffs
                }
            for file, content in contents.items():
                with open(subtarget+"/"+file+".txt", "w") as f:
                    f.write(normalize.sub(" ", regex.sub(" ", content.strip())))
        i += 1
    print()
    print(SUBTASK_SEPARATOR+"{}/{} texts done".format(i, i))
    print(SUBTASK_SEPARATOR+"{}/{} texts not converted because they lacked SemanticCut information".format(y, i))
