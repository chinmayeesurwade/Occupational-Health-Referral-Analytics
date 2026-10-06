-- Expected: 1200 accepted rows, 1200 unique IDs, 0 bad dates.
SELECT COUNT(*) AS rows,COUNT(DISTINCT referral_id) AS unique_ids FROM referrals;
SELECT COUNT(*) AS invalid_dates FROM referrals WHERE completed_date<received_date OR issued_date<completed_date;
-- Same filtered population must be used in both BI tools.
SELECT COUNT(*) AS referrals,SUM(backlog_flag) AS backlog,SUM(overdue_report_flag) AS overdue,
 SUM(no_show_flag)::numeric/NULLIF(SUM(attended_or_missed_flag),0) AS no_show_rate,
 AVG(appointment_wait_days) AS mean_wait,AVG(report_turnaround_days) AS mean_report_turnaround
FROM reporting_referrals;
EXPLAIN SELECT * FROM referrals WHERE employer_id='C01' AND received_date>=DATE '2026-09-01';
