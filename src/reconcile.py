"""Produce independent SQLite/Python control totals for BI reconciliation."""
import sqlite3,json,csv
from pathlib import Path
from datetime import date
from statistics import mean
ROOT=Path(__file__).resolve().parents[1];AS_OF=date(2026,10,6)
conn=sqlite3.connect(ROOT/'data/demo.db');conn.row_factory=sqlite3.Row;rows=[dict(r) for r in conn.execute('SELECT * FROM referrals')];conn.close()
def metrics(rows):
 waits=[(date.fromisoformat(r['completed_date'])-date.fromisoformat(r['received_date'])).days for r in rows if r['completed_date']]
 turns=[(date.fromisoformat(r['issued_date'])-date.fromisoformat(r['completed_date'])).days for r in rows if r['issued_date']]
 no=sum(r['appointment_status']=='no_show' for r in rows);den=sum(r['appointment_status'] in ['completed','no_show'] for r in rows)
 return {'referrals':len(rows),'backlog':sum(r['appointment_status']!='cancelled' and not r['issued_date'] for r in rows),'overdue':sum(bool(r['completed_date']) and not r['issued_date'] and (AS_OF-date.fromisoformat(r['completed_date'])).days>5 for r in rows),'no_show_rate':no/den if den else None,'mean_wait':mean(waits) if waits else None,'mean_report_turnaround':mean(turns) if turns else None}
out={'as_of':str(AS_OF),'all':metrics(rows),'C01':metrics([r for r in rows if r['employer_id']=='C01']),'note':'SQLite/Python control totals executed; compare native PostgreSQL and BI outputs after local setup.'};(ROOT/'evidence/reconciliation.json').write_text(json.dumps(out,indent=2))
with (ROOT/'data/validated_referrals.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
print(json.dumps(out,indent=2))
