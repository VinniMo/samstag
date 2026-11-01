"""Collection health is distinct from whether the web process responds."""
import time
from collections import Counter

import db
from source_registry import active_sources


def health(now=None):
    now = time.time() if now is None else now
    latest = {s['url']: s for s in db.source_status()}
    sources = active_sources()
    states = Counter()
    attention = []
    for source in sources:
        row = latest.get(source['canal'])
        if row is None:
            state = 'never_collected'
        elif now-row['timestamp'] > 86400:
            state = 'stale'
        else:
            state = row['status']
        states[state] += 1
        if state not in {'ok','empty'}:
            attention.append({'source_id':source['id'], 'name':source['nom'], 'status':state,
                              'automatic':source['auto_publish']})
    return {'status': 'degraded' if attention else 'ok',
            'sources': len(sources), 'states': dict(states), 'attention': attention}
