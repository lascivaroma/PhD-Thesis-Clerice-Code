from MyCapytain.resolvers.cts.local import CtsCapitainsLocalResolver
import glob


def make_resolver(directories=None, additional_metadata=None):
    """ Generate the CapiTainS Resolver and add metadata to it
    """
    if directories is None:
        directories = glob.glob("data/raw/corpora/**/**")
    print(directories)
