-- ============================================================================
-- SEED DATA: Kundenstamm - Testdaten
-- Generated: 2025-10-27 19:54:50
-- Total Records: ~50
-- ============================================================================


-- ============================================================================
-- SEED DATA: Kunden
-- ============================================================================

INSERT INTO kunden (
    kunden_nr, name1, name2, strasse, plz, ort, land,
    tel, fax, email, homepage,
    zahlungsbedingungen_tage, skonto, waehrung,
    selbstabholer_rabatt, gueltig_ab, gueltig_bis,
    sprachschluessel, webshop_kunde, erstellt_am
) VALUES (
    'K00001',
    'Bauernhof Fischer KG',
    'Landwirtschaftsbetrieb',
    'Bahnhofstraße 66',
    '01069',
    'Dresden',
    'Deutschland',
    '+49 441 127938',
    '+49 441 127455',
    'info@bauernhoffischer.de',
    'www.bauernhoffischer.de',
    15,
    1.22,
    'EUR',
    2.47,
    CURRENT_DATE - INTERVAL '463 days',
    CURRENT_DATE + INTERVAL '452 days',
    'DE',
    false,
    CURRENT_TIMESTAMP
);

INSERT INTO kunden (
    kunden_nr, name1, name2, strasse, plz, ort, land,
    tel, fax, email, homepage,
    zahlungsbedingungen_tage, skonto, waehrung,
    selbstabholer_rabatt, gueltig_ab, gueltig_bis,
    sprachschluessel, webshop_kunde, erstellt_am
) VALUES (
    'K00002',
    'Bauernhof Fischer KG',
    'Landwirtschaftsbetrieb',
    'Gartenstraße 15',
    '26127',
    'Oldenburg',
    'Deutschland',
    '+49 441 125271',
    '+49 441 124516',
    'info@bauernhoffischer.de',
    'www.bauernhoffischer.de',
    18,
    0.22,
    'EUR',
    1.98,
    CURRENT_DATE - INTERVAL '8 days',
    CURRENT_DATE + INTERVAL '1025 days',
    'DE',
    true,
    CURRENT_TIMESTAMP
);

INSERT INTO kunden (
    kunden_nr, name1, name2, strasse, plz, ort, land,
    tel, fax, email, homepage,
    zahlungsbedingungen_tage, skonto, waehrung,
    selbstabholer_rabatt, gueltig_ab, gueltig_bis,
    sprachschluessel, webshop_kunde, erstellt_am
) VALUES (
    'K00003',
    'Agrar-Betrieb Hansen GmbH',
    'Landwirtschaftsbetrieb',
    'Hauptstraße 68',
    '30159',
    'Hannover',
    'Deutschland',
    '+49 441 128393',
    '+49 441 121113',
    'info@rar-betriebhansen.de',
    'www.rar-betriebhansen.de',
    23,
    1.03,
    'EUR',
    2.77,
    CURRENT_DATE - INTERVAL '538 days',
    CURRENT_DATE + INTERVAL '1051 days',
    'DE',
    false,
    CURRENT_TIMESTAMP
);

INSERT INTO kunden (
    kunden_nr, name1, name2, strasse, plz, ort, land,
    tel, fax, email, homepage,
    zahlungsbedingungen_tage, skonto, waehrung,
    selbstabholer_rabatt, gueltig_ab, gueltig_bis,
    sprachschluessel, webshop_kunde, erstellt_am
) VALUES (
    'K00004',
    'Landwirtschaft Meier AG',
    'Landwirtschaftsbetrieb',
    'Hauptstraße 77',
    '26127',
    'Oldenburg',
    'Deutschland',
    '+49 441 121795',
    '+49 441 125841',
    'info@landwirtschaftmeier.de',
    'www.landwirtschaftmeier.de',
    21,
    2.16,
    'EUR',
    3.91,
    CURRENT_DATE - INTERVAL '307 days',
    CURRENT_DATE + INTERVAL '1042 days',
    'DE',
    false,
    CURRENT_TIMESTAMP
);

INSERT INTO kunden (
    kunden_nr, name1, name2, strasse, plz, ort, land,
    tel, fax, email, homepage,
    zahlungsbedingungen_tage, skonto, waehrung,
    selbstabholer_rabatt, gueltig_ab, gueltig_bis,
    sprachschluessel, webshop_kunde, erstellt_am
) VALUES (
    'K00005',
    'Agrar-Genossenschaft Ost e.V.',
    'Landwirtschaftsbetrieb',
    'Kirchplatz 37',
    '48143',
    'Münster',
    'Deutschland',
    '+49 441 125817',
    '+49 441 126772',
    'info@rar-genossenschaftostev.de',
    'www.rar-genossenschaftostev.de',
    19,
    2.51,
    'EUR',
    2.11,
    CURRENT_DATE - INTERVAL '325 days',
    CURRENT_DATE + INTERVAL '800 days',
    'DE',
    false,
    CURRENT_TIMESTAMP
);

INSERT INTO kunden (
    kunden_nr, name1, name2, strasse, plz, ort, land,
    tel, fax, email, homepage,
    zahlungsbedingungen_tage, skonto, waehrung,
    selbstabholer_rabatt, gueltig_ab, gueltig_bis,
    sprachschluessel, webshop_kunde, erstellt_am
) VALUES (
    'K00006',
    'Landhandel Weber e.K.',
    'Landwirtschaftsbetrieb',
    'Kirchplatz 19',
    '20095',
    'Hamburg',
    'Deutschland',
    '+49 441 125553',
    '+49 441 126787',
    'info@landhandelweberek.de',
    'www.landhandelweberek.de',
    17,
    2.3,
    'EUR',
    3.1,
    CURRENT_DATE - INTERVAL '445 days',
    CURRENT_DATE + INTERVAL '382 days',
    'DE',
    true,
    CURRENT_TIMESTAMP
);

INSERT INTO kunden (
    kunden_nr, name1, name2, strasse, plz, ort, land,
    tel, fax, email, homepage,
    zahlungsbedingungen_tage, skonto, waehrung,
    selbstabholer_rabatt, gueltig_ab, gueltig_bis,
    sprachschluessel, webshop_kunde, erstellt_am
) VALUES (
    'K00007',
    'Bauernhof Müller GmbH',
    'Landwirtschaftsbetrieb',
    'Stallgasse 7',
    '26127',
    'Oldenburg',
    'Deutschland',
    '+49 441 129801',
    '+49 441 129571',
    'info@bauernhofmüller.de',
    'www.bauernhofmüller.de',
    10,
    0.11,
    'EUR',
    1.87,
    CURRENT_DATE - INTERVAL '308 days',
    CURRENT_DATE + INTERVAL '930 days',
    'DE',
    false,
    CURRENT_TIMESTAMP
);

INSERT INTO kunden (
    kunden_nr, name1, name2, strasse, plz, ort, land,
    tel, fax, email, homepage,
    zahlungsbedingungen_tage, skonto, waehrung,
    selbstabholer_rabatt, gueltig_ab, gueltig_bis,
    sprachschluessel, webshop_kunde, erstellt_am
) VALUES (
    'K00008',
    'Agrar-Betrieb Hansen GmbH',
    'Landwirtschaftsbetrieb',
    'Mühlenweg 62',
    '48143',
    'Münster',
    'Deutschland',
    '+49 441 128760',
    '+49 441 124397',
    'info@rar-betriebhansen.de',
    'www.rar-betriebhansen.de',
    10,
    1.34,
    'EUR',
    3.2,
    CURRENT_DATE - INTERVAL '203 days',
    CURRENT_DATE + INTERVAL '866 days',
    'DE',
    false,
    CURRENT_TIMESTAMP
);

INSERT INTO kunden (
    kunden_nr, name1, name2, strasse, plz, ort, land,
    tel, fax, email, homepage,
    zahlungsbedingungen_tage, skonto, waehrung,
    selbstabholer_rabatt, gueltig_ab, gueltig_bis,
    sprachschluessel, webshop_kunde, erstellt_am
) VALUES (
    'K00009',
    'Landhandel Weber e.K.',
    'Landwirtschaftsbetrieb',
    'Bahnhofstraße 23',
    '01069',
    'Dresden',
    'Deutschland',
    '+49 441 126084',
    '+49 441 127072',
    'info@landhandelweberek.de',
    'www.landhandelweberek.de',
    27,
    2.61,
    'EUR',
    2.55,
    CURRENT_DATE - INTERVAL '414 days',
    CURRENT_DATE + INTERVAL '1093 days',
    'DE',
    false,
    CURRENT_TIMESTAMP
);

INSERT INTO kunden (
    kunden_nr, name1, name2, strasse, plz, ort, land,
    tel, fax, email, homepage,
    zahlungsbedingungen_tage, skonto, waehrung,
    selbstabholer_rabatt, gueltig_ab, gueltig_bis,
    sprachschluessel, webshop_kunde, erstellt_am
) VALUES (
    'K00010',
    'Landwirtschaft Becker AG',
    'Landwirtschaftsbetrieb',
    'Dorfstraße 12',
    '26127',
    'Oldenburg',
    'Deutschland',
    '+49 441 121945',
    '+49 441 126915',
    'info@landwirtschaftbecker.de',
    'www.landwirtschaftbecker.de',
    18,
    2.52,
    'EUR',
    2.18,
    CURRENT_DATE - INTERVAL '391 days',
    CURRENT_DATE + INTERVAL '509 days',
    'DE',
    false,
    CURRENT_TIMESTAMP
);


-- ============================================================================
-- SEED DATA: Kundenprofil
-- ============================================================================

INSERT INTO kunden_profil (
    kunden_nr, firmenname, gruendung, jahresumsatz, branche,
    mitarbeiteranzahl, erstellt_am
) VALUES (
    'K00001',
    'Biohof Schmidt KG',
    '1997-02-05',
    3912338,
    'Ackerbau',
    22,
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_profil (
    kunden_nr, firmenname, gruendung, jahresumsatz, branche,
    mitarbeiteranzahl, erstellt_am
) VALUES (
    'K00002',
    'Agrar-Genossenschaft Süd e.V.',
    '2014-10-13',
    3855888,
    'Gemüseanbau',
    13,
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_profil (
    kunden_nr, firmenname, gruendung, jahresumsatz, branche,
    mitarbeiteranzahl, erstellt_am
) VALUES (
    'K00003',
    'Agrar-Genossenschaft Ost e.V.',
    '2010-10-13',
    848100,
    'Gemüseanbau',
    37,
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_profil (
    kunden_nr, firmenname, gruendung, jahresumsatz, branche,
    mitarbeiteranzahl, erstellt_am
) VALUES (
    'K00004',
    'Agrarhandel Nord GmbH',
    '2021-11-20',
    889686,
    'Landwirtschaft',
    41,
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_profil (
    kunden_nr, firmenname, gruendung, jahresumsatz, branche,
    mitarbeiteranzahl, erstellt_am
) VALUES (
    'K00005',
    'Agrarhandel Nord GmbH',
    '2018-05-03',
    4346875,
    'Gemüseanbau',
    32,
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_profil (
    kunden_nr, firmenname, gruendung, jahresumsatz, branche,
    mitarbeiteranzahl, erstellt_am
) VALUES (
    'K00006',
    'Agrarhandel Nord GmbH',
    '2018-08-18',
    983137,
    'Viehzucht',
    49,
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_profil (
    kunden_nr, firmenname, gruendung, jahresumsatz, branche,
    mitarbeiteranzahl, erstellt_am
) VALUES (
    'K00007',
    'Agrar-Betrieb Hansen GmbH',
    '2003-01-12',
    2913942,
    'Landwirtschaft',
    26,
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_profil (
    kunden_nr, firmenname, gruendung, jahresumsatz, branche,
    mitarbeiteranzahl, erstellt_am
) VALUES (
    'K00008',
    'Bauernhof Müller GmbH',
    '2008-08-27',
    4489982,
    'Viehzucht',
    46,
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_profil (
    kunden_nr, firmenname, gruendung, jahresumsatz, branche,
    mitarbeiteranzahl, erstellt_am
) VALUES (
    'K00009',
    'Agrar-Genossenschaft Süd e.V.',
    '2004-06-13',
    1249187,
    'Agrarhandel',
    39,
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_profil (
    kunden_nr, firmenname, gruendung, jahresumsatz, branche,
    mitarbeiteranzahl, erstellt_am
) VALUES (
    'K00010',
    'Agrarhandel Nord GmbH',
    '2001-03-20',
    3393960,
    'Gemüseanbau',
    49,
    CURRENT_TIMESTAMP
);


-- ============================================================================
-- SEED DATA: Kunden-Ansprechpartner
-- ============================================================================

INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    'K00001',
    0,
    'Andreas',
    'Schmidt',
    'Lagerleiter',
    '+49 441 128893',
    'andreas.schmidt@k00001.de',
    'Herr',
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    'K00001',
    1,
    'Andreas',
    'Weber',
    'Einkaufsleiter',
    '+49 441 127838',
    'andreas.weber@k00001.de',
    'Herr',
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    'K00001',
    2,
    'Wolfgang',
    'Becker',
    'Geschäftsführer',
    '+49 441 128132',
    'wolfgang.becker@k00001.de',
    'Herr',
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    'K00002',
    0,
    'Thomas',
    'Schmidt',
    'Landwirt',
    '+49 441 125638',
    'thomas.schmidt@k00002.de',
    'Herr',
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    'K00003',
    0,
    'Christian',
    'Schmidt',
    'Disponent',
    '+49 441 124277',
    'christian.schmidt@k00003.de',
    'Herr',
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    'K00003',
    1,
    'Christian',
    'Schmidt',
    'Disponent',
    '+49 441 122761',
    'christian.schmidt@k00003.de',
    'Herr',
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    'K00004',
    0,
    'Wolfgang',
    'Müller',
    'Lagerleiter',
    '+49 441 122754',
    'wolfgang.müller@k00004.de',
    'Herr',
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    'K00005',
    0,
    'Andreas',
    'Fischer',
    'Landwirt',
    '+49 441 126935',
    'andreas.fischer@k00005.de',
    'Herr',
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    'K00005',
    1,
    'Andreas',
    'Schmidt',
    'Einkaufsleiter',
    '+49 441 126240',
    'andreas.schmidt@k00005.de',
    'Herr',
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    'K00006',
    0,
    'Michael',
    'Schmidt',
    'Meister',
    '+49 441 121370',
    'michael.schmidt@k00006.de',
    'Herr',
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    'K00006',
    1,
    'Thomas',
    'Meier',
    'Disponent',
    '+49 441 128249',
    'thomas.meier@k00006.de',
    'Herr',
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    'K00006',
    2,
    'Peter',
    'Wagner',
    'Geschäftsführer',
    '+49 441 125077',
    'peter.wagner@k00006.de',
    'Herr',
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    'K00007',
    0,
    'Michael',
    'Fischer',
    'Disponent',
    '+49 441 127545',
    'michael.fischer@k00007.de',
    'Herr',
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    'K00007',
    1,
    'Wolfgang',
    'Becker',
    'Leiter Produktion',
    '+49 441 122694',
    'wolfgang.becker@k00007.de',
    'Herr',
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    'K00007',
    2,
    'Andreas',
    'Meier',
    'Meister',
    '+49 441 126638',
    'andreas.meier@k00007.de',
    'Herr',
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    'K00008',
    0,
    'Andreas',
    'Fischer',
    'Landwirt',
    '+49 441 126433',
    'andreas.fischer@k00008.de',
    'Herr',
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    'K00008',
    1,
    'Andreas',
    'Hansen',
    'Leiter Produktion',
    '+49 441 127043',
    'andreas.hansen@k00008.de',
    'Herr',
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    'K00008',
    2,
    'Thomas',
    'Hansen',
    'Landwirt',
    '+49 441 125600',
    'thomas.hansen@k00008.de',
    'Herr',
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    'K00009',
    0,
    'Andreas',
    'Müller',
    'Meister',
    '+49 441 129501',
    'andreas.müller@k00009.de',
    'Herr',
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    'K00009',
    1,
    'Wolfgang',
    'Müller',
    'Geschäftsführer',
    '+49 441 128058',
    'wolfgang.müller@k00009.de',
    'Herr',
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    'K00009',
    2,
    'Michael',
    'Müller',
    'Geschäftsführer',
    '+49 441 127608',
    'michael.müller@k00009.de',
    'Herr',
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    'K00010',
    0,
    'Hans',
    'Schmidt',
    'Landwirt',
    '+49 441 123414',
    'hans.schmidt@k00010.de',
    'Herr',
    CURRENT_TIMESTAMP
);

INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    'K00010',
    1,
    'Michael',
    'Hansen',
    'Einkaufsleiter',
    '+49 441 122800',
    'michael.hansen@k00010.de',
    'Herr',
    CURRENT_TIMESTAMP
);

