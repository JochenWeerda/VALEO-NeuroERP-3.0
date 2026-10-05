"""FSX-MENGENMODELL — Zuordnen von Teilmengen zwischen Belegpositionen.

Grundlage: ``docs/design/agrar-mengen-gebinde-modell.md``, Abschnitt 6.

Die drei Regeln, die hier durchgesetzt werden:

1. **Keine Umrechnung ohne belegten Faktor.** Masse und Volumen global,
   Zaehleinheiten nur ueber die Gebindeleiter des Artikels. Fehlt der Faktor,
   wird die Zuordnung abgelehnt — nicht geschaetzt.
2. **Teilbarkeit ist Artikeleigenschaft.** Pflanzenschutz in Originalgebinde und
   gesperrte Packs lassen nur ganze Gebinde zu.
3. **Parallele Zuordnungen duerfen dieselbe Restmenge nicht doppelt vergeben.**
   Die Quellzeile wird gesperrt, bevor gerechnet wird; die Grenze selbst haelt
   eine CHECK-Bedingung in der Datenbank.

Und eine Regel, die ausdruecklich **nicht** aus der Mengenrechnung folgt: Eine
Gutschrift gibt nicht automatisch Liefermenge zur erneuten Berechnung frei. Ob
sie das tut, entscheidet der Fall — Warenrueckgabe ja, Preisnachlass nein.
``release`` verlangt deshalb eine ausdrueckliche Angabe.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Literal

from sqlalchemy.orm import Session

from app.core.agrar_units import ArtikelEinheiten, ist_zulaessige_menge, normalisiere
from app.domains.documents.allocation_models import (
    DocumentAllocation,
    DocumentAllocationSource,
)


class AllocationError(RuntimeError):
    """Fachlicher Grund, warum eine Zuordnung nicht moeglich ist."""


class UnitNotConvertibleError(AllocationError):
    """Die Einheiten lassen sich nicht ineinander umrechnen."""


class NotDivisibleError(AllocationError):
    """Der Artikel laesst keine Teilmengen zu."""


class OverAllocationError(AllocationError):
    """Mehr zugeordnet als vorhanden."""


@dataclass(frozen=True)
class PositionRef:
    document_type: str
    document_id: str
    line_id: str


@dataclass(frozen=True)
class LineToRegister:
    """Eine Belegposition, so weit sie fuer den Mengenstand zaehlt."""

    line_id: str
    quantity: Decimal | None
    unit: str | None
    article_id: str | None = None

    @classmethod
    def from_mapping(cls, zeile: "dict[str, Any]") -> "LineToRegister":
        """Aus einer Positionszeile, wie die Belegendpunkte sie fuehren.

        Die Positionsnummer ist der Schluessel, nicht die Datensatz-ID: Beim
        Speichern werden Positionen geloescht und neu eingefuegt, die ID
        wechselt dabei. Die Nummer bleibt — und mit ihr die Zuordnung.
        """
        return cls(
            line_id=str(zeile.get("pos_nr") or zeile.get("line_id") or zeile.get("id") or ""),
            quantity=zeile.get("menge") if zeile.get("menge") is not None else zeile.get("quantity"),
            unit=zeile.get("einheit") or zeile.get("unit"),
            article_id=zeile.get("artikel_id") or zeile.get("article_id"),
        )


@dataclass(frozen=True)
class AllocationResult:
    allocation_id: str
    #: Zugeordnete Menge in der Einheit der Quellposition.
    quantity: Decimal
    unit: str
    #: Was nach dieser Zuordnung offen bleibt.
    remaining: Decimal
    status: Literal["offen", "teilweise", "vollstaendig"]


def _status(quantity: Decimal, allocated: Decimal) -> Literal["offen", "teilweise", "vollstaendig"]:
    if allocated <= 0:
        return "offen"
    if allocated >= quantity:
        return "vollstaendig"
    return "teilweise"


class DocumentAllocationService:
    """Zuordnungen anlegen, loesen und auswerten."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # -- Quellpositionen -------------------------------------------------------

    def register_source(
        self,
        ref: PositionRef,
        quantity: Decimal,
        unit: str,
        article_id: str | None = None,
    ) -> DocumentAllocationSource:
        """Eine Quellposition bekanntmachen — idempotent.

        Die Menge wird beim erneuten Aufruf **aktualisiert** (eine Lieferposition
        kann sich vor der Fakturierung noch aendern), aber nie unter die bereits
        zugeordnete Menge gesenkt: Das waere eine nachtraegliche Ueberbuchung.
        """
        vorhanden = self._find_source(ref)
        if vorhanden is None:
            quelle = DocumentAllocationSource(
                tenant_id=self.tenant_id,
                document_type=ref.document_type,
                document_id=ref.document_id,
                line_id=ref.line_id,
                article_id=article_id,
                quantity=quantity,
                allocated_quantity=Decimal(0),
                unit=normalisiere(unit),
            )
            self.db.add(quelle)
            self.db.flush()
            return quelle

        if normalisiere(unit) != normalisiere(vorhanden.unit):
            raise AllocationError(
                f"Die Quellposition ist in {vorhanden.unit!r} gefuehrt; eine "
                f"Aenderung auf {unit!r} wuerde bestehende Zuordnungen "
                "unvergleichbar machen."
            )
        if quantity < Decimal(str(vorhanden.allocated_quantity)):
            raise OverAllocationError(
                f"Die Position ist bereits mit {vorhanden.allocated_quantity} "
                f"{vorhanden.unit} zugeordnet; eine Menge von {quantity} waere "
                "rueckwirkend ueberbucht."
            )
        vorhanden.quantity = quantity
        if article_id:
            vorhanden.article_id = article_id
        self.db.flush()
        return vorhanden

    def register_document_lines(
        self,
        document_type: str,
        document_id: str,
        lines: "Iterable[LineToRegister]",
    ) -> list[DocumentAllocationSource]:
        """Alle Positionen eines Belegs auf einmal bekanntmachen.

        Das ist der Aufruf, der beim **Speichern** eines Belegs gehoert. Ohne
        ihn bleibt die Quelltabelle leer, und das Mengenmodell ist zwar da, aber
        an keiner Position sichtbar: ``allocate`` findet dann nichts, worauf es
        sich beziehen koennte.

        Positionen ohne Menge oder ohne Einheit werden **uebersprungen**, nicht
        mit einem Ersatzwert angelegt. Eine Quellposition mit geratener Menge
        waere schlimmer als eine fehlende: Sie liesse sich zuordnen.

        Der Aufruf ist idempotent — beim erneuten Speichern werden die Mengen
        fortgeschrieben. Faellt eine Menge dabei unter das bereits Zugeordnete,
        schlaegt er fehl; genau dann soll das Speichern scheitern, weil sonst
        mehr berechnet waere als geliefert.
        """
        registriert: list[DocumentAllocationSource] = []
        for zeile in lines:
            if zeile.quantity is None or not zeile.unit:
                continue
            menge = Decimal(str(zeile.quantity))
            if menge <= 0:
                continue
            registriert.append(
                self.register_source(
                    PositionRef(document_type, document_id, str(zeile.line_id)),
                    menge,
                    zeile.unit,
                    article_id=zeile.article_id,
                )
            )

        self._prune_removed_lines(document_type, document_id, {q.line_id for q in registriert})
        return registriert

    def _prune_removed_lines(
        self, document_type: str, document_id: str, behalten: set[str]
    ) -> None:
        """Geloeschte Positionen aufraeumen — aber nur die unbelegten.

        Wird eine Position aus einem Beleg entfernt, soll ihre Quellzeile nicht
        als Karteileiche zurueckbleiben. Hat sie aber bereits Zuordnungen, wird
        sie **nicht** geloescht: Dann ist auf sie berechnet worden, und das
        stillschweigend zu entfernen hiesse, eine Rechnung ihrer Grundlage zu
        berauben. Sie bleibt stehen und faellt im Mengenstand auf — das ist der
        Zweck.
        """
        verwaist = (
            self.db.query(DocumentAllocationSource)
            .filter(
                DocumentAllocationSource.tenant_id == self.tenant_id,
                DocumentAllocationSource.document_type == document_type,
                DocumentAllocationSource.document_id == document_id,
                DocumentAllocationSource.allocated_quantity <= 0,
            )
            .all()
        )
        for quelle in verwaist:
            if quelle.line_id not in behalten:
                self.db.delete(quelle)
        self.db.flush()

    def _find_source(self, ref: PositionRef, for_update: bool = False):
        query = self.db.query(DocumentAllocationSource).filter(
            DocumentAllocationSource.tenant_id == self.tenant_id,
            DocumentAllocationSource.document_type == ref.document_type,
            DocumentAllocationSource.document_id == ref.document_id,
            DocumentAllocationSource.line_id == ref.line_id,
        )
        if for_update:
            # Serialisiert gleichzeitige Zuordnungen auf dieselbe Quellposition.
            # Ohne diese Sperre laesen zwei Transaktionen denselben Restbestand
            # und beide haetten recht — bis die CHECK-Bedingung eine von beiden
            # abweist. Die Sperre macht daraus ein Warten statt eines Fehlers.
            query = query.with_for_update()
        return query.first()

    # -- Zuordnen --------------------------------------------------------------

    def allocate(
        self,
        source: PositionRef,
        target: PositionRef,
        quantity: Decimal,
        unit: str,
        article_units: ArtikelEinheiten | None = None,
        reason: str | None = None,
        note: str | None = None,
        user_id: str | None = None,
    ) -> AllocationResult:
        """Eine Teilmenge der Quell- auf die Zielposition zuordnen."""
        if quantity <= 0:
            raise AllocationError("Die zugeordnete Menge muss groesser als null sein.")

        quelle = self._find_source(source, for_update=True)
        if quelle is None:
            raise AllocationError(
                f"Quellposition {source.document_type}/{source.document_id}/"
                f"{source.line_id} ist nicht bekannt. Vor dem Zuordnen "
                "registrieren."
            )

        menge_quelle = self._in_source_unit(quantity, unit, quelle.unit, article_units)

        if article_units is not None and not ist_zulaessige_menge(
            article_units, quantity, unit
        ):
            raise NotDivisibleError(
                f"{quantity} {unit} ist fuer diesen Artikel keine zulaessige "
                "Menge — er darf nur in ganzen Gebinden bewegt werden."
            )

        bereits = Decimal(str(quelle.allocated_quantity))
        gesamt = Decimal(str(quelle.quantity))
        if bereits + menge_quelle > gesamt:
            offen = gesamt - bereits
            raise OverAllocationError(
                f"Offen sind noch {offen} {quelle.unit}; zugeordnet werden "
                f"sollten {menge_quelle} {quelle.unit}."
            )

        zuordnung = DocumentAllocation(
            tenant_id=self.tenant_id,
            source_id=quelle.id,
            target_document_type=target.document_type,
            target_document_id=target.document_id,
            target_line_id=target.line_id,
            quantity=menge_quelle,
            unit=quelle.unit,
            entered_quantity=quantity,
            entered_unit=normalisiere(unit),
            reason=reason,
            note=note,
            created_by=user_id,
        )
        self.db.add(zuordnung)
        quelle.allocated_quantity = bereits + menge_quelle
        self.db.flush()

        neu = Decimal(str(quelle.allocated_quantity))
        return AllocationResult(
            allocation_id=zuordnung.id,
            quantity=menge_quelle,
            unit=quelle.unit,
            remaining=gesamt - neu,
            status=_status(gesamt, neu),
        )

    def _in_source_unit(
        self,
        quantity: Decimal,
        unit: str,
        source_unit: str,
        article_units: ArtikelEinheiten | None,
    ) -> Decimal:
        """In die Einheit der Quellposition umrechnen — oder ablehnen."""
        von, nach = normalisiere(unit), normalisiere(source_unit)
        if von == nach:
            return quantity

        faktor = None
        if article_units is not None:
            faktor = article_units.faktor(von, nach)
        else:
            from app.core.agrar_units import globaler_faktor

            faktor = globaler_faktor(von, nach)

        if faktor is None:
            raise UnitNotConvertibleError(
                f"{unit} laesst sich nicht in {source_unit} umrechnen. "
                "Zaehleinheiten brauchen einen am Artikel hinterlegten "
                "Gebindefaktor; ohne ihn waere jede Zahl geraten."
            )
        return quantity * faktor

    # -- Loesen und Auswerten --------------------------------------------------

    def release(self, allocation_id: str, *, frees_quantity: bool) -> AllocationResult:
        """Eine Zuordnung loesen.

        ``frees_quantity`` ist **Pflicht und hat keinen Vorgabewert**, weil die
        Antwort fachlich ist und nicht aus der Mengenrechnung folgt: Eine
        Warenrueckgabe gibt die Liefermenge zur erneuten Berechnung frei, ein
        Preisnachlass nicht. Wer hier raet, erzeugt entweder doppelt berechnete
        oder nie berechnete Mengen.
        """
        zuordnung = (
            self.db.query(DocumentAllocation)
            .filter(
                DocumentAllocation.id == allocation_id,
                DocumentAllocation.tenant_id == self.tenant_id,
            )
            .first()
        )
        if zuordnung is None:
            raise AllocationError(f"Zuordnung {allocation_id} nicht gefunden.")

        quelle = (
            self.db.query(DocumentAllocationSource)
            .filter(DocumentAllocationSource.id == zuordnung.source_id)
            .with_for_update()
            .first()
        )
        if quelle is None:  # pragma: no cover - FK verhindert das
            raise AllocationError("Quellposition zur Zuordnung fehlt.")

        menge = Decimal(str(zuordnung.quantity))
        self.db.delete(zuordnung)
        if frees_quantity:
            quelle.allocated_quantity = max(
                Decimal(0), Decimal(str(quelle.allocated_quantity)) - menge
            )
        self.db.flush()

        gesamt = Decimal(str(quelle.quantity))
        belegt = Decimal(str(quelle.allocated_quantity))
        return AllocationResult(
            allocation_id=allocation_id,
            quantity=menge,
            unit=quelle.unit,
            remaining=gesamt - belegt,
            status=_status(gesamt, belegt),
        )

    def source_state(self, ref: PositionRef) -> dict | None:
        """Stand einer Quellposition: geliefert, berechnet, offen.

        Genau die drei Zahlen, die die schlanke Maske an der Position zeigen
        soll — „100 dt geliefert · 60 dt berechnet · 40 dt offen".
        """
        quelle = self._find_source(ref)
        if quelle is None:
            return None
        gesamt = Decimal(str(quelle.quantity))
        belegt = Decimal(str(quelle.allocated_quantity))
        zuordnungen = (
            self.db.query(DocumentAllocation)
            .filter(
                DocumentAllocation.source_id == quelle.id,
                DocumentAllocation.tenant_id == self.tenant_id,
            )
            .order_by(DocumentAllocation.created_at.asc())
            .all()
        )
        return {
            "document_type": quelle.document_type,
            "document_id": quelle.document_id,
            "line_id": quelle.line_id,
            "quantity": gesamt,
            "allocated_quantity": belegt,
            "open_quantity": gesamt - belegt,
            "unit": quelle.unit,
            "status": _status(gesamt, belegt),
            "allocations": [
                {
                    "id": z.id,
                    "target_document_type": z.target_document_type,
                    "target_document_id": z.target_document_id,
                    "target_line_id": z.target_line_id,
                    "quantity": Decimal(str(z.quantity)),
                    "unit": z.unit,
                    "entered_quantity": (
                        Decimal(str(z.entered_quantity)) if z.entered_quantity is not None else None
                    ),
                    "entered_unit": z.entered_unit,
                    "reason": z.reason,
                }
                for z in zuordnungen
            ],
        }
