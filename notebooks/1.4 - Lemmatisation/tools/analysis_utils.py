from tqdm import tqdm
from typing import Set, Tuple, Union, List, Dict
from collections import defaultdict, Counter

def import_known_tokens(
    dataset="/home/thibault/dev/LASLA/mood-tense-voice-pft-clitics/train.tsv",
    lower_tokens=True
) -> Tuple[Set[str], Set[str]]:
    """ This functions returns sets formed of (1) the known tokens and (2) the known lemmas
    """
    known_tokens = set()
    known_lemmas = set()
    with open(dataset) as f:
        headers = None
        for line in f:
            if line.strip():
                line = line.split("\t")
            else:
                continue
                
            if not headers:
                headers = line
                continue
            annot = dict(zip(headers, line))
            if lower_tokens:
                known_tokens.add(annot["token"].lower())
            else:
                known_tokens.add(annot["token"])
            known_lemmas.add(annot["lemma"])
            
    return known_tokens, known_lemmas


Sentence = List
TaskName = str
InputToken = str
AnnotationValue = str
Count = int
TokenAnnotation = Dict[TaskName, str]
Accuracy_Dict = Dict[TaskName, bool]


def compile_scores(
    preds, truthes, 
    task_list, 
    known_tokens=None, known_lemmas=None, lower_lemma=False, lower_tokens=True
) -> Tuple[
    List[Sentence[Tuple[TokenAnnotation, TokenAnnotation, Accuracy_Dict]]],
    Dict[TaskName, Tuple[List[AnnotationValue], List[AnnotationValue]]],
    Dict[TaskName, Tuple[List[AnnotationValue], List[AnnotationValue]]],
    Dict[TaskName, Dict[AnnotationValue, Dict[AnnotationValue, Dict[InputToken, Count]]]],
    Dict[str, Union[TokenAnnotation, bool]]
]:
    """
    Takes a list of predictions and a list of truth, as well as the tasks to compute for.
    
    Returns
    
        (1) List of sentence where tokens are (pred, truth, AccuracyDict)
        (2) Dictionary of POS -> (List of Pred, List of Truth)
        (3) Dictionary of POS -> (List of Pred, List of Truth) when Truth != "_"
        (4) Dictionary of errors in the form POS -> (Truth -> (Pred -> (Token, Number of Errors)))
        (5) List of annotations in the form of a dictionary with:
            (a) Each tasks as a key with a bool value indicating Pred = Truth
            (b) A key "GOLD" containing all truths
            (c) [Optional] A `known_token` and a `known_lemma` key as bool
    """
    _results = []
    _raw_scores = {
        task: ([], []) # Pred, Truth
        for task in task_list
    }
    _raw_scores_not_empty = {
        task: ([], []) # Pred, Truth
        for task in task_list
    }
    _errors = {
        #{truth: {pred: {token: int}} # (token, pred, truth)
        task: defaultdict(lambda: defaultdict(Counter))
        for task in task_list
    }
    scores_lemma_pos = [
        # {"known_token": bool, "known_lemma": bool, "tasks_scores": {tasks: bool}}
    ]
    for p_sent, t_sent in zip(preds, truthes):
        score_sentence = []
        for (_, p_tags), (t_tags) in zip(p_sent, t_sent):
            token = t_tags["form"]
            if lower_lemma:
                p_tags["lemma"] = p_tags["lemma"].lower()
                
            try:
                score_sentence.append((
                    p_tags,
                    t_tags,
                    {task: p_tags.get(task, "_") == t_tags.get(task, "_") for task in task_list}
                ))
                for task in task_list:
                    t_value = t_tags.get(task, "_")
                    p_value = p_tags.get(task, "_")
                    _raw_scores[task][0].append(p_value)
                    _raw_scores[task][1].append(t_value)
                    if t_value != "_":
                        _raw_scores_not_empty[task][0].append(p_value)
                        _raw_scores_not_empty[task][1].append(t_value)
                    if t_value != p_tags[task]:
                        _errors[task][t_value][p_value][token] += 1
                        
                scores_lemma_pos.append(
                    score_sentence[-1][-1]
                )
                scores_lemma_pos[-1]["GOLD"] = t_tags
                if known_tokens:
                    if lower_tokens:
                        scores_lemma_pos[-1]["known_token"] = token in known_tokens or token.lower() in known_tokens
                    else:
                        scores_lemma_pos[-1]["known_token"] = token in known_tokens
                    
                if known_lemmas:
                    scores_lemma_pos[-1]["known_lemma"] = p_tags["lemma"] in known_lemmas
            except:
                print(p_sent)
                print(t_sent)
                raise
        _results.append(score_sentence)
    return _results, _raw_scores, _raw_scores_not_empty, _errors, scores_lemma_pos


def vjui(tok):
    """ Replace Vs by Us and Js by Is """
    return tok.replace("v", "u").replace("j", "i").replace("J", "I").replace("V", "U")


def convert_raw(gold, task_list=[], 
                form_fn=lambda x: vjui(x).lower(), 
                lemma_fn=lambda x: vjui(x).lower(), 
                pos_fn=lambda x: x.replace("com", "").replace("pro", ""),
                clitics_are_duplicate=True,
                clitics_starts_with_dash=False, pos_key="POS", remove_disambiguation: bool = True
               ):
    """ Converts input data into Gold data
    """
    temp_out = []
    for sentence in tqdm(gold):
        temp_sentence = []
        for token in sentence:
            new_token = {task: "_" for task in task_list}
            new_token.update({
                "form": form_fn(token["form"]),
                "lemma": lemma_fn(token["lemma"]),
                "pos": pos_fn(token[pos_key]),
            })
            # No disambiguation at the lemmatizer lever
            if remove_disambiguation and new_token["lemma"][-1].isnumeric():
                new_token["lemma"] = new_token["lemma"][:-1]

            #print(token)
            # Treat morph as separate tasks
            for morph in token["morph"].split("|"):
                task, value = morph.split("=")
                new_token[task] = value
            new_token["Mood_Tense_Voice"] = "|".join([
                new_token.get(task, "_")
                for task in ("Mood", "Tense", "Voice")
            ]).replace("_|_|_", "_")

            if clitics_are_duplicate and temp_sentence and new_token["form"] == temp_sentence[-1]["form"]:
                temp_sentence[-1]["lemma"] += "界" + new_token["lemma"]
                continue
            elif clitics_starts_with_dash and new_token["form"].startswith("-"):
                temp_sentence[-1]["form"] += new_token["form"][1:]
                temp_sentence[-1]["lemma"] += "界" + new_token["lemma"]
                continue
            temp_sentence.append(new_token)

        temp_out.append(temp_sentence)
    return temp_out
