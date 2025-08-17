import streamlit as st
from decimal import Decimal, ROUND_UP, ROUND_DOWN
from dataclasses import dataclass
from typing import Optional

hb_knapp_rv = {
    '2023' : 26528,
    '2024' : 27566,
    '2025' : 29344
}

def show_sonderausgaben(switch_page):

    st.title('Sonderausgaben - Vorsorgeaufwendungen')

    @dataclass(kw_only=True)
    class PersonA:
        personenkreis_a: str
        ek_zu_personenkreis_a: Optional[Decimal] = None
        grv_a: Decimal
        ruerup_a: Decimal
        gkv_a: Decimal
        pkv_basis_a: Decimal
        pv_a: Decimal
        pkv_plus_a: Decimal
        ppv_plus_a: Decimal
        alv_a: Decimal
        summe_weitere_versicherungen: Decimal
        gesamte_erstattungen_nr3_a: Decimal
        gesamte_erstattungen_nr3a_a: Decimal
        summe_beitraege_ex_a: Decimal

    @dataclass(kw_only=True)
    class PersonB:
        personenkreis_b: Optional[str] = None
        ek_zu_personenkreis_b: Optional[Decimal] = None
        grv_b: Decimal
        ruerup_b: Decimal
        gkv_b: Decimal
        pkv_basis_b: Decimal
        pv_b: Decimal
        pkv_plus_b: Decimal
        ppv_plus_b:Decimal
        alv_b:Decimal
        summe_weitere_versicherungen_b: Decimal
        gesamte_erstattungen_nr3_b: Decimal
        gesamte_erstattungen_nr3a_b: Decimal
        summe_beitraege_ex_b: Decimal



    def bestimme_vsa(person_a: PersonA,
                     person_b: Optional[PersonB] = None,
                     hb_vsa: Decimal = Decimal('0')):

        grv_a = person_a.grv_a
        ruerup_a = person_a.ruerup_a

        grv_b = person_b.grv_b
        ruerup_b = person_b.ruerup_b


        # Multiplikation mit 2, falls Arbeitnehmer, wegen ArbG-Anteil
        if person_a.personenkreis_a == 'Arbeitnehmer':
            grv_a *= Decimal('2')
        if person_b.personenkreis_b == 'Arbeitnehmer':
            grv_b *= Decimal('2')


        vorsorgebeitraege = grv_a + grv_b + ruerup_a + ruerup_b


        # Höchstbetrag abzüglich 18,6 % der Einnahmen, falls Beamter
        hb_abzug_a = person_a.ek_zu_personenkreis_a * Decimal('0.186')
        hb_abzug_b = person_b.ek_zu_personenkreis_b * Decimal('0.186')
        hb_abzug_a = hb_abzug_a.quantize(Decimal('1'), rounding=ROUND_DOWN)
        hb_abzug_b = hb_abzug_b.quantize(Decimal('1'), rounding=ROUND_DOWN)
        if person_a.personenkreis_a == 'Beamter':
            hb_vsa -= hb_abzug_a
        if person_b.personenkreis_b == 'Beamter':
            hb_vsa -= hb_abzug_b

        # niedrigeren Betrag ansetzen
        anzusetzender_betrag_vsa = min(hb_vsa, vorsorgebeitraege)


        # abzgl. stfr. ArbG-Anteil, falls ArbN
        if person_a.personenkreis_a == 'Arbeitnehmer':
            anzusetzender_betrag_vsa -= person_a.grv_a.quantize(Decimal('1'), rounding=ROUND_DOWN)
        if person_b.personenkreis_b == 'Arbeitnehmer':
            anzusetzender_betrag_vsa -= person_b.grv_b.quantize(Decimal('1'), rounding=ROUND_DOWN)


        return anzusetzender_betrag_vsa


    def bestimme_weitere_vsa(
        person_a: PersonA,
        person_b: PersonB,
        veranlagungsart: str,
        summe_beitraege_kinder: Decimal,
    ):

        gkv_a = person_a.gkv_a
        gkv_b = person_b.gkv_b

        hb_b = Decimal('0')
        hb_a = Decimal('2800')

        if veranlagungsart == 'Zusammenveranlagung':
            hb_b = Decimal('2800')

        # verminderter HB für bestimmte Personengruppen
        if person_a.personenkreis_a in ('Beamter', 'Arbeitnehmer', 'Rentner'):
            hb_a = Decimal('1900')
        if person_b.personenkreis_b in ('Beamter', 'Arbeitnehmer', 'Rentner'):
            hb_b = Decimal('1900')

        hb_gesamt = hb_a + hb_b

        gkv_rest_a = Decimal('0')
        gkv_rest_b = Decimal('0')
        if person_a.personenkreis_a == 'Arbeitnehmer':
            gkv_rest_a = person_a.gkv_a * Decimal('0.04')
            gkv_rest_a = gkv_rest_a.quantize(Decimal('1'), rounding=ROUND_DOWN)
            gkv_a *= Decimal('0.96')
            gkv_a = gkv_a.quantize(Decimal('1'), rounding=ROUND_UP)
            st.warning('Aus den Beiträgen zur gesetzlichen Krankenversicherung ergibt sich ein Anspruch auf Krankengeld. '
                       'Die Beiträge werden deshalb pauschal um 4% gekürzt. Der übrige Betrag wird bei den weiteren '
                       'sonstigen Vorsorgeaufwendungen i.S.v. § 10 (1) Nr.3a EStG berücksichtigt.\n  '
                       '§ 10 (1) Nr.3 Bst.a S.4 EStG')
        if person_b.personenkreis_b == 'Arbeitnehmer':
            gkv_rest_b = person_b.gkv_b * Decimal('0.04')
            gkv_rest_b = gkv_rest_b.quantize(Decimal('1'), rounding=ROUND_DOWN)
            gkv_b *= Decimal('0.96')
            gkv_b = gkv_b.quantize(Decimal('1'), rounding=ROUND_UP)
            st.warning('Aus den Beiträgen zur gesetzlichen Krankenversicherung ergibt sich ein Anspruch auf Krankengeld. '
                       'Die Beiträge werden deshalb pauschal um 4% gekürzt. Der übrige Betrag wird bei den weiteren '
                       'sonstigen Vorsorgeaufwendungen i.S.v. § 10 (1) Nr.3a EStG berücksichtigt.\n  '
                       '§ 10 (1) Nr.3 Bst.a S.4 EStG')

        sonstige_vsa = (
            gkv_a + person_a.pkv_basis_a + person_a.pv_a
            - person_a.gesamte_erstattungen_nr3_a
            + gkv_b + person_b.pkv_basis_b + person_b.pv_b
            - person_b.gesamte_erstattungen_nr3_b
            + summe_beitraege_kinder
        )

        weitere_sonstige_vsa = (
            person_a.pkv_plus_a + person_a.ppv_plus_a + person_a.alv_a + person_a.summe_weitere_versicherungen
            + gkv_rest_a
            - person_a.gesamte_erstattungen_nr3a_a
            + person_b.pkv_plus_b + person_b.ppv_plus_b + person_b.alv_b + person_b.summe_weitere_versicherungen_b
            + gkv_rest_b
            - person_b.gesamte_erstattungen_nr3a_b
        )

        abziehbare_weitere_vsa = sonstige_vsa + weitere_sonstige_vsa

        if sonstige_vsa > hb_gesamt:
            abziehbare_weitere_vsa -= weitere_sonstige_vsa
            st.warning(f'Die sonstigen Vorsorgeaufwendungen (Nr.3) übersteigen den Höchstbetrag i.H.v. '
                       f'{hb_gesamt} €, die weiteren sonstigen Vorsorgeaufwendungen (Nr.3a) können deswegen nicht abgezogen werden.')
        else:
            if abziehbare_weitere_vsa > hb_gesamt:
                st.warning(
                    f'Die Vorsorgeaufwendungen i.S.d. Nr.3 und Nr.3a übersteigen mit {abziehbare_weitere_vsa} € den Höchstbetrag'
                    f'i.H.v. {hb_gesamt} €, sie werden deswegen auf den Höchstbetrag begrenzt.')
                abziehbare_weitere_vsa = hb_gesamt


        return abziehbare_weitere_vsa




    # EINGABEN

    # allgemein
    st.write('Informationen zur Veranlagung')

    optionen_veranlagungsart = ['Einzelveranlagung', 'Zusammenveranlagung']
    veranlagungsart = st.selectbox('Veranlagungsart', optionen_veranlagungsart)

    optionen_vaz = ['2023', '2024', '2025']
    vaz = st.selectbox('Veranlagungszeitraum', optionen_vaz)

    optionen_personenkreis = ['Arbeitnehmer', 'Selbständiger', 'Beamter', 'Rentner', 'Student']
    eingabe_personenkreis_a = st.selectbox('Personenkreis', optionen_personenkreis)
    if eingabe_personenkreis_a == 'Beamter':
        eingabe_ek_zu_personenkreis_a = Decimal(str(st.number_input('Höhe der Einnahmen, welche die Zugehörigkeit zu diesem Personenkreis begründen: ')))
    else:
        eingabe_ek_zu_personenkreis_a = Decimal('0')

    if veranlagungsart == 'Zusammenveranlagung':
        eingabe_personenkreis_b = st.selectbox('Personenkreis Ehegatte:', optionen_personenkreis, key='pk_b')
        if eingabe_personenkreis_b == 'Beamter':
            eingabe_ek_zu_personenkreis_b = Decimal(str(st.number_input('Höhe der Einnahmen, welche die Zugehörigkeit zu diesem Personenkreis begründen: ', key='ek_zu_pk_b')))
        else:
            eingabe_ek_zu_personenkreis_b = Decimal('0')
    else:
        eingabe_personenkreis_b = None
        eingabe_ek_zu_personenkreis_b = Decimal('0')


    # zu Vorsorgeaufwendungen

    st.write('-')
    st.write('-')
    st.write('Altersvorsorgeaufwendungen i.S.d. § 10 (1) Nr.2 EStG')

    eingabe_grv_a = Decimal(str(st.number_input('gesetzliche Altersvorsorge (bei gRV nur Arbeitnehmeranteil): ')))
    eingabe_grv_a = eingabe_grv_a.quantize(Decimal('1'), rounding=ROUND_UP)

    eingabe_ruerup_a = Decimal(str(st.number_input('Rürup-Versicherung: ')))
    eingabe_ruerup_a = eingabe_ruerup_a.quantize(Decimal('1'), rounding=ROUND_UP)


    # zu weiteren Vorsorgeaufwendungen

    st.write('-')
    st.write('sonstige Vorsorgeaufwendungen i.S.d. § 10 (1) Nr.3 EStG')

    eingabe_gkv_a = Decimal(str(st.number_input('gesetzlichen Krankenversicherung')))
    eingabe_gkv_a = eingabe_gkv_a.quantize(Decimal('1'), rounding=ROUND_UP)

    eingabe_pkv_basis_a = Decimal(str(st.number_input('private Krankenversicherung, soweit für Basisleistungen:')))
    eingabe_pkv_basis_a = eingabe_pkv_basis_a.quantize(Decimal('1'), rounding=ROUND_UP)

    eingabe_pv_a = Decimal(str(st.number_input('gesetzliche und/oder private Pflegeversicherung, soweit für Basisleistungen')))
    eingabe_pv_a = eingabe_pv_a.quantize(Decimal('1'), rounding=ROUND_UP)


    # zu sonstigen Vorsorgeaufwendungen

    st.write('-')
    st.write('weitere sonstige Vorsorgeaufwendungen i.S.d. § 10 Nr.3a EStG')

    eingabe_pkv_plus_a = Decimal(str(st.number_input('private Krankenversicherung, soweit für Zusatzleistungen:')))
    eingabe_pkv_plus_a = eingabe_pkv_plus_a.quantize(Decimal('1'), rounding=ROUND_UP)

    eingabe_ppv_plus_a = Decimal(str(st.number_input('private Pflegeversicherung, soweit für Zusatzleistungen:')))
    eingabe_ppv_plus_a = eingabe_ppv_plus_a.quantize(Decimal('1'), rounding=ROUND_UP)

    eingabe_alv_a = Decimal(str(st.number_input('Arbeitslosenversicherung:')))
    eingabe_alv_a = eingabe_alv_a.quantize(Decimal('1'), rounding=ROUND_UP)

    optionen_weitere_versicherung = \
                        ['zusätzliche Krankenversicherung',
                        'Berufsunfähigkeitsersicherung',
                        'Erwerbsunfähigkeitsversicherung',
                        'Haftpflichtversicherung',
                        'Unfallversicherung',
                        'Risikolebensversicherung'
                        ]
    auswahl_weitere_versicherungen_a = st.multiselect('weitere Versicherungen: ', optionen_weitere_versicherung)
    beitraege_a = [Decimal('0')]
    eingaben_weitere_versicherungen_a = {}

    for versicherung in auswahl_weitere_versicherungen_a:
        eingabe_betrag_a = st.number_input(f'{versicherung}: ')
        betrag_a = Decimal(str(eingabe_betrag_a))
        betrag_a = betrag_a.quantize(Decimal('1'), rounding=ROUND_UP)
        beitraege_a.append(betrag_a)
        eingaben_weitere_versicherungen_a[versicherung] = eingabe_betrag_a

    summe_beitraege_nr3a_a = Decimal(sum(beitraege_a))


    # Erstattungen

    st.write('-')
    st.write('Erstattungen:')

    optionen_erstattung = ['KV - Basis', 'KV - Zusatz', 'PV - Basis', 'PV - Zusatz', 'sonstige']
    auswahl_erstattungen_a = st.multiselect('Erstattungen: ', optionen_erstattung)
    eingaben_erstattungen_a = {}
    erstattungen_nr3_a = [Decimal('0')]
    erstattungen_nr3a_a = [Decimal('0')]
    for erstattung_a in auswahl_erstattungen_a:
        eingabe_betrag_erstattung_a = st.number_input(f'{erstattung_a}: ')
        betrag_erstattung_a = Decimal(str(eingabe_betrag_erstattung_a))
        betrag_erstattung_a = betrag_erstattung_a.quantize(Decimal('1'), rounding=ROUND_DOWN)
        eingaben_erstattungen_a[erstattung_a] = eingabe_betrag_erstattung_a
        if erstattung_a in ('KV - Basis', 'PV - Basis'):
            erstattungen_nr3_a.append(betrag_erstattung_a)
        else:
            erstattungen_nr3a_a.append(betrag_erstattung_a)
    summe_erstattungen_nr3_a = Decimal(sum(erstattungen_nr3_a))
    summe_erstattungen_nr3a_a = Decimal(sum(erstattungen_nr3a_a))


    # Beiträge Ex-Partner

    summe_beitraege_ex_a = Decimal('0')

    st.write('-')
    if 'beitraege_ex_a_erfassen' not in st.session_state:
        st.session_state.beitraege_ex_a_erfassen = False

    if st.button('Beiträge eines geschiedenen Ehegatten hinzufügen'):
        st.session_state.beitraege_ex_a_erfassen = True

    if st.session_state.beitraege_ex_a_erfassen:
        st.write('sonstige Vorsorgeaufwendungen i.S.d. § 10 (1) Nr.3 EStG')

        eingabe_gkv_ex_a = Decimal(str(st.number_input('gesetzlichen Krankenversicherung', key='gkv_ex_a')))
        eingabe_gkv_ex_a = eingabe_gkv_ex_a.quantize(Decimal('1'), rounding=ROUND_UP)

        eingabe_pkv_basis_ex_a = Decimal(str(st.number_input('private Krankenversicherung, soweit für Basisleistungen:', key='pkv_basis_ex_a')))
        eingabe_pkv_basis_ex_a = eingabe_pkv_basis_ex_a.quantize(Decimal('1'), rounding=ROUND_UP)

        eingabe_pv_ex_a = Decimal(str(st.number_input('gesetzliche und/oder private Pflegeversicherung, soweit für Basisleistungen', key='pv_ex_a')))
        eingabe_pv_ex_a = eingabe_pv_ex_a.quantize(Decimal('1'), rounding=ROUND_UP)

        summe_beitraege_ex_a = eingabe_gkv_ex_a + eingabe_pkv_basis_ex_a + eingabe_pv_ex_a





    if veranlagungsart == 'Zusammenveranlagung':
        st.write('-')
        st.write('-')
        st.write('Ehepartner - Altersvorsorgeaufwendungen i.S.d. § 10 (1) Nr.2 EStG')

        eingabe_grv_b = Decimal(str(st.number_input('gesetzliche Altersvorsorge: ', key='grv_b')))
        eingabe_grv_b = eingabe_grv_b.quantize(Decimal('1'), rounding=ROUND_UP)

        eingabe_ruerup_b = Decimal(str(st.number_input('Rürup-Versicherung: ', key='ruerup_b')))
        eingabe_ruerup_b = eingabe_ruerup_b.quantize(Decimal('1'), rounding=ROUND_UP)


        st.write('-')
        st.write('Ehepartner - sonstige Vorsorgeaufwendungen i.S.d. § 10 (1) Nr.3 EStG')

        eingabe_gkv_b = Decimal(str(st.number_input('gesetzlichen Krankenversicherung', key='gkv_b')))
        eingabe_gkv_b = eingabe_gkv_b.quantize(Decimal('1'),rounding=ROUND_UP)

        eingabe_pkv_basis_b = Decimal(str(st.number_input('private Krankenversicherung, soweit für Basisleistungen:', key='pkv_basis_b')))
        eingabe_pkv_basis_b = eingabe_pkv_basis_b.quantize(Decimal('1'), rounding=ROUND_UP)

        eingabe_pv_b = Decimal(str(st.number_input('gesetzliche und/oder private Pflegeversicherung, soweit für Basisleistungen', key='pv_b')))
        eingabe_pv_b = eingabe_pv_b.quantize(Decimal('1'), rounding=ROUND_UP)


        st.write('-')
        st.write('Ehepartner - weitere sonstige Vorsorgeaufwendungen i.S.d. § 10 Nr.3a EStG')

        eingabe_pkv_plus_b = Decimal(str(st.number_input('private Krankenversicherung, soweit für Zusatzleistungen:', key='pkv_plus_b')))
        eingabe_pkv_plus_b = eingabe_pkv_plus_b.quantize(Decimal('1'), rounding=ROUND_UP)

        eingabe_ppv_plus_b = Decimal(str(st.number_input('private Pflegeversicherung, soweit für Zusatzleistungen:', key='pv_plus_b')))
        eingabe_ppv_plus_b = eingabe_ppv_plus_b.quantize(Decimal('1'), rounding=ROUND_UP)

        eingabe_alv_b = Decimal(str(st.number_input('Arbeitslosenversicherung:', key='alv_b')))
        eingabe_alv_b = eingabe_alv_b.quantize(Decimal('1'), rounding=ROUND_UP)


        auswahl_weitere_versicherungen_b = st.multiselect('weitere Versicherungen: ', optionen_weitere_versicherung, key='auswahl_versicherungen_b')
        beitraege_b = [Decimal('0')]
        eingaben_weitere_versicherungen_b = {}

        a=1
        for versicherung in auswahl_weitere_versicherungen_b:
            eingabe_betrag_b = st.number_input(f'{versicherung}: ', key=f'weitere_versicherung_b{a}')
            betrag_b = Decimal(str(eingabe_betrag_b))
            betrag_b = betrag_b.quantize(Decimal('1'), rounding=ROUND_UP)
            beitraege_b.append(betrag_b)
            eingaben_weitere_versicherungen_b[versicherung] = eingabe_betrag_b
            a+=1

        summe_beitraege_nr3a_b = Decimal(sum(beitraege_b))


        st.write('-')
        st.write('Ehepartner - Erstattungen:')

        auswahl_erstattungen_b = st.multiselect('Erstattungen: ', optionen_erstattung, key='auswahl_erstattungen_b')
        eingaben_erstattungen_b = {}
        erstattungen_nr3_b = [Decimal('0')]
        erstattungen_nr3a_b = [Decimal('0')]
        b=1
        for erstattung_b in auswahl_erstattungen_b:
            eingabe_betrag_erstattung_b = st.number_input(f'{erstattung_b}: ', key=f'eingabe_erstattungen_b{b}')
            betrag_erstattung_b = Decimal(str(eingabe_betrag_erstattung_b))
            betrag_erstattung_b = betrag_erstattung_b.quantize(Decimal('1'), rounding=ROUND_DOWN)
            eingaben_erstattungen_b[erstattung_b] = eingabe_betrag_erstattung_b
            if erstattung_b in ('KV - Basis', 'PV - Basis'):
                erstattungen_nr3_b.append(betrag_erstattung_b)
            else:
                erstattungen_nr3a_b.append(betrag_erstattung_b)
            b+=1
        summe_erstattungen_nr3_b = Decimal(sum(erstattungen_nr3_b))
        summe_erstattungen_nr3a_b = Decimal(sum(erstattungen_nr3a_b))


        summe_beitraege_ex_b = Decimal('0')
        st.write('-')
        if 'beitraege_ex_b_erfassen' not in st.session_state:
            st.session_state.beitraege_ex_b_erfassen = False

        if st.button('Beiträge eines geschiedenen Ehegatten hinzufügen', key='button_beitraege_ex_b'):
            st.session_state.beitraege_ex_b_erfassen = True

        if st.session_state.beitraege_ex_b_erfassen:
            st.write('sonstige Vorsorgeaufwendungen i.S.d. § 10 (1) Nr.3 EStG')

            eingabe_gkv_ex_b = Decimal(str(st.number_input('gesetzlichen Krankenversicherung', key='gkv_ex_b')))
            eingabe_gkv_ex_b = eingabe_gkv_ex_b.quantize(Decimal('1'), rounding=ROUND_UP)

            eingabe_pkv_basis_ex_b = Decimal(str(st.number_input('private Krankenversicherung, soweit für Basisleistungen:',key='pkv_basis_ex_b')))
            eingabe_pkv_basis_ex_b = eingabe_pkv_basis_ex_b.quantize(Decimal('1'), rounding=ROUND_UP)

            eingabe_pv_ex_b = Decimal(str(st.number_input('gesetzliche und/oder private Pflegeversicherung, soweit für Basisleistungen',key='pv_ex_b')))
            eingabe_pv_ex_b = eingabe_pv_ex_b.quantize(Decimal('1'), rounding=ROUND_UP)

            summe_beitraege_ex_b = eingabe_gkv_ex_b + eingabe_pkv_basis_ex_b + eingabe_pv_ex_b


    else:
        eingabe_grv_b = Decimal('0')
        eingabe_ruerup_b = Decimal('0')
        eingabe_gkv_b = Decimal('0')
        eingabe_pkv_basis_b = Decimal('0')
        eingabe_pv_b = Decimal('0')
        eingabe_pkv_plus_b = Decimal('0')
        eingabe_ppv_plus_b = Decimal('0')
        eingabe_alv_b = Decimal('0')
        summe_beitraege_nr3a_b = Decimal('0')
        summe_erstattungen_nr3_b = Decimal('0')
        summe_erstattungen_nr3a_b = Decimal('0')
        summe_beitraege_ex_b = Decimal('0')


    # eigene Beiträge eines Kindes

    st.write('-')
    st.write('-')

    beitraege_kinder = [Decimal('0')]

    if 'kinder_erfassen_aktiv' not in st.session_state:
        st.session_state.kinder_erfassen_aktiv = False

    if 'anzahl_kinder' not in st.session_state:
        st.session_state.anzahl_kinder = 0

    if st.button('eigene Beiträge für Kinder erfasssen'):
        st.session_state.kinder_erfassen_aktiv = True


    if st.session_state.kinder_erfassen_aktiv:

        anzahl_kinder = st.number_input(f'Anzahl kinder:', key=f'anzahl_kinder', min_value=1, step=1)


        st.write(f'Kind 1 - sonstige Vorsorgeaufwendungen i.S.d. § 10 (1) Nr.3 EStG')

        personenkreis_kind1 = st.selectbox('Personenkreis:', optionen_personenkreis, key=f'pk_kind1')

        eingabe_gkv_k = Decimal(str(st.number_input('gesetzlichen Krankenversicherung', key=f'gkv_k1')))
        if personenkreis_kind1 == 'Arbeitnehmer':
            eingabe_gkv_k *= Decimal('0.96')
            st.warning('Beiträge werden wegen Anspruch auf Krankengeld um 4% gekürzt.')
        eingabe_gkv_k = eingabe_gkv_k.quantize(Decimal('1'), rounding=ROUND_UP)

        eingabe_pkv_basis_k = Decimal(str(st.number_input('private Krankenversicherung, soweit für Basisleistungen:',key=f'pkv_basis_k1')))
        eingabe_pkv_basis_k = eingabe_pkv_basis_k.quantize(Decimal('1'), rounding=ROUND_UP)

        eingabe_pv_k = Decimal(str(st.number_input('gesetzliche und/oder private Pflegeversicherung, soweit für Basisleistungen',key=f'pv_k1')))
        eingabe_pv_k = eingabe_pv_k.quantize(Decimal('1'), rounding=ROUND_UP)

        beitraege_kind1 = eingabe_gkv_k + eingabe_pkv_basis_k + eingabe_pv_k
        beitraege_kinder.append(beitraege_kind1)


        for c in range(st.session_state.anzahl_kinder - 1):

            st.write('-')
            st.write(f'Kind {c+2} - sonstige Vorsorgeaufwendungen i.S.d. § 10 (1) Nr.3 EStG')

            personenkreis_kn = st.selectbox('Personenkreis:', optionen_personenkreis, key=f'pk_kind{c+2}')

            eingabe_gkv_kn = Decimal(str(st.number_input('gesetzlichen Krankenversicherung', key=f'gkv_k{c+2}')))
            if personenkreis_kn == 'Arbeitnehmer':
                eingabe_gkv_kn *= Decimal('0.96')
                st.warning('Beiträge werden wegen Anspruch auf Krankengeld um 4% gekürzt.')
            eingabe_gkv_kn = eingabe_gkv_kn.quantize(Decimal('1'), rounding=ROUND_UP)

            eingabe_pkv_basis_kn = Decimal(str(st.number_input('private Krankenversicherung, soweit für Basisleistungen:', key=f'pkv_basis_k{c+2}')))
            eingabe_pkv_basis_kn = eingabe_pkv_basis_kn.quantize(Decimal('1'), rounding=ROUND_UP)

            eingabe_pv_kn = Decimal(str(st.number_input('gesetzliche und/oder private Pflegeversicherung, soweit für Basisleistungen', key=f'pv_k{c+2}')))
            eingabe_pv_kn = eingabe_pv_kn.quantize(Decimal('1'), rounding=ROUND_UP)

            beitraege_kn = eingabe_gkv_kn + eingabe_pkv_basis_kn + eingabe_pv_kn
            beitraege_kinder.append(beitraege_kn)

    summe_beitraege_kinder = Decimal(sum(beitraege_kinder))

    person_a = PersonA(
        personenkreis_a = eingabe_personenkreis_a,
        ek_zu_personenkreis_a = eingabe_ek_zu_personenkreis_a,
        grv_a = eingabe_grv_a,
        ruerup_a = eingabe_ruerup_a,
        gkv_a = eingabe_gkv_a,
        pkv_basis_a = eingabe_pkv_basis_a,
        pv_a = eingabe_pv_a,
        pkv_plus_a=eingabe_pkv_plus_a,
        ppv_plus_a=eingabe_ppv_plus_a,
        alv_a=eingabe_alv_a,
        summe_weitere_versicherungen=summe_beitraege_nr3a_a,
        gesamte_erstattungen_nr3_a=summe_erstattungen_nr3_a,
        gesamte_erstattungen_nr3a_a=summe_erstattungen_nr3a_a,
        summe_beitraege_ex_a=summe_beitraege_ex_a,
    )

    person_b = PersonB(
        personenkreis_b=eingabe_personenkreis_b,
        ek_zu_personenkreis_b=eingabe_ek_zu_personenkreis_b,
        grv_b=eingabe_grv_b,
        ruerup_b=eingabe_ruerup_b,
        gkv_b=eingabe_gkv_b,
        pkv_basis_b=eingabe_pkv_basis_b,
        pv_b=eingabe_pv_b,
        pkv_plus_b=eingabe_pkv_plus_b,
        ppv_plus_b=eingabe_ppv_plus_b,
        alv_b=eingabe_alv_b,
        summe_weitere_versicherungen_b=summe_beitraege_nr3a_b,
        gesamte_erstattungen_nr3_b=summe_erstattungen_nr3_b,
        gesamte_erstattungen_nr3a_b=summe_erstattungen_nr3a_b,
        summe_beitraege_ex_b=summe_beitraege_ex_b,
    )


    # Berechnungen

    hb_vsa = Decimal(hb_knapp_rv[vaz])
    if veranlagungsart == 'Zusammenveranlagung':
        hb_vsa = Decimal(str(hb_knapp_rv[vaz])) * Decimal('2')


    st.write('-')
    st.write('-')
    if st.button('berechnen'):

        anzusetzender_betrag_vsa = bestimme_vsa(
            person_a=person_a,
            person_b=person_b,
            hb_vsa=hb_vsa
        )

        abziehbare_weitere_vsa = bestimme_weitere_vsa(
            person_a=person_a,
            person_b=person_b,
            veranlagungsart=veranlagungsart,
            summe_beitraege_kinder=summe_beitraege_kinder
        )

        st.write(f'Höchstbetrag zur knappschaftlichen Rentenversicherung: {hb_vsa} €')
        st.write(f'abziehbare Sonderausgaben für Altersvorsorge: {anzusetzender_betrag_vsa} €')
        st.write(f'abziehbare Sonderausgaben für weitere VSA: {abziehbare_weitere_vsa} €')


    if st.button('zurück'):
        switch_page('menu')
