from collections import namedtuple
import re
import os

Lemma = namedtuple("Lemma", field_names=["form", "lemma", "pos", "morph"])
splitter = re.compile("\W+")


class LemmatizerBase(object):
    dirName = "base"
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
            yield from self.from_string(f.read(), path)

    @staticmethod
    def lemma_to_string(lemma_collection):
        """ Format a lemma collection to a string

        :param lemma_collection:
        :return:
        """
        return "\n".join(["\t".join(val for val in token) for token in lemma_collection])

    def path(self, file_path):
        return file_path.replace("/generic/", "/{}/".format(self.dirName))

    def output(self, file_path):
        """ Write the output of the lemmatizer to the default directory

        :param file_path:
        :return:
        """
        lemmatized = [tok for tok in self.from_file(file_path)]
        simplified = " ".join([lemma.lemma for lemma in lemmatized])
        output_path = self.path(file_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as output_io:
            output_io.write(simplified)

