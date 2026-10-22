


| Katman | Teknoloji |
|---|---|
| LLM | Claude (`langchain-anthropic`) |
| Embedding | `paraphrase-multilingual-MiniLM-L12-v2` (yerel, çok dilli) |
| Vektör DB | Chroma |
| Arayüz | Streamlit |


 Değerlendirme

`eval/tests.json` içinde üç tür soru var: dokümanda yalnızca kurgusal kooperatif bölümünde geçen bilgiler, genel arıcılık bilgileri ve dokümanda hiç olmayan bilgiler. Ölçümler:

- **Retrieval isabeti:** Beklenen bölüm getirilen parçalar arasında mı?
- **Cevap doğruluğu:** Cevap beklenen anahtar kelimeyi içeriyor mu?
- **"Bilmiyorum" testi:** Dokümanda olmayan soruda uydurmak yerine "bulunmuyor" diyor mu?


| chunk_size | top_k | min_score | Retrieval | Doğruluk | Bilmiyorum |
|---|---|---|---|---|---|
| 800 | 4 | 0.30 | _ | _ | _ |
| 500 | 4 | 0.30 | _ | _ | _ |
| 800 | 6 | 0.30 | _ | _ | _ |
| 800 | 4 | 0.40 | _ | _ | _ |


Proje yapısı

```
doc-chatbot/
├── data/dokuman.docx        # örnek doküman
├── src/
│   ├── config.py            # tüm ayarlar
│   ├── ingest.py            # docx -> vektör DB
│   ├── chain.py             # RAG mantığı
│   └── app.py               # Streamlit arayüzü
├── eval/
│   ├── tests.json           # test soruları
│   └── evaluate.py          # ölçüm betiği
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
