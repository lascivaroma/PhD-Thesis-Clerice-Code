import os
import sys
import csv
import subprocess
import glob
import math
import copy
import random
import logging  # Setting up the loggings to monitor gensim
from time import time


from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from typing import List, Tuple

from helpers.embeddings.gensim_model import GensimIterator

# Important to get information from gensim
logging.basicConfig(format="%(levelname)s - %(asctime)s: %(message)s", datefmt= '%H:%M:%S', level=logging.INFO)

# In case it takes ./notebooks
sys.path.append('../')

###############
#
#
#   Constants
#
#
################

# Number of models to build
EXPERIENCES_COUNT = 50
MIN_WORD_COUNT = 5


###############
#
#
#   Utils
#
#
################

def size(path) -> int:
    """ Returns the number of words of a text file
    """
    with open(path) as f:
        x = len(f.read().split())
    return x


def fill_with(expected_fill: int, available_corpus: List[Tuple[str, int]]) -> List[str]:
    """ Return a list of file that can be use to make the corpus around the same size at it was
    before deleting some of its members

    :param expected_fill: Number of words needed to balance the corpus
    :param available_corpus: List of texts and their size
    :return:
    """
    corpus = copy.deepcopy(available_corpus)
    counter = 0 + expected_fill
    random.shuffle(corpus)
    for path, word_count in corpus:
        # If we are close to 100 words
        if counter <= 100:
            break
        counter -= word_count
        yield path


###############
#
#
#   Ordering function
#       These functions are here to build the list of text files needed for one model building
#
#
#
################


# Constants required by multiple functions / call

FIXED_ORDER = sorted(glob.glob("../data/curated/corpus/pie-http/**/*.txt"))
SIZES = {
    fpath: size(fpath)
    for fpath in FIXED_ORDER
}


def fixed_order() -> List[str]:
    """ List of text files in a fixed order
    """
    return []+FIXED_ORDER


def random_order() -> List[str]:
    """ List of text files in a random order """
    x = []+FIXED_ORDER
    random.shuffle(x)
    return x


def replaced_order() -> List[str]:
    """ List of text files where a third has been replaced by files around the same size from the two third kept"""
    x = []+FIXED_ORDER
    random.shuffle(x)
    milestone = math.ceil(len(x)*0.66)
    kept, lost = x[:milestone], x[milestone:]
    length = sum([SIZES[path] for path in lost])
    kept = kept + list(fill_with(length, [(key, value) for key, value in SIZES.items() if key in kept]))
    return sorted(kept)


# Set of functions that gives the right order of file
corpus_arrangements = [fixed_order, random_order, replaced_order]


####################
#
#
#   Step 1 : Training Models
#
#
####################


class Iterator:
    def __init__(self, files):
        self.files = files

    def iter(self):
        for fname in self.files:
            with open(fname) as fp:
                for line in fp:
                    yield line.split()

    def __iter__(self):
        for fname in self.files:
            with open(fname) as fp:
                for line in fp:
                    yield line


def word2vec(iterator: Iterator, output: str):
    """ Given an iterator and a file where it needs to be saved, build a Word2Vec model
    """
    model = Word2Vec(min_count=MIN_WORD_COUNT, workers=4, size=100)
    t = time()
    print("Building vocab")
    model.build_vocab(iterator, progress_per=1000)
    print('Time to build vocab: {} mins'.format(round((time() - t) / 60, 2)))
    t = time()
    print("Training")
    model.train(iterator, total_examples=model.corpus_count, epochs=50, report_delay=1)
    print('Time to train the model: {} mins'.format(round((time() - t) / 60, 2)))
    model.wv.save(output)
    return KeyedVectors.load(output, mmap='r')


def make_models():
    """ Run the building of models for each function {EXPERIENCES_COUNT} times """
    csv_file = open("embedding_stability_orders.csv", "w")
    csv_writer = csv.writer(csv_file)
    # For each kind of file order
    for corpus_arrangement in corpus_arrangements:

        # For each iteration of our algorithm
        for experience in range(EXPERIENCES_COUNT):
            # We generate the order
            order = corpus_arrangement()
            # We save it to a CSV to be able to source this later
            csv_writer.writerow([corpus_arrangement.__name__, str(experience)] + order)
            # Create the reader
            iterator = GensimIterator(order)
            model = word2vec(iterator, "{fname}.{iter}.wv".format(fname=corpus_arrangement.__name__, iter=experience))


####################
#
#
#   Step 2 : Topic Modelling for extracting relevant words
#
#
####################


class Mallet(object):
    def __init__(self, mallet_bin_path: str=None, stopwords: str=None):
        """ Object running commands for mallets keeping state about files that needs to be moved from one place to
        another.


        :param mallet_bin_path:
        :param stopwords:
        """
        self.path = mallet_bin_path or "/home/thibault/apps/mallet-2.0.8/bin/"
        self.working_dir = "."
        self.stopwords = stopwords or "./stopwords.txt"
        self.corpus_file = os.path.join(self.working_dir, "corpus.mallet")
        self.composition_file = os.path.join(self.working_dir, "mallet.composition.txt")
        self.keys = os.path.join(self.working_dir, "mallet.keys.txt")
        # --stoplist-file

    def build(self, input_dir):
        """ Build the corpus for Mallet (Necessary for training, but only once) """
        print("[Mallet] Building the corpus")
        command = self.run_mallet_cmd("mallet", "import-dir",
                                      "--input", input_dir,
                                      "--output", self.corpus_file,
                                      "--keep-sequence",
                                      "--stoplist-file", self.stopwords)

    def train(self, num_topics=200):
        """ Train the model """
        print("[Mallet] Training")
        command = self.run_mallet_cmd("mallet", "train-topics",
                                      "--input", self.corpus_file,
                                      "--num-topics", num_topics,
                                      "--output-stage", "topic-state.gz",
                                      "--output-topic-keys", self.keys,
                                      "--output-doc-topics", self.composition_file,
                                      "--optimize-interval", "20")

    def run_mallet_cmd(self, cmd, *args):
        """ Run {cmd}'s mallet binary with {args} parameters """
        command = subprocess.run([self.path + cmd] + list(args))
        try:
            command.check_returncode()
            print("[Mallet] Success")
        except subprocess.CalledProcessError:
            print("[Mallet] Error")
            print(command.stderr)
        return command

    def topics(self) -> List[List[str]]:
        """ Generates a list of words per topic found in the trained model
        """
        with open(self.keys) as f:
            for line in f.readlines():
                yield line.split("\t")[-1].split()
