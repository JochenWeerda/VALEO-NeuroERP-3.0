"""Kunden-Dubletten-Erkennung (DOM-CRM-004).

Read-only Heuristik: findet wahrscheinliche Dubletten in public.kunden über
normalisierte Blocking-Schlüssel und gruppiert sie per Union-Find zu Clustern:

  • E-Mail (lower)                         → starkes Signal
  • Telefon (Ziffern-Tail, letzte 7)       → starkes Signal
  • Name1 (normalisiert) + PLZ             → mittleres Signal

Liefert je Cluster die Mitglieder + Treffergründe + Konfidenz. Basis für die
Zusammenführung (Folge-Slice 004.2). Keine Schreibvorgänge.
"""

from __future__ import annotations

import re
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"

# Rechtsform-/Füllwörter, die für den Namensabgleich entfernt werden.
_LEGAL = {
    "gmbh", "mbh", "co", "kg", "gbr", "ag", "ek", "e", "k", "ohg", "ug",
    "und", "u", "the", "fa", "firma", "landw", "betrieb", "hof",
}
_REASON_WEIGHT = {"email": 3, "telefon": 2, "name_plz": 2}


def _norm_name(s: Optional[str]) -> str:
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"[.\-,/&+]", " ", s)
    tokens = [t for t in re.split(r"\s+", s) if t and t not in _LEGAL]
    return " ".join(sorted(tokens))  # sortiert → "Mueller, Heinrich" == "Heinrich Mueller"


def _norm_phone(s: Optional[str]) -> str:
    d = re.sub(r"[^\d]", "", s or "")
    return d[-7:] if len(d) >= 7 else ""


def _norm_email(s: Optional[str]) -> str:
    return (s or "").strip().lower()


class _UnionFind:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        self.parent.setdefault(x, x)
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


class CrmDuplicateService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def find_duplicates(self, limit_groups: int = 100) -> dict:
        rows = self.db.execute(
            text(
                "SELECT kunden_nr, name1, name2, plz, ort, tel, email "
                "FROM public.kunden "
                "WHERE COALESCE(geloescht, false) = false"
            )
        ).mappings().all()

        by_email: dict[str, list[str]] = {}
        by_phone: dict[str, list[str]] = {}
        by_nameplz: dict[str, list[str]] = {}
        info: dict[str, dict] = {}
        for r in rows:
            kn = r["kunden_nr"]
            info[kn] = {"kunden_nr": kn, "name1": r["name1"], "plz": r["plz"],
                        "ort": r["ort"], "tel": r["tel"], "email": r["email"]}
            em = _norm_email(r["email"])
            if em:
                by_email.setdefault(em, []).append(kn)
            ph = _norm_phone(r["tel"])
            if ph:
                by_phone.setdefault(ph, []).append(kn)
            nm = _norm_name(r["name1"])
            if nm and r["plz"]:
                by_nameplz.setdefault(f"{nm}|{r['plz']}", []).append(kn)

        uf = _UnionFind()
        # Treffergründe je Kundennummer-Paar-Cluster sammeln (auf Root gemappt später).
        reasons_by_member: dict[str, set[tuple[str, str]]] = {}

        def link(members: list[str], rtype: str, value: str) -> None:
            uniq = sorted(set(members))
            if len(uniq) < 2:
                return
            base = uniq[0]
            for m in uniq[1:]:
                uf.union(base, m)
            for m in uniq:
                reasons_by_member.setdefault(m, set()).add((rtype, value))

        for em, members in by_email.items():
            link(members, "email", em)
        for ph, members in by_phone.items():
            link(members, "telefon", ph)
        for key, members in by_nameplz.items():
            link(members, "name_plz", key.split("|")[0])

        # Cluster bilden.
        clusters: dict[str, list[str]] = {}
        for member in reasons_by_member:
            clusters.setdefault(uf.find(member), []).append(member)

        out = []
        for root, members in clusters.items():
            members = sorted(set(members))
            if len(members) < 2:
                continue
            reasons: set[tuple[str, str]] = set()
            for m in members:
                reasons |= reasons_by_member.get(m, set())
            reason_types = {t for t, _ in reasons}
            score = sum(_REASON_WEIGHT.get(t, 1) for t in reason_types)
            confidence = "hoch" if (reason_types & {"email", "telefon"}) and len(reason_types) >= 2 else (
                "hoch" if "email" in reason_types else "mittel")
            out.append({
                "id": root,
                "mitglieder": [info[m] for m in members if m in info],
                "anzahl": len(members),
                "gruende": sorted([{"typ": t, "wert": v} for t, v in reasons], key=lambda x: x["typ"]),
                "grund_typen": sorted(reason_types),
                "score": score,
                "konfidenz": confidence,
            })
        out.sort(key=lambda c: (-c["score"], -c["anzahl"]))
        total = len(out)
        return {"groups": out[:limit_groups], "total": total,
                "geprueft": len(rows)}
