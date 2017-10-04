import click
import helpers.download
import helpers.reader


@click.group()
def cli():
    pass


@cli.command()
@click.option('--corpus', is_flag=True, help='Update corpus')
def download(corpus=False):
    """ Refresh corpora if need be """
    if corpus:
        helpers.download.download_corpora()


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