-- NiyamGuard synthetic dataset schema starter (PostgreSQL-compatible style)
-- Import CSV files in this order: regulators, organizations, users, circulars, policies, obligations, mappings, controls, evidence, findings, drift, risk, audit.
-- These tables are intentionally simple for hackathon seeding; add indexes/FKs in production.

CREATE TABLE IF NOT EXISTS regulators (regulator_code TEXT PRIMARY KEY, regulator_name TEXT, scope TEXT, country TEXT, notes TEXT);
CREATE TABLE IF NOT EXISTS organizations (org_id TEXT PRIMARY KEY, org_name TEXT, sector TEXT, region TEXT, asset_size_cr INT, risk_tier TEXT, compliance_officer TEXT, onboarded_at DATE, status TEXT);
CREATE TABLE IF NOT EXISTS users_seed (user_id TEXT PRIMARY KEY, org_id TEXT, name TEXT, email TEXT, role TEXT, mfa_enabled BOOLEAN, status TEXT, created_at TIMESTAMP);
CREATE TABLE IF NOT EXISTS regulatory_circulars (circular_id TEXT PRIMARY KEY, regulator_code TEXT, sector TEXT, title TEXT, issue_date DATE, effective_date DATE, due_date DATE, category TEXT, severity TEXT, jurisdiction TEXT, summary TEXT, full_text TEXT, source_url TEXT, status TEXT, keywords TEXT, version TEXT);
CREATE TABLE IF NOT EXISTS internal_policies (policy_id TEXT PRIMARY KEY, org_id TEXT, policy_title TEXT, department TEXT, owner_role TEXT, version TEXT, effective_from DATE, last_updated_at TIMESTAMP, next_review_date DATE, status TEXT, policy_text TEXT, tags TEXT);
CREATE TABLE IF NOT EXISTS obligations (obligation_id TEXT PRIMARY KEY, circular_id TEXT, regulator_code TEXT, sector TEXT, category TEXT, obligation_type TEXT, obligation_text TEXT, accountable_actor TEXT, action_required TEXT, frequency TEXT, evidence_required TEXT, due_days_from_effective_date INT, penalty_risk TEXT, risk_weight INT, expected_control TEXT, created_by_extractor TEXT, extractor_confidence NUMERIC);
