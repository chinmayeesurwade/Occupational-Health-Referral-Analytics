# BI and DBeaver setup
## PostgreSQL and DBeaver
Run `docker compose up -d postgres api`, then `docker compose run --rm etl`.
Connect DBeaver to localhost, port 5432, database occupational_health, user portfolio, password portfolio-local-only. These are disposable local demo credentials. Inspect referrals and the three reporting views. Execute sql/validation.sql; use EXPLAIN to discuss the index without assuming every small-table query uses it.

## Apache Superset native dashboard
Run `docker compose --profile bi up -d superset`. Wait for login at http://localhost:8088; admin / portfolio-local-only. Run `python bi/create_superset_dashboard.py` on the host once. It creates database, dataset, five KPI charts and draft dashboard. Inspect the UI; APIs can vary by Superset version. If bootstrap fails, use the same expressions below through the UI; capture the error rather than claiming success.

Create a monthly trend chart from reporting_referrals: temporal column received_date, month grain, COUNT(*) metric. Add employer_name and service filters plus referral received-date filter. All cards use the same cohort filters. Backlog is the current status of referrals in that selected receipt cohort, not a historical point-in-time backlog.
Create a service comparison bar chart: service, AVG(appointment_wait_days). Report missing averages as no completed appointments, not zero.

## Power BI Desktop (Windows)
A compiled PBIX is not included: Power BI Desktop is not available in the build environment. The M query, DAX measures and layout are supplied for native authoring.
1. Open Desktop, Get Data > PostgreSQL, localhost:5432, occupational_health. Enter the local demo database credentials.
2. Use Import mode for this small project. Alternatively paste bi/Power_Query.m into a blank query named Referrals.
3. Create each measure in bi/Measures.dax separately. Format No Show Rate as percentage, averages to one decimal.
4. Page Operations: 5 KPI cards (count, backlog, overdue, no-show rate, average wait). Monthly referral line chart; wait by service bar chart; employer/service/date slicers. Date slicer is received_date.
5. Page Reporting: referral ID, employer, service, completed_date, issued_date and overdue_report_flag table. Keep employee IDs and medical details out of employer-facing reporting.
6. Reset filters, compare cards to evidence/reconciliation.json and sql/validation.sql. Then repeat with C01 employer filter in both BI tools. Save your native PBIX and screenshots locally.
7. Add a simple tooltip explaining snapshot date and metric denominator.

## Expressions used in both tools
Count = COUNT(*). Backlog = SUM(backlog_flag). Overdue = SUM(overdue_report_flag).
No-show rate = SUM(no_show_flag) / SUM(attended_or_missed_flag), null/blank if denominator zero.
Wait = mean(completed_date - received_date), excluding missing completions. Report turnaround = mean(issued_date - completed_date), excluding reports not issued. Display overdue counts beside turnaround; excluding pending reports can bias the average.

## Refresh and ownership
Refresh PostgreSQL only after a successful API ingestion. Refresh Power BI import afterward; Superset queries current views but may cache charts. Force refresh during reconciliation. BA owns definitions, IT owns API/database connectivity, operations owner approves acceptance. No employer-level row security is implemented by this demo; do not expose it to real users.
