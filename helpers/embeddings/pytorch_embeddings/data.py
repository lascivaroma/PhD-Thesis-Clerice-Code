import glob
import pickle
import collections
import typing
import os.path


# For typing reasons
import torch.autograd as autograd
from torch.utils.data import Dataset
import torch

from tqdm import tqdm


class Iterator:
    def __init__(self, files, window: typing.Tuple[int, int]):
        self.w_left, self.w_right = window
        self.files = glob.glob(files) + glob.glob(files.replace("*.", "."))

    def __len__(self):
        return len(self.files)

    def __iter__(self):
        for file in self.files:
            with open(file) as fread:
                yield fread.read().split()

    def get_unit(
            self,
            sentence: typing.List[str]
        ) -> typing.Iterator(typing.Tuple[autograd.Variable, str]):
        max_index = len(sentence)
        for index in range(self.w_left, len(sentence)-self.w_right):
            token = sentence[index]
            left_context, right_context = [], []
            if index != 0:
                left_context = sentence[max(index-self.w_left, 0):index]
            if index != max_index:
                right_context = sentence[index+1: min(index+self.w_right+1, max_index)]
            yield (left_context+right_context, token)


class Vocabulary:
    def __init__(self, iterator: Iterator, build: bool=True):
        self.counter = collections.Counter()
        self.word2idx = {}
        self.idx2word = {}
        self.iterator = iterator

        if build:
            self.build()

    def build(self):
        for sentence in self.iterator:
            self.counter.update(sentence)
        self.word2idx = {w: idx for (idx, w) in enumerate(self.counter.keys())}
        self.idx2word = {idx: w for w, idx in self.word2idx.items()}

    def __getstate__(self):
        return self.__dict__

    def size(self) -> int:
        return len(self.counter)

    def get_index(self, word: str) -> int:
        return self.word2idx[word]

    def get_word(self, index: int) -> str:
        return self.idx2word[index]

    def save(self, path: str):
        with open(path, "wb") as file:
            pickle.dump(self, file)

    @classmethod
    def load(cls, path):
        with open(path, "rb") as file:
            return pickle.load(file)


class WordContextDataset(Dataset):
    """
    Attributes:
        corpus (list): list of corpus word.
        vocab_size (int): size of vocabulary.
        idx_word_dict (dict): dictionary which consists of
                              index as key and word as value.
        word_idx_dict (dict): dictionary which consists of
                              word as key and index as value.
    """

    def transform(self, tokens: typing.List[int]) -> autograd.Variable:
        tensor = torch.tensor(tokens, dtype=torch.long)
        return tensor  # autograd.Variable(tensor)

    def build_data(self, sentence):
        for context, token in self.corpus.get_unit(sentence):
            yield (
                [self.vocabulary.get_index(tok) for tok in context],  # Ids only
                self.vocabulary.get_index(token)  # Token only
            )

    @staticmethod
    def compile_or_load(path: str, test: bool= False, **kwargs):
        if not test:
            if os.path.exists(path):
                return WordContextDataset.load(path)

        data = WordContextDataset(**kwargs)
        if not test:
            data.save(path)
        return data

    def save(self, path: str):
        with open(path, "wb") as file:
            pickle.dump(self, file)

    @classmethod
    def load(cls, path):
        with open(path, "rb") as file:
            return pickle.load(file)

    def __init__(
        self,
        corpus: Iterator=None,
        vocabulary: Vocabulary=None
    ):
        self.corpus = corpus
        self.vocabulary = vocabulary

        # Make dataset
        self.data = []

        with tqdm(total=len(self.corpus), unit=" passage") as bar:
            bar.set_description("[Loading source texts]")
            for sentence in self.corpus:
                self.data += list(self.build_data(sentence))
                bar.update(1)

        print("\t%s training examples loaded" % len(self.data))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        context, token = self.data[idx]
        context, token = self.transform(context), self.transform([token])
        return context, token
