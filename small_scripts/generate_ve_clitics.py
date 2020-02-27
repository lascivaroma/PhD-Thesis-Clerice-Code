from cltk.stem.latin.declension import CollatinusDecliner
import json

decliner = CollatinusDecliner()
known = []
errors = []
for lemma in decliner.__lemmas__:
    try:
        for form, _ in decliner.decline(lemma):
            if form:
                known.append(form)
            else:
                raise Exception("No form")
    except Exception as E:
        print(lemma, "Got an error", E)
        errors.append(lemma)

with open("knownforms.json", "w") as f:
    json.dump(sorted(list(set(known))), f)

with open("-ne.json", "w") as f:
    json.dump([tok for tok in sorted(list(set(known))) if tok.endswith("ue") or tok.endswith("ve")], f)
    print(len([tok for tok in sorted(list(set(known))) if tok.endswith("ue") or tok.endswith("ve")]),
          " valid words ending with -ve or -v.")