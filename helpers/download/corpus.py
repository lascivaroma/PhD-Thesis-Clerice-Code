import requests
import zipfile
import csv
import os
import shutil
from io import BytesIO
import glob

from ..reader import make_resolver
from ..printing import TASK_SEPARATOR, SUBTASK_SEPARATOR

def download_corpus(tgt, corpus_name, corpus_version):
    """ Download a corpus

    :param tgt: Directory where to download
    :param corpus_name: Corpus Name
    :param corpus_version: Corpus version
    :return: Status
    :rtype: bool
    """
    target_dir = tgt+"/"+corpus_name.replace("/", "_")
    if os.path.isdir(target_dir):
        shutil.rmtree(target_dir)
    print(TASK_SEPARATOR+"Starting download")
    webfile = requests.get("https://github.com/{name}/archive/{version}.zip".format(
        name=corpus_name, version=corpus_version
    ))
    print(TASK_SEPARATOR+"Starting Unzipping")
    with zipfile.ZipFile(BytesIO(webfile.content)) as z:
        z.extractall(target_dir)
    print(TASK_SEPARATOR+"Done")
    return True, target_dir


def download_corpora(src="data/raw/corpora.csv", tgt="data/raw/corpora/", force=False):
    with open(src) as src_file:
        corpora = [corpus for corpus in csv.DictReader(src_file, delimiter=";")]
        new_corpora = []
        for corpus in corpora:
            if corpus["Current"] == corpus["Version"] and force is not True:
                print("{} stays on version {}".format(corpus["Name"], corpus["Current"]))
            else:
                print("{}'s version is {}. Downloading {}".format(corpus["Name"], corpus["Current"], corpus["Version"]))
                status, path = download_corpus(tgt, corpus["Name"], corpus["Version"])
                if status is True:
                    corpus["Current"] = corpus["Version"]
                    print(TASK_SEPARATOR+"Cleaning up the corpus")
                    clean_up_corpora(path)
            new_corpora.append({k: v for k, v in corpus.items()})

    # Update the corpus
    with open(src, "w") as src_file:
        writer = csv.DictWriter(src_file, delimiter=";", fieldnames=["Name", "Version", "Current"])
        writer.writeheader()
        writer.writerows(new_corpora)


def clean_up_corpora(src):
    resolver = make_resolver(glob.glob(src+"/**"))
    translations = [x.path for x in resolver.getMetadata().readableDescendants if x.lang != "lat"]
    for trans in translations:
        os.remove(trans)
    print(SUBTASK_SEPARATOR+"Removed {} text(s) not in Latin".format(len(translations)))
    print(SUBTASK_SEPARATOR+"Kept {} text(s) in Latin".format(
        len([x for x in resolver.getMetadata().readableDescendants if x.lang == "lat"]))
    )
