from sqlalchemy import text
from app.core.database import SessionLocal

db = SessionLocal()
rows = db.execute(
    text("SELECT kunden_nr, lat, lon, precision FROM public.kunden_geo WHERE kunden_nr = :k"),
    {"k": "KD-10001"},
).mappings().all()
print("geo", [dict(r) for r in rows])
k = db.execute(
    text("SELECT kunden_nr, plz, ort, strasse FROM public.kunden WHERE kunden_nr = :k"),
    {"k": "KD-10001"},
).mappings().first()
print("kunde", dict(k) if k else None)
print("geo_count", db.execute(text("SELECT count(*) FROM public.kunden_geo WHERE lat IS NOT NULL")).scalar())
sample = db.execute(
    text("SELECT kunden_nr, lat, lon, precision FROM public.kunden_geo WHERE lat IS NOT NULL LIMIT 3")
).mappings().all()
print("sample", [dict(r) for r in sample])
db.close()
