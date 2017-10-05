import click
import helpers.download
import helpers.reader
import helpers.metadata


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
    if corpus:
        print("{} Texts".format(len(resolver.getMetadata().readableDescendants)))


if __name__ == "__main__":
    cli()