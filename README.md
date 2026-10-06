# Occupational Health Referral Analytics
Prepared for Chinmayee Surwade 
## Start here
This project demonstrates SQL, Python, REST APIs, nested JSON, reporting requirements, data-quality handling and BI delivery. PostgreSQL/DBeaver and Superset setup are provided; Power BI M/DAX and a native authoring guide are included. It is not professional healthcare employment or a production system.

## Fast route: Python only, no installation
1. Open a terminal in this folder. Python 3.10+ is required.
2. Run `python src/api.py` and keep that terminal open.
3. In another terminal run `python src/ingest.py --sqlite data/demo.db`.
4. Run `python src/reconcile.py` to produce SQL/Python control totals and a validated CSV.
5. Run `python -m unittest discover -s tests -v` to repeat the executed pipeline checks.
6. Read docs/Project_Case_Study.docx, docs/BI_Setup.md and docs/UAT.csv.

## Full JD stack: Docker Desktop + Power BI Desktop + DBeaver
On Windows use Docker Desktop with Linux containers. Downloading images requires internet and disk space. Keep services local: credentials here are public demo values for synthetic data.
1. `docker compose up -d postgres api`
2. `docker compose run --rm etl`
3. Inspect PostgreSQL through DBeaver and run sql/validation.sql.
4. `docker compose --profile bi up -d superset`
5. When Superset login responds, run `python bi/create_superset_dashboard.py` once. Inspect the created native dashboard and add filters/charts using docs/BI_Setup.md.
6. Create the native Power BI report with bi/Power_Query.m and bi/Measures.dax, following docs/BI_Setup.md.
7. Reconcile SQL and both native BI tools against evidence/reconciliation.json. Capture screenshots and complete UAT.csv.
8. Stop services with `docker compose --profile bi down`. Do not use `down -v` unless intentionally deleting local demo databases.

## Results and validation boundary
Executed API/SQLite checks: authentication, pagination, rejection of three bad records, duplicate-free reruns and failed-request atomicity. Snapshot: 6 October 2026. 1,200 valid referrals; 486 backlog; 90 overdue reports; no-show rate 14.55%; mean wait 10.81 days; mean issued-report turnaround 5.92 days.
PostgreSQL execution, Docker startup, Superset API/dashboard rendering and Power BI refresh/rendering are NOT verified here because those runtimes are unavailable. No PBIX is supplied. The chart PNG is a Python-generated preview, not evidence of Superset or Power BI execution.

## Important model decisions
Grain: one referral, with a single current appointment outcome and report. A rescheduling/event-history model is a next extension. Data covers 7 October 2025 through 6 October 2026. Backend snapshot is fixed, not today's date. Backlog includes non-cancelled referrals without issued reports, including no-shows awaiting resolution. Date filters select referral-received cohorts; this is not historical backlog reconstruction. Overdue means completed, not reported, strictly more than 5 calendar days old. No-show denominator excludes scheduled and cancelled appointments. Issued-report averages omit pending reports: interpret with overdue counts.
Ingestion uses a full snapshot and monotonic updated_at upserts. It does not delete records missing from a later source extract. Rejects and source duplicate keys are recorded; accepted rows commit only after all pages arrive. It is not incremental watermark ingestion, multi-tenant access control or a scheduler.

## Skills evidence
See docs/Skill_Mapping.csv. Jira_Import.csv is a ready-to-import backlog, not an actual Jira board. Stakeholder notes are simulated. Record your own walkthrough and UAT after running the stack.

## Sources
Official references checked 6 October 2026:
- https://superset.apache.org/docs/installation/docker-compose/
- https://superset.apache.org/developer-docs/api/dashboards/
- https://superset.apache.org/user-docs/databases/supported/postgresql/
- https://learn.microsoft.com/en-us/powerquery-m/postgresql-database
- https://www.postgresql.org/docs/current/tutorial-window.html
- https://www.hse.gov.uk/health-surveillance/record-keeping.htm (domain illustration; no jurisdiction-specific compliance claim)

