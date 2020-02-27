from typing import List
from pie_extended.cli.sub import get_tagger, get_model, download

# In case you need to download
if False:
    for dl in download("lasla"):
        x = 1

# model_path allows you to override the model loaded by another .tar
model_name = "lasla"
tagger = get_tagger(model_name, batch_size=256, device="cpu", model_path=None)

module = get_model(model_name)

sentences: List[str] = ["Lorem ipsumque ? Ok ok !"]
for sentence_group in sentences:
    iterator, formatter = getattr(module, "get_iterator_and_formatter")()
    print(tagger.tag_str(sentence_group, iterator=iterator, formatter_class=formatter) ) # Output CSV like str
