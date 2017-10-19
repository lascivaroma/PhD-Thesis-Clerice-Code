import glob
import os


class BaseEmbedding:
    def __init__(self, model_path, corpus_path="data/curated/corpus/generic/**/*.txt"):
        self.model_path = model_path
        self.corpus_path = corpus_path
        self.__model__ = None
        if isinstance(corpus_path, str):
            self.corpus_path = glob.glob(corpus_path) + glob.glob(corpus_path.replace("*.", "."))

    @property
    def model(self):
        return self.__model__

    def load_or_compile(self):
        if os.path.isfile(self.model_path):
            self.load()
        else:
            self.compile()

    def persist(self):
        raise NotImplemented

    def compile(self):
        raise NotImplemented

    def most_similar(self, word):
        raise NotImplemented

    def load(self):
        raise NotImplemented

    def vector_comparison(self, positive=None, negative=None):
        """ Compute the most similar addition of vector

        Example : most_similar(positive=['woman', 'king'], negative=['man']) -> Queen
        :param positive: List of words to add to form the vector
        :param negative: List of words to substract to form the vector
        :return: List of tuples of close vector (Label, Score)
        """
        raise NotImplemented