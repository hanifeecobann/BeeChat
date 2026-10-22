#web arayüzü


import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import streamlit as st
from src.chain import ask
from src.config import MIN_SCORE

st.set_page_config(page_title="Arı döküman asistanı")
st.title("Arı Dökümanı Asistanı ")
st.caption("Bu uygulama sorularınızı yalnızca yüklenen dökümantasyona dayanarak cevaplayacaktır")

with st.sidebar:
    st.header("Ayarlar")
    min_score=st.slider(
        "Benzerlik Eşiği", 0.0,1.0, MIN_SCORE,0.05,
        help ="Değer yükselirse asistan daha temkinli olacak ve sorulara saha sık bulunmuyor cevabı verecektir.",
    )
    if st.button("Sohbeti Temizle"):
        st.session_state.history=[]
        st.rerun()
if "history" not in st.session_state:
    st.session_state.history=[]

for role, text in st.session_state.history:
    st.chat_message(role).write(text)

if q:= st.chat_input("Dökümana bir soru sor.."):
    st.chat_message("user").write(q)
    with st.spinner("Düşünüyorum..."):
        answer , docs   =ask(q,st.session_state.history,min_score=min_score)
    st.chat_message("assistant").write(answer)
    if docs:
        with st.expander("Kaynaklar"):
            for d in docs:
                st.markdown(f"**{d.metadata['heading']}** · skor {d.metadata['score']}")
                st.caption(d.page_content[:300]+ "...")

    history = st.session_state.setdefault("history", [])
    history += [("user", q), ("assistant", answer)]

