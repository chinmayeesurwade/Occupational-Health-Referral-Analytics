"""Deterministic synthetic referrals. No patient or clinician personal data."""
import json,random
from datetime import date,timedelta
from pathlib import Path
random.seed(42)
AS_OF=date(2026,10,6)
rows=[]
for i in range(1,1201):
 received=AS_OF-timedelta(days=random.randint(0,364)); completed=received+timedelta(days=random.randint(1,21)); issued=completed+timedelta(days=random.randint(0,12))
 state=random.choices(['completed','no_show','scheduled','cancelled'],[65,12,18,5])[0]
 if completed>AS_OF:state='scheduled'
 if state!='completed':completed=None;issued=None
 elif issued>AS_OF or i%9==0:issued=None
 rows.append({'referral_id':f'R{i:05}','employee':{'id':f'E{i%300:04}'},'employer':{'id':f'C{i%4+1:02}','name':['Atlas Manufacturing','Harbor Logistics','Cedar Services','Northstar Engineering'][i%4]},'service':random.choice(['Health surveillance','Return-to-work review','Management referral']),'received_date':str(received),'appointment':{'status':state,'completed_date':str(completed) if completed else None},'report':{'issued_date':str(issued) if issued else None},'updated_at':'2026-10-06T08:00:00Z'})
# Deliberate quality failures: must be quarantined, not silently included.
rows.extend([dict(rows[0],referral_id='BAD01',received_date='2026-99-01'),dict(rows[1],referral_id='BAD02',employer={'id':'','name':'Missing'}),dict(rows[2],referral_id='BAD03',appointment={'status':'completed','completed_date':'2024-01-01'})])
p=Path(__file__).resolve().parents[1]/'data';p.mkdir(exist_ok=True);(p/'api_records.json').write_text(json.dumps(rows,indent=2));print(f'{len(rows)} synthetic API records')
