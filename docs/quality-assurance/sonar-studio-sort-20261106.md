# Sonar Studio Sort 2026-11-06

Die Sortierung von Berechtigungssignaturen, Overlay-Schlüsseln und Twin-Tastaturreihenfolge verwendet einen expliziten UTF-16-Vergleich. Die Reihenfolge entspricht dem bisherigen parameterlosen JavaScript-`sort()`: insbesondere `10` vor `2`, Großbuchstaben vor `z` und `ä` nach `z`. Weder Locale noch numerische Sortierung verändern Cache-Schlüssel oder Zellreihenfolge.

Regressionen prüfen Eingabereihenfolge, verschachtelte Overlay-Schlüssel und unveränderte Eingabezellen. Gezielte Vitest-Abnahme: drei Testsuiten, 45 Tests bestanden (maximal zwei Worker).
