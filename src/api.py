"""Local paginated REST API with bearer auth and repeatable failure injection."""
import json,os
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse,parse_qs
DATA=Path(__file__).resolve().parents[1]/'data/api_records.json'
class Handler(BaseHTTPRequestHandler):
 def reply(self,status,obj):
  body=json.dumps(obj).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 def do_GET(self):
  u=urlparse(self.path)
  if u.path=='/health':return self.reply(200,{'status':'ok'})
  if u.path!='/api/referrals':return self.reply(404,{'error':'not found'})
  if self.headers.get('Authorization')!='Bearer '+os.getenv('API_TOKEN','portfolio-local-token'):return self.reply(401,{'error':'invalid bearer token'})
  if self.headers.get('X-Demo-Fail')=='true':return self.reply(503,{'error':'simulated transient outage'})
  try:
   q=parse_qs(u.query);page=int(q.get('page',['1'])[0]);size=int(q.get('page_size',['100'])[0]);assert page>=1 and 1<=size<=200
  except (ValueError,AssertionError):return self.reply(400,{'error':'invalid pagination'})
  rows=json.loads(DATA.read_text());subset=rows[(page-1)*size:page*size];self.reply(200,{'data':subset,'page':page,'total':len(rows),'next_page':page+1 if page*size<len(rows) else None})
 def log_message(self,*args):pass
if __name__=='__main__':ThreadingHTTPServer(('0.0.0.0',8000),Handler).serve_forever()
