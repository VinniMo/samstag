"""Run the real Flask app against a disposable copy of a public API snapshot.

Only the product clock is frozen. Collection, production storage and external
writes are disabled; the actual templates, assets, database readers and feedback
endpoints are exercised.
"""
import os
from pathlib import Path
import sys,json
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ.get('CULTURA_E2E_OUTPUT', str(ROOT/'validation/playwright-2026-10-19')))
OUT.mkdir(exist_ok=True)
DB=OUT/'parcours-test.sqlite3'
if DB.exists():DB.unlink()
os.environ.update(LAUSANNE_DB=str(DB),COLLECTION_ON_VISIT='0',DEMO_ENABLED='0',FLASK_DEBUG='0',CULTURA_SESSION_SECRET='local-e2e-only-never-use-in-production')
sys.path.insert(0,str(ROOT))
snapshot=json.loads((ROOT/'e2e/fixtures/public-snapshot.json').read_text())
fixed=datetime.fromisoformat(snapshot['checked_at'])
class ProductClock(datetime):
    @classmethod
    def now(cls,tz=None):
        return fixed.astimezone(tz) if tz else fixed.replace(tzinfo=None)
import agenda,collection_quality
agenda.datetime=ProductClock
collection_quality.datetime=ProductClock
from app import app
import db
with db.get_conn() as conn:
    for e in snapshot['events']['events']:
        conn.execute('INSERT INTO collection_items(id,payload,status,reason,evidence_urls) VALUES(?,?,?,?,?)',
                     (e['id'],json.dumps(e,ensure_ascii=False),'approved','qualified_source_complete_event',json.dumps(e.get('evidence_urls',[]))))
for source in snapshot['sources']['sources']:
    db.log_scrape('e2e_snapshot',source['url'],source['status'],source['events'],'Instantané public de test, aucune collecte distante')
print('E2E isolated public snapshot:',len(db.list_public_events()),'events',flush=True)
app.run(host='127.0.0.1',port=8768,debug=False,threaded=True)
