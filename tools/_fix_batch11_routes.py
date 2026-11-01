import runpy
from pathlib import Path

m = runpy.run_path("tools/apply_batch11_listen_migration.py")
BATCH11 = m["BATCH11"]
listen = Path("app/core/screen_definitions_listen.py")
text = listen.read_text(encoding="utf-8")

route_lines = []
syn_lines = []
for page, screen_id, route_path, spec in BATCH11:
    if f'"{screen_id}":' not in text.split("LISTEN_ROUTEN = {", 1)[1].split("LISTEN_SYNONYME", 1)[0]:
        route_lines.append(f'                "{screen_id}": "{route_path}"')
    if f'"{screen_id}":' not in text.split("LISTEN_SYNONYME = {", 1)[1]:
        syn_lines.append(f'                   "{screen_id}": [{spec["title"]!r}, {screen_id.split("/")[-1]!r}]')

if route_lines:
    text = text.replace(
        '"admin/audit-log-liste": "/admin/audit-log"}',
        '"admin/audit-log-liste": "/admin/audit-log",\n' + ",\n".join(route_lines) + "}",
        1,
    )
if syn_lines:
    text = text.replace(
        '"admin/audit-log-liste": [\'audit-log\', \'audit-log\']}',
        '"admin/audit-log-liste": [\'audit-log\', \'audit-log\'],\n' + ",\n".join(syn_lines) + "}",
        1,
    )

listen.write_text(text, encoding="utf-8")
print(f"added {len(route_lines)} routes, {len(syn_lines)} synonyms")
