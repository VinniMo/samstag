"""Create and verify a consistent local SQLite backup; keep seven copies."""
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

root = Path('/var/lib/samstag')
folder = root / 'backups'
folder.mkdir(mode=0o750, exist_ok=True)
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
target = folder / f'samstag-{stamp}.sqlite3'
with sqlite3.connect(f'file:{root / "samstag.sqlite3"}?mode=ro', uri=True) as source:
    with sqlite3.connect(target) as copy:
        source.backup(copy)
        assert copy.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
for old in sorted(folder.glob('samstag-*.sqlite3'), reverse=True)[7:]:
    old.unlink()
print(f'Sauvegarde vérifiée : {target.name}')
