from .collatinus import Collatinus
import os
import shutil
from multiprocessing.pool import ThreadPool
from helpers.printing import TASK_SEPARATOR, SUBTASK_SEPARATOR


def run_collatinus(text_files, target_path="data/curated/corpus/generic/", verbose=False):
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

    with ThreadPool(processes=7) as pool:
        for source in pool.imap_unordered(lemmatizer.output, text_files):
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
