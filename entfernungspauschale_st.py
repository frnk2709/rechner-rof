import math
from decimal import Decimal
import streamlit as st


def show_entfernungspauschale(switch_page):

    st.title('Entfernungspauschale')


    def berechne_entfernungspauschale(tage, strecke, abfrage_pkw):
        if strecke <= 20:

            entfernungspauschale = tage * strecke * Decimal('0.3')

            st.info(f'{tage} Tage * {strecke} km * 0,30 € = {entfernungspauschale} €')

        elif strecke > 20:

            strecke_ab_20 = strecke - Decimal('20')
            ep_bis_20 = tage * Decimal('20') * Decimal('0.3')
            ep_ab_20 = tage * strecke_ab_20 * Decimal('0.3')
            entfernungspauschale = ep_bis_20 + ep_ab_20

            st.info(
                f'{tage} Tage * 20 km * 0,30 € = {ep_bis_20} €  \n{tage} Tage * {strecke_ab_20} km * 0,38 € = {ep_ab_20} €')

        if abfrage_pkw == 'nein':

            st.warning(
                'Die Entfernungspauschale kann nur bis zu einer Höhe von 4500 € angesetzt werden. § 9 (1) S.3 Nr.4 S.2 Hs.1 EStG')

            return min(entfernungspauschale, Decimal('4500'))

        elif abfrage_pkw == 'für die ganze Strecke':

            st.info(
                'Für die Entfernungspauschale kann ein höherer Betrag als 4500 € angesetzt werden. § 9 (1) S.3 Nr.4 S.2 Hs.2 EStG')

            return entfernungspauschale


    def berechne_entfernungspauschale_gemischt(tage, strecke, entfernung_pkw):
        strecke_pkw = Decimal(str(math.floor(entfernung_pkw)))
        strecke_rest = strecke - strecke_pkw

        st.info('Die erhöhte Entfernungspauschale ist vorrangig für die Teilstrecke anzusetzen, welche '
                'mit dem eigenen Pkw zurückgelegt wurde.')

        if strecke_rest <= 20:

            strecke_pkw_bis_20 = min(strecke_pkw, Decimal('20'))
            strecke_pkw_ab_20 = max(strecke_pkw - Decimal('20'), Decimal('0'))

            ep_rest_bis_20 = tage * strecke_rest * Decimal('0.3')
            ep_pkw_bis_20 = tage * strecke_pkw_bis_20 * Decimal('0.3')
            ep_pkw_ab_20 = tage * strecke_pkw_ab_20 * Decimal('0.38')
            entfernungspauschale = ep_rest_bis_20 + ep_pkw_bis_20 + ep_pkw_ab_20

            st.info(f'''
                    Teiltrecke mit anderen Verkehrsmitteln:  
                    {tage} Tage * {strecke_rest} km * 0,30 € = {ep_rest_bis_20} €  
    
                    Teilstrecke mit Pkw:  
                    {tage} Tage * {strecke_pkw_bis_20} km * 0,30 € = {ep_pkw_bis_20} €  
                    {tage} Tage * {strecke_pkw_ab_20} km * 0,38 € = {ep_pkw_ab_20} €  
                    ''')

            return entfernungspauschale

        elif strecke_rest > 20:

            strecke_rest_ab_20 = strecke_rest - Decimal('20')

            ep_rest_bis_20 = tage * Decimal('20') * Decimal('0.3')
            ep_rest_ab_20 = tage * strecke_rest_ab_20 * Decimal('0.38')
            ep_pkw = tage * strecke_pkw * Decimal('0.38')
            ep_rest = ep_rest_bis_20 + ep_rest_ab_20

            st.info(f'''
                    Teiltrecke mit anderen Verkehrsmitteln:  
                    {tage} Tage * 20 km * 0,30 € = {ep_rest_bis_20} €  
                    {tage} Tage * {strecke_rest_ab_20} km * 0,38 € = {ep_rest_ab_20} €  
    
                    Teilstrecke mit Pkw:  
                    {tage} Tage * {strecke_pkw} km * 0,30 € = {ep_pkw} €  
                    ''')

            if ep_rest > 4500:
                st.warning('''Die Entfernungspauschale für die Teilstrecke, welche mit anderen Verkehrsmitteln
                           zurückgelegt wurde, übersteigt 4500 €. Sie wird deshalb auf 4500 € gedeckelt.  
                           § 9 (1) S.3 Nr.4 S.2 Hs.1 EStG
                           ''')

                ep_rest = Decimal('4500')

            entfernungspauschale = ep_rest + ep_pkw

            return entfernungspauschale


    # Eingaben

    anzahl_tage = st.number_input('Anzahl der Tage, an denen die erste Tätigkeitstätte aufgesucht wurde:', step=1,
                                  min_value=0)
    tage = Decimal(str(anzahl_tage))

    entfernung = st.number_input('kürzeste Straßenverbindung zur ersten Tätigkeitsstätte in km:', min_value=0.0)
    strecke = Decimal(str(math.floor(entfernung)))

    optionen_pkw = ['für die ganze Strecke', 'für einen Teil der Strecke', 'nein']
    abfrage_pkw = st.selectbox('wurde ein eigener Pkw verwendet?', options=optionen_pkw)

    entfernung_pkw = Decimal('0')
    if abfrage_pkw == 'für einen Teil der Strecke':
        entfernung_pkw = st.number_input('Strecke, die mit dem Pkw zurückgelegt wurde', min_value=0.0)

    aufwendungen_oeffentliche = st.number_input('Aufwendungen für öffentliche Verkehrsmittel:', min_value=0.0)
    aufwendungen_ovm = Decimal(str(aufwendungen_oeffentliche))

    # Berechnungen

    if abfrage_pkw == 'für die ganze Strecke' or abfrage_pkw == 'nein':

        entfernungspauschale = berechne_entfernungspauschale(anzahl_tage, strecke, abfrage_pkw)

    elif abfrage_pkw == 'für einen Teil der Strecke':

        entfernungspauschale = berechne_entfernungspauschale_gemischt(anzahl_tage, strecke, entfernung_pkw)

    if entfernungspauschale < aufwendungen_ovm:
        wk_ovm = aufwendungen_ovm - entfernungspauschale

    # Button

    if st.button('berechnen'):

        st.success(f'Entfernungspauschale: {entfernungspauschale} €')

        if aufwendungen_ovm != 0:

            if entfernungspauschale < aufwendungen_ovm:

                st.success(
                    f'Die Aufwendungen für öffentliche Verkehrsmittel übersteigen die anzusetzende Entfernungspauschale '
                    f'in Höhe von {wk_ovm} €, insoweit können diese als Werbungskosten angesetzt werden. '
                    f'§ 9 (2) S.2 EStG')

            else:
                st.warning('''Die Aufwendungen für öffentliche Verkehrsmittel übersteigen nicht die anzusetztende Entfernungspauschale.
                           Ein Abzug dieser Aufwendungen als Werbungskosten ist daher ausgeschlossen, weil mit der Entfernungspauschale 
                           sämtliche Aufwendungen abgegolten werden, welche durch die Wege zwischen der Wohnung und der 
                           ersten Tätigkeitsstätte veranlasst sind.  
                           § 9 (2) S.1 EStG.
                           ''')

    if st.button('zurück'):
        switch_page('menu')
