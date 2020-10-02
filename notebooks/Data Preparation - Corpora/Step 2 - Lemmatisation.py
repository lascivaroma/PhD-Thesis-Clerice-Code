#!/usr/bin/env python
# coding: utf-8

# In[3]:


#!pip install ../../../nlp-pie-taggers --upgrade
#!pip install https://github.com/PonteIneptique/pie/archive/improvement/AttentionDecoder.predict_max.zip --upgrade

get_ipython().system('rm ./lemmatized/plain-text/*-pie*.txt')


# In[1]:


from typing import List
from pie_extended.cli.utils import get_tagger, get_model, download

# In case you need to download
do_download = False
if do_download:
    for dl in download("lasla"):
        x = 1

# model_path allows you to override the model loaded by another .tar
model_name = "lasla"
tagger = get_tagger(model_name, batch_size=128, device="cuda", model_path=None)


# In[3]:


# Get the main object from the model (: data iterator + postprocesor
from pie_extended.models.lasla.imports import get_iterator_and_processor
import glob
import tqdm

for file in tqdm.tqdm(glob.glob("lemmatized/plain-text/*.txt")):
    try:
        if "-pie" not in file:
            iterator, processor = get_iterator_and_processor()
            tagger.tag_file(file, iterator=iterator, processor=processor)
    except Exception as E:
        print(file)
        print(E)


# In[ ]:





# ## Debug

# In[2]:


# Get the main object from the model (: data iterator + postprocesor
from pie_extended.models.lasla.imports import get_iterator_and_processor

iterator, processor = get_iterator_and_processor()
file = "lemmatized/plain-text/urn:cts:latinLit:stoa0275.stoa006.opp-lat1.txt"
with open(file) as f:
    print(f.read())

tagger.tag_file(file, iterator=iterator, processor=processor)


# In[ ]:


get_ipython().system('mkdir -p lemmatized/tsv')
get_ipython().system('mv lemmatized/plain-text/*-pie.txt lemmatized/tsv/')

