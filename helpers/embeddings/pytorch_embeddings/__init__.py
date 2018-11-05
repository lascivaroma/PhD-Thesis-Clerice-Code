from .data import Iterator, Vocabulary, WordContextDataset
from .modules import CBOW
from .models import Model


def run(test_mode: bool=False):
    directory = "/home/thibault/dev/these/data/curated/corpus/generic/**/*.txt"
    print("Setting up iterator")
    sentences = Iterator(directory, window=(2, 2))
    if test_mode:
        sentences.files = sentences.files[0:2]

    print("Setting up vocabulary")
    vocabulary = Vocabulary(sentences)
    print("-> size : %s" % vocabulary.size())
    print("Setting up dataset")
    dataset = WordContextDataset.compile_or_load(
        "./dataset.pickle", test=test_mode,
        corpus=sentences, vocabulary=vocabulary
    )
    print(dataset.data)
    print("Most common word", vocabulary.counter.most_common(10))

    print("Creating model")
    model = Model(vocabulary=vocabulary)

    print("Starting training...")
    model.train(dataset, epochs=10)
    print(model.n_closest("mihi"))


if __name__ == "__main__":
    run()
