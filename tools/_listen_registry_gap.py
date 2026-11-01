import re
from pathlib import Path

text = Path("app/core/screen_definitions_listen.py").read_text(encoding="utf-8")
ids = set(re.findall(r'screen_id="([^"]+)"', text))
m = re.search(r"LISTEN_SCREEN_BUILDERS = \{", text)
start = m.end() if m else 0
depth = 1
i = start
while i < len(text) and depth:
    if text[i] == "{":
        depth += 1
    elif text[i] == "}":
        depth -= 1
    i += 1
body = text[start : i - 1]
registered = set(re.findall(r'"([^"]+)":', body))
unreg = sorted(ids - registered)
print("total", len(ids), "registered", len(registered), "unregistered", len(unreg))
for x in unreg:
    print(x)
