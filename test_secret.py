import streamlit as st

psw= st.secrets['password']

try:
    st.subheader(psw)
    st.success('Funziona')
except:
    st.warning('Secret non funziona bene')