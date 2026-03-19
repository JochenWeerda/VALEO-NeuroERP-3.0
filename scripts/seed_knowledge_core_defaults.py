from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.database import SessionLocal
from app.core.knowledge_core_contracts import get_default_knowledge_objects
from app.infrastructure import models as shared_models  # noqa: F401
from app.repositories.knowledge_repository import KnowledgeRepository


def main() -> None:
    db = SessionLocal()
    try:
        repo = KnowledgeRepository(db)
        for obj in get_default_knowledge_objects():
            existing = repo.get_object(obj.knowledge_id)
            versionen = sorted(obj.versionen, key=lambda eintrag: eintrag.version)
            if existing is None:
                initial = versionen[0]
                repo.create_object(
                    knowledge_id=obj.knowledge_id,
                    titel=obj.titel,
                    typ=obj.typ.value,
                    status=obj.status.value,
                    tenant_id=obj.tenant_id,
                    beschreibung=obj.beschreibung,
                    tags=obj.tags,
                    zielrollen=obj.zielrollen,
                    agentenfreigabe=obj.agentenfreigabe,
                    version_payload={
                        "version": initial.version,
                        "format": initial.format.value,
                        "inhalt": initial.inhalt,
                        "strukturierte_daten": initial.strukturierte_daten,
                        "quelle": initial.quelle,
                    },
                )

            for version in versionen:
                if repo.has_version(obj.knowledge_id, version.version):
                    continue
                repo.add_version(
                    obj.knowledge_id,
                    {
                        "version": version.version,
                        "format": version.format.value,
                        "inhalt": version.inhalt,
                        "strukturierte_daten": version.strukturierte_daten,
                        "quelle": version.quelle,
                        "status": obj.status.value,
                    },
                )
        print("knowledge-core defaults seeded")
    finally:
        db.close()


if __name__ == "__main__":
    main()
