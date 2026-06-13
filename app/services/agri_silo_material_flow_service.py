"""Agrar-Siloanlagen und Materialfluss (Knoten/Kanten) — WM-AGRI-SILO-001.

Digitales Modell ohne PLC; Plausibilitätsregeln für Routen und Kantenstatus.
"""

from __future__ import annotations

from collections import deque
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

_ALLOWED_QS = frozenset({"frei", "gesperrt", "in_pruefung", "reinigung", "reserviert"})
_ALLOWED_NODE_STATUS = frozenset({"active", "blocked", "maintenance", "cleaning"})
_ALLOWED_EDGE_STATUS = frozenset({"open", "blocked", "maintenance", "cleaning"})


class AgriSiloMaterialFlowService:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    # ── Siloanlagen ────────────────────────────────────────────

    def list_silo_systems(self, warehouse_id: str | None = None) -> list[dict]:
        filters = ["tenant_id = :tid", "is_active = true"]
        params: dict = {"tid": self.tenant_id}
        if warehouse_id:
            filters.append("warehouse_id = :wid")
            params["wid"] = warehouse_id
        where = " AND ".join(filters)
        rows = self.db.execute(
            text(f"SELECT * FROM domain_inventory.silo_systems WHERE {where} ORDER BY system_code"),  # noqa: S608
            params,
        ).fetchall()
        return [dict(r._mapping) for r in rows]

    def create_silo_system(self, warehouse_id: str, payload: dict) -> dict:
        sid = str(uuid4())
        self.db.execute(
            text("""
                INSERT INTO domain_inventory.silo_systems
                  (id, warehouse_id, system_code, name, description, tenant_id, is_active)
                VALUES (:id, :wid, :code, :name, :desc, :tid, true)
            """),
            {
                "id": sid,
                "wid": warehouse_id,
                "code": payload["system_code"],
                "name": payload["name"],
                "desc": payload.get("description"),
                "tid": self.tenant_id,
            },
        )
        self.db.commit()
        return {"id": sid, "warehouse_id": warehouse_id, **payload}

    # ── Silozellen ─────────────────────────────────────────────

    def list_silo_cells(self, warehouse_id: str | None = None, silo_system_id: str | None = None) -> list[dict]:
        filters = ["tenant_id = :tid", "is_active = true"]
        params: dict = {"tid": self.tenant_id}
        if warehouse_id:
            filters.append("warehouse_id = :wid")
            params["wid"] = warehouse_id
        if silo_system_id:
            filters.append("silo_system_id = :ssid")
            params["ssid"] = silo_system_id
        where = " AND ".join(filters)
        rows = self.db.execute(
            text(f"SELECT * FROM domain_inventory.silo_cells WHERE {where} ORDER BY cell_code"),  # noqa: S608
            params,
        ).fetchall()
        return [dict(r._mapping) for r in rows]

    def create_silo_cell(self, silo_system_id: str, warehouse_id: str, payload: dict) -> dict:
        sys_row = self.db.execute(
            text("""
                SELECT id, warehouse_id FROM domain_inventory.silo_systems
                WHERE id = :sid AND tenant_id = :tid AND is_active = true
            """),
            {"sid": silo_system_id, "tid": self.tenant_id},
        ).fetchone()
        if not sys_row:
            raise ValueError("Siloanlage nicht gefunden")
        if str(sys_row.warehouse_id) != warehouse_id:
            raise ValueError("warehouse_id passt nicht zur Siloanlage")
        cid = str(uuid4())
        self.db.execute(
            text("""
                INSERT INTO domain_inventory.silo_cells
                  (id, silo_system_id, warehouse_id, zone_id, aisle_id, bin_id,
                   cell_code, name, capacity_kg, current_material_id, current_lot_id,
                   qs_status, contamination_risk_class, tenant_id, is_active)
                VALUES (:id, :ssid, :wid, :zid, :aid, :bid, :ccode, :name, :cap,
                        :mat, :lot, :qs, :crc, :tid, true)
            """),
            {
                "id": cid,
                "ssid": silo_system_id,
                "wid": warehouse_id,
                "zid": payload.get("zone_id"),
                "aid": payload.get("aisle_id"),
                "bid": payload.get("bin_id"),
                "ccode": payload["cell_code"],
                "name": payload["name"],
                "cap": payload.get("capacity_kg") or Decimal("0"),
                "mat": payload.get("current_material_id"),
                "lot": payload.get("current_lot_id"),
                "qs": payload.get("qs_status", "frei"),
                "crc": payload.get("contamination_risk_class"),
                "tid": self.tenant_id,
            },
        )
        self.db.commit()
        return {"id": cid, "silo_system_id": silo_system_id, "warehouse_id": warehouse_id, **payload}

    def patch_silo_cell(self, cell_id: str, warehouse_id: str, payload: dict) -> dict:
        """Teilupdate Silozelle (Mandant + Lager); mindestens ein erlaubtes Feld."""
        fields: dict[str, object] = {}
        if payload.get("qs_status") is not None:
            qs = str(payload["qs_status"])
            if qs not in _ALLOWED_QS:
                raise ValueError("qs_status ungueltig")
            fields["qs_status"] = qs
        if payload.get("name") is not None:
            fields["name"] = str(payload["name"])
        if payload.get("capacity_kg") is not None:
            fields["capacity_kg"] = payload["capacity_kg"]
        if "current_material_id" in payload:
            fields["current_material_id"] = payload.get("current_material_id")
        if "current_lot_id" in payload:
            fields["current_lot_id"] = payload.get("current_lot_id")
        if "contamination_risk_class" in payload:
            fields["contamination_risk_class"] = payload.get("contamination_risk_class")
        if "layout_x" in payload:
            fields["layout_x"] = payload.get("layout_x")
        if "layout_y" in payload:
            fields["layout_y"] = payload.get("layout_y")
        if not fields:
            raise ValueError("Keine Felder zum Aktualisieren")
        set_parts = [f"{k} = :{k}" for k in fields]
        params: dict = {**fields, "cid": cell_id, "wid": warehouse_id, "tid": self.tenant_id}
        row = self.db.execute(
            text(f"""
                UPDATE domain_inventory.silo_cells
                SET {", ".join(set_parts)}
                WHERE id = :cid AND warehouse_id = :wid AND tenant_id = :tid AND is_active = true
                RETURNING *
            """),  # noqa: S608
            params,
        ).fetchone()
        if not row:
            raise ValueError("Silozelle nicht gefunden")
        self.db.commit()
        return dict(row._mapping)

    # ── Materialfluss-Knoten ───────────────────────────────────

    def list_material_flow_nodes(self, warehouse_id: str | None = None) -> list[dict]:
        filters = ["tenant_id = :tid", "is_active = true"]
        params: dict = {"tid": self.tenant_id}
        if warehouse_id:
            filters.append("warehouse_id = :wid")
            params["wid"] = warehouse_id
        where = " AND ".join(filters)
        rows = self.db.execute(
            text(f"SELECT * FROM domain_inventory.material_flow_nodes WHERE {where} ORDER BY code"),  # noqa: S608
            params,
        ).fetchall()
        return [dict(r._mapping) for r in rows]

    def create_material_flow_node(self, warehouse_id: str, payload: dict) -> dict:
        nid = str(uuid4())
        self.db.execute(
            text("""
                INSERT INTO domain_inventory.material_flow_nodes
                  (id, warehouse_id, node_type, ref_type, ref_id, code, name, status,
                   geo_lat, geo_lng, layout_x, layout_y, tenant_id, is_active)
                VALUES (:id, :wid, :ntype, :rtype, :rid, :code, :name, :st,
                        :lat, :lng, :lx, :ly, :tid, true)
            """),
            {
                "id": nid,
                "wid": warehouse_id,
                "ntype": payload["node_type"],
                "rtype": payload.get("ref_type"),
                "rid": payload.get("ref_id"),
                "code": payload["code"],
                "name": payload["name"],
                "st": payload.get("status", "active"),
                "lat": payload.get("geo_lat"),
                "lng": payload.get("geo_lng"),
                "lx": payload.get("layout_x"),
                "ly": payload.get("layout_y"),
                "tid": self.tenant_id,
            },
        )
        self.db.commit()
        return {"id": nid, "warehouse_id": warehouse_id, **payload}

    def patch_material_flow_node(self, node_id: str, warehouse_id: str, payload: dict) -> dict:
        """Teilupdate Knoten (Lager + Mandant); kein Wechsel von node_type/code/warehouse_id."""
        fields: dict[str, object] = {}
        if payload.get("status") is not None:
            st = str(payload["status"])
            if st not in _ALLOWED_NODE_STATUS:
                raise ValueError("Knoten-status ungueltig")
            fields["status"] = st
        if payload.get("name") is not None:
            fields["name"] = str(payload["name"])
        if "ref_type" in payload:
            fields["ref_type"] = payload.get("ref_type")
        if "ref_id" in payload:
            fields["ref_id"] = payload.get("ref_id")
        if "geo_lat" in payload:
            fields["geo_lat"] = payload.get("geo_lat")
        if "geo_lng" in payload:
            fields["geo_lng"] = payload.get("geo_lng")
        if "layout_x" in payload:
            fields["layout_x"] = payload.get("layout_x")
        if "layout_y" in payload:
            fields["layout_y"] = payload.get("layout_y")
        if not fields:
            raise ValueError("Keine Felder zum Aktualisieren")
        set_parts = [f"{k} = :{k}" for k in fields]
        params: dict = {**fields, "nid": node_id, "wid": warehouse_id, "tid": self.tenant_id}
        row = self.db.execute(
            text(f"""
                UPDATE domain_inventory.material_flow_nodes
                SET {", ".join(set_parts)}
                WHERE id = :nid AND warehouse_id = :wid AND tenant_id = :tid AND is_active = true
                RETURNING *
            """),  # noqa: S608
            params,
        ).fetchone()
        if not row:
            raise ValueError("Knoten nicht gefunden")
        self.db.commit()
        return dict(row._mapping)

    # ── Kanten ────────────────────────────────────────────────

    def _node_row(self, node_id: str) -> dict | None:
        r = self.db.execute(
            text("""
                SELECT * FROM domain_inventory.material_flow_nodes
                WHERE id = :id AND tenant_id = :tid
            """),
            {"id": node_id, "tid": self.tenant_id},
        ).fetchone()
        return dict(r._mapping) if r else None

    def _edge_row(self, edge_id: str, warehouse_id: str) -> dict | None:
        r = self.db.execute(
            text("""
                SELECT * FROM domain_inventory.material_flow_edges
                WHERE id = :eid AND warehouse_id = :wid AND tenant_id = :tid
            """),
            {"eid": edge_id, "wid": warehouse_id, "tid": self.tenant_id},
        ).fetchone()
        return dict(r._mapping) if r else None

    def _silo_cell_qs_for_ref(self, ref_type: str | None, ref_id: str | None) -> str | None:
        if ref_type != "silo_cell" or not ref_id:
            return None
        r = self.db.execute(
            text("""
                SELECT qs_status FROM domain_inventory.silo_cells
                WHERE id = :id AND tenant_id = :tid AND is_active = true
            """),
            {"id": ref_id, "tid": self.tenant_id},
        ).fetchone()
        return str(r.qs_status) if r else None

    def _assert_open_edge_allowed(self, to_node_id: str, edge_status: str) -> None:
        if edge_status != "open":
            return
        to_node = self._node_row(to_node_id)
        if not to_node:
            raise ValueError("Zielknoten nicht gefunden")
        st = str(to_node.get("status") or "")
        if st in ("blocked", "maintenance", "cleaning"):
            raise ValueError(f"Kante darf nicht 'open' sein: Zielknoten ist '{st}'")
        qs = self._silo_cell_qs_for_ref(to_node.get("ref_type"), to_node.get("ref_id"))
        if qs == "gesperrt":
            raise ValueError("Route/Kante in gesperrte Silozelle nicht als 'open' zulaessig")

    def list_material_flow_edges(self, warehouse_id: str | None = None) -> list[dict]:
        filters = ["tenant_id = :tid"]
        params: dict = {"tid": self.tenant_id}
        if warehouse_id:
            filters.append("warehouse_id = :wid")
            params["wid"] = warehouse_id
        where = " AND ".join(filters)
        rows = self.db.execute(
            text(f"SELECT * FROM domain_inventory.material_flow_edges WHERE {where} ORDER BY created_at"),  # noqa: S608
            params,
        ).fetchall()
        return [dict(r._mapping) for r in rows]

    def create_material_flow_edge(self, warehouse_id: str, payload: dict) -> dict:
        fn = payload["from_node_id"]
        tn = payload["to_node_id"]
        est = payload.get("status", "open")
        for nid in (fn, tn):
            n = self._node_row(nid)
            if not n or str(n.get("warehouse_id")) != warehouse_id:
                raise ValueError("Knoten ungueltig oder falsches Lager")
        self._assert_open_edge_allowed(tn, est)
        eid = str(uuid4())
        flush_flag = bool(payload.get("flush_required", False))
        self.db.execute(
            text("""
                INSERT INTO domain_inventory.material_flow_edges
                  (id, warehouse_id, from_node_id, to_node_id, conveyor_type, status,
                   contamination_guard_enabled, flush_required, max_capacity_kg_h, tenant_id)
                VALUES (:id, :wid, :fn, :tn, :ctype, :st, :guard, :flush, :maxkg, :tid)
            """),
            {
                "id": eid,
                "wid": warehouse_id,
                "fn": fn,
                "tn": tn,
                "ctype": payload.get("conveyor_type", "generic"),
                "st": est,
                "guard": payload.get("contamination_guard_enabled", True),
                "flush": flush_flag,
                "maxkg": payload.get("max_capacity_kg_h"),
                "tid": self.tenant_id,
            },
        )
        self.db.commit()
        return {"id": eid, "warehouse_id": warehouse_id, **payload}

    def patch_material_flow_edge(self, edge_id: str, warehouse_id: str, payload: dict) -> dict:
        """Teilupdate Kante; bei status='open' Zielknoten-QS/Sperre pruefen."""
        cur = self._edge_row(edge_id, warehouse_id)
        if not cur:
            raise ValueError("Kante nicht gefunden")
        fields: dict[str, object] = {}
        if payload.get("status") is not None:
            st = str(payload["status"])
            if st not in _ALLOWED_EDGE_STATUS:
                raise ValueError("Kanten-status ungueltig")
            if st == "open":
                self._assert_open_edge_allowed(str(cur["to_node_id"]), "open")
            fields["status"] = st
        if payload.get("conveyor_type") is not None:
            fields["conveyor_type"] = str(payload["conveyor_type"])
        if "contamination_guard_enabled" in payload:
            fields["contamination_guard_enabled"] = bool(payload["contamination_guard_enabled"])
        if "flush_required" in payload:
            fields["flush_required"] = bool(payload["flush_required"])
        if "max_capacity_kg_h" in payload:
            fields["max_capacity_kg_h"] = payload.get("max_capacity_kg_h")
        if not fields:
            raise ValueError("Keine Felder zum Aktualisieren")
        set_parts = [f"{k} = :{k}" for k in fields]
        params: dict = {**fields, "eid": edge_id, "wid": warehouse_id, "tid": self.tenant_id}
        row = self.db.execute(
            text(f"""
                UPDATE domain_inventory.material_flow_edges
                SET {", ".join(set_parts)}
                WHERE id = :eid AND warehouse_id = :wid AND tenant_id = :tid
                RETURNING *
            """),  # noqa: S608
            params,
        ).fetchone()
        if not row:
            raise ValueError("Kante nicht gefunden")
        self.db.commit()
        return dict(row._mapping)

    # ── Routen-Validierung (BFS) ───────────────────────────────

    def validate_route(
        self,
        warehouse_id: str,
        from_node_id: str,
        to_node_id: str,
        material_id: str | None = None,
        previous_material_id: str | None = None,
    ) -> dict:
        """BFS nur in **Speicher-Richtung** from_node_id → to_node_id (gerichteter Graph).

        Kanten status='open'; Zwischenknoten müssen status='active' sein.
        """
        if from_node_id == to_node_id:
            return {"ok": True, "path": [from_node_id], "warnings": [], "flush_required": False}

        edges = self.db.execute(
            text("""
                SELECT from_node_id, to_node_id, contamination_guard_enabled, flush_required, status
                FROM domain_inventory.material_flow_edges
                WHERE warehouse_id = :wid AND tenant_id = :tid AND status = 'open'
            """),
            {"wid": warehouse_id, "tid": self.tenant_id},
        ).fetchall()
        adj: dict[str, list[tuple[str, dict]]] = {}
        for e in edges:
            d = dict(e._mapping)
            a, b = str(d["from_node_id"]), str(d["to_node_id"])
            adj.setdefault(a, []).append((b, d))

        prev: dict[str, str | None] = {from_node_id: None}
        q: deque[str] = deque([from_node_id])
        found = False
        while q:
            cur = q.popleft()
            if cur == to_node_id:
                found = True
                break
            for nxt, _edata in adj.get(cur, []):
                if nxt not in prev:
                    prev[nxt] = cur
                    q.append(nxt)
        if not found:
            return {"ok": False, "reason": "Keine offene Route zwischen den Knoten", "path": []}

        path: list[str] = []
        cur: str | None = to_node_id
        while cur is not None:
            path.append(cur)
            cur = prev.get(cur)
        path.reverse()

        warnings: list[str] = []
        flush_required = False
        for nid in path:
            node = self._node_row(nid)
            if not node or str(node.get("warehouse_id")) != warehouse_id:
                return {"ok": False, "reason": "Knoten ausserhalb des Lagers", "path": path}
            nst = str(node.get("status") or "")
            if nst != "active":
                return {"ok": False, "reason": f"Knoten {node.get('code')} ist nicht aktiv ({nst})", "path": path}
            qs = self._silo_cell_qs_for_ref(node.get("ref_type"), node.get("ref_id"))
            if qs == "gesperrt":
                return {"ok": False, "reason": f"Silozelle gesperrt (Knoten {node.get('code')})", "path": path}
            if qs in ("in_pruefung", "reinigung", "reserviert"):
                warnings.append(f"Hinweis: Silozelle qs_status={qs} bei {node.get('code')}")

        if (
            material_id
            and previous_material_id
            and material_id != previous_material_id
        ):
            edge_rows = [dict(e._mapping) for e in edges]
            for i in range(len(path) - 1):
                a, b = path[i], path[i + 1]
                edge_meta = None
                for ed in edge_rows:
                    if str(ed["from_node_id"]) == a and str(ed["to_node_id"]) == b:
                        edge_meta = ed
                        break
                if edge_meta and edge_meta.get("contamination_guard_enabled"):
                    flush_required = True
                    warnings.append(
                        "Verschleppungsrisiko: Materialwechsel auf geschuetzter Kante — Spuelcharge pruefen"
                    )
                    break

        return {
            "ok": True,
            "path": path,
            "warnings": warnings,
            "flush_required": flush_required,
        }
