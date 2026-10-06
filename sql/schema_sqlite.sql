CREATE TABLE IF NOT EXISTS referrals (
 referral_id TEXT PRIMARY KEY, employee_id TEXT NOT NULL, employer_id TEXT NOT NULL,
 employer_name TEXT NOT NULL, service TEXT NOT NULL, received_date TEXT NOT NULL,
 appointment_status TEXT NOT NULL, completed_date TEXT, issued_date TEXT, updated_at TEXT NOT NULL
);
