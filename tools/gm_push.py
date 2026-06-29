#!/usr/bin/env python3
"""GM live-write tool for Dara Dara.

Writes per-key patches straight into the live Firestore doc (named DB 'kotor')
so GM/Claude edits merge concurrently with players, matching firebase-sync.js
v5's per-key 'f' map shape. A still-legacy ({data:blob}) doc is auto-migrated to
the v5 shape before the patch is applied.

Credentials: ~/.gmcreds (line1=email, line2=password) or env GM_EMAIL / GM_PW.
No secrets are stored in this file.

Usage:
  gm_push.py get   <charId>                 # dump the live per-key f-map
  gm_push.py patch <charId> <patch.json>    # {topKey: value, ...} -> writes f.<topKey> (field-level merge)
  gm_push.py delete <charId>                 # delete a doc (test cleanup)
  gm_push.py seed-legacy <charId> <char.json>   # TEST: write a raw whole-blob 'data' field
"""
import sys, os, json, time, urllib.request, urllib.error, urllib.parse

API_KEY  = "AIzaSyA2dj_J5d4OTMDEmeSTGin1s_DCRCV3kHg"   # public Firebase web apiKey (also in firebase-sync.js)
PROJECT  = "kotor-gurps"
DATABASE = "kotor"
FS = "https://firestore.googleapis.com/v1/projects/%s/databases/%s/documents" % (PROJECT, DATABASE)

def _creds():
    e = os.environ.get("GM_EMAIL"); p = os.environ.get("GM_PW")
    if e and p: return e, p
    path = os.path.expanduser("~/.gmcreds")
    if os.path.exists(path):
        lines = [l.rstrip("\n") for l in open(path)]
        if len(lines) >= 2 and lines[0] and lines[1]: return lines[0], lines[1]
    sys.exit("No credentials: set GM_EMAIL/GM_PW or write ~/.gmcreds (email line1, password line2).")

def _req(url, data=None, method="GET", headers=None):
    h = {"Content-Type": "application/json"}; h.update(headers or {})
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as ex:
        try: return ex.code, json.loads(ex.read().decode() or "{}")
        except Exception: return ex.code, {}

def sign_in():
    email, pw = _creds()
    url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=" + API_KEY
    st, d = _req(url, {"email": email, "password": pw, "returnSecureToken": True}, "POST")
    if st != 200 or "idToken" not in d:
        sys.exit("Sign-in failed (%s): %s" % (st, (d.get("error", {}) or {}).get("message", d)))
    return d["idToken"]

def _bearer(tok): return {"Authorization": "Bearer " + tok}

def get_doc(char_id, tok):
    st, d = _req("%s/characters/%s" % (FS, char_id), None, "GET", _bearer(tok))
    if st == 404: return None
    if st != 200: sys.exit("GET failed (%s): %s" % (st, d))
    return d

def _f_map(doc):
    if not doc or "fields" not in doc: return {}
    fields = doc["fields"].get("f", {}).get("mapValue", {}).get("fields", {})
    return {k: v.get("stringValue", "") for k, v in fields.items()}

def _now(): return time.strftime("%Y-%m-%dT%H:%M:%S.000000Z", time.gmtime())

def patch_keys(char_id, patch, tok):
    """patch = {topKey: value}. value may be a python object (will be JSON-stringified)
    or an already-serialised JSON string. Writes f.<topKey> for each, field-level merge."""
    f_fields, masks = {}, []
    for k, v in patch.items():
        s = v if isinstance(v, str) else json.dumps(v, separators=(",", ":"))
        f_fields[k] = {"stringValue": s}
        masks.append("f.%s" % k)
    body = {"fields": {
        "f": {"mapValue": {"fields": f_fields}},
        "writer":    {"stringValue": "claude-gm"},
        "char":      {"stringValue": char_id},
        "updatedAt": {"timestampValue": _now()},
    }}
    masks += ["writer", "char", "updatedAt"]
    qs = "&".join("updateMask.fieldPaths=" + urllib.parse.quote(m) for m in masks)
    st, d = _req("%s/characters/%s?%s" % (FS, char_id, qs), body, "PATCH", _bearer(tok))
    if st != 200: sys.exit("PATCH failed (%s): %s" % (st, d))
    return list(patch.keys())

def delete_doc(char_id, tok):
    st, _ = _req("%s/characters/%s" % (FS, char_id), None, "DELETE", _bearer(tok))
    return st

def seed_legacy(char_id, whole, tok):   # TEST helper: emulate a <=v4.1 whole-blob doc
    body = {"fields": {"data": {"stringValue": json.dumps(whole, separators=(",", ":"))},
                       "char": {"stringValue": char_id}, "updatedAt": {"timestampValue": _now()}}}
    qs = "updateMask.fieldPaths=data&updateMask.fieldPaths=char&updateMask.fieldPaths=updatedAt"
    st, _ = _req("%s/characters/%s?%s" % (FS, char_id, qs), body, "PATCH", _bearer(tok))
    return st

def main():
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    cmd, tok = a[0], sign_in()
    if cmd == "get":
        doc = get_doc(a[1], tok)
        if doc is None: print("(no doc)"); return
        fm = _f_map(doc)
        legacy = "data" in doc.get("fields", {}) and "f" not in doc.get("fields", {})
        print("keys:", sorted(fm.keys()), "(legacy data-blob)" if legacy else "")
        for k in sorted(fm.keys()):
            try: val = json.loads(fm[k])
            except Exception: val = fm[k]
            print("  %s = %s" % (k, json.dumps(val)[:200]))
    elif cmd == "patch":
        patch = json.load(open(a[2]))
        doc = get_doc(a[1], tok); fm = _f_map(doc)
        legacy = None
        if not fm and doc and "fields" in doc:
            dv = doc["fields"].get("data")
            if dv: legacy = dv.get("stringValue")
        if legacy and not fm:
            whole = json.loads(legacy); merged = dict(whole); merged.update(patch)
            patch_keys(a[1], merged, tok)
            print("migrated legacy doc -> f-map + patched (%d keys) on '%s'" % (len(merged), a[1]))
        else:
            patch_keys(a[1], patch, tok)
            print("patched %s on '%s'" % (list(patch.keys()), a[1]))
    elif cmd == "delete":
        print("delete:", delete_doc(a[1], tok))
    elif cmd == "seed-legacy":
        print("seed-legacy:", seed_legacy(a[1], json.load(open(a[2])), tok))
    else:
        sys.exit("unknown cmd: " + cmd)

if __name__ == "__main__":
    main()
