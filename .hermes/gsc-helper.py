#!/usr/bin/env python3
"""GSC helper: query Google Search Console for tkvibes.in"""
import json, urllib.request, time, os

CRED_FILE = r"C:\Users\takcl\Desktop\tkvibes-agency\.hermes\gsc-credentials.json"
TOKEN_FILE = r"C:\Users\takcl\Desktop\tkvibes-agency\.hermes\gsc-token.json"
SITE = "sc-domain:tkvibes.in"

def load_tokens():
    with open(TOKEN_FILE) as f:
        return json.load(f)

def save_tokens(tokens):
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)

def refresh_access():
    with open(CRED_FILE) as f:
        creds = json.load(f)["web"]
    tokens = load_tokens()
    data = urllib.parse.urlencode({
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
        "refresh_token": tokens["refresh_token"],
        "grant_type": "refresh_token"
    }).encode()
    req = urllib.request.Request(creds["token_uri"], data=data)
    resp = json.loads(urllib.request.urlopen(req).read())
    tokens["access_token"] = resp["access_token"]
    tokens["expires_in"] = resp.get("expires_in", 3599)
    save_tokens(tokens)
    return tokens["access_token"]

def gsc_query(endpoint, body=None, method="GET"):
    tokens = load_tokens()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    url = f"https://www.googleapis.com/webmasters/v3/{endpoint}"
    
    if body:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
    
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 401:
            # Token expired, refresh and retry
            headers["Authorization"] = f"Bearer {refresh_access()}"
            if body:
                req = urllib.request.Request(url, data=data, headers=headers, method=method)
            else:
                req = urllib.request.Request(url, headers=headers, method=method)
            resp = urllib.request.urlopen(req)
            return json.loads(resp.read())
        raise

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "sites"
    
    if cmd == "sites":
        print(json.dumps(gsc_query("sites"), indent=2))
    elif cmd == "analytics":
        body = {
            "startDate": sys.argv[2] if len(sys.argv) > 2 else "2026-07-01",
            "endDate": sys.argv[3] if len(sys.argv) > 3 else "2026-07-31",
            "dimensions": ["query"],
            "rowLimit": 10
        }
        print(json.dumps(gsc_query(f"sites/{urllib.parse.quote(SITE,'')}/searchAnalytics/query", body, "POST"), indent=2))
    elif cmd == "inspect":
        url = sys.argv[2]
        body = {"inspectionUrl": url, "siteUrl": SITE}
        print(json.dumps(gsc_query(f"sites/{urllib.parse.quote(SITE,'')}/urlInspection/index", body, method="POST"), indent=2))
    else:
        print(f"Commands: sites, analytics [start end], inspect <url>")