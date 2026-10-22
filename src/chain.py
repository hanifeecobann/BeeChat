#sorgulama ve cevabın üretildiği kısım

from functools import lru_cache #bilgiyi cachede saklar tekrr çağırdığımızda ordan getirir

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
#placeholder; LLM'e gönderilecek şablonu ve sohbet geçmişinin dinamik olarak yerleştirileceği (placeholder) alanı tanımlamak için kullanılır

from src.config import LLM_MODEL, MIN_SCORE, NOT_FOUND_MSG, TOP_K, get_db #veritabanındaki verileri içe aktarır.


SYSTEM = """Sen bir doküman asistanısın. SADECE aşağıdaki bağlamdaki bilgilere dayanarak cevap ver.
Cevap bağlamda yoksa uydurma; "Bu bilgi dokümanda bulunmuyor." de.
Cevabı Türkçe, açık ve kısa ver.

BAĞLAM:
{context}"""

#ana talimat bloğu burası.
#MessagesPlaceholder("history"): Multi-turn (çok turlu) sohbetlerde geçmiş konuşmaların dinamik olarak araya yerleştirilmesini sağlar. Böylece model önceki soruları ve bağlamı hatırlar.
prompt= ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM),
        MessagesPlaceholder("history"),
        ("human","{question}"),
    ]
)


@lru_cache(maxsize=1)
def _llm():

    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(model=LLM_MODEL)

@lru_cache(maxsize=1)
def _db():
    return get_db()

"""
Anthropic LLM istemcisi ve Veritabanı bağlantısı (_db) her soru sorulduğunda sıfırdan tekrar oluşturulmaz (singleton deseni gibi çalışır). Bellekte tek bir örnek (instance) olarak tutulur, bu da uygulamaya ciddi bir performans kazandırır."""
def _to_text(content) -> str:

    if isinstance(content, str):
        return content
    return "".join(
        block.get("text", "")
        for block in content
        if isinstance(block, dict) and block.get("type") == "text"
    ) #Bu fonksiyon, gelen yanıtın tipini kontrol ederek güvenli bir şekilde düz metne (str) dönüştürür.


def _to_messages(history):
    return[HumanMessage(c) if role=="user" else AIMessage(c) for role,c in history]#Dışarıdan ham tuple listesi ([("user", "merhaba"), ("ai", "selam")]) şeklinde gelen sohbet geçmişini, LangChain'in anlayacağı HumanMessage ve AIMessage nesnelerine dönüştürür.

#bilgi getirme kısmı
def retrieve(question:str, k: int=TOP_K, min_score: float=MIN_SCORE):
    results=_db().similarity_search_with_relevance_scores(question, k=k)
    docs=[]
    for doc, score in results:
        if score>= min_score :
            doc.metadata["score"]=round(float(score),3)
            docs.append(doc)
    return docs


#ana cevap üretilen kısım
def ask(
    question: str,
    history: list[tuple[str, str]] | None = None,
    min_score: float = MIN_SCORE,
    k: int = TOP_K,
):
    docs= retrieve(question, k=k, min_score=min_score)
    if not docs:
        return NOT_FOUND_MSG, []

    context="\n\n".join(f"[{d.metadata['heading']}]\n{d.page_content}" for d in docs)
    messages = prompt.invoke(
        {
            "context": context,
            "history": _to_messages(history or []),
            "question": question,
        }
    )

    answer=_to_text(_llm().invoke(messages).content)
    return answer,docs
