Antoniak et Mimno, 2018


- Remove words appearing less than 20 times

# Compute

- Number of documents
- Unique Words
- Vocabulary Density (Unique Word / Number of words ?)
- Words per document (Average)

# Corpus Parameters

##  Set-up three reader for three different process

- One which reads document in the same order every time
	- Evaluates randomness of algorithm (Random initialization, etc.)
- One which shuffle documents
	- Evaluates impact of document order in the learning
- One which removes documents from the set and replace them to keep the same size of of corpus
	- Evaluates variability due to the presence of specific sequences

## Size of corpus 

- Keep 20% of the corpus, preferably the beginning

## Documents length

2 Settings :

- 1 document = 1 sentence
- 1 document = multiple sentences

# Algorithms

## LSA

- Term-Document matrix with TF-IDF
- L2 Normalization
- Sublinear TF Scaling
- Dimensionality reduction via randomized solver

## SGNS

- Skip-gram with negative sampling (Mikolov 2013 : Word2Vec ?)
- Gensim


## Glove

Nothing specific

## PPMI

- library `hyperwords`
- `cds`=0.75
- `eig`=0.5
- `sub`=10^-5
- `win`=5

# Methods


1. Train 50 of each
2. Generate topic models to get 20 relevant words using 200 topics from an LDA topic model
3. Compute cosine similarity of each word to other words, calculate mean and standard deviation across each set of 50 models

eg.


