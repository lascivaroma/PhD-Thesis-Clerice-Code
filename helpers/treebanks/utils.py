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


def doc_token_dict_sum(data):
    """ Token count Dict into count of words {docId : [words]} -> int

    :param data:{docId : [tokenCount]}
    :type data: dict
    :return:
    """
    return sum([
        len(tokenCount)
        for tokenCountList in data.values()
        for tokenCount in tokenCountList
    ])


