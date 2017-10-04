import urllib
import zipfile
import csv
import os
import shutil


def download_corpus(tgt, corpus_name, corpus_version):
    """ Download a corpus

    :param tgt: Directory where to download
    :param corpus_name: Corpus Name
    :param corpus_version: Corpus version
    :return: Status
    :rtype: bool
    """
    dir = tgt+"/"+corpus_name.replace("/", "_")
    if os.path.isdir(dir):
        shutil.rmtree(dir)


def download_corpora(src="data/raw/corpora.csv", tgt="data/raw/corpora/"):
    with open(src) as src_file:
        corpora = [corpus for corpus in csv.DictReader(src_file)]
        for corpus in corpora:
            if corpus["Current"] == corpus["Version"]:
                print("{} stays on version {}".format(corpus["Name"], corpus["Current"]))
            else:
                print("{}'s version is {}. Downloading {}".format(corpus["Name"], corpus["Current"], corpus["Version"]))
                status = download_corpus(tgt, corpus["Name"], corpus["Version"])