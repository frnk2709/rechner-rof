import streamlit as st
from decimal import Decimal, ROUND_HALF_UP
import datetime

from narwhals.exceptions import InvalidOperationError


def show_afa_gb(switch_page):
    st.title('AfA für Gebäude')



    # Eingaben

    anschaffungskosten = st.number_input('Anschaffungskosten: ')

    today = datetime.date.today()
    today_years_ago = today.replace(year=today.year - 200)
    datum_anschaffung = st.date_input('Datum der Anschaffung / Übergang Besitz, Nutzen und Lasten:',
                                      value=today,
                                      min_value=today_years_ago,
                                      key='a')

    optionen_eigenschaften = ['Betriebsvermögen und keine Wohnzwecke und Bauantrag nach 31. März 1958 gestellt',
                              'andere']
    nutzung = st.selectbox('Nutzung / Eigenschaften des Gebäudes', optionen_eigenschaften)


    datum_fertigstellung = None
    if nutzung == 'andere':
        datum_fertigstellung = st.date_input('Datum der Fertigstellung:',
                                             value=today,
                                             min_value=today_years_ago,
                                             key='b')
        optionen = ['ja', 'nein']
        eigene_wohnzwecke = st.selectbox('teilweise Nutzung für eigene Wohnzwecke?', optionen)

    elif nutzung == 'Betriebsvermögen und keine Wohnzwecke und Bauantrag nach 31. März 1958 gestellt':
        eigene_wohnzwecke = 'nein'



    # Berechnungen

    bmg = bestimme_bmg(eigene_wohnzwecke, anschaffungskosten)

    afa_satz = bestimme_afa_satz(datum_fertigstellung, nutzung)

    jahres_afa = berechne_jahres_afa(bmg, afa_satz)

    zeitanteilige_afa = berechne_zeitanteilige_afa(jahres_afa, datum_anschaffung)



    # Ergebnisanzeige

    if st.button('Berechnen'):
        st.success(f'Bemessungsgrundlage: {bmg}')
        st.success(f'AfA-Satz: {float(afa_satz) * 100} %')
        st.success(f'jährliche Afa: {jahres_afa}')
        st.success(f'AfA in {datum_anschaffung.year}: {zeitanteilige_afa}')
    if st.button('zurück'):
        switch_page('menu')



def bestimme_bmg(eigene_wohnzwecke, anschaffungskosten):
    ak = Decimal(str(anschaffungskosten))

    if eigene_wohnzwecke == 'ja':
        nutzflaeche_gesamt = st.number_input('gesamte Nutzfläche:')
        nf_g = Decimal(str(nutzflaeche_gesamt))
        nutzflaeche_vermietet = st.number_input('vermietete Nutzfläche:')
        nf_v = Decimal(str(nutzflaeche_vermietet))
        try:
            if nf_g == 0:
                return 'bitte Nutzfläche eingeben'
            verhaeltnis = (nf_v / nf_g)
        except (InvalidOperationError, ZeroDivisionError) as e:
            print(e)

        bmg = ak * verhaeltnis

    elif eigene_wohnzwecke == 'nein':
        bmg = ak

    return bmg


def bestimme_afa_satz(datum_fertigstellung, nutzung):
    if nutzung == 'andere':
        if datum_fertigstellung > datetime.date(2022, 12, 31):
            return Decimal('0.03')
        elif datetime.date(1924, 12, 31) < datum_fertigstellung < datetime.date(2023, 1, 1):
            return Decimal('0.02')
        elif datum_fertigstellung < datetime.date(1925, 1, 1):
            return Decimal('0.025')
    elif nutzung == 'Betriebsvermögen und keine Wohnzwecke und Bauantrag nach 31. März 1985 gestellt':
        return Decimal('0.03')


def berechne_jahres_afa(bmg, afa_satz):
    if bmg and afa_satz:
        try:
            satz = Decimal(str(afa_satz))
            jahres_afa = bmg * satz
            return Decimal(jahres_afa).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except TypeError:
            st.error('bitte alle Felder ausfüllen')
    else:
        st.warning('bitte alle Felder ausfüllen')


def berechne_zeitanteilige_afa(jahres_afa, datum_anschaffung):
    if jahres_afa and datum_anschaffung:
        try:
            monat_anschaffung = datum_anschaffung.month
            zeitanteilige_afa = (jahres_afa / 12) * (12 - monat_anschaffung + 1)
            return Decimal(zeitanteilige_afa).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        except TypeError:
            st.error('bitte alle Felder ausfüllen')
    else:
        st.warning('bitte alle Felder ausfüllen')
