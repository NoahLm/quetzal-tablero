"""Tablero: a small dashboard of the numbers in Quetzal CRM.

It reads the CRM over the address Momoto gives it ($APP_QUETZAL_CRM_URL).
Until the CRM's owner allows it, that address does not answer and the page says so.
"""

import html
import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CRM = "Quetzal CRM"


def crm_json(path):
    """JSON from the CRM, or None while this app is still waiting for access."""
    base = os.environ.get("APP_QUETZAL_CRM_URL")
    if not base:
        return None
    try:
        with urllib.request.urlopen(base.rstrip("/") + path, timeout=3) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, ValueError):
        return None


def accounts_panel():
    stats = crm_json("/api/stats")
    if stats is None:
        return f'<p class="wait">Waiting for access to {CRM}.</p>'
    rows = "".join(
        f"<tr><td>{html.escape(str(s.get('ciudad', '')))}</td><td>{int(s.get('cuentas', 0))}</td></tr>"
        for s in stats
    )
    return f"<h2>Accounts by city</h2><table><tr><th>City</th><th>Accounts</th></tr>{rows}</table>"


STAGES = (("prospecto", "Lead"), ("propuesta", "Proposal"), ("ganado", "Won"), ("perdido", "Lost"))


def deals_panel():
    deals = crm_json("/api/deals")
    if deals is None:
        return ""
    totals = deals.get("totals_mxn") or {}
    rows = "".join(
        f"<tr><td>{label}</td><td>${float(totals.get(key, 0)):,.0f} MXN</td></tr>" for key, label in STAGES
    )
    return f"<h2>Deals by stage</h2><table><tr><th>Stage</th><th>Total</th></tr>{rows}</table>"


def top_accounts_panel():
    deals = crm_json("/api/deals")
    if deals is None:
        return ""
    totals = {}
    for d in deals.get("items") or []:
        name = str(d.get("account_name") or "")
        totals[name] = totals.get(name, 0.0) + float(d.get("amount_mxn") or 0)
    top = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:5]
    rows = "".join(f"<tr><td>{html.escape(name)}</td><td>${amount:,.0f} MXN</td></tr>" for name, amount in top)
    return f"<h2>Top accounts</h2><table><tr><th>Account</th><th>Deals</th></tr>{rows}</table>"


def page():
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tablero</title>
<style>
 body {{ font-family: system-ui, sans-serif; margin: 2rem auto; max-width: 48rem; padding: 0 1rem; color: #222; }}
 table {{ border-collapse: collapse; width: 100%; margin-bottom: 2rem; }}
 th, td {{ text-align: left; padding: .4rem .6rem; border-bottom: 1px solid #ddd; }}
 .wait {{ padding: 1rem; background: #fff6e0; border-radius: .5rem; }}
</style></head><body>
<h1>Tablero</h1>
<p>The numbers of {CRM}, at a glance.</p>
{accounts_panel()}
{deals_panel()}
{top_accounts_panel()}
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            body, ctype = b'{"ok": true}', "application/json"
        elif self.path in ("/", "/index.html"):
            body, ctype = page().encode("utf-8"), "text/html; charset=utf-8"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "8080"))), Handler).serve_forever()
