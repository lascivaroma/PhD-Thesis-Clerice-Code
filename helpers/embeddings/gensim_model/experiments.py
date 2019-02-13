import glob
from gensim.models.word2vec import Word2Vec, Word2VecKeyedVectors
from .models import GensimIterator


class Experiment:
    def __init__(self, corpus: str, identifier: int= 1, model_count: int=10, epochs: int=100):
        self.vocabulary = None
        self.models = []
        self.identifier = identifier
        self.model_count = model_count
        self.epochs = epochs

        self.corpus = glob.glob(corpus) + glob.glob(corpus.replace("*.", "."))
        self.corpus_size = len(self.corpus)
        self.corpus = GensimIterator(self.corpus)

        self.save_template = ".models/model.exp{}.epoch{}"

    def make_model(self, size=100, window=5, min_count=1, workers=7,
                hs=1, negative=0) -> Word2Vec:
        """ Creates a model by reusing available data

        :param size:
        :param window:
        :param min_count:
        :param workers:
        :param hs:
        :param negative:
        :return:
        """
        model = Word2Vec(
            size=size, window=window,
            min_count=min_count, workers=workers,
            hs=hs, negative=negative
        )

        if self.vocabulary:
            model.vocabulary = self.vocabulary
        return model

    def train_model(self, model: Word2Vec) -> Word2Vec:
        """ Train a given Word2Vec model with the experiments properties

        :param model: Model to train
        :return: Trained Model
        """
        if not self.vocabulary:
            model.build_vocab(self.corpus)
            self.vocabulary = model.vocabulary
        else:
            model.vocabulary = self.vocabulary

        model.train(self.corpus, total_examples=self.corpus_size, epochs=self.epochs)
        return model

    def load_model(self, experiment) -> Word2VecKeyedVectors:
        try:
            return Word2VecKeyedVectors.load(self.save_template.format(self.identifier, experiment))
        except Exception as E:
            print(E)
            return None

    def run(self, size=100, window=5, min_count=1, workers=7,
                hs=1, negative=0, test_word="ego"):
        """ Run the experiment

        :return:
        """
        for experiment in range(self.model_count):
            print("Training model {} of experiment {}".format(experiment, self.identifier))
            model = self.load_model(experiment)
            if not model:
                model = self.make_model(
                    size=size, window=window,
                    min_count=min_count, workers=workers,
                    hs=hs, negative=negative
                )
                self.train_model(model)
            else:
                self.vocabulary = model.vocab
            self.models.append(model)
            model.wv.save(self.save_template.format(self.identifier, experiment))
            print("Top 10 {} :".format(test_word), model.wv.similar_by_word(test_word))