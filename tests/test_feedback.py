"""Feedback must persist, reject cross-site writes, and bound user input."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import app
import db

class FeedbackTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.patch = patch.object(db, 'DB_PATH', str(Path(self.tmp.name)/'feedback.sqlite3'))
        self.patch.start()
        self.web = app.create_app()
        self.web.config['TESTING'] = True
        self.client = self.web.test_client()
        self.token = self.client.get('/api/feedback/token').json['token']

    def tearDown(self):
        self.patch.stop()
        self.tmp.cleanup()

    def post(self, **overrides):
        payload = dict(kind='idea', message='Un retour de test suffisamment précis.', event_id='', token=self.token)
        payload.update(overrides)
        return self.client.post('/api/feedback', json=payload, headers={'Origin':'http://localhost'})

    def test_persists_feedback_and_event_context(self):
        self.assertEqual(self.post(kind='event', event_id='a1b2').status_code, 201)
        with db.get_conn() as conn:
            row = conn.execute('SELECT kind,event_id,message FROM feedback').fetchone()
        self.assertEqual((row['kind'],row['event_id']), ('event','a1b2'))
        self.assertIn('précis', row['message'])

    def test_token_and_session_required(self):
        self.assertEqual(self.post(token='wrong').status_code, 403)
        self.assertEqual(self.web.test_client().post('/api/feedback',json={'token':self.token}).status_code, 403)

    def test_cross_site_rejected_and_no_cors_for_feedback(self):
        res = self.client.post('/api/feedback',json=dict(token=self.token),headers={'Origin':'https://other.test'})
        self.assertEqual(res.status_code,403)
        token = self.client.get('/api/feedback/token',headers={'Origin':'https://other.test'})
        self.assertNotIn('Access-Control-Allow-Origin',token.headers)
        self.assertEqual(token.headers['Cache-Control'],'no-store')

    def test_invalid_inputs_do_not_write(self):
        for override in [dict(message='court'),dict(message='x'*2001),dict(kind='invalid'),dict(message=[]),dict(kind='event'),dict(event_id='x'*101)]:
            with self.subTest(override=override): self.assertEqual(self.post(**override).status_code,400)
        with db.get_conn() as conn:self.assertEqual(conn.execute('SELECT COUNT(*) FROM feedback').fetchone()[0],0)

    def test_rate_limit_is_persistent(self):
        for _ in range(5):self.assertEqual(self.post().status_code,201)
        self.assertEqual(self.post().status_code,429)

    def test_oversized_body_is_refused(self):
        self.assertEqual(self.post(message='x'*20000).status_code,413)
