import os
import sys
import csv
from typing import List, Tuple

import logging  # Setting up the loggings to monitor gensim
logging.basicConfig(format="%(levelname)s - %(asctime)s: %(message)s", datefmt= '%H:%M:%S', level=logging.INFO)

# In case it takes ./notebooks
sys.path.append('../')

EXPERIENCES_COUNT = 50
ITERATION_COUNT = 3

csv_file = open("embedding_stability_orders.csv", "w")
csv_writer = csv.writer(csv_file)

import glob
import math
import copy
import random
from helpers.embeddings.gensim_model import GensimIterator


# Generic function reused below
def size(path) -> int:
    with open(path) as f:
        x = len(f.read().split())
    return x


def fill_with(expected_fill: int, available_corpus: List[Tuple[str, int]]) -> List[str]:
    """ Return a list of file that can be use to make the corpus around the same size at it was
    before deleting some of its members

    :param expected_fill: Number of words needed to balance the corpus
    :param size: List of texts and their size
    :return:
    """
    corpus = copy.deepcopy(available_corpus)
    counter = 0 + expected_fill
    random.shuffle(corpus)
    for path, word_count in corpus:
        # If we are close to 100 words
        if counter  <= 100:
            break
        counter -= word_count
        yield path


# Constants required by multiple functions / call

FIXED_ORDER = sorted(glob.glob("../data/curated/corpus/pie-http/**/*.txt"))
SIZES = {
    fpath: size(fpath)
    for fpath in FIXED_ORDER
}


def fixed_order() -> List[str]:
    """

    :return:
    """
    return []+FIXED_ORDER


def random_order() -> List[str]:
    x = []+FIXED_ORDER
    random.shuffle(x)
    return x


def replaced_order() -> List[str]:
    x = []+FIXED_ORDER
    random.shuffle(x)
    milestone = math.ceil(len(x)*0.66)
    kept, lost = x[:milestone], x[milestone:]
    length = sum([SIZES[path] for path in lost])
    kept = kept + list(fill_with(length, [(key, value) for key, value in SIZES.items() if key in kept]))
    return sorted(kept)


from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from time import time

min_count = 5


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


def word2vec(iterator, output):
    model = Word2Vec(min_count=5, workers=4, size=100)
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

####################
#
#
#   Step 1 : Training Models
#
#
####################


# Set of functions that gives the right order of file
corpus_arrangements = [fixed_order, random_order, replaced_order]


def make_models():
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


# Continue ?
