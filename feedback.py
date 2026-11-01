"""Small first-party feedback inbox; no email, IP address or user account stored."""
import secrets
import time
from urllib.parse import urlsplit

from flask import Blueprint, jsonify, request, session
import db

feedback = Blueprint('feedback', __name__)
KINDS = {'idea', 'bug', 'event'}
SCHEMA = '''CREATE TABLE IF NOT EXISTS feedback (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 created_at REAL NOT NULL,
 kind TEXT NOT NULL,
 message TEXT NOT NULL,
 event_id TEXT NOT NULL DEFAULT '',
 client_key TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'new'
);
CREATE INDEX IF NOT EXISTS feedback_created ON feedback(created_at);
'''


def init_feedback():
    with db.get_conn() as conn:
        conn.executescript(SCHEMA)


@feedback.get('/api/feedback/token')
def token():
    session.setdefault('feedback_key', secrets.token_hex(24))
    session.setdefault('feedback_csrf', secrets.token_urlsafe(32))
    response = jsonify(token=session['feedback_csrf'])
    response.headers['Cache-Control'] = 'no-store'
    return response


@feedback.post('/api/feedback')
def submit():
    # Cross-site forms and scripts must not be able to write to the inbox.
    origin = request.headers.get('Origin', '')
    if (origin and urlsplit(origin).netloc != request.host) or request.headers.get('Sec-Fetch-Site') == 'cross-site':
        return jsonify(error='Envoi refusé. Rechargez la page et réessayez.'), 403
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error='Le formulaire est incomplet.'), 400
    expected = session.get('feedback_csrf', '')
    supplied = payload.get('token')
    if not expected or not isinstance(supplied, str) or not secrets.compare_digest(expected, supplied):
        return jsonify(error='La session a expiré. Rechargez la page et réessayez.'), 403
    kind, message, event_id = (payload.get(k, '') for k in ('kind', 'message', 'event_id'))
    if not all(isinstance(v, str) for v in (kind, message, event_id)):
        return jsonify(error='Le formulaire est incomplet.'), 400
    message = message.strip()
    if kind not in KINDS or not 10 <= len(message) <= 2000 or len(event_id) > 100:
        return jsonify(error='Écrivez un message entre 10 et 2 000 caractères et choisissez un sujet.'), 400
    if kind == 'event' and not event_id:
        return jsonify(error='Ouvrez la fiche concernée pour signaler une erreur.'), 400
    now = time.time()
    with db.get_conn() as conn:
        conn.execute('BEGIN IMMEDIATE')
        recent = conn.execute('SELECT COUNT(*) FROM feedback WHERE created_at > ? AND client_key = ?',
                              (now-3600, session['feedback_key'])).fetchone()[0]
        total = conn.execute('SELECT COUNT(*) FROM feedback WHERE created_at > ?', (now-3600,)).fetchone()[0]
        if recent >= 5 or total >= 200:
            return jsonify(error='Trop de retours rapprochés. Réessayez dans une heure.'), 429
        conn.execute('INSERT INTO feedback(created_at,kind,message,event_id,client_key) VALUES(?,?,?,?,?)',
                     (now, kind, message, event_id, session['feedback_key']))
    return jsonify(ok=True), 201
