import streamlit as st
from afa_wg_streamlit import show_afa_wg
from afa_gebaeude import show_afa_gb
from ertragswertverfahren.ertragswertferfahren_rechner_streamlit import show_ertragswertverfahren_rechner
from entfernungspauschale_st import show_entfernungspauschale

# Session-State initialisieren
if 'page' not in st.session_state:
    st.session_state.page = 'menu'

# Navigation
def switch_page(page):
    st.session_state.page = page

# Menüverwaltung
if st.session_state.page == 'menu':
    st.title('Wähle einen Rechner')
    if st.button('AfA einzelnes Wirtschaftsgut'):
        switch_page('afa_wg')
    if st.button('AfA für Gebäude'):
        switch_page('afa_gb')
    if st.button('Ertragswertferfahren'):
        switch_page('ertragswertverfahren')
    if st.button('Entfernungspauschale'):
    switch_page('entfernungspauschale')

elif st.session_state.page == 'afa_wg':
    show_afa_wg(switch_page)
elif st.session_state.page == 'afa_gb':
    show_afa_gb(switch_page)
elif st.session_state.page == 'ertragswertverfahren':
    show_ertragswertverfahren_rechner(switch_page)
elif st.session_state.page == 'entfernungspauschale':
    show_entfernungspauschale(switch_page)
