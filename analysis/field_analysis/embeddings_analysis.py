from helpers.embeddings import GensimW2Vec, GensimFasttext
from os import getcwd

WORDS = ["lascivus"]


def test_eval(model):
    model.load_or_compile()

    print("Bellum")
    print(model.most_similar(word="bellvm"))
    print("Lasciva")
    print(model.most_similar(word="lascivvs"))
    print("Mentula")
    print(model.most_similar(word="mentvla"))
    # Interesting !
    print("Lasciva+Mentula")
    print(model.vector_comparison(positive=["lascivvs", "mentvla"]))
    print("Lascivus-Vir")
    print(model.vector_comparison(positive=["lascivvs"], negative=["vir"]))
    print("Lascivus+Vir")
    print(model.vector_comparison(positive=["lascivvs", "vir"]))


def run():
    print("=== GENSIM.Word2Vec ===")
    GModel = GensimW2Vec(model_path=getcwd()+"/data/models/gensim/raw.model")
    test_eval(GModel)
    print("=== GENSIM.FastText ===")
    GModel = GensimFasttext(model_path=getcwd()+"/data/models/gensim-fasttext/raw.model")
    test_eval(GModel)

