"""Rationseditor: Draft-Bewertung gegen Katalog und Bedarfsprofil (FEED-EDITOR-021).

Reine Lese-/Rechenoperation: aufloesen der Komponenten ueber den kanonischen
Futtermittelkatalog (FEED-CORE-018), Bedarf aus dem persistierten
RequirementProfile (FEED-CORE-020), Bewertung ueber die deterministische
Draft-Funktion (Code-SSOT). Persistiert wird hier nichts — Speichern bleibt
der append-only Lifecycle-Pfad.
"""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agrar.rations.ration_draft import compare_drafts, evaluate_draft
from app.core.uuid7 import uuid7
from app.services.feeding_feed_catalog_service import FeedingFeedCatalogService


class EmptyRationVersionError(ValueError):
    """Version ohne Komponenten kann nicht fachlich bewertet werden."""


class IncomparableVersionsError(ValueError):
    """Versionen unterschiedlicher Gruppen sind fachlich nicht vergleichbar."""


class FeedingRationEditorService:
    def __init__(self, db: Session, tenant_id: str, actor: str):
        self.db, self.tenant_id, self.actor = db, tenant_id, actor
        self._catalog = FeedingFeedCatalogService(db, tenant_id, actor)

    def _requirements(self, group_id: str, requirement_profile_id: str | None) -> tuple[str, dict[str, Any]]:
        if requirement_profile_id:
            row = self.db.execute(text("""
              SELECT id, requirements FROM domain_agrar.requirement_profiles
              WHERE tenant_id=:tenant_id AND id=:profile_id AND group_id=:group_id
            """), {"tenant_id": self.tenant_id, "profile_id": requirement_profile_id,
                   "group_id": group_id}).mappings().first()
        else:
            row = self.db.execute(text("""
              SELECT id, requirements FROM domain_agrar.requirement_profiles
              WHERE tenant_id=:tenant_id AND group_id=:group_id
              ORDER BY created_at DESC LIMIT 1
            """), {"tenant_id": self.tenant_id, "group_id": group_id}).mappings().first()
        if not row:
            raise LookupError("Kein Bedarfsprofil fuer diese Gruppe gefunden — bitte zuerst Bedarf berechnen.")
        return row["id"], dict(row["requirements"])

    def evaluate(self, *, group_id: str, requirement_profile_id: str | None,
                 components: list[dict[str, Any]]) -> dict[str, Any]:
        profile_id, requirements = self._requirements(group_id, requirement_profile_id)
        feeds: dict[str, dict[str, Any]] = {}
        for component in components:
            feed_id = str(component["feed_id"])
            if feed_id in feeds:
                continue
            detail = self._catalog.get_feed(feed_id)
            feeds[feed_id] = detail["solver_feed"]
        result = evaluate_draft(components, feeds, requirements)
        result["requirement_profile_id"] = profile_id
        result["group_id"] = group_id
        return result

    # ── Persistierte Versionsbewertung (FEED-EDITOR-022) ───────────────────

    def _version_components(self, version_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        version = self.db.execute(text("""
          SELECT v.id, v.ration_id, v.snapshot, r.group_id
          FROM domain_agrar.ration_versions v
          JOIN domain_agrar.rations r ON r.id=v.ration_id AND r.tenant_id=v.tenant_id
          WHERE v.tenant_id=:tenant_id AND v.id=:version_id
        """), {"tenant_id": self.tenant_id, "version_id": version_id}).mappings().first()
        if not version:
            raise LookupError("Rationsversion nicht gefunden.")
        snapshot = version["snapshot"] or {}
        raw = snapshot.get("components") if isinstance(snapshot, dict) else None
        components = []
        for item in (raw or []):
            if not isinstance(item, dict) or not item.get("feed_id"):
                continue
            component = {"feed_id": str(item["feed_id"]), "kg_fm": float(item.get("kg_fm") or 0)}
            if item.get("min_kg_fm") is not None:
                component["min_kg_fm"] = float(item["min_kg_fm"])
            if item.get("max_kg_fm") is not None:
                component["max_kg_fm"] = float(item["max_kg_fm"])
            components.append(component)
        if not components:
            raise EmptyRationVersionError(
                "Diese Version enthaelt keine bewertbaren Komponenten (leerer Snapshot).")
        return dict(version), components

    def evaluate_version(self, version_id: str) -> dict[str, Any]:
        """Bewertung serverseitig aus dem unveraenderlichen Snapshot ableiten
        und append-only persistieren — keine Client-Payload, keine zweite Wahrheit."""
        version, components = self._version_components(version_id)
        result = self.evaluate(group_id=version["group_id"],
                               requirement_profile_id=None, components=components)
        row = self.db.execute(text("""
          INSERT INTO domain_agrar.ration_evaluations
            (id,tenant_id,ration_id,ration_version_id,requirement_profile_id,
             totals,deltas,findings,coverage,evaluated_by)
          VALUES (:id,:tenant_id,:ration_id,:version_id,:profile_id,
             CAST(:totals AS jsonb),CAST(:deltas AS jsonb),CAST(:findings AS jsonb),
             CAST(:coverage AS jsonb),:actor)
          RETURNING *
        """), {"id": str(uuid7()), "tenant_id": self.tenant_id,
               "ration_id": version["ration_id"], "version_id": version_id,
               "profile_id": result["requirement_profile_id"],
               "totals": json.dumps(result["totals"], ensure_ascii=False),
               "deltas": json.dumps(result["deltas"], ensure_ascii=False),
               "findings": json.dumps(result["findings"], ensure_ascii=False),
               "coverage": json.dumps(result["coverage"], ensure_ascii=False),
               "actor": self.actor}).mappings().one()
        self.db.commit()
        return dict(row)

    def compare_versions(self, base_version_id: str, variant_version_id: str) -> dict[str, Any]:
        """Zwei Versionen derselben Gruppe gegen dasselbe (juengste) Bedarfsprofil
        vergleichen — deterministisch, ohne Persistenz (FEED-MASK-010)."""
        base_version, base_components = self._version_components(base_version_id)
        variant_version, variant_components = self._version_components(variant_version_id)
        if base_version["group_id"] != variant_version["group_id"]:
            raise IncomparableVersionsError(
                "Versionen gehoeren zu unterschiedlichen Fuetterungsgruppen und sind nicht vergleichbar.")
        base_eval = self.evaluate(group_id=base_version["group_id"],
                                  requirement_profile_id=None, components=base_components)
        variant_eval = self.evaluate(group_id=base_version["group_id"],
                                     requirement_profile_id=base_eval["requirement_profile_id"],
                                     components=variant_components)
        result = compare_drafts(base_eval, variant_eval)
        result["group_id"] = base_version["group_id"]
        result["requirement_profile_id"] = base_eval["requirement_profile_id"]
        result["base"] = {"version_id": base_version_id, "ration_id": base_version["ration_id"],
                          "totals": base_eval["totals"]}
        result["variant"] = {"version_id": variant_version_id, "ration_id": variant_version["ration_id"],
                             "totals": variant_eval["totals"]}
        return result

    # ── Optimieren im Editor (FEED-OPT-042) ─────────────────────────────────

    # LP-Konvention des Solvers (wie _gfa_to_feed im Optimierungsmodul):
    # fehlende Koeffizienten zaehlen als 0-Beitrag (konservativ fuer >=-Grenzen),
    # omdfan1 65 als Standard-Verdaulichkeit. Das ist Solver-Arithmetik, keine
    # Anzeige — Anzeige-Luecken bleiben None (Kap. 16).
    _LP_FEED_DEFAULTS: dict[str, Any] = {
        "lid": None, "konservierung": "", "sidp": None, "ndf": 0.0, "adf": 0.0,
        "st": 0.0, "bst": 0.0, "zu": 0.0, "nfc": 0.0, "xl": 0.0,
        "ca": 0.0, "p": 0.0, "na": 0.0, "mg": 0.0, "k": 0.0,
        "dcab": None, "edg": None, "rmd": 0.0, "omdfan1": 65.0,
        "ndfd": None, "ge": None, "sidlys": None, "sidmet": None,
    }
    # max_kg ist im LP ein hartes Bound (0 = Futter gesperrt); ohne gesetzte
    # Grenze gilt das physiologische DMI-Maximum als Nicht-Limit.
    _LP_NO_LIMIT_KG_DM = 28.5

    def _lp_feed(self, solver_feed: dict[str, Any]) -> dict[str, Any]:
        feed = {**self._LP_FEED_DEFAULTS,
                **{key: value for key, value in solver_feed.items() if value is not None}}
        if feed.get("sidp") is None:
            # Monolith-Konvention (_gfa_to_feed): ohne sidP-Analyse 60 % von XP.
            feed["sidp"] = float(feed.get("cp") or 0.0) * 0.60
        if not float(feed.get("max_kg") or 0.0):
            feed["max_kg"] = self._LP_NO_LIMIT_KG_DM
        # Grobfutter-Konvention des LP: der Mindest-Grobfutteranteil (>=40 % DMI)
        # erkennt Grobfutter am group-String ("grobfutter"); Katalogfutter mit
        # forage-Kennzeichen muessen dieser Konvention folgen.
        group = str(feed.get("group") or "")
        if feed.get("forage") and "grobfutter" not in group.lower():
            feed["group"] = f"{group}/Grobfutter" if group else "Grobfutter"
        return feed

    def optimize_version(self, version_id: str, *,
                         expected_latest_version_no: int) -> dict[str, Any]:
        """Optimieren erzeugt eine Candidate-Version (nie Aktivierung) atomar
        mit einem OptimizationRun — kein Ergebnis ohne persistierten Run
        (FEED-OPT-005). Unloesbarkeit dokumentiert den Run mit status
        `infeasible` und erklaert die Konfliktgrenzen (Erklaerschicht + 024)."""
        import time

        version, components = self._version_components(version_id)
        profile_row = self.db.execute(text("""
          SELECT id, inputs FROM domain_agrar.requirement_profiles
          WHERE tenant_id=:tenant_id AND group_id=:group_id
          ORDER BY created_at DESC LIMIT 1
        """), {"tenant_id": self.tenant_id, "group_id": version["group_id"]}).mappings().first()
        if not profile_row:
            raise LookupError(
                "Kein Bedarfsprofil fuer diese Gruppe gefunden — bitte zuerst Bedarf berechnen.")

        # Kandidatenmenge = Editor-Positionen mit ihren Grenzen (FM -> TM).
        custom_feeds: list[dict[str, Any]] = []
        feed_ids: list[str] = []
        for component in components:
            detail = self._catalog.get_feed(component["feed_id"])
            feed = self._lp_feed(dict(detail["solver_feed"]))
            dm_frac = float(feed.get("dm_frac") or 0)
            if component.get("min_kg_fm") is not None and dm_frac > 0:
                feed["min_kg"] = float(component["min_kg_fm"]) * dm_frac
            if component.get("max_kg_fm") is not None and dm_frac > 0:
                feed["max_kg"] = float(component["max_kg_fm"]) * dm_frac
            custom_feeds.append(feed)
            feed_ids.append(str(feed["id"]))

        # Lazy-Import: rations_optimization inkludiert diesen Router am Dateiende
        # (Import beim Modul-Load waere zirkulaer). feed_ids filtert die
        # DLG-Basisfeeds heraus; custom_feeds kommen danach als Kandidaten dazu.
        from app.api.v1.endpoints.rations_optimization import _optimize_internal
        started = time.monotonic()
        result = _optimize_internal(dict(profile_row["inputs"]),
                                    custom_feeds=custom_feeds, feed_ids=feed_ids)
        duration_ms = int((time.monotonic() - started) * 1000)
        status = str(result.get("status") or "error")
        if status not in {"optimal", "infeasible", "unbounded", "timeout"}:
            status = "error"
        objective = str(result.get("objective_strategy") or "balance_then_cost")
        run_parameters: dict[str, Any] = {
            "trigger": "editor",
            "source_version_id": version_id,
            "requirement_profile_id": profile_row["id"],
            "candidate_feed_ids": feed_ids,
            "bounds": [{key: component.get(key) for key in
                        ("feed_id", "min_kg_fm", "max_kg_fm")} for component in components],
        }

        def insert_run(run_version_id: str, extra: dict[str, Any]) -> dict[str, Any]:
            row = self.db.execute(text("""
              INSERT INTO domain_agrar.optimization_runs
                (id,tenant_id,ration_id,ration_version_id,solver_version,objective,
                 status,duration_ms,parameters,created_by)
              VALUES (:id,:tenant_id,:ration_id,:version_id,:solver_version,:objective,
                      :status,:duration_ms,CAST(:parameters AS jsonb),:actor)
              RETURNING *
            """), {"id": str(uuid7()), "tenant_id": self.tenant_id,
                   "ration_id": version["ration_id"], "version_id": run_version_id,
                   "solver_version": "rations-lp-highs", "objective": objective,
                   "status": status, "duration_ms": duration_ms,
                   "parameters": json.dumps({**run_parameters, **extra}, ensure_ascii=False),
                   "actor": self.actor}).mappings().one()
            return dict(row)

        if status != "optimal":
            # Erklaerschicht: Solver-Diagnose + strukturelle Grenzbefunde (024).
            evaluation = self.evaluate(group_id=version["group_id"],
                                       requirement_profile_id=str(profile_row["id"]),
                                       components=components)
            bound_findings = [finding for finding in evaluation["findings"]
                              if finding["metric"] in {"bounds", "dm_kg"}]
            explanation = {
                "diagnosis": result.get("diagnosis"),
                "warnings": result.get("warnings") or [],
                "bound_findings": bound_findings,
            }
            run = insert_run(version_id, {"explanation": explanation})
            self.db.commit()
            return {"status": status, "candidate_version": None,
                    "optimization_run": run, "explanation": explanation}

        # optimal: Candidate-Version + Run in EINER Transaktion (atomar).
        source_by_feed = {component["feed_id"]: component for component in components}
        candidate_components = []
        for index, item in enumerate(result.get("ration_items") or []):
            source_component = source_by_feed.get(str(item.get("feed_id")), {})
            candidate_components.append({
                "feed_id": str(item.get("feed_id")),
                "name": item.get("name"),
                "kg_fm": float(item.get("kgfm") or 0),
                "min_kg_fm": source_component.get("min_kg_fm"),
                "max_kg_fm": source_component.get("max_kg_fm"),
                "mixing_sequence": index + 1,
            })
        from app.services.rations_lifecycle_service import RationLifecycleService
        lifecycle = RationLifecycleService(self.db, self.tenant_id, self.actor)
        candidate = lifecycle._create_version_locked(
            ration_id=version["ration_id"],
            snapshot={"components": candidate_components},
            source="optimizer",
            comment="Optimierungslauf aus dem Rationseditor",
            based_on_version_id=version_id,
            expected_latest_version_no=expected_latest_version_no,
        )
        run = insert_run(candidate["id"], {
            "total_cost_eur_day": result.get("total_cost_eur_day"),
            "objective_value": result.get("objective_value"),
        })
        self.db.commit()
        return {"status": status, "candidate_version": candidate,
                "optimization_run": run, "explanation": None}

    def latest_evaluation(self, version_id: str) -> dict[str, Any]:
        row = self.db.execute(text("""
          SELECT * FROM domain_agrar.ration_evaluations
          WHERE tenant_id=:tenant_id AND ration_version_id=:version_id
          ORDER BY evaluated_at DESC LIMIT 1
        """), {"tenant_id": self.tenant_id, "version_id": version_id}).mappings().first()
        if not row:
            raise LookupError("Fuer diese Version liegt noch keine Bewertung vor.")
        return dict(row)
