from collections import namedtuple


Lemma = namedtuple("Lemma", field_names=["form", "lemma", "pos", "morph"])


class LemmatizerBase(object):
    def load(self):
        """ Load the lemmatizer
        """
        return True

    def from_string(self, string):
        """

        :param string:
        :return: List of annotated forms
        :rtype: list of Lemma
        """
        return []

    def from_file(self, path):
        with open(path) as f:
            r = self.from_string(path.read)
        return r

    @staticmethod
    def lemma_to_string(lemma_collection):
        """ Format a lemma collection to a string

        :param lemma_collection:
        :return:
        """
        return "\n".join(["\t".join(val for val in token) for token in lemma_collection])
