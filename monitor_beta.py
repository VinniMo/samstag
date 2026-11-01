"""Bounded 24-hour beta observation; records aggregates, never feedback content."""
import argparse
import datetime
import json
from pathlib import Path
import time
import urllib.request


def sample():
    result = {'checked_at': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        with urllib.request.urlopen('http://127.0.0.1:8011/api/health',timeout=30) as response:
            data=json.load(response)
        states=data['collection']['states']
        result.update(web_ok=data.get('status')=='ok',public_events=data['public_events'],
                      scrape_age_seconds=round(time.time()-data['last_scrape']),states=states,
                      collection_attention=states.get('stale',0)+states.get('error',0)+states.get('never_collected',0))
    except Exception as exc:
        result.update(web_ok=False,error=type(exc).__name__)
    backups=sorted(Path('/var/lib/cultura/backups').glob('cultura-*.sqlite3'), key=lambda p: p.stat().st_mtime)
    result['latest_backup']=backups[-1].name if backups else None
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--duration',type=int,default=86400)
    parser.add_argument('--interval',type=int,default=900)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    if args.duration<0 or args.interval<1:parser.error('Invalid duration or interval')
    output=Path(args.output)
    start=time.monotonic()
    samples=[]
    while True:
        item=sample(); samples.append(item)
        with output.open('a') as stream:stream.write(json.dumps(item)+'\n')
        elapsed=time.monotonic()-start
        if elapsed>=args.duration:break
        time.sleep(min(args.interval,args.duration-elapsed))
    summary=dict(elapsed_seconds=round(elapsed),requested_seconds=args.duration,samples=len(samples),
                 web_failures=sum(not s['web_ok'] for s in samples),
                 collection_alert_samples=sum(s.get('collection_attention',0)>0 for s in samples),
                 completed_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    output.with_suffix('.summary.json').write_text(json.dumps(summary,indent=2))


if __name__=='__main__':main()
