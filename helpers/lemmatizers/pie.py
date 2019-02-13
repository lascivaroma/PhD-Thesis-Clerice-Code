from .base import LemmatizerBase, Lemma
import requests


class HttpPieLemmatizer(object):
    dirName = "pie-http"
    unknown = []

    def load(self):
        """ Load the lemmatizer
        """
        return True

    def from_string(self, string, text_id=""):
        """

        :param string:
        :return: List of annotated forms
        :rtype: list of Lemma
        """
        return []

    def from_file(self, path):
        with open(path) as f:
            r = self.from_string(f.read(), path)
        yield from r

    @staticmethod
    def lemma_to_string(lemma_collection):
        """ Format a lemma collection to a string

        :param lemma_collection:
        :return:
        """
        return "\n".join(["\t".join(val for val in token) for token in lemma_collection])

    def path(self, file_path):
        return file_path.replace("/generic/", "/{}/".format(self.dirName))
