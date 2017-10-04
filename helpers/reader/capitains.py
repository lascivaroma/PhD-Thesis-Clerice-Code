from MyCapytain.resolvers.cts.local import CtsCapitainsLocalResolver
from capitains_nautilus.cts.resolver import NautilusCTSResolver
import glob


def make_resolver(directories=None, additional_metadata=None):
    """ Generate the CapiTainS Resolver and add metadata to it
    """
    if directories is None:
        directories = glob.glob("data/raw/corpora/**/**")
    resolver = NautilusCTSResolver(resource=directories)
    return resolver
