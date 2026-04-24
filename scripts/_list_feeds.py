from app.api.v1.endpoints.rations_optimization import _get_feeds

feeds = list(_get_feeds())
print(f"total: {len(feeds)}")
for f in feeds:
    name = f.get("name", "?")
    fid = f.get("id", "?")
    group = f.get("group", "-")
    forage = f.get("forage", False)
    me = f.get("me", 0.0)
    st = f.get("st", 0.0)
    ndf = f.get("ndf", 0.0)
    print(f"{fid:<35s} | forage={forage!s:<5s} | group={group:<30s} | me={me:5.2f} | st={st:5.0f} | ndf={ndf:5.0f} | {name}")
