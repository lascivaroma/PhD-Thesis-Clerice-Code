from .models import GensimW2Vec, GensimIterator, GensimFasttext
from .experiments import Experiment

def run(test_mode: bool = False, sample=None):
    directory = "/home/thibault/dev/these/data/curated/corpus/generic/**/*.txt"
    print("Setting up Model")
    experiment = Experiment(directory, model_count=20)
    experiment.run()



if __name__ == "__main__":
    run()
