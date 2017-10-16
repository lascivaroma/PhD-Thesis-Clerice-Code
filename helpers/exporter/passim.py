import json
from helpers.reader.curated import get_passage_dict, get_texts


def make_passim_source(path="data/curated/passim/corpus.json"):
    texts = get_passage_dict(get_texts())
    full_dict = {}
    for text_id, plaintext in texts.items():
        full_dict[text_id] = plaintext

    with open(path, "w") as target:
        json.dump(full_dict, target)

