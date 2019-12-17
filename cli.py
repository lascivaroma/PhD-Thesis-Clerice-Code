#!./these_env/bin/python
import click
import glob
import os
import shutil
import typing as t
from multiprocessing.pool import ThreadPool
from subprocess import call

from helpers.printing import TASK_SEPARATOR, SUBTASK_SEPARATOR

import helpers.download
import helpers.reader
import helpers.metadata
import helpers.exporter
import helpers.treebanks
import helpers.metadata.wordcounts

import analysis.general_analysis.treebank_analysis
import analysis.general_analysis.corpus_analysis
import analysis.field_analysis.embeddings_analysis


CORPUS_PATH = "data/curated/corpus/generic/**/*.txt"


@click.group()
def cli():
    pass


@cli.group("corpus")
def corpus_group():
    """ Group of function to deal with corpora """


@corpus_group.command("download")
@click.argument('targets', type=click.Choice(['corpus', 'treebank', 'perseus-catalog']), nargs=-1)
@click.option('--force', is_flag=True, help='Force download')
def download(targets: t.List[str], force=False):
    """ Refresh targets corpora if need be """
    if "corpus" in targets:
        helpers.download.download_corpora(force=force)
    if "treebank" in targets:
        helpers.download.download_corpora(
            src="data/raw/treebanks_xml.csv", tgt="data/raw/treebanks_xml/", force=force,
            is_capitains=False
        )
        helpers.download.download_corpora(
            src="data/raw/treebanks_conllu.csv", tgt="data/raw/treebanks_conllu/", force=force,
            is_capitains=False
        )
    if "perseus-catalog" in targets:
        helpers.download.download_corpora(
            src="data/raw/metadatas.csv", tgt="data/raw/metadatas/", force=force,
            is_capitains=False
        )


@corpus_group.command("build")
@click.argument('targets', type=click.Choice(['texts', 'treebank', 'metadata', 'wordcount']),
                nargs=-1)
def corpus_build(targets: t.List[str]):
    """ Get TARGETS corpora built in plain text """
    # We do texts first

    if "texts" in targets:
        resolver = helpers.reader.make_resolver()
        metadata = helpers.metadata.read_datation_spreadsheet()
        resolver = helpers.metadata.feed_resolver(metadata, resolver)
        helpers.reader.create_raw_text(resolver=resolver)

    # Then we update the metadata
    if "metadata" in targets:
        print("Enhancing the metadata")
        metadata = helpers.metadata.read_datation_spreadsheet()
        resolver = helpers.metadata.feed_resolver(metadata, helpers.reader.make_resolver())
        helpers.metadata.write_inventory(resolver)

    # We could do the treebank
    if "treebank" in targets:
        for corpus in helpers.treebanks.Corpora:
            corpus.parse()
            print(corpus.diversity)

    # We can also build the wordcounts
    if "wordcount" in targets:
        helpers.metadata.wordcounts.build()


@corpus_group.command("lemmatize", help="Lemmatize texts")
@click.argument('lemmatizers', type=click.Choice(['collatinus', 'pie']), nargs=-1)
@click.option("--debug", is_flag=True)
def lemmatize(lemmatizers=[], debug=False):
    """ Lemmatize using LEMMATIZERS"""
    import helpers.lemmatizers
    text_files = glob.glob(CORPUS_PATH) + glob.glob(CORPUS_PATH.replace("*.", "."))
    if debug:
        text_files = text_files[-10:]
    if "collatinus" in lemmatizers:
        helpers.lemmatizers.run_collatinus(text_files=text_files, target_path="data/curated/corpus/generic/")
    if "pie" in lemmatizers:
        helpers.lemmatizers.run_pie_web(text_files=text_files, target_path="data/curated/corpus/generic/", threads=1)


@corpus_group.command()
def check():
    """ Checks which text has no datation or split scheme """
    from MyCapytain.resolvers.cts.local import CtsCapitainsLocalResolver
    from MyCapytain.common.reference import URN
    from collections import defaultdict
    import csv
    print("Checking: {}".format(", ").join(glob.glob("data/raw/corpora/*/*")))
    print()

    dates = {

    }
    schemes = {

    }

    # Loading schemes
    with open("data/raw/datation.tsv") as f:
        reader = csv.DictReader(f, delimiter="\t")
        header = reader.fieldnames
        for text_dict in reader:
            urn = URN(text_dict["URN"])
            text_group = str(urn.upTo(URN.TEXTGROUP))
            text = str(urn)
            date, scheme = (text_dict["Birth"], text_dict["Death"]), text_dict["Citation level"]
            dates[text_group] = dates[text] = date
            schemes[text] = scheme

    # Loading texts
    resolver = CtsCapitainsLocalResolver(resource=glob.glob("data/raw/corpora/*/*"))
    from io import StringIO
    texts = defaultdict(lambda: dict(date=False, scheme=False))
    false_file = StringIO()
    output = csv.DictWriter(false_file, fieldnames=header, delimiter=";")
    output.writeheader()
    for obj in resolver.inventory.readableDescendants:
        if obj.lang != "lat":
            if obj.lang != "eng":
                print(obj)
            continue
        text = str(obj.id)
        sc, da = True, True
        if str(text) not in schemes:
            sc = False
        if str(URN(text).upTo(URN.TEXTGROUP)) not in dates:
            da = False
        if not sc or not da:
            ds = dates.get(str(URN(text).upTo(URN.TEXTGROUP)), ("", ""))
            output.writerow({
                "URN": text,
                "Nom FR": obj.parent.parent.get_label(),
                "Birth": ds[0],
                "Death": ds[1],
                "Name of citation level": ",".join([citation.name for citation in obj.citation])
            })
    # Retournons au début
    false_file.seek(0)
    # Affichons
    print(false_file.read())


@corpus_group.command()
def infos():
    """ Retrieve statistics and information about the corpus """
    resolver = helpers.reader.make_resolver()
    print("{} Texts".format(len(resolver.getMetadata().readableDescendants)))


@cli.group("analysis")
def ana():
    """ Command related to build analysis or experiences """


@ana.command("corpus", help="Analyse texts corpora")
def analize_corpus():
    analysis.general_analysis.corpus_analysis.run()


@ana.command("treebanks", help="Analyse treebanks")
def analize_tb():
    analysis.general_analysis.treebank_analysis.run(helpers.treebanks.Corpora)


@ana.command("embeddings", help="Analyse embeddings")
def analize_embs():
    analysis.field_analysis.embeddings_analysis.run()


@cli.command("cache-clear", help="Clear cache")
def clear_cache():
    """ Clear the cache from resolvers """
    files = glob.glob(".pickle_dir/*.pickle")
    print(TASK_SEPARATOR+"Deleting {} pickle files".format(len(files)))
    for file in files:
        os.remove(file)


@cli.group("thirdparties")
def third_parties():
    """ Interactions with third parties """


@third_parties.command("export", help="Export data for third parties tools")
def export():
    print(TASK_SEPARATOR+"Exporting for other pipelines")
    print(SUBTASK_SEPARATOR + "Exporting for passim")
    helpers.exporter.make_passim_source()


@third_parties.command("install", help="Install non-python tools")
def install_third_parties():
    installs = glob.glob("third_parties/build-*.sh")
    print(TASK_SEPARATOR+"Installing {} 3rd parties pipelines".format(len(installs)))
    for install in installs:
        print(SUBTASK_SEPARATOR+"Installing {}".format(install.split("/")[-1].replace("build-", "").replace(".sh", "")))
        call(["sh", install.replace("third_parties/", "")], cwd=os.getcwd()+"/third_parties")
    print(TASK_SEPARATOR+"Installing LaTeX dependencies".format(len(installs)))
    deps = ["babel", "babel-french", "biblatex", "tocbibind", "minitoc", "nomencl", "multirow", "lipsum"]
    call(["tlmgr", "install"]+deps)


@cli.command("latex-pdf", help="Generate the thesis PDF")
def pdf():
    call(["make", "all"], cwd=os.getcwd()+"/redaction")
    call(["make", "purge"], cwd=os.getcwd()+"/redaction")


@cli.group()
def install():
    """ Install tools """

@install.command()
def cltk():
    """ Install CLTK data """
    from cltk.corpus.utils.importer import CorpusImporter
    corpus_importer = CorpusImporter('latin')
    corpus_importer.import_corpus('latin_models_cltk')


if __name__ == "__main__":
    cli()
