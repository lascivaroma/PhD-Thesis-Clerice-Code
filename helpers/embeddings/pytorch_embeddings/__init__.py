from .data import Iterator, Vocabulary, WordContextDataset
from .modules import CBOW
from .models import Model


def run(test_mode: bool=False, sample=None):
    directory = "/home/thibault/dev/these/data/curated/corpus/collatinus-lemmatizer/**/*.txt"
    print("Setting up iterator")
    sentences = Iterator(directory, window=(2, 2))
    if test_mode:
        sentences.files = sentences.files[0:2]
    if sample:
        sentences.files = sentences.files[:sample]

    print("Setting up vocabulary")
    vocabulary = Vocabulary(sentences)
    print("-> size : %s" % vocabulary.size())
    print("-> Number of < 3 chars : %s" % sum(
        [
            int(len(word) < 3)
            for word in vocabulary.word2idx.keys()
        ]
    ))
    print("-> Number of < 2 occ: %s" % sum(
        [
            int(decompte == 1)
            for decompte in vocabulary.counter.values()
        ]
    ))
    print(len(list(vocabulary.idx2word.keys())))
    print("Setting up dataset")
    dataset = WordContextDataset.compile_or_load(
        "./dataset.pickle", test=test_mode or sample is not None,
        corpus=sentences, vocabulary=vocabulary
    )
    print("Most common word", vocabulary.counter.most_common(10))

    print("Creating model")
    model = Model(vocabulary=vocabulary)

    print("Starting training...")
    model.train(dataset, epochs=1, batch_size=512)
    print(model.n_closest("mihi"))


if __name__ == "__main__":
    run()
