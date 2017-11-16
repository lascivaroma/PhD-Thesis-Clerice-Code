from helpers.embeddings import GensimW2Vec, GensimFasttext
from os import getcwd

WORDS = ["lascivus"]


def test_eval(model):
    model.load_or_compile()
    print("Bellum")
    print(model.most_similar(word="bellum"))
    print("Lasciva")
    print(model.most_similar(word="lasciva"))
    print("Mentula")
    print(model.most_similar(word="mentula"))
    print("Mentulam")
    print(model.most_similar(word="mentulam"))
    # Interesting !
    print("Lasciva+Mentula")
    print(model.vector_comparison(positive=["lasciva", "mentula"]))
    print("Lascivus-Vir")
    print(model.vector_comparison(positive=["lascivus"], negative=["vir"]))
    print("Lascivus+Vir")
    print(model.vector_comparison(positive=["lascivus", "vir"]))


def run():
    print("=== GENSIM.Word2Vec ===")
    GModel = GensimW2Vec(model_path=getcwd()+"/data/models/gensim/raw.model")
    test_eval(GModel)
    print("=== GENSIM.FastText ===")
    GModel = GensimFasttext(model_path=getcwd()+"/data/models/gensim-fasttext/raw.model")
    test_eval(GModel)

