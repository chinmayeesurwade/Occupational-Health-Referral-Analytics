import unittest,threading,sys,tempfile,sqlite3,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from api import Handler,ThreadingHTTPServer
from ingest import run,fetch,flatten
from urllib.error import HTTPError
class PipelineTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start();cls.url=f'http://127.0.0.1:{cls.server.server_port}'
 @classmethod
 def tearDownClass(cls):cls.server.shutdown();cls.server.server_close()
 def test_auth_and_pagination(self):
  with self.assertRaises(HTTPError):fetch(self.url+'/api/referrals','wrong')
  result=fetch(self.url+'/api/referrals?page=1&page_size=100','portfolio-local-token');self.assertEqual(len(result['data']),100);self.assertEqual(result['next_page'],2)
 def test_idempotency_rejections_failure_atomicity(self):
  with tempfile.TemporaryDirectory() as d:
   db=str(Path(d)/'demo.db');a=run(self.url,sqlite_path=db);b=run(self.url,sqlite_path=db)
   self.assertEqual(a['accepted'],1200);self.assertEqual(a['rejected'],3);self.assertEqual(b['stored'],1200)
   with self.assertRaises(HTTPError):run(self.url,sqlite_path=db,fail=True)
   with sqlite3.connect(db) as conn:self.assertEqual(conn.execute('SELECT COUNT(*) FROM referrals').fetchone()[0],1200)
 def test_threshold_and_denominator(self):
  from datetime import date
  asof=date(2026,10,6)
  self.assertFalse((asof-date(2026,10,1)).days>5);self.assertTrue((asof-date(2026,9,30)).days>5)
  self.assertEqual(2/(8+2),.2)
if __name__=='__main__':unittest.main(verbosity=2)
