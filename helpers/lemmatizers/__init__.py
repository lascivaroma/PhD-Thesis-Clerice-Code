from .collatinus import Collatinus
from .pie_impl import PieLemmatizer, PieLemmatizerWeb
import os
import shutil
from multiprocessing.pool import ThreadPool
from helpers.printing import TASK_SEPARATOR, SUBTASK_SEPARATOR


def run_pie_web(text_files, target_path="data/curated/corpus/generic/", verbose=True, threads=1):
    if verbose:
        print(TASK_SEPARATOR+"Lemmatizing {} texts with Pie".format(len(text_files)))

    files = 0
    lemmatizer = PieLemmatizerWeb()

    if os.path.isdir(lemmatizer.path(target_path)):
        if verbose:
            print(SUBTASK_SEPARATOR+"Cleaning up old text")
        shutil.rmtree(lemmatizer.path(target_path))

    for filepath in text_files:
        print(SUBTASK_SEPARATOR + "Starting {}".format(filepath))
        lemmatizer.output(filepath)
        files += 1
        if verbose:
            print(
                SUBTASK_SEPARATOR +
                "{filename} done ({texts_done}/{total_texts}) ".format(
                    filename=filepath,
                    texts_done=files,
                    total_texts=len(text_files)
                )
            )


def run_collatinus(text_files, target_path="data/curated/corpus/generic/", verbose=False, threads=7):
    if verbose:
        print(TASK_SEPARATOR+"Lemmatizing {} texts".format(len(text_files)))
    lemmatizer = Collatinus()
    files = 0

    with open("data/curated/corpus/collatinus-lemmatizer.unknown.tsv", "w") as f:
        f.write("Source\tPassage\tForm\n")

    if os.path.isdir(lemmatizer.path(target_path)):
        if verbose:
            print(SUBTASK_SEPARATOR+"Cleaning up old text")
        shutil.rmtree(lemmatizer.path(target_path))

    with ThreadPool(processes=threads) as pool:
        for source, *_ in pool.imap_unordered(lemmatizer.output, text_files):
            unk = [
                (source.replace(target_path, ""), form)
                for form in lemmatizer.unknown[source]
            ]
            files += 1
            if verbose:
                print(
                    SUBTASK_SEPARATOR +
                    "{filename} done ({texts_done}/{total_texts}) [+{diff_forms} new unknown forms]".format(
                        filename=source,
                        texts_done=files,
                        total_texts=len(text_files),
                        diff_forms=len(lemmatizer.unknown[source])
                    )
                )

            with open("data/curated/corpus/collatinus-lemmatizer.unknown.tsv", "a") as f:
                f.write("\n".join(
                    src.replace(".txt", "").replace("/", "\t")+"\t"+frm
                    for src, frm in unk
                ))
                f.write("\n")
