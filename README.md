# these

## Description of folders

| Folder or file path | Role |
|-------------|------|
| data/raw/corpora      | Raw download CapiTainS Corpora |
| data/raw/corpora.txt  | List of texts using line        |
| data/raw/corpora.csv  | Date and cut information to deal with corpora |
| data/raw/lemmatization| Folder for lemmatization evaluation |


## Command to run

```shell
python cli.py download --corpus --force
python cli.py enhance_metadata --corpus
python cli.py generate_raw_texts
python cli.py run --part corpus_analysis
```
