from .base import LemmatizerBase, Lemma, splitter
from collatinus_lemmatizer import CollatinusLemmatizer, GensimW2Vec
from pycollatinus import Lemmatiseur
from collections import defaultdict


_lemmatiseur = Lemmatiseur()


class Collatinus(LemmatizerBase):
    dirName = "collatinus-lemmatizer"

    def __init__(self):
        self.lemmatizer = CollatinusLemmatizer(
            _lemmatiseur,
            vector=GensimW2Vec(
                model="data/models/collatinus_lemmatizer/w2vec/w2vec.w2.5min.model",
                model_is_path=True,
                method=GensimW2Vec.METHODS.score_with_declensions
            ),
            with_morph=True,
            left_window=3,
            right_window=2
        )
        self.unknown = defaultdict(list)

    def load(self):
        """ Load the lemmatizer
        """
        pass

    def from_string(self, string, text_id=""):
        """

        :param string:
        :return: List of annotated forms
        :rtype: list of Lemma
        """
        tokens = []
        for tok in splitter.split(string):
            if tok:
                if tok.endswith("que") and tok != "que":
                    tokens.append(tok.replace("que", ""))
                else:
                    tokens.append(tok)

        for form, result in self.lemmatizer.lemmatize(tokens):
            lemma, morph = result
            if lemma:
                yield Lemma(form=form, lemma=lemma, pos="", morph=morph)
            else:
                self.unknown[text_id].append(form)
                yield Lemma(form=form, lemma=form, pos="", morph="")
