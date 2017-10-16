from helpers.embeddings import GensimW2Vec
from os import getcwd

WORDS = ["lascivus"]


def run():
    GModel = GensimW2Vec(model_path=getcwd()+"/data/models/gensim/raw.model")
    GModel.load_or_compile()
    print(GModel.most_similar(word="bellum"))
    print(GModel.most_similar(word="lasciva"))
    print(GModel.most_similar(word="mentula"))
    print(GModel.most_similar(word="mentulam"))
