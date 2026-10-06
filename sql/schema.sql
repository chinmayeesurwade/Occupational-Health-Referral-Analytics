CREATE TABLE IF NOT EXISTS referrals (
 referral_id text PRIMARY KEY, employee_id text NOT NULL, employer_id text NOT NULL,
 employer_name text NOT NULL, service text NOT NULL, received_date date NOT NULL,
 appointment_status text NOT NULL CHECK(appointment_status IN ('completed','no_show','scheduled','cancelled')),
 completed_date date, issued_date date, updated_at timestamptz NOT NULL,
 CHECK(completed_date IS NULL OR completed_date >= received_date),
 CHECK(issued_date IS NULL OR (completed_date IS NOT NULL AND issued_date >= completed_date))
);
CREATE INDEX IF NOT EXISTS ix_referrals_employer_date ON referrals(employer_id,received_date);
