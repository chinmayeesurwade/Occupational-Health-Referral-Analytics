"""REST JSON -> validated records -> transactionally upserted SQL store.
SQLite provides a runnable lightweight check. PostgreSQL is the BI target.
"""
import argparse,json,logging,os,sqlite3,time
from datetime import date,datetime
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
ROOT=Path(__file__).resolve().parents[1];AS_OF=date(2026,10,6)
FIELDS=['referral_id','employee_id','employer_id','employer_name','service','received_date','appointment_status','completed_date','issued_date','updated_at']
def flatten(r):
 x=dict(zip(FIELDS,[r.get('referral_id'),r.get('employee',{}).get('id'),r.get('employer',{}).get('id'),r.get('employer',{}).get('name'),r.get('service'),r.get('received_date'),r.get('appointment',{}).get('status'),r.get('appointment',{}).get('completed_date'),r.get('report',{}).get('issued_date'),r.get('updated_at')]))
 for k in ['referral_id','employee_id','employer_id','employer_name','service','received_date','updated_at']:
  if not x[k]:raise ValueError('missing '+k)
 received=date.fromisoformat(x['received_date']);completed=date.fromisoformat(x['completed_date']) if x['completed_date'] else None;issued=date.fromisoformat(x['issued_date']) if x['issued_date'] else None
 datetime.fromisoformat(x['updated_at'].replace('Z','+00:00'))
 if received>AS_OF:raise ValueError('future referral')
 if x['appointment_status'] not in ['completed','no_show','scheduled','cancelled']:raise ValueError('invalid status')
 if (x['appointment_status']=='completed') != bool(completed):raise ValueError('status/date mismatch')
 if completed and (completed<received or completed>AS_OF):raise ValueError('invalid completion sequence')
 if issued and (not completed or issued<completed or issued>AS_OF):raise ValueError('invalid report sequence')
 return x
def fetch(url,token,fail=False,attempts=3):
 for attempt in range(attempts):
  try:
   headers={'Authorization':'Bearer '+token}
   if fail:headers['X-Demo-Fail']='true'
   with urlopen(Request(url,headers=headers),timeout=10) as response:return json.load(response)
  except HTTPError as e:
   if e.code not in [429,500,502,503,504]:raise
   logging.warning('HTTP %s attempt %s',e.code,attempt+1)
   if attempt==attempts-1:raise
  except URLError:
   logging.warning('Network failure attempt %s',attempt+1)
   if attempt==attempts-1:raise
  time.sleep(.1*2**attempt)
def run(base,sqlite_path=None,dsn=None,fail=False):
 logging.basicConfig(level=logging.INFO,format='%(levelname)s %(message)s')
 page=1;valid=[];rejected=[];seen=set()
 # Complete snapshot fetched and validated before transaction: failure cannot partially replace data.
 while page:
  result=fetch(f'{base}/api/referrals?page={page}&page_size=100',os.getenv('API_TOKEN','portfolio-local-token'),fail)
  for row in result['data']:
   try:
    x=flatten(row)
    if x['referral_id'] in seen:raise ValueError('duplicate source key')
    seen.add(x['referral_id']);valid.append(x)
   except (ValueError,TypeError) as e:rejected.append({'referral_id':row.get('referral_id'),'reason':str(e)})
  page=result['next_page']
 pg=bool(dsn)
 if pg:
  import psycopg
  conn=psycopg.connect(dsn);schema=(ROOT/'sql/schema.sql').read_text();ph='%s'
 else:conn=sqlite3.connect(sqlite_path);schema=(ROOT/'sql/schema_sqlite.sql').read_text();ph='?'
 try:
  cur=conn.cursor()
  if pg:cur.execute(schema)
  else:conn.executescript(schema)
  cols=','.join(FIELDS);updates=','.join(f'{k}=excluded.{k}' for k in FIELDS[1:])
  sql=f'INSERT INTO referrals ({cols}) VALUES ({",".join([ph]*len(FIELDS))}) ON CONFLICT(referral_id) DO UPDATE SET {updates} WHERE excluded.updated_at >= referrals.updated_at'
  cur.executemany(sql,[tuple(x[k] for k in FIELDS) for x in valid]);conn.commit()
  if pg:cur.execute((ROOT/'sql/views.sql').read_text());conn.commit()
  cur.execute('SELECT COUNT(*) FROM referrals');stored=cur.fetchone()[0]
 except Exception:conn.rollback();raise
 finally:conn.close()
 summary={'as_of':str(AS_OF),'source_records':len(valid)+len(rejected),'accepted':len(valid),'rejected':len(rejected),'stored':stored,'backend':'postgresql' if pg else 'sqlite','rejects':rejected}
 (ROOT/'evidence/ingestion_result.json').write_text(json.dumps(summary,indent=2));logging.info('Accepted %s; rejected %s; stored %s',len(valid),len(rejected),stored);return summary
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--base-url',default=os.getenv('API_URL','http://localhost:8000'));a.add_argument('--sqlite',default=None);a.add_argument('--fail',action='store_true');args=a.parse_args()
 run(args.base_url,sqlite_path=args.sqlite or str(ROOT/'data/demo.db'),dsn=None if args.sqlite else os.getenv('DATABASE_URL'),fail=args.fail)
