import requests
import zipfile
import csv
import os
import shutil
from io import BytesIO


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
    print("+    Starting download")
    webfile = requests.get("https://github.com/{name}/archive/{version}.zip".format(
        name=corpus_name, version=corpus_version
    ))
    print("+    Starting Unzipping")
    with zipfile.ZipFile(BytesIO(webfile.content)) as z:
        z.extractall(target_dir)
    print("+    Done")
    return True


def download_corpora(src="data/raw/corpora.csv", tgt="data/raw/corpora/"):
    with open(src) as src_file:
        corpora = [corpus for corpus in csv.DictReader(src_file, delimiter=";")]
        new_corpora = []
        for corpus in corpora:
            if corpus["Current"] == corpus["Version"]:
                print("{} stays on version {}".format(corpus["Name"], corpus["Current"]))
            else:
                print("{}'s version is {}. Downloading {}".format(corpus["Name"], corpus["Current"], corpus["Version"]))
                status = download_corpus(tgt, corpus["Name"], corpus["Version"])
                if status is True:
                    corpus["Current"] = corpus["Version"]
            new_corpora.append({k: v for k, v in corpus.items()})

    # Update the corpus
    with open(src, "w") as src_file:
        writer = csv.DictWriter(src_file, delimiter=";", fieldnames=["Name", "Version", "Current"])
        writer.writeheader()
        writer.writerows(new_corpora)
