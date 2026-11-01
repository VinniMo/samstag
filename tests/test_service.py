import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

from run_service import runtime_settings, supervise


class ServiceTest(unittest.TestCase):
    def test_runtime_requires_explicit_storage_and_overrides_demo_and_visit_collection(self):
        for env in [{},{'LAUSANNE_DB':'relative.sqlite3'}]:
            with self.assertRaises(ValueError):
                runtime_settings(env)
        with tempfile.TemporaryDirectory() as tmp:
            env,commands,grace=runtime_settings({'LAUSANNE_DB':tmp+'/shared.sqlite3','DEMO_ENABLED':'1','FLASK_DEBUG':'1'})
            self.assertEqual([env[k] for k in ['DEMO_ENABLED','FLASK_DEBUG','COLLECTION_ON_VISIT']],['0','0','0'])
            self.assertEqual(set(commands),{'web','collection'})
            self.assertIn('--interval',commands['collection'])

    def test_visit_refresh_is_disabled_with_managed_worker(self):
        import app
        with patch.object(app,'config',COLLECTION_ON_VISIT=False),patch.object(app.db,'last_scrape_time') as read:
            app.maybe_refresh_from_scraper()
        read.assert_not_called()

    def test_child_failure_stops_the_sibling_process(self):
        with tempfile.TemporaryDirectory() as tmp:
            ready=Path(tmp)/'ready';stopped=Path(tmp)/'stopped'
            sibling=('import signal,time,sys; from pathlib import Path; '
                     f'signal.signal(signal.SIGTERM,lambda *a:(Path({str(stopped)!r}).write_text("stopped"),sys.exit(0))); '
                     f'Path({str(ready)!r}).write_text("ready"); time.sleep(20)')
            fail=('import time,sys; from pathlib import Path\n'
                  f'while not Path({str(ready)!r}).exists(): time.sleep(.01)\n'
                  'sys.exit(3)')
            with self.assertLogs('run_service',level='ERROR'):
                code=supervise({'sibling':[sys.executable,'-c',sibling], 'fails':[sys.executable,'-c',fail]},os.environ.copy(),threading.Event(),grace=2)
            self.assertEqual(code,1)
            self.assertEqual(stopped.read_text(),'stopped')

    def test_requested_stop_terminates_both_children(self):
        stop=threading.Event()
        with tempfile.TemporaryDirectory() as tmp:
            paths=[Path(tmp)/str(i) for i in range(2)]
            commands={str(i):[sys.executable,'-c',f'import time; from pathlib import Path; Path({str(p)!r}).write_text("ready"); time.sleep(20)'] for i,p in enumerate(paths)}
            def request_when_ready():
                import time
                deadline=time.monotonic()+3
                while not all(p.exists() for p in paths) and time.monotonic()<deadline:
                    time.sleep(.01)
                stop.set()
            thread=threading.Thread(target=request_when_ready)
            thread.start()
            code=supervise(commands,os.environ.copy(),stop,grace=2)
            thread.join()
            self.assertEqual(code,0)
            self.assertTrue(all(p.exists() for p in paths))

    def test_invalid_runtime_values_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            for field,value in [('PORT','0'),('SCRAPE_INTERVAL','0'),('WEB_WORKERS','0'),('SERVICE_STOP_GRACE','0')]:
                with self.assertRaises(ValueError):
                    runtime_settings({'LAUSANNE_DB':tmp+'/db.sqlite3',field:value})
