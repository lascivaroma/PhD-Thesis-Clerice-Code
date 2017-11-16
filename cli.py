import click
import helpers.download
import helpers.reader
from helpers.printing import TASK_SEPARATOR, SUBTASK_SEPARATOR
import helpers.metadata
import helpers.exporter
import helpers.lemmatizers
import analysis.general_analysis.corpus_analysis
import analysis.field_analysis.embeddings_analysis
import glob
import os
from multiprocessing.pool import ThreadPool
from subprocess import call


CORPUS_PATH = "data/curated/corpus/generic/**/*.txt"


@click.group()
def cli():
    pass


@cli.command()
@click.option('--corpus', is_flag=True, help='Update corpus')
@click.option('--force', is_flag=True, help='Force download')
def download(corpus=False, force=False):
    """ Refresh corpora if need be """
    if corpus:
        helpers.download.download_corpora(force=force)


@cli.command()
def enhance_metadata():
    """ Enhance the metadata using the spreadsheet and other informations"""
    print("Enhancing the metadata")
    metadata = helpers.metadata.read_datation_spreadsheet()
    resolver = helpers.metadata.feed_resolver(metadata, helpers.reader.make_resolver())
    helpers.metadata.write_inventory(resolver)


@cli.command()
def generate_raw_texts():
    """ Prepare the whole corpus """
    resolver = helpers.reader.make_resolver()
    metadata = helpers.metadata.read_datation_spreadsheet()
    resolver = helpers.metadata.feed_resolver(metadata, resolver)
    helpers.reader.create_raw_text(resolver=resolver)


@cli.command()
@click.option('--corpus', is_flag=True, help='Stats of corpus')
def stats(corpus=False):
    """ Refresh corpora if need be """
    if corpus:
        resolver = helpers.reader.make_resolver()
        print("{} Texts".format(len(resolver.getMetadata().readableDescendants)))


@cli.command()
@click.argument('parts', nargs=-1)
def run_analysis(parts=None):
    parts = list(parts)
    if "corpus_analysis" in parts:
        analysis.general_analysis.corpus_analysis.run()
    if "embedding_analysis" in parts:
        analysis.field_analysis.embeddings_analysis.run()


@cli.command()
def clear_cache():
    files = glob.glob(".pickle_dir/*.pickle")
    print(TASK_SEPARATOR+"Deleting {} pickle files".format(len(files)))
    for file in files:
        os.remove(file)


@cli.command()
def export():
    print(TASK_SEPARATOR+"Exporting for other pipelines")
    print(SUBTASK_SEPARATOR + "Exporting for passim")
    helpers.exporter.make_passim_source()


@cli.command()
def install_third_parties():
    installs = glob.glob("third_parties/build-*.sh")
    print(TASK_SEPARATOR+"Installing {} 3rd parties pipelines".format(len(installs)))
    for install in installs:
        print(SUBTASK_SEPARATOR+"Installing {}".format(install.split("/")[-1].replace("build-", "").replace(".sh", "")))
        call(["sh", install.replace("third_parties/", "")], cwd=os.getcwd()+"/third_parties")
    print(TASK_SEPARATOR+"Installing LaTeX dependencies".format(len(installs)))
    deps = ["babel", "babel-french", "biblatex", "tocbibind", "minitoc", "nomencl", "multirow", "lipsum"]
    call(["tlmgr", "install"]+deps)


@cli.command()
def lemmatize():
    text_files = glob.glob(CORPUS_PATH) + glob.glob(CORPUS_PATH.replace("*.", "."))
    text_files = text_files
    print(TASK_SEPARATOR+"Lemmatizing {} texts".format(len(text_files)))
    lemmatizer = helpers.lemmatizers.Collatinus()
    unknowns = 0
    unk = []
    with ThreadPool(processes=7) as pool:
        for source in pool.imap_unordered(lemmatizer.output, text_files):
            diff = len(lemmatizer.unknown) - unknowns
            unknowns = len(lemmatizer.unknown)
            unk = [(source.replace("data/curated/corpus/generic/", ""), form) for form in lemmatizer.unknown]
            print(SUBTASK_SEPARATOR+"{} done [+{} new unknown forms]".format(source, diff))

            with open("data/curated/corpus/collatinus-lemmatizer.unknown.tsv", "w") as f:
                f.write("\n".join(u[0]+"\t"+u[1] for u in unk))
                f.write("\n")


@cli.command()
def pdf():
    call(["make", "all"], cwd=os.getcwd()+"/redaction")
    call(["make", "purge"], cwd=os.getcwd()+"/redaction")

if __name__ == "__main__":
    cli()
