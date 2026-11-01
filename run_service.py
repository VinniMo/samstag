"""Supervise the web process and collector on one persistent local database.

Prepared entry point only: running this file does not change a hosting account.
An explicit absolute SAMSTAG_DB is required to avoid an accidental temporary DB.
"""
import argparse
import json
import logging
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time

log = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parent


def runtime_settings(environ=None):
    env = dict(os.environ if environ is None else environ)
    database = env.get('SAMSTAG_DB', '')
    if not database or not Path(database).is_absolute():
        raise ValueError('SAMSTAG_DB doit désigner un fichier par un chemin absolu sur le stockage persistant')
    if Path(database).is_dir():
        raise ValueError('SAMSTAG_DB doit désigner un fichier, pas un dossier')
    port = int(env.get('PORT', '5000'))
    host = env.get('HOST', '0.0.0.0')
    workers = int(env.get('WEB_WORKERS', '2'))
    interval = int(env.get('SCRAPE_INTERVAL', '3600'))
    grace = int(env.get('SERVICE_STOP_GRACE', '120'))
    if host not in {'0.0.0.0','127.0.0.1'} or not 1 <= port <= 65535 or not 1 <= workers <= 4 or interval < 60 or not 1 <= grace <= 600:
        raise ValueError('Port, nombre de processus, intervalle ou délai d’arrêt invalide')
    env.update(SAMSTAG_DB=str(Path(database).resolve()), FLASK_DEBUG='0',
               DEMO_ENABLED='0', COLLECTION_ON_VISIT='0', PYTHONUNBUFFERED='1')
    commands = {
        'web': [sys.executable, '-m', 'gunicorn', 'app:app', '--bind', f'{host}:{port}',
                '--workers', str(workers), '--timeout', '60'],
        'collection': [sys.executable, str(ROOT/'collection_worker.py'), '--interval', str(interval)],
    }
    return env, commands, grace


def stop_children(children, grace):
    # Signal whole process groups: Gunicorn owns its own child workers.
    for name, child in children.items():
        try:
            os.killpg(child.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    deadline = time.monotonic() + grace
    for name, child in children.items():
        try:
            child.wait(timeout=max(0, deadline-time.monotonic()))
        except subprocess.TimeoutExpired:
            log.warning('Arrêt forcé de %s après expiration du délai', name)
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            child.wait()
    # A failed leader may have left grandchildren behind in its group.
    for child in children.values():
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def supervise(commands, env, stop, grace=120):
    children = {}
    code = 0
    try:
        for name, command in commands.items():
            children[name] = subprocess.Popen(command, cwd=ROOT, env=env, start_new_session=True)
            log.info('Processus %s démarré', name)
        while not stop.wait(0.2):
            failed = [(name, p.returncode) for name, p in children.items() if p.poll() is not None]
            if failed:
                log.error('Processus arrêté inopinément : %s ; arrêt du service pour redémarrage supervisé', failed)
                code = 1
                break
    except (OSError, ValueError):
        log.exception('Impossible de démarrer les processus')
        code = 1
    finally:
        stop_children(children, grace)
    return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-config', action='store_true', help='Vérifier les réglages sans démarrer de service')
    args = parser.parse_args()
    try:
        env, commands, grace = runtime_settings()
    except (ValueError, TypeError) as exc:
        parser.error(str(exc))
    if args.check_config:
        # No credentials or complete environment dump in the output.
        print(json.dumps({'database':env['SAMSTAG_DB'], 'collection_interval_seconds':int(env.get('SCRAPE_INTERVAL', '3600')),
                          'collection_on_visit':False, 'demo':False, 'debug':False,
                          'web_workers':int(env.get('WEB_WORKERS', '2')), 'stop_grace_seconds':grace}))
        return 0
    os.environ.update(env)
    import db
    Path(env['SAMSTAG_DB']).parent.mkdir(parents=True, exist_ok=True)
    db.init_db()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    stop = threading.Event()
    def request_stop(signum, frame):
        log.info('Arrêt du site et de la collecte demandé')
        stop.set()
    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    return supervise(commands, env, stop, grace)


if __name__ == '__main__':
    raise SystemExit(main())
