import glob
import os.path as p
import os
import shutil

for file in glob.glob("./data/curated/corpus/generic/**/*pie*"):
    real_file_name = p.basename(file).replace("-pie", "").replace(".txt", ".tsv")
    directory = p.split(p.dirname(file))[-1]
    output_directory = p.join("data", "curated", "corpus", "pie", directory)
    if not p.isdir(output_directory):
        os.makedirs(output_directory)
    shutil.move(file, p.join(output_directory, real_file_name))
