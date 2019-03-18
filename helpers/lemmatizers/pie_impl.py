import csv
import os
from pie.tagger import Tagger, simple_tokenizer
import pie.utils
from .base import LemmatizerBase, Lemma

from cltk.tokenize.sentence import TokenizeSentence
from cltk.tokenize.word import WordTokenizer

import re


class PieLemmatizer(LemmatizerBase):
    dirName = "pie-http"

    MORPH_PART = ["Case", "Numb", "Deg", "Mood", "Tense", "Voice", "Person"]

    def tokenize(self, string):
        string = string.replace("U", "V").replace("v", "u").replace("J", "I").replace("j", "i")
        #for sentence in simple_tokenizer(string, lower=False):
        #    yield sentence, len(sentence)
        for sentence in self.sentence_tokenizer.tokenize_sentences(string):
            toks = self.word_tokenizer.tokenize(sentence)
            yield toks, len(toks)

    def __init__(self, model_path="data/models/latin.tar"):
        super(PieLemmatizer, self).__init__()
        self.tagger = Tagger(device="cuda", batch_size=100)
        self.tagger.add_model(model_path)
        self.sentence_tokenizer = TokenizeSentence("latin")
        self.word_tokenizer = WordTokenizer("latin")

    def from_string(self, string, text_id=""):
        """

        :param string:
        :param text_id:
        :return:
        """
        for chunk in pie.utils.chunks(self.tokenize(string), self.tagger.batch_size):
            sents, lengths = zip(*chunk)
            tagged, tasks = self.tagger.tag(sents, lengths)

            for sent in tagged:
                for token, tags in sent:
                    result = {"token": token}
                    result.update(dict(zip(tasks, tags)))
                    if token in ["qve"]:
                        yield Lemma(
                            form="-"+token,
                            lemma=token,
                            pos="COO",
                            morph="MORPH=empty"
                        )
                    elif re.match(r"^\W+$", token):
                        yield Lemma(form=token, lemma=token, pos="PUNC", morph="MORPH=empty")
                    elif result:
                        yield Lemma(
                            form=result["token"],
                            lemma=result["lemma"],
                            pos=result["pos"],
                            morph="|".join(
                                "{cat}={tag}".format(
                                    cat=morph_part,
                                    tag=tags[tasks.index(morph_part)]
                                )
                                for morph_part in type(self).MORPH_PART
                                if morph_part in tasks and tags[tasks.index(morph_part)] != "_"
                            ) or "MORPH=empty"
                        )
            del sents, lengths

    def output(self, file_path):
        """ Write the output of the lemmatizer to the default directory

        :param file_path:
        :return:
        """
        text_file_path = self.path(file_path)
        csv_file_path = self.path(file_path.replace(".txt", ".tsv"))

        # Create directories
        os.makedirs(os.path.dirname(text_file_path), exist_ok=True)

        with open(text_file_path, "w") as text_io:
            with open(csv_file_path, "w") as csv_io:
                csv_writer = csv.DictWriter(csv_io, fieldnames=["form", "lemma", "pos", "morph"])
                csv_writer.writeheader()

                for token in self.from_file(file_path):
                    text_io.write(token.lemma + " ")
                    csv_writer.writerow(token._asdict())


if __name__ == "__main__":
    import pprint
    piel = PieLemmatizer()
    pprint.pprint(list(piel.from_string("""Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut 
    labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco
     laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit 
     in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat 
     cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.""")))
