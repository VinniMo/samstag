"""Read the private feedback inbox over the administrator's existing SSH access."""
import argparse
import json
import sqlite3
import datetime
from config import config

parser=argparse.ArgumentParser()
parser.add_argument('--limit',type=int,default=50)
args=parser.parse_args()
conn=sqlite3.connect('file:'+config.DB_PATH+'?mode=ro',uri=True)
conn.row_factory=sqlite3.Row
rows=conn.execute('SELECT id,created_at,kind,event_id,message,status FROM feedback ORDER BY id DESC LIMIT ?',
                  (max(1,min(args.limit,200)),)).fetchall()
print(json.dumps([dict(row) for row in rows],ensure_ascii=False,indent=2))
