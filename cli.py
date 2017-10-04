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
    helpers.reader.make_resolver()


if __name__ == "__main__":
    cli()