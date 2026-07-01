#!/usr/bin/env python3
"""Read-only backup of live Firestore character docs -> backups/<id>.json.

Lists the `characters` collection on the named `kotor` DB, reconstructs each
character from the v5 per-key `f`-map (or a legacy `data` blob), and writes a
pretty JSON per character. NEVER writes to Firestore — this cannot conflict
with players' live edits. Git history provides the timestamped versioning.

Credentials: ~/.gmcreds (line1=email, line2=password) or env GM_EMAIL / GM_PW.
Usage: python3 tools/backup_live.py [outdir]   (default outdir = backups/)
"""
import os, sys, json, urllib.request, urllib.error
API_KEY  = "AIzaSyA2dj_J5d4OTMDEmeSTGin1s_DCRCV3kHg"   # public web apiKey (also in firebase-sync.js / gm_push.py)
PROJECT, DATABASE = "kotor-gurps", "kotor"
FS = "https://firestore.googleapis.com/v1/projects/%s/databases/%s/documents" % (PROJECT, DATABASE)

def _creds():
    e, p = os.environ.get("GM_EMAIL"), os.environ.get("GM_PW")
    if e and p: return e, p
    path = os.path.expanduser("~/.gmcreds")
    if os.path.exists(path):
        ls = [x.rstrip("\n") for x in open(path)]
        if len(ls) >= 2 and ls[0] and ls[1]: return ls[0], ls[1]
    sys.exit("No credentials: set GM_EMAIL/GM_PW or write ~/.gmcreds (email line1, password line2).")

def _req(url, data=None, method="GET", headers=None):
    hdr = {"Content-Type": "application/json"}; hdr.update(headers or {})
    body = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(url, data=body, method=method, headers=hdr)
    try:
        with urllib.request.urlopen(r) as resp: return resp.status, json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")

def sign_in():
    e, p = _creds()
    st, d = _req("https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=" + API_KEY,
                 {"email": e, "password": p, "returnSecureToken": True}, "POST")
    if st != 200: sys.exit("AUTH FAILED (%s): %s" % (st, json.dumps(d)[:200]))
    return d["idToken"]

def _unwrap(v):
    if "stringValue"    in v: return v["stringValue"]
    if "integerValue"   in v: return int(v["integerValue"])
    if "doubleValue"    in v: return v["doubleValue"]
    if "booleanValue"   in v: return v["booleanValue"]
    if "timestampValue" in v: return v["timestampValue"]
    if "nullValue"      in v: return None
    if "mapValue"       in v: return {k: _unwrap(x) for k, x in v["mapValue"].get("fields", {}).items()}
    if "arrayValue"     in v: return [_unwrap(x) for x in v["arrayValue"].get("values", [])]
    return v

def reconstruct(doc):
    fields = doc.get("fields", {})
    if "f" in fields:                                   # v5 per-key f-map
        fmap = _unwrap(fields["f"]); C = {}
        for k, raw in fmap.items():
            try: C[k] = json.loads(raw)
            except Exception: C[k] = raw
        return C
    if "data" in fields:                                # legacy whole-blob
        return json.loads(fields["data"]["stringValue"])
    return {}

# Firestore security rules permit per-doc `get` but not collection `list`, so we
# fetch known ids. Ids match the sheet's ?char= slug (= characters/*.json names).
# Extra ids can be appended as CLI args after the output dir.
CHAR_IDS = ["truman", "chatni", "sekan", "default"]

def get_doc(cid, tok):
    st, d = _req("%s/characters/%s" % (FS, cid), None, "GET", {"Authorization": "Bearer " + tok})
    if st == 404: return None
    if st != 200: sys.exit("GET %s failed (%s): %s" % (cid, st, json.dumps(d)[:200]))
    return d

def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "backups"
    ids = CHAR_IDS + [a for a in sys.argv[2:] if a not in CHAR_IDS]
    os.makedirs(outdir, exist_ok=True)
    tok = sign_in()
    n = 0
    for cid in ids:
        doc = get_doc(cid, tok)
        if doc is None:
            print("  %-12s (no doc)" % cid); continue
        C = reconstruct(doc)
        json.dump(C, open(os.path.join(outdir, cid + ".json"), "w"), indent=1, ensure_ascii=False, sort_keys=True)
        upd = _unwrap(doc["fields"]["updatedAt"]) if "updatedAt" in doc.get("fields", {}) else "?"
        print("  %-12s keys=%-3d skills=%-3d powers=%-3d updatedAt=%s"
              % (cid, len(C),
                 len([x for x in C.get("skills", []) if isinstance(x, dict) and x.get("name")]),
                 len((C.get("force", {}) or {}).get("powers", [])), upd))
        n += 1
    print("backed up %d character doc(s) -> %s/" % (n, outdir))

if __name__ == "__main__":
    main()
