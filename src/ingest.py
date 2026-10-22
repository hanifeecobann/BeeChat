#veri hazırlık ve indexleme aşaması;ham bir Word belgesini alıp temizleyen, hiyerarşik başlıklarla etiketleyen, anlamlı parçalara bölen ve vektör veritabanına kaydeden kritik boru hattıdır (pipeline).

import shutil #dosya kopyalama,taşıma, silme işlemlerini yürüten modül
from pathlib import Path

from docx import Document as Docx #word dosyasını okur
from langchain_core.documents import Document #LangChain ekosisteminde metni ve o metne ait meta verileri (metadata) birlikte tutan standart veri nesnesi
from langchain_text_splitters import RecursiveCharacterTextSplitter #metinleri önce paragraf sonra cümleler olarak böler

from src.config import CHUNK_OVERLAP, CHUNK_SIZE, DB_DIR, DOCX_PATH, get_embeddings

"""
load_docx: Word’ü paragraf paragraf okur. “Heading” stilli paragrafı başlık olarak hatırlar, altındaki metinleri o başlıkla birleştirir. Her bölüm {metin, başlık} olarak saklanır. Bu başlık sonra “kaynak” olarak gösterilir.
burada bağlam koruma (context preservation) yapılıyor.
"""
def load_docx(path:str)->list[Document]:
    doc=Docx(path)
    heading, buf, sections="Giriş", [],[]
#heading; metnin hangi başlıkta olduğunu,
#buf; aynı başlık altındaki paragrafları geçiçi listeler
#sections: Oluşturulan nihai LangChain Document nesnelerinin saklandığı liste
#(buf) biriken metinleri alt alta (\n) birleştirir ve o anki heading bilgisini metadata olarak ekleyerek yeni bir Document nesnesi üretip sections listesine ekler.
    def flush():
        if buf:
            sections.append(
                Document(page_content="\n".join(buf),metadata={"heading": heading})
            )
    for p in doc.paragraphs:
        text =p.text.strip()
        if not text:
            continue
        if p.style.name.startswith(("Heading", "Başlık")):
            flush()
            buf=[]
            heading=text
        else:
            buf.append(text)
    flush()
    return sections # burada yeni bilgiler yeni bir başlığın altına eklenerek kişiye cevap gösterilir.

"""
Metin parçalama evresi
build_chunks: Uzun bölümleri 800 karakterlik parçalara böler. LLM’ler uzun metinde odağını kaybeder, küçük parçalar aramayı daha isabetli yapar."""
def build_chunks(path: str=DOCX_PATH)-> list[Document]:
    sections=load_docx(path) #döküman başlığa göre mantıklı bölünür
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    ) #chunklara bölünür
    return splitter.split_documents(sections)


"""Her parçayı embedding modeliyle bir sayı listesine (vektör) çevirir ve chroma_db’ye kaydeder. Eski veritabanını silip baştan kurar."""
def main():
    from langchain_chroma import Chroma

    if not Path(DOCX_PATH).exists():
        raise SystemExit(f"Döküman bulunamadı: {DOCX_PATH} ")
    chunks=build_chunks()
    print(f"{len(chunks)} parça oluşturuldu (chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")

    if Path(DB_DIR).exists():
        try:
            shutil.rmtree(DB_DIR)
        except PermissionError:
            raise SystemExit("chroma_db silinemedi: önce çalışan Streamlit uygulamasını kapatın.")
    Chroma.from_documents(
        chunks,
        get_embeddings(),
        persist_directory=DB_DIR,
        collection_metadata={"hnsw:space": "cosine"},
    )
    print (f"Vektör veritabanı hazır: {DB_DIR}/")


if __name__ == "__main__":
    main()
