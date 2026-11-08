# Service-Inventar: DocFlow-Nachlauf

Docs Build 38937984526 scheiterte am veralteten Service-Inventar. Alle direkten Python-Servicepfade und ihre Docstrings wurden aus kanonischem Git HEAD gelesen und durch den bestehenden Generator gerendert. Syntaxfehler werden wie im Originalgenerator als fehlende Beschreibung behandelt. Physische fremde Inventarfassung unveraendert; kein Gate abgeschwaecht. GitHub-Nachlauf nach Push erforderlich.

## Lokaler Betrieb

Der zuvor abgenommene Frontendstand auf Port 3000 wurde unter dem vorhandenen lokalen Image-Tag gesichert. Ausschliesslich frontend-web mit --no-deps --no-build daraus neu erstellt; keine Datenbank, Rolle oder anderer Container veraendert. Das verhindert die Rueckkehr zum alten Test-Login beim lokalen Neuerstellen. Es ist ein lokales Laufzeitimage, kein Nachweis eines vollstaendigen Dockerfile-Builds. Eine bestehende synthetische Testsitzung war danach weiterhin vorhanden und wurde regulaer abgemeldet.
