import click
import helpers.download


@click.group()
def cli():
    pass


@click.command()
@click.option('--corpus', is_flag=True, help='Update corpus')
def download(corpus=False):
    """ Refresh corpora if need be """
    if corpus:
        helpers.download.download_corpora()
