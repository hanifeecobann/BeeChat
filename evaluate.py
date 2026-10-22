import json
from src.chain import ask

tests = json.load(open("eval/tests.json", encoding="utf-8"))

hit = kw = n_doc = 0          # dokümanda cevabı olan sorular
refuse_ok = n_out = 0         # dokümanda cevabı OLMAYAN sorular

for t in tests:
    answer, docs = ask(t["question"])
    if t["expected_heading"] is None:
        n_out += 1
        if any(k.lower() in answer.lower() for k in t["keywords"]):
            refuse_ok += 1
        else:
            print("UYDURMA OLABİLİR:", t["question"], "->", answer[:100])
        continue
    n_doc += 1
    if any(d.metadata["heading"] == t["expected_heading"] for d in docs):
        hit += 1
    if any(k.lower() in answer.lower() for k in t["keywords"]):
        kw += 1
    else:
        print("KAÇIRDI:", t["question"], "->", answer[:100])

print(f"Retrieval isabeti : {hit}/{n_doc} ({hit/n_doc:.0%})")
print(f"Cevap doğruluğu   : {kw}/{n_doc} ({kw/n_doc:.0%})")
print(f"'Bilmiyorum' testi: {refuse_ok}/{n_out} ({refuse_ok/n_out:.0%})")
