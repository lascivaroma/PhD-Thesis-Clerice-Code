import glob
import pickle
import collections
import typing

import torch
import torch.nn as nn
import torch.autograd as autograd
import torch.optim as optim
import torch.nn.functional as F

__all__ = [
    "Iterator",
    "Vocabulary"
]


class Iterator:
    def __init__(self, files):
        self.files = glob.glob(files) + glob.glob(files.replace("*.", "."))

    def __iter__(self):
        for file in self.files:
            with open(file) as fread:
                yield fread.read().split()

    def iter_context(
            self,
            window: typing.Tuple[int, int],
            get_variable: typing.Callable[
                [typing.List[str]],  # Args
                autograd.Variable  # Result
            ]
    ) -> typing.Iterator(typing.Tuple[autograd.Variable, str]):
        w_left, w_right = window
        for sentence in self:
            max_index = len(sentence) - 1
            for index, token in enumerate(sentence):
                left_context, right_context = [], []
                if index != 0:
                    left_context = sentence[max(index-w_left, 0):index]
                if index != max_index:
                    right_context = sentence[index+1: min(index+w_right, max_index)]
                yield get_variable(left_context + right_context), token


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


class CBOW(nn.Module):
    def __init__(self, vocabulary: Vocabulary, embedding_size: int=100):
        super(CBOW, self).__init__()
        self.embeddings = nn.Embedding(vocabulary.size(), embedding_size)
        self.linear1 = nn.Linear(embedding_size, vocabulary.size())

    def forward(self, inputs):
        lookup_embeds = self.embeddings(inputs)
        embeds = lookup_embeds.sum(dim=0)
        out = self.linear1(embeds)
        out = F.log_softmax(out)
        return out


class Model:
    def __init__(self, vocabulary: Vocabulary, embedding_size: int=100):
        self.vocabulary = vocabulary
        self.embedding_size = embedding_size
        self.net = CBOW(vocabulary=self.vocabulary, embedding_size=embedding_size)

    def get_vector(self, context: typing.List[str]) -> autograd.Variable:
        idxs = [self.vocabulary.get_index(w) for w in context]
        tensor = torch.LongTensor(idxs)
        return autograd.Variable(tensor)

    def train(self,
              iterator: Iterator,
              epochs: int= 100,
              window: typing.Tuple[int, int]=(5, 5),
              lr: float=0.01
              ):
        loss_func = nn.CrossEntropyLoss()
        optimizer = optim.SGD(self.net.parameters(), lr=lr)

        for epoch in range(epochs):
            print("Starting epoch %s " % epoch)
            total_loss = 0
            for context_var, target in iterator.iter_context(window, self.get_vector):
                self.net.zero_grad()
                log_probs = self.net(context_var)

                loss = loss_func(log_probs, autograd.Variable(
                    torch.LongTensor([self.vocabulary.get_index(target)])
                ))

                loss.backward()
                optimizer.step()
                total_loss += loss.data

            print("Loss at epoch %s : %s" % (epoch, total_loss))


if __name__ == "__main__":
    directory = "/home/thibault/dev/these/data/curated/corpus/generic/**/*.txt"
    sentences = Iterator(directory)
    vocabulary = Vocabulary(sentences)
    print("Most common word", vocabulary.counter.most_common(10))
    print(vocabulary.word2idx)
    model = Model(vocabulary=vocabulary)
    model.train(iterator=sentences)
