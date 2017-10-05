from capitains_nautilus.cts.resolver import NautilusCTSResolver
import glob
from ..metadata.ns import THESE_NS, THESE_NS_PREFIX
import logging


def make_resolver(directories=None, additional_metadata=None):
    """ Generate the CapiTainS Resolver and add metadata to it
    """
    if directories is None:
        directories = glob.glob("data/raw/corpora/**/**")
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.CRITICAL)

    resolver = NautilusCTSResolver(resource=directories, logger=logger)
    resolver.inventory.graph.namespace_manager.bind(THESE_NS_PREFIX, THESE_NS)
    return resolver
