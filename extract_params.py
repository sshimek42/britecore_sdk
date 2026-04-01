import json
with open("britecore_api.json") as f:
    api = json.load(f)

domains = ["custom_ui", "dashboards", "data", "errors", "intacct", "nightly_jobs", "notifications", "printing", "return_premium", "search", "signatures", "uploads"]
for domain in domains:
    endpoints = [e for e in api if domain in e.get("path", "")]
    print(f"=== {domain} ===")
    for ep in endpoints:
        print(f"  {ep['path']}")
        props = ep.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema", {}).get("properties", {})
        required = ep.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema", {}).get("required", [])
        for p, v in props.items():
            req = " [required]" if p in required else ""
            print(f"    {p}: {v.get('type', '?')}{req}")
    print("")

