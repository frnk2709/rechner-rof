import streamlit as st
import datetime
from decimal import Decimal, ROUND_HALF_UP


def show_afa_wg(switch_page):

    st.title('AfA Rechner für Wirtschaftsgüter')

    #Eingaben

    anschaffungskosten = st.number_input('Anschaffungskosten: ', value=0)

    nutzungsdauer = st.number_input('Nutzungsdauer in Jahren: ', value=1)

    datum_anschaffung = st.date_input('Datum der Anschaffung (ggf. bei Montage R 7.4 (1) S.3 beachten): ')


    #Berechnungen

    jahres_afa = berechne_jahre_afa(anschaffungskosten, nutzungsdauer)

    monat_anschaffung = bestimme_monat_anschaffung(datum_anschaffung)

    zeitanteilige_afa = berechne_zeitanteilige_afa(jahres_afa, monat_anschaffung)


    #Ergebnisanzeige
    if st.button('Berechnen'):
        st.success(f'jährliche AfA: {jahres_afa} €')
        st.success(f'zeitanteilige AfA in {datum_anschaffung.year}: {zeitanteilige_afa} €')
    if st.button('zurück'):
        switch_page('menu')



def berechne_jahre_afa(anschaffungskosten, nutzungsdauer):
    if nutzungsdauer <= 0:
        st.error('Nutzungsdauer muss mindestens 1 Jahr betragen')

    anschaffungskosten_decimal = Decimal(str(anschaffungskosten))
    jahres_afa = anschaffungskosten_decimal / nutzungsdauer
    return Decimal(jahres_afa).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)

def bestimme_monat_anschaffung(datum_anschaffung):
    monat_anschaffung = datum_anschaffung.month
    return monat_anschaffung

def berechne_zeitanteilige_afa(jahres_afa, monat_anschaffung):
    zeitanteilige_afa = (jahres_afa / 12) * (12 - monat_anschaffung + 1)
    return Decimal(zeitanteilige_afa).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
