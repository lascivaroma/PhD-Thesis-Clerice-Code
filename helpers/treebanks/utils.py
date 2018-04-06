import collections


def flatten_doc_dict(data):
    """ Flatten a count dict from Data wher {doc_id: {key: count}}

    :param data:
    :return: {key: count}
    """
    new = collections.Counter()
    for count_dict in data.values():
        new.update(count_dict)
    return new
