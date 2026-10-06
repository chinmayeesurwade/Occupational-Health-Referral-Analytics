-- Fixed reproducible snapshot. Rolling production reporting must define an explicit as-of parameter.
CREATE OR REPLACE VIEW reporting_referrals AS
SELECT referral_id,employer_id,employer_name,service,received_date,appointment_status,completed_date,issued_date,
 DATE '2026-10-06' AS as_of_date,
 CASE WHEN appointment_status NOT IN ('cancelled') AND issued_date IS NULL THEN 1 ELSE 0 END AS backlog_flag,
 CASE WHEN completed_date IS NOT NULL AND issued_date IS NULL AND DATE '2026-10-06'-completed_date>5 THEN 1 ELSE 0 END AS overdue_report_flag,
 completed_date-received_date AS appointment_wait_days,
 issued_date-completed_date AS report_turnaround_days,
 CASE WHEN appointment_status='no_show' THEN 1 ELSE 0 END AS no_show_flag,
 CASE WHEN appointment_status IN ('completed','no_show') THEN 1 ELSE 0 END AS attended_or_missed_flag
FROM referrals;
CREATE OR REPLACE VIEW monthly_reporting AS
SELECT date_trunc('month',received_date)::date AS referral_month,employer_id,employer_name,service,
 COUNT(*) AS referrals,SUM(backlog_flag) AS open_backlog,SUM(overdue_report_flag) AS overdue_reports,
 SUM(no_show_flag) AS no_shows,SUM(attended_or_missed_flag) AS outcome_appointments,
 AVG(appointment_wait_days) AS avg_wait_days,AVG(report_turnaround_days) AS avg_report_days
FROM reporting_referrals GROUP BY 1,2,3,4;
-- Latest referral per employer (window function example)
CREATE OR REPLACE VIEW latest_employer_referral AS
SELECT * FROM (SELECT referral_id,employer_id,received_date,
 ROW_NUMBER() OVER(PARTITION BY employer_id ORDER BY received_date DESC,referral_id DESC) AS rn FROM referrals) ranked WHERE rn=1;
