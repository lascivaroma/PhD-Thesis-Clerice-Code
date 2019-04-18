import os
import sys
import csv
import subprocess
import glob
import math
import copy
import json
import random
import logging  # Setting up the loggings to monitor gensim
from time import time


from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from typing import List, Tuple

from helpers.embeddings.gensim_model import GensimIterator

# Important to get information from gensim
if __name__ == "__main__":
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


####################
#
#
#   Step 2 : Topic Modelling for extracting relevant words
#
#
####################

def word2vec_similarities(word1: str, word2: str, models: List[KeyedVectors]) -> List[float]:
    """ Given word1  and word 2, returns the distance between these word
    if they appear in the models
    """
    x = []
    for model in models:
        if word1 in model and word2 in model:
            x.append(model.n_similarity([word1], [word2]))
    return x


def build_proximity(topics, models):
    """ Build a proximity dictionary for the topics given where each word combination
    in a topic are scored in proximity against each other
    """
    structure = {
        # Topic
        # topic_index: {
        word1: {
            # List of scores over one model
            word2: []
            for word2 in words if word2 != word1
        }
        for words in topics
        for word1 in words
    }
    #    for topic_index, words in enumerate(topics)
    # }
    for word1 in structure:
        for word2 in structure[word1]:
            structure[word1][word2] = word2vec_similarities(word1, word2, models=models)
    return structure


def get_models(order="fixed_order", glob_pattern="../reproduction/mimno.models/{order}.*.wv"):
    """ Get all models in {order} arrangement
    """
    if len(glob.glob(glob_pattern.format(order=order))) == 0:
        raise Exception("No models found")
    for model in glob.glob(glob_pattern.format(order=order)):
        yield KeyedVectors.load(model)


def get_proximities_dict(topics: List[str], path: str = ".", arrangements: List = None, force=False) -> dict:
    if not arrangements:
        arrangements = corpus_arrangements
    output = {}
    for arrangement in arrangements:
        jsonname = os.path.join(path, arrangement.__name__+".json")
        if os.path.isfile(jsonname) and not force:
            with open(jsonname) as f:
                output[arrangement.__name__] = json.load(f)
        else:
            proximity_dict = build_proximity(topics, list(get_models(order=arrangement.__name__)))
            with open(jsonname, "w") as f:
                # Floats conversion because of numpy float
                output[arrangement.__name__] = json.dump({
                    w1: {
                        w2: [float(score) for score in proximity_dict[w1][w2]]
                        for w2 in proximity_dict[w1]
                    }
                    for w1 in proximity_dict
                }, f)
            output[arrangement.__name__] = proximity_dict
    return output
