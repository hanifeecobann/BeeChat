#projenin test edildiği kısım
"""
Retrieval isabeti: Doğru başlık getirilen parçalar arasında mı?
Cevap doğruluğu: Cevapta beklenen anahtar kelime var mı?
“Bilmiyorum” testi: Cevabı olmayan sorularda bot uydurmadan reddediyor mu?

değerlendirmeyi yaptığımız kısım burası. chunksize ya da topk, minscore gibi değerleri değiştirmemiz verimli mi değil mi buradan ölçeriz.
"""

import json
from pathlib import Path
from src.chain import ask

tests = json.load(open(Path(__file__).parent / "tests.json", encoding="utf-8"))
hit = kw = n_doc = 0
refuse_ok = n_out = 0

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
