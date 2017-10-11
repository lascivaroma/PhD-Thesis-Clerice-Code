import pickle
import os
from helpers.printing import TASK_SEPARATOR


def memoize(method):
    """ Decorator to help cache function

    ..note :: Helps to deal with cache path

    :param method: Function to cache
    :return: Function with cache implementation
    """
    def cached_method(*args, **kwargs):

        name = "./.pickle_dir/{}.pickle".format(method.__name__)

        if os.path.isfile(name):
            with open(name, "rb") as f:
                results = pickle.load(f)
            return results

        results = method(*args, **kwargs)
        with open(name, "wb") as f:
            pickle.dump(results, f)
        return results

    return cached_method