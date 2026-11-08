# Lokale Anmeldung auf Port 3000

## Ursache

Der vorhandene Docker-Webcontainer wurde am 17.09.2026 erstellt und lieferte noch einen alten Build mit statischer Test-Admin-Anzeige aus. Der aktuelle Quellstand verwendet dagegen bereits den zentralen OIDC-Anmeldedienst und geschuetzte private Routen. Keine neue Authentifizierungsumgehung eingefuehrt.

## Reparatur und Abnahme

Kanonischen Frontendexport mit vorhandenem Vite-Werkzeug im Produktionsmodus gebaut; generierte Assets gezielt in den vorhandenen Webcontainer kopiert. Proxykonfiguration, Datenbanken, Rollen und andere Container unveraendert. 29 bestehende Auth-/Sicherheitsvertraege bestanden. Browser nach Neuladen von localhost:3000/ auf /login; auch direkter Aufruf von /admin/screen-studio fuehrt dorthin. Kein automatischer Test-Admin mehr. Anonyme Anfragen auf /api/v1/docflow/ und /api/v1/identity/me ergeben jeweils HTTP 401. Screenshot lokal unter artifacts/auth-localhost-acceptance/login-3000.png.

## Betriebsgrenze

Die lokale Assetaktualisierung ersetzt keinen spaeteren reproduzierbaren Image-Neubau. Bei erneutem Erstellen aus dem alten Image kaeme der Altstand zurueck; den Frontenddienst daher aus aktuellem freigegebenem Quellstand neu bauen. Ein dauerhaftes Verlangen nach einem Kennwort bei jedem Aufruf ist keine Voraussetzung: eine gueltige Sitzung darf weiterverwendet werden. Die positive erneute Kennworteingabe wurde in diesem Slice nicht behauptet.
