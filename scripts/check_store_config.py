import sqlite3, json
conn = sqlite3.connect("data/prices.db")
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT id, name, url, fetch_method, config FROM stores").fetchall()
for r in rows:
    cfg = json.loads(r["config"]) if r["config"] else {}
    print(f"--- {r['name']} ---")
    print(f"fetch_method: {r['fetch_method']}")
    print(f"url: {r['url']}")
    print(json.dumps(cfg, indent=2, ensure_ascii=False)[:4000])
    print()
conn.close()
