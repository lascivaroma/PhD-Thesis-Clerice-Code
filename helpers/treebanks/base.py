import abc
import glob
import statistics
import collections


class TreebankCorpus:
    """ Class to read a treebank corpus

    :param files: Files that needs to be read (can be a glob pattern)
    """
    def __init__(self, files):
        if isinstance(files, str):
            files = glob.glob(files)
        self.files = files
        self._diversity = None
        self._words = collections.defaultdict(list)
        self._lemmas = collections.defaultdict(list)
        self._types = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))

    @property
    def doc_count(self):
        return len(self.words)

    @property
    def words(self):
        return self._words

    @property
    def lemmas(self):
        return self._lemmas

    @property
    def types(self):
        return self._types

    @abc.abstractmethod
    def parse(self):
        """ Parse the corpus"""

    @property
    def diversity(self):
        return {
            "forms": 0,
            "forms_unique": 0,
            "lemmas": 0,
            "lemmas_unique": 0
        }

    @staticmethod
    def dict_map(dic, transform=lambda x: x, call=statistics.median):
        return call([
                len(transform(value)) for value in dic.values()
        ])

    @property
    def diversity(self):
        global_words = [word for doc in self.words.values() for word in doc]
        global_lemma = [word for doc in self.lemmas.values() for word in doc]

        return {
            "Formes": len(global_words),
            "Formes Uniques": len(set(global_words)),
            "Lemmas": len(global_lemma),
            "Lemmas Uniques": len(set(global_lemma)),
            "Documents": len(self.words),

            # Lemmes
            "Moyennes Formes / Lemmes": len(global_words) / len(set(global_lemma)),
            "Moyennes Formes Uniques / Lemmes": len(set(global_words)) / len(set(global_lemma)),

            # Means
            "Moyenne Lemmas": int(len(global_lemma) / len(self.lemmas)),
            "Moyenne Lemmas Uniques": int(len(set(global_lemma)) / self.doc_count),

            # Medians
            "Médiane Lemmas": self.dict_map(self.lemmas),
            "Médiane Lemmas Unique": self.dict_map(self.lemmas, transform=set),
            "Médiane Formes": self.dict_map(self.words),
            "Médiane Formes Unique": self.dict_map(self.words, transform=set),

            # Variance
            "Écart Type Lemmas": self.dict_map(self.lemmas, call=statistics.stdev),
            "Écart Type Lemmas Uniques": self.dict_map(self.lemmas, transform=set, call=statistics.stdev),
            "Écart Type Formes": self.dict_map(self.words, call=statistics.stdev),
            "Écart Type Formes Uniques": self.dict_map(self.words, transform=set, call=statistics.stdev),
        }

    @property
    def documents_diversity(self):
        return {
            # Statistiques par document
            "Lemmas par document": self.dict_map(self.lemmas, call=list),
            "Lemmas Uniques par document": self.dict_map(self.lemmas, transform=set, call=list),
            "Formes par document": self.dict_map(self.words, call=list),
            "Formes Uniques par document": self.dict_map(self.words, transform=set, call=list),
        }