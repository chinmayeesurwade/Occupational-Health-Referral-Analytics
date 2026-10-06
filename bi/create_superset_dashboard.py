"""Create native Superset database, dataset, charts and dashboard through REST APIs.
Run once after docker compose --profile bi up -d. UI verification remains required.
"""
import json,os
from urllib.request import Request,build_opener,HTTPCookieProcessor
from http.cookiejar import CookieJar
base=os.getenv('SUPERSET_URL','http://localhost:8088');opener=build_opener(HTTPCookieProcessor(CookieJar()));token=None;csrf=None
def call(path,payload=None,method=None):
 headers={'Content-Type':'application/json','Referer':base}
 if token:headers['Authorization']='Bearer '+token
 if csrf:headers['X-CSRFToken']=csrf
 req=Request(base+path,data=json.dumps(payload).encode() if payload is not None else None,headers=headers,method=method)
 with opener.open(req,timeout=60) as r:return json.load(r)
token=call('/api/v1/security/login',{'username':'admin','password':os.getenv('SUPERSET_PASSWORD','portfolio-local-only'),'provider':'db','refresh':True})['access_token']
csrf=call('/api/v1/security/csrf_token/')['result']
db=call('/api/v1/database/',{'database_name':'Occupational Health Portfolio','sqlalchemy_uri':'postgresql+psycopg2://portfolio:portfolio-local-only@postgres:5432/occupational_health','expose_in_sqllab':True})['id']
ds=call('/api/v1/dataset/',{'database':db,'schema':'public','table_name':'reporting_referrals'})['id']
charts=[]
for title,expression,fmt in [('Referrals','COUNT(*)',',d'),('Open backlog','SUM(backlog_flag)',',d'),('Overdue reports','SUM(overdue_report_flag)',',d'),('No-show rate','SUM(no_show_flag)::numeric / NULLIF(SUM(attended_or_missed_flag),0)','.1%'),('Average wait days','AVG(appointment_wait_days)','.1f')]:
 metric={'expressionType':'SQL','sqlExpression':expression,'label':title}
 params={'viz_type':'big_number_total','datasource':f'{ds}__table','metric':metric,'subheader':'Synthetic snapshot: 6 October 2026','y_axis_format':fmt,'time_range':'No filter'}
 charts.append(call('/api/v1/chart/',{'slice_name':title,'viz_type':'big_number_total','datasource_id':ds,'datasource_type':'table','params':json.dumps(params)})['id'])
position={'DASHBOARD_VERSION_KEY':'v2','ROOT_ID':{'id':'ROOT_ID','type':'ROOT','children':['GRID_ID']},'GRID_ID':{'id':'GRID_ID','type':'GRID','children':['ROW-1','ROW-2'],'parents':['ROOT_ID']}}
for n,subset in enumerate([charts[:3],charts[3:]],1):
 row=f'ROW-{n}';position[row]={'id':row,'type':'ROW','children':[f'CHART-{c}' for c in subset],'parents':['ROOT_ID','GRID_ID'],'meta':{'background':'BACKGROUND_TRANSPARENT'}}
 for c in subset:position[f'CHART-{c}']={'id':f'CHART-{c}','type':'CHART','children':[],'parents':['ROOT_ID','GRID_ID',row],'meta':{'chartId':c,'width':4 if n==1 else 6,'height':40}}
dash=call('/api/v1/dashboard/',{'dashboard_title':'Occupational Health Operations','published':False,'position_json':json.dumps(position),'json_metadata':json.dumps({'chart_configuration':{},'global_chart_configuration':{'scope':{'rootPath':['ROOT_ID'],'excluded':[]}}})})['id']
for c in charts:call(f'/api/v1/chart/{c}',{'dashboards':[dash]},method='PUT')
print(f'Created draft dashboard: {base}/superset/dashboard/{dash}/. Verify charts and add employer/service/date filters in UI. Run this script once; rerunning creates another set of assets.')
