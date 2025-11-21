# Inventory-Service Betriebsprofile

Dieser Leitfaden beschreibt, wie der Inventory-Microservice zwischen Test- und Realbetrieb umgeschaltet werden kann und wie sich die Konfiguration feingranular steuern lässt.

## Globale Steuerung
| Variable | Werte | Standard | Beschreibung |
| --- | --- | --- | --- |
| `INVENTORY_GLOBAL_OPERATION_MODE` | `test` \| `real` | `test` | Legt fest, ob der Dienst im Testmodus (sichere Defaults, deaktivierte Integrationen) oder Realmodus (produktive Integrationen aktiv) startet. |

Der Modus kann zur Laufzeit über `settings.get_module_mode("<modul>")` bzw. `settings.is_real_mode("<modul>")` überprüft werden.

## Modulweise Overrides
| Variable | Format | Beispiel | Beschreibung |
| --- | --- | --- | --- |
| `INVENTORY_MODULE_MODE_OVERRIDES` | Komma-separierte Liste `modul=modus` | `event_bus=real,database=test` | Überschreibt den globalen Modus für einzelne Funktionsbereiche. Das Modul wird kleingeschrieben ausgewertet. |

Aktuell werden folgende Module ausdrücklich ausgewertet:
- `event_bus`: Schaltet das NATS-Publishing ein/aus. Standardwert richtet sich nach dem globalen Modus.

Weitere Module (z. B. `database`, `scheduler`, `workflow`) können sukzessive ergänzt werden. Nicht konfigurierte Schlüssel fallen automatisch auf den globalen Modus zurück.

## Beispiel-Setups
### Lokaler Testbetrieb (ohne externe Abhängigkeiten)
```env
INVENTORY_GLOBAL_OPERATION_MODE=test
INVENTORY_EVENT_BUS_ENABLED=false
INVENTORY_DATABASE_URL=sqlite+aiosqlite:///./inventory-test.db
```

### Produktivbetrieb
```env
INVENTORY_GLOBAL_OPERATION_MODE=real
INVENTORY_EVENT_BUS_URL=nats://nats:4222
INVENTORY_EVENT_BUS_SUBJECT_PREFIX=inventory
INVENTORY_DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<host>:5432/valeo_inventory
```

### Selektive Aktivierung des EventBus bei ansonsten testnaher Umgebung
```env
INVENTORY_GLOBAL_OPERATION_MODE=test
INVENTORY_MODULE_MODE_OVERRIDES=event_bus=real
```

## Implementierungsdetails
- Die Logik ist in `services/inventory/app/config/settings.py` implementiert.
- `EVENT_BUS_ENABLED` wird automatisch vom gewählten Modus abgeleitet, kann jedoch wie bisher manuell gesetzt werden.
- Neue Module können auf dieselbe Weise eingebunden werden, indem die Geschäftslogik `settings.is_real_mode("<modul>")` auswertet.

