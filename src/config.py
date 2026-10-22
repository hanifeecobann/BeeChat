#ayarlamanın yapıldığı kısım

import os
from pathlib import Path #işleti sistemi uyumsuzluğunu giderir.
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
#projenin ana kök dizinini (root directory) dinamik olarak belirler. Bu sayede kod hangi bilgisayarda veya sunucuda çalıştırılırsa çalıştırılsın dosya yolları asla patlamaz.
load_dotenv(BASE_DIR / ".env")

#configurasyon hiperparametre ayarları
DOCX_PATH = os.getenv("DOCX_PATH", str(BASE_DIR / "data" / "dokuman.docx"))
DB_DIR = os.getenv("DB_DIR", str(BASE_DIR / "chroma_db"))
EMBED_MODEL=os.getenv("EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-V2"
) #Metni sayılara çeviren model,Metinleri ve arama sorgularını makinenin anlayacağı sayısal vektörlere (embeddings) çevirecek olan Hugging Face modelidir. Çok dilli (multilingual) olması Türkçe destek açısından kritiktir.
LLM_MODEL=os.getenv("LLM_MODEL", "claude-sonnet-5-5") #cevap üreten model
CHUNK_SIZE=int(os.getenv("CHUNK_SIZE","400")) #Büyük dokümanların vektör veritabanına eklenmeden önce kaç karakterlik parçalara bölüneceğini belirler (burada her parça maksimum 800 karakterdir).
CHUNK_OVERLAP=int(os.getenv("CHUNK_OVERLAP", "120")) #Ardışık iki parça arasında 120 karakterlik bir örtüşme (kesişim) olmasını sağlar. Amaç, cümlelerin parça sınırlarında ikiye bölünmesinden kaynaklı bağlam (context) ve anlam kayıplarını engellemektir.
TOP_K=int(os.getenv("TOP_K","4")) #her soruda en az benzer 4 parça
MIN_SCORE=float(os.getenv("MIN_SCORE","0.30")) #benzerlik skoru %30un altındaysa alakasız de

NOT_FOUND_MSG="Bu bilgi sahip olduğum dökümanda bulunmamaktadır" #benzerlik bulamadığında döner

def get_embeddings():
    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )#Vektörlerin (embedding) normalizasyonunu sağlar. Cosine similarity (kosinüs benzerliği) hesaplamalarında normalizasyon, matematiksel olarak işlemleri hızlandırır ve skoru doğrudan 0-1 aralığında hassas biçimde normalize etmeye yardımcı olur.
#Vektör Veritabanı (Chroma) Bağlantı Fonksiyonu
def get_db():
    from langchain_chroma import Chroma

    return Chroma(
        persist_directory=DB_DIR,
        embedding_function=get_embeddings(),
        collection_metadata={"hnsw:space": "cosine"},

    )
"""
persist_directory=DB_DIR: Vektörlerin RAM'de uçup gitmemesini, diskteki DB_DIR klasörüne kalıcı (persistent) olarak kaydedilmesini sağlar.
embedding_function=get_embeddings(): Veritabanına metin eklenirken veya veritabanından arama yapılırken hangi embedding modelinin kullanılacağını Chroma'ya bildirir.
collection_metadata={"hnsw:space": "cosine"}: Vektörler arasındaki benzerlik hesabının Cosine Similarity (Kosinüs Benzerliği) metriğine göre yapılacağını konfigüre eder. HNSW (Hierarchical Navigable Small World) indeksi sayesinde büyük veri setlerinde bile milisaniyeler içinde en yakın parçalar taranabilir.
"""