from gensim.models.word2vec import LineSentence, Word2Vec
from gensim.models.fasttext import FastText
from ..base import BaseEmbedding


class GensimIterator:
    def __init__(self, files):
        self.files = files

    def __iter__(self):
        for file in self.files:
            for line in LineSentence(file, max_sentence_length=300000):
                yield line


class GensimW2Vec(BaseEmbedding):
    def compile(self):
        corpus = GensimIterator(self.corpus_path)
        self.__model__ = Word2Vec(
            size=100, window=5, min_count=1, workers=7,
            hs=1, negative=0  # Needed for lemmatisation
        )
        self.model.build_vocab(corpus)                 # can be a non-repeatable, 1-pass generator
        self.model.train(corpus, total_examples=self.model.corpus_count, epochs=self.model.iter)
        self.persist()

    def persist(self):
        self.model.save(self.model_path)

    def load(self):
        self.__model__ = Word2Vec.load(self.model_path)

    def most_similar(self, word):
        return self.model.wv.most_similar([word])

    def vector_comparison(self, positive=None, negative=None):
        """ Compute the most similar addition of vector

        Example : most_similar(positive=['woman', 'king'], negative=['man']) -> Queen
        :param positive: List of words to add to form the vector
        :param negative: List of words to substract to form the vector
        :return: List of tuples of close vector (Label, Score)
        """
        return self.model.wv.most_similar(positive=positive, negative=negative)


class GensimFasttext(GensimW2Vec):
    def compile(self):
        self.model = FastText(
            sentences=GensimIterator(self.corpus_path),
            size=100, window=5, min_count=4, workers=3, min_n=4, max_n=6,
            hs=1, negative=0
        )
        self.model.train()
        self.persist()

    def persist(self):
        self.model.save(self.model_path)

    def load(self):
        self.model = FastText.load(self.model_path)

    def most_similar(self, word):
        return self.model.wv.most_similar([word])

    def vector_comparison(self, positive=None, negative=None):
        """ Compute the most similar addition of vector

        Example : most_similar(positive=['woman', 'king'], negative=['man']) -> Queen
        :param positive: List of words to add to form the vector
        :param negative: List of words to substract to form the vector
        :return: List of tuples of close vector (Label, Score)
        """
        return self.model.wv.most_similar(positive=positive, negative=negative)
