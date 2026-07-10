import { vi } from "vitest";

export const fields = [
  {
    key: "applicant_name",
    label: "Applicant Full Name",
    type: "text",
    required: true,
    validation: "non_empty",
    help: {
      english: "Enter your full name.",
      telugu: "మీ పూర్తి పేరు టైప్ చేయండి.",
      hindi: "अपना पूरा नाम लिखें.",
    },
  },
  {
    key: "monthly_income",
    label: "Monthly Income",
    type: "number",
    required: true,
    validation: "positive_number",
    help: {
      english: "Enter monthly income.",
      telugu: "నెలవారీ ఆదాయం టైప్ చేయండి.",
      hindi: "महीने की आमदनी लिखें.",
    },
  },
  {
    key: "mobile_number",
    label: "Mobile Number",
    type: "phone",
    required: true,
    validation: "10_digits",
    help: {
      english: "Enter mobile number.",
      telugu: "మొబైల్ నంబర్ టైప్ చేయండి.",
      hindi: "मोबाइल नंबर लिखें.",
    },
  },
  {
    key: "district",
    label: "District",
    type: "text",
    required: true,
    validation: "non_empty",
    help: {
      english: "Enter district.",
      telugu: "జిల్లా టైప్ చేయండి.",
      hindi: "जिला लिखें.",
    },
  },
  {
    key: "mandal",
    label: "Mandal",
    type: "text",
    required: true,
    validation: "non_empty",
    help: {
      english: "Enter mandal.",
      telugu: "మండలం టైప్ చేయండి.",
      hindi: "मंडल लिखें.",
    },
  },
  {
    key: "purpose",
    label: "Purpose of Certificate",
    type: "text",
    required: true,
    validation: "non_empty",
    help: {
      english: "Enter why you need the certificate.",
      telugu: "Certificate ఎందుకు కావాలో టైప్ చేయండి.",
      hindi: "Certificate क्यों चाहिए लिखें.",
    },
  },
];

export const documents = [
  {
    key: "aadhaar",
    label: "Aadhaar Card",
    required: true,
    accepted_file_types: ["pdf", "jpg", "jpeg", "png"],
    max_size_mb: 5,
    examples: ["Aadhaar PDF"],
    help: {
      english: "Upload Aadhaar card.",
      telugu: "Aadhaar upload చేయండి.",
      hindi: "Aadhaar upload करें.",
    },
  },
  {
    key: "income_proof",
    label: "Income Proof",
    required: true,
    accepted_file_types: ["pdf", "jpg", "jpeg", "png"],
    max_size_mb: 1,
    examples: ["Salary slip", "Income affidavit"],
    help: {
      english: "Upload salary slip or affidavit.",
      telugu: "Salary slip లేదా affidavit upload చేయండి.",
      hindi: "Salary slip या affidavit upload करें.",
    },
  },
];

export const incomeForm = {
  form_id: "income_certificate",
  service_name: "Income Certificate",
  form_name: "Income Certificate Application",
  department: "Revenue",
  category: "Certificates",
  description: "Test income form",
  common_use_cases: ["Scholarship", "Fee reimbursement"],
  fields,
  required_documents: documents,
  assistant_examples: {
    english: ["monthly income"],
    telugu: ["purpose lo emi rayali"],
    hindi: ["purpose mein kya likhna hai"],
  },
  assistant_guidance: {},
  translations: {},
  status: "ready",
};

export const services = [
  {
    form_id: "income_certificate",
    service_name: "Income Certificate",
    department: "Revenue",
    category: "Certificates",
    description: "Citizen-friendly income certificate.",
    common_use_cases: ["Scholarship", "Fee reimbursement", "Jobs", "Benefits"],
    required_document_count: 2,
    status: "ready",
    has_detailed_schema: true,
  },
  {
    form_id: "birth_certificate",
    service_name: "Birth Certificate",
    department: "Municipal / Panchayat",
    category: "Certificates",
    description: "Birth certificate guidance.",
    common_use_cases: ["School admission", "Passport"],
    required_document_count: 2,
    status: "ready",
    has_detailed_schema: true,
  },
  {
    form_id: "loan_eligibility_card",
    service_name: "Loan Eligibility Card",
    department: "Agriculture / Revenue",
    category: "Agriculture",
    description: "General guidance for loan eligibility card requirements.",
    common_use_cases: ["Agriculture loan", "Bank support"],
    required_document_count: 0,
    status: "catalog_only",
    has_detailed_schema: false,
  },
];

export const adminSummary = {
  total_circulars: 2,
  pending_extractions: 0,
  verified_rules: 2,
  connected_systems: 5,
  compliance_findings: 4,
  drifted_findings: 3,
  critical_findings: 3,
  open_conflicts: 1,
  recent_audit_events: 2,
};

export const connectedSystems = [
  {
    id: "sys_meeseva_portal",
    name: "MeeSeva Income Certificate Portal",
    system_type: "portal",
    service_id: "income_certificate",
  },
  {
    id: "sys_officer_sop",
    name: "Officer SOP Manual",
    system_type: "sop",
    service_id: "income_certificate",
  },
  {
    id: "sys_public_faq",
    name: "Public FAQ",
    system_type: "faq",
    service_id: "income_certificate",
  },
  {
    id: "sys_simplified_form",
    name: "Simplified Citizen Form",
    system_type: "form",
    service_id: "income_certificate",
  },
];

export const complianceFindings = [
  {
    id: "find_rule_001_sys_meeseva_portal",
    verified_rule_id: "rule_001",
    service_id: "income_certificate",
    rule_key: "validity",
    expected_value: "6 months",
    actual_value: "12 months",
    status: "drifted",
    severity: "high",
    finding_summary: "MeeSeva Income Certificate Portal still shows 12 months.",
    recommended_fix: "Update portal validation rule from 12 months to 6 months.",
    citizen_impact_reason: "Citizens may follow an outdated requirement and face rejection.",
    source_clause: "Income certificate must be issued within 6 months.",
    connected_system_id: "sys_meeseva_portal",
  },
  {
    id: "find_rule_001_sys_officer_sop",
    verified_rule_id: "rule_001",
    service_id: "income_certificate",
    rule_key: "validity",
    expected_value: "6 months",
    actual_value: "12 months",
    status: "drifted",
    severity: "high",
    finding_summary: "Officer SOP Manual still shows 12 months.",
    recommended_fix: "Update Officer SOP Manual from 12 months to 6 months.",
    citizen_impact_reason: "Officers may ask citizens to follow the old rule.",
    source_clause: "Income certificate must be issued within 6 months.",
    connected_system_id: "sys_officer_sop",
  },
  {
    id: "find_rule_001_sys_public_faq",
    verified_rule_id: "rule_001",
    service_id: "income_certificate",
    rule_key: "validity",
    expected_value: "6 months",
    actual_value: "12 months",
    status: "drifted",
    severity: "medium",
    finding_summary: "Public FAQ still shows 12 months.",
    recommended_fix: "Update Public FAQ from 12 months to 6 months.",
    citizen_impact_reason: "Citizens may read stale validity guidance.",
    source_clause: "Income certificate must be issued within 6 months.",
    connected_system_id: "sys_public_faq",
  },
  {
    id: "find_rule_001_sys_simplified_form",
    verified_rule_id: "rule_001",
    service_id: "income_certificate",
    rule_key: "validity",
    expected_value: "6 months",
    actual_value: "6 months",
    status: "compliant",
    severity: "low",
    finding_summary: "Simplified Citizen Form reflects the current rule.",
    recommended_fix: "No fix required.",
    citizen_impact_reason: "No current citizen impact detected.",
    source_clause: "Income certificate must be issued within 6 months.",
    connected_system_id: "sys_simplified_form",
  },
];

export const priorityFindings = [
  {
    finding_id: "find_rule_001_sys_meeseva_portal",
    score: 100,
    priority_level: "critical",
    reason: "Portal validity mismatch affects citizens immediately.",
  },
];

export const conflicts = [
  {
    id: "conf_rule_001_rule_conflict_001",
    service_id: "income_certificate",
    rule_key: "validity",
    conflict_type: "active_value_conflict",
    rule_a_id: "rule_001",
    rule_b_id: "rule_conflict_001",
    severity: "high",
    status: "open",
    summary: "Two active verified rules have different values.",
    recommendation: "Resolve by superseding the older rule.",
  },
];

export const knowledgeRules = [
  {
    id: "rule_001",
    circular_id: "circ_001",
    rule_name: "Income Certificate Validity",
    service_id: "income_certificate",
    current_value: "6",
    previous_value: "12",
    unit: "months",
    status: "active",
    source_clause: "Income certificate must be issued within 6 months.",
  },
  {
    id: "rule_conflict_001",
    circular_id: "circ_000",
    rule_name: "Income Certificate Validity",
    service_id: "income_certificate",
    current_value: "12",
    previous_value: null,
    unit: "months",
    status: "active",
    source_clause: "Income certificate validity is 12 months from date of issue.",
  },
];

export const publicRule = {
  success: true,
  verified: true,
  answer: "Income Certificate validity is currently 6 months.",
  source: {
    circular_id: "circ_001",
    circular_number: "GO-138",
    department: "Revenue",
    effective_date: "2026-07-01",
    confidence: 0.91,
  },
};

export const adminUser = {
  id: "user_admin",
  email: "admin@niyamguard.local",
  role: "admin",
  is_active: true,
  created_at: "2026-07-09T00:00:00+00:00",
  updated_at: "2026-07-09T00:00:00+00:00",
};

export const citizenUser = {
  id: "user_citizen",
  email: "citizen@niyamguard.local",
  role: "citizen",
  is_active: true,
  created_at: "2026-07-09T00:00:00+00:00",
  updated_at: "2026-07-09T00:00:00+00:00",
};

export const officerUser = {
  id: "user_officer",
  email: "officer@niyamguard.local",
  role: "officer",
  is_active: true,
  created_at: "2026-07-09T00:00:00+00:00",
  updated_at: "2026-07-09T00:00:00+00:00",
};

export const auditEvents = [
  {
    id: "audit_001",
    actor_user_id: "user_admin",
    actor_email: "admin@niyamguard.local",
    actor_role: "admin",
    action: "login_success",
    entity_type: "auth",
    entity_id: "user_admin",
    request_id: "req_001",
    created_at: "2026-07-09T00:00:00+00:00",
  },
  {
    id: "audit_002",
    actor_user_id: "user_admin",
    actor_email: "admin@niyamguard.local",
    actor_role: "admin",
    action: "report_exported",
    entity_type: "report",
    entity_id: "compliance",
    request_id: "req_002",
    created_at: "2026-07-09T00:05:00+00:00",
  },
];

export const chatAnswer = {
  success: true,
  answer:
    "For Post-Matric Scholarship, the retrieved source lists these documents: Valid Income Certificate; Caste Certificate if applicable; Previous year mark sheet; Bonafide certificate; Bank passbook copy.",
  language: "english",
  language_code: "en-IN",
  intent: "documents",
  scheme_or_service: "post_matric_scholarship",
  source: {
    type: "rag",
    label: "NiyamGuard knowledge index",
    references: [
      {
        chunk_id: "chunk_post_matric_scholarship",
        service_id: "post_matric_scholarship",
        title: "Post-Matric Scholarship",
        source_type: "seed_demo",
        source_label: "NiyamGuard demo knowledge base",
        verified: false,
        score: 0.78,
      },
    ],
  },
  confidence: 0.78,
  verified: false,
  fallback: true,
  provider: "fallback",
};

export const aiStatus = {
  enabled: false,
  provider: "ollama",
  configured: false,
  model: "qwen2.5:7b-instruct",
  rag_enabled: true,
  status: "fallback",
  message: "Ollama is unavailable. Deterministic fallback is active.",
};

export const aiImpactSummary = {
  success: true,
  provider: "fallback",
  model: "deterministic-template",
  summary: "MeeSeva Income Certificate Portal is drifted. It shows 12 months, while the verified rule expects 6 months.",
  citizen_friendly_explanation: "A citizen may receive outdated guidance if this connected system is not updated.",
  officer_friendly_explanation: "Update MeeSeva Income Certificate Portal to match the verified rule value 6 months.",
  risk_explanation: "Portal validity mismatch affects citizens immediately.",
  recommended_action: "Update portal validation rule from 12 months to 6 months.",
  source: {
    rule: "Income Certificate Validity",
    circular: "GO-138",
    verified: true,
  },
  fallback: true,
  limitations: "AI summary is explanatory only. Verified rules remain the source of truth.",
};

export const datasetStatus = {
  success: true,
  pack_version: "niyamguard_dataset_pack_v1",
  pack_available: true,
  loaded_records: 18531,
  collections: {
    regulatory_circulars: 220,
    internal_policies: 314,
    obligations: 758,
    gap_findings: 594,
    regulatory_drift_cases: 500,
    risk_scoring_labels: 30,
    dataset_audit_events: 2500,
    policy_qa_pairs: 900,
  },
  rag_index_ready: true,
};

export const datasetAnswer = {
  success: true,
  answer:
    "Intent: explain_risk_score. NiyamGuard should retrieve linked regulatory text, obligation mappings, evidence, and risk labels; then provide a concise compliance answer with citations to internal records.",
  provider: "dataset",
  fallback: false,
  references: [
    {
      chunk_id: "chunk_qa_org_0029",
      title: "Why is ORG-0029 high risk?",
      service_id: "ORG-0029",
      score: 0.86,
      source: { type: "policy_qa_pair", label: "QA-000217", verified: false },
      metadata: { org_id: "ORG-0029", obligation_id: "OBL-000409", circular_id: "CIR-00195" },
    },
  ],
};

export const datasetFlow = {
  success: true,
  org_id: "ORG-0029",
  question: "What changed for ORG-0029 and what should compliance fix first?",
  regulation: {
    payload: {
      circular_id: "CIR-00192",
      regulator_code: "IRDAI",
      sector: "Mutual Funds",
      title: "IRDAI circular on data privacy requirements for mutual funds entities",
      effective_date: "2025-10-02",
      severity: "Medium",
      summary: "Synthetic Data Privacy requirement for Mutual Funds firms to review investor disclosures.",
    },
  },
  obligation: {
    payload: {
      obligation_id: "OBL-000664",
      accountable_actor: "Legal Reviewer",
      action_required: "update the internal policy and maintain approval evidence",
      frequency: "Quarterly",
      evidence_required: "Data retention proof",
      penalty_risk: "High",
      obligation_text: "Legal Reviewer must update the internal policy and maintain approval evidence.",
    },
  },
  internal_policy: {
    payload: {
      policy_id: "POL-000301",
      org_id: "ORG-0029",
      policy_title: "Data Retention and Privacy Policy",
      department: "Compliance",
      owner_role: "Compliance Officer",
      status: "Active",
      policy_text: "Policy defines ownership, review cadence, exception handling, and evidence retention.",
    },
  },
  gap: {
    payload: {
      finding_id: "FND-000301",
      severity: "High",
      finding_type: "Policy Wording Gap",
      owner_team: "Compliance",
      status: "Open",
      target_date: "2026-08-07",
      recommended_fix: "Update policy clause, assign owner, and add evidence workflow.",
    },
  },
  drift: {
    payload: {
      drift_id: "DRF-000301",
      drift_type: "New Control Required",
      old_requirement: "periodic audit",
      new_requirement: "continuous monitoring dashboard",
      drift_score: "67",
      ground_truth_label: "Minor Drift",
      recommended_action: "Revise policy, update controls, and collect new evidence.",
    },
  },
  risk: {
    payload: {
      org_id: "ORG-0029",
      risk_band: "Medium",
      risk_score: "56",
      open_findings_count: "15",
      bad_evidence_count: "20",
      label_source: "synthetic_rule_based_ground_truth",
    },
  },
  risk_explanation:
    "ORG-0029 has risk band Medium with score 56. Top factors: coverage=64.9; open_findings=15; weak_evidence=20.",
  evidence: [
    {
      payload: {
        evidence_id: "EVD-0000046",
        status: "Accepted",
        evidence_title: "Cybersecurity evidence package 46",
        evidence_score: "96",
      },
    },
  ],
  audit_trail: [
    {
      payload: {
        audit_id: "AUD-0000146",
        event_type: "CREATE",
        entity_type: "user",
        entity_id: "USE-005080",
        success: "true",
      },
    },
  ],
};

export const sources = [
  {
    id: "src_revenue_demo",
    name: "Revenue Department Demo Circular Feed",
    department: "Revenue",
    source_type: "local_demo",
    url: "demo://revenue/go-138",
    enabled: true,
    last_checked_at: null,
    last_success_at: null,
  },
];

export const circularDocuments = [
  {
    id: "cirdoc_go_138",
    source_id: "src_revenue_demo",
    circular_number: "GO-138",
    title: "Income Certificate Validity Amendment",
    department: "Revenue",
    published_date: "2026-06-20",
    effective_date: "2026-07-01",
    status: "pending_review",
  },
];

export const ruleCandidates = [
  {
    id: "cand_cirdoc_go_138_income_validity",
    circular_id: "cirdoc_go_138",
    service_id: "income_certificate",
    rule_key: "validity",
    old_value: "12",
    new_value: "6",
    unit: "months",
    effective_date: "2026-07-01",
    confidence_score: 0.91,
    extraction_method: "deterministic",
    source_excerpt: "Income Certificate validity changed from 12 months to 6 months.",
    status: "pending_review",
    delta: {
      change_type: "no_change",
      impact_level: "high",
    },
  },
];

export const policyHistory = [
  {
    id: "pub_cand_cirdoc_go_138_income_validity",
    candidate_id: "cand_cirdoc_go_138_income_validity",
    rule_version_id: "version_rule_001_3",
    service_id: "income_certificate",
    rule_key: "validity",
    old_value: "12",
    new_value: "6",
    created_at: "2026-07-09T00:00:00+00:00",
  },
];

export const ruleVersions = [
  {
    id: "version_rule_001_2",
    rule_id: "rule_001",
    version_number: 2,
    service_id: "income_certificate",
    rule_key: "validity",
    value: "6",
    unit: "months",
    source_circular_number: "GO-138",
    effective_date: "2026-07-01",
    is_current: true,
  },
];

export const knowledgeEvents = [
  {
    id: "knowledge_version_rule_001_2",
    rule_version_id: "version_rule_001_2",
    service_id: "income_certificate",
    rule_key: "validity",
    update_type: "verified_rule_public_api_and_rag",
    status: "completed",
  },
];

export const propagationTasks = [
  {
    id: "task_version_rule_001_2_sys_meeseva_portal",
    rule_version_id: "version_rule_001_2",
    connected_system_id: "sys_meeseva_portal",
    task_type: "update_portal",
    status: "pending",
    old_value: "12 months",
    new_value: "6 months",
  },
];

export const schedulerStatus = {
  enabled: false,
  interval_minutes: 60,
  source_mode: "manual",
  running: false,
  message: "Scheduler is disabled unless AUTO_SYNC_ENABLED=true.",
};

export const complianceRuns = [
  {
    id: "compliance_run_0001",
    trigger_type: "policy_update",
    affected_rule_id: "rule_001",
    finding_count: 4,
  },
];

export const mockSystems = {
  meeseva: {
    id: "meeseva",
    system_name: "Mock MeeSeva Portal",
    service_id: "income_certificate",
    rule_key: "validity",
    expected_value: "6 months",
    source_circular: "old_portal_config",
    sync_status: "outdated",
    displayed_value: "12 months",
  },
  public_faq: {
    id: "public_faq",
    system_name: "Mock Public FAQ / Citizen Form",
    service_id: "income_certificate",
    rule_key: "validity",
    expected_value: "6 months",
    source_circular: "old_content",
    sync_status: "outdated",
    faq_value: "12 months",
    form_hint_value: "12 months",
  },
};

export const schemeFinderResponse = {
  success: true,
  profile_summary: {
    age: 19,
    income: 180000,
    student: true,
    purpose: "scholarship",
    district: "Hyderabad",
  },
  recommendations: [
    {
      form_id: "income_certificate",
      service_name: "Income Certificate",
      department: "Revenue",
      category: "Certificates",
      why_it_may_match: "Scholarship workflows commonly require an income certificate.",
      basic_eligibility: ["Citizen needs income proof for scholarship."],
      required_documents: ["Aadhaar Card", "Income Proof", "Address Proof"],
      confidence: 0.92,
      status: "ready",
      start_application_available: true,
      safe_note: "You may be eligible. Please verify with official rules before applying.",
      source: { type: "local_demo_rules", label: "Verified GO-138 public rule plus local form catalog", verified: false },
    },
  ],
  limitations: "Demo recommendations are guidance only.",
};

export const portalServices = [
  {
    id: "svc_income_certificate",
    service_id: "income_certificate",
    name: "Income Certificate",
    category: "Revenue Certificates",
    description: "Certificate confirming declared family income for scholarships and public benefit checks.",
    eligibility_json: ["Resident applicant", "Income proof available"],
    required_documents_json: [
      { key: "aadhaar", label: "Aadhaar Card", required: true, accepted_file_types: ["pdf", "jpg"], max_size_mb: 5 },
      { key: "income_proof", label: "Income Proof", required: true, accepted_file_types: ["pdf", "jpg"], max_size_mb: 5 },
      { key: "address_proof", label: "Address Proof", required: true, accepted_file_types: ["pdf", "jpg"], max_size_mb: 5 },
    ],
    fee_amount: 35,
    processing_days: 7,
    enabled: true,
    rule_bindings_json: { application_code: "INC", latest_rule_id: "rule_001" },
  },
  {
    id: "svc_residence_certificate",
    service_id: "residence_certificate",
    name: "Residence Certificate",
    category: "Revenue Certificates",
    description: "Certificate confirming local residence.",
    eligibility_json: ["Resident applicant"],
    required_documents_json: [
      { key: "aadhaar", label: "Aadhaar Card", required: true, accepted_file_types: ["pdf"], max_size_mb: 5 },
      { key: "address_proof", label: "Address Proof", required: true, accepted_file_types: ["pdf"], max_size_mb: 5 },
    ],
    fee_amount: 25,
    processing_days: 7,
    enabled: true,
    rule_bindings_json: { application_code: "RES" },
  },
];

export const portalForm = {
  id: "form_income_certificate_v1",
  service_id: "income_certificate",
  version: 1,
  fields_json: [
    { key: "applicant_name", label: "Applicant Full Name", type: "text", required: true },
    { key: "mobile_number", label: "Mobile Number", type: "phone", required: true },
    { key: "district", label: "District", type: "text", required: true },
    { key: "mandal", label: "Mandal", type: "text", required: true },
    { key: "address", label: "Address", type: "textarea", required: true },
    { key: "purpose", label: "Purpose", type: "textarea", required: true },
    { key: "annual_income", label: "Annual Income", type: "number", required: true },
    { key: "occupation", label: "Occupation", type: "text", required: true },
  ],
  validation_rules_json: { required_documents: ["aadhaar", "income_proof", "address_proof"] },
  is_current: true,
};

export const portalApplication = {
  id: "app_portal_001",
  application_number: "NGSP-2026-INC-000001",
  citizen_user_id: "user_citizen",
  service_id: "income_certificate",
  status: "under_review",
  current_stage: "Officer review",
  submitted_at: "2026-07-09T00:00:00+00:00",
  district: "Hyderabad",
  mandal: "Ameerpet",
  fee_status: "paid",
  certificate_id: null,
  form_values_json: { applicant_name: "Ravi Kumar" },
  due_date: "2026-07-16",
  created_at: "2026-07-09T00:00:00+00:00",
  updated_at: "2026-07-09T00:00:00+00:00",
  service: portalServices[0],
  documents: [
    { id: "doc_1", document_type: "aadhaar", file_name: "aadhaar.pdf", verification_status: "pending" },
  ],
  payments: [],
  certificate: null,
  sla: { status: "within_sla", due_date: "2026-07-16", processing_days: 7, days_remaining: 7 },
};

export const portalCertificate = {
  id: "cert_001",
  certificate_number: "NGCERT-2026-INC-000001",
  service_id: "income_certificate",
  status: "valid",
  issued_at: "2026-07-09T00:00:00+00:00",
  expires_at: "2027-01-09",
  verification_hash: "hash_demo",
};

export const readinessReport = {
  success: true,
  pilot_status: "ready",
  ready_controls: 10,
  total_controls: 10,
  controls: [
    {
      control_id: "GOV-001",
      name: "Verified source-backed answers",
      status: "ready",
      ready: true,
      evidence: "Hybrid answer engine uses exact rules, decision tables, RAG, and safe fallback.",
    },
    {
      control_id: "GOV-008",
      name: "Backup and restore",
      status: "ready",
      ready: true,
      evidence: "scripts/backup_restore.py supports SQLite backup and restore.",
    },
  ],
  ops: {
    dataset: { imported_records: 18531 },
    search: { indexed_chunks: 42, enabled: true, engine: "hybrid_intelligence" },
    ai: { active_provider: "fallback", fallback_available: true, status: "fallback" },
  },
};

export const virtualGovStatus = {
  success: true,
  sandbox: "virtual_government",
  applications: 0,
  certificates: 0,
  payments: 0,
  audit_events: 0,
  scenarios: 1,
};

export const virtualGovScenarios = [
  {
    scenario_id: "income_certificate_full_flow",
    title: "Income certificate regulation-to-certificate sandbox",
    description: "Full synthetic service scenario.",
    service_id: "income_certificate",
  },
];

export const virtualGovResult = {
  success: true,
  scenario_id: "income_certificate_full_flow",
  title: "Income certificate regulation-to-certificate sandbox",
  steps: [
    {
      step_id: "regulation_question",
      title: "User asks about a regulation",
      status: "completed",
      payload: { method: "exact_rule_engine", answer: "As per GO-138, Income Certificate validity is 6 months." },
    },
    {
      step_id: "certificate_issued",
      title: "Officer approves and certificate is issued",
      status: "completed",
      payload: { certificate_number: "NGCERT-2026-INC-000001", certificate_valid: true },
    },
  ],
  artifacts: {
    application_number: "NGSP-2026-INC-000001",
    certificate_number: "NGCERT-2026-INC-000001",
    verification_hash: "hash_demo",
    tracking: { status: "certificate_issued" },
  },
};

export const fullDemoResult = {
  success: true,
  steps: [
    ["reset_sandbox", "Reset sandbox", "Demo store reset to known GO-138 baseline."],
    ["publish_circular", "Published GO-138 circular", "Virtual Gazette made GO-138 available."],
    ["ingest_circular", "Ingested circular and extracted rule candidate", "Extracted 12 month to 6 month change."],
    ["update_verified_rule", "Updated verified rule engine", "Verified rule now points to GO-138."],
    ["update_service_portal", "Updated service portal rule context", "Income Certificate service is available."],
    ["create_citizen_identity", "Created sandbox citizen identity", "Citizen profile and OTP were created."],
    ["submit_application", "Submitted citizen application", "Application submitted with synthetic documents."],
    ["verify_otp", "Verified sandbox OTP", "Demo OTP verification succeeded."],
    ["complete_payment", "Completed sandbox payment", "Virtual payment gateway marked the fee paid."],
    ["officer_approval", "Officer approved application", "Officer review completed."],
    ["generate_certificate", "Generated certificate", "Certificate number and hash created."],
    ["sign_certificate", "Signed certificate in sandbox", "Verification hash used as sandbox signature."],
    ["verify_certificate", "Verified certificate publicly", "Certificate is valid."],
    ["patch_connected_systems", "Patched connected systems", "Mock systems were patched to 6 months."],
    ["rerun_compliance", "Reran compliance drift check", "Compliance findings refreshed."],
    ["write_audit_trail", "Wrote audit trail", "Audit event added."],
    ["ask_hybrid_answer", "Asked hybrid answer engine", "Answered from GO-138 context."],
    ["generate_ollama_explanation", "Generated Ollama explanation if available", "Fallback active.", { provider: "fallback", model: "deterministic-template", fallback: true, text: "GO-138 means the demo Income Certificate validity is 6 months instead of 12 months." }],
  ].map(([key, label, details, payload = {}]) => ({
    key,
    label,
    status: "success",
    details,
    payload,
  })),
  entities: {
    application_id: "app_portal_001",
    application_number: "NGSP-2026-INC-000001",
    certificate_id: "cert_001",
    certificate_number: "NGCERT-2026-INC-000001",
    verification_hash: "hash_demo",
    rule_id: "rule_001",
    rule_version_id: "version_rule_001_2",
    ollama_provider: "fallback",
    ollama_model: "deterministic-template",
    ollama_fallback: true,
  },
  circular_number: "GO-138",
  application_number: "NGSP-2026-INC-000001",
  certificate_number: "NGCERT-2026-INC-000001",
  verification_hash: "hash_demo",
  verified_rule: {
    rule_id: "rule_001",
    rule_version_id: "version_rule_001_2",
    service_id: "income_certificate",
    rule_key: "validity",
    value: "6 months",
    source_circular_number: "GO-138",
  },
  audit_event_count: 7,
};

export const verifiedAIExplanation = {
  success: true,
  question: "Explain GO-138 in simple words",
  provider: "fallback",
  model: "deterministic-template",
  fallback: true,
  answer: "GO-138 means the demo Income Certificate validity is 6 months instead of 12 months.",
  source: {
    type: "verified_rule",
    circular_number: "GO-138",
    department: "Revenue",
    service_id: "income_certificate",
    rule_key: "validity",
    verified: true,
  },
};

export const hybridDemoAnswer = {
  success: true,
  question: "income certificate validity entha",
  answer: "Income Certificate validity is 6 months as per verified GO-138.",
  method: "exact_rule_engine",
  provider: "verified-rule",
  verified: true,
  source: {
    type: "verified_rule",
    circular_number: "GO-138",
    department: "Revenue",
  },
};

export function jsonResponse(payload, status = 200) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    headers: { get: () => null },
    json: () => Promise.resolve(payload),
    blob: () => Promise.resolve(new Blob()),
  });
}

export function audioResponse(
  content = "fake-mp3",
  {
    languageCode = "te-IN",
    provider = "gtts",
    cacheStatus = "MISS",
  } = {},
) {
  const headers = new Map([
    ["x-tts-language-code", languageCode],
    ["x-tts-provider", provider],
    ["x-tts-cache", cacheStatus],
  ]);
  return Promise.resolve({
    ok: true,
    status: 200,
    headers: {
      get: (name) => headers.get(name.toLowerCase()) || null,
    },
    json: () => Promise.reject(new Error("Audio response")),
    blob: () => Promise.resolve(new Blob([content], { type: "audio/mpeg" })),
  });
}

export function installApiMock(overrides = {}) {
  function maybeDelay(payload) {
    if (!overrides.askDelayMs) return jsonResponse(payload);
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(jsonResponse(payload));
      }, overrides.askDelayMs);
    });
  }

  const fetchMock = vi.fn((url, options = {}) => {
    if (url.endsWith("/api/auth/login")) {
      const requestBody = JSON.parse(options.body);
      if (requestBody.email === "admin@niyamguard.local" && requestBody.password === "Admin@12345") {
        return jsonResponse({
          success: true,
          access_token: "test-access-token",
          refresh_token: "test-refresh-token",
          token_type: "bearer",
          user: adminUser,
        });
      }
      if (requestBody.email === "citizen@niyamguard.local" && requestBody.password === "Citizen@12345") {
        return jsonResponse({
          success: true,
          access_token: "test-access-token",
          refresh_token: "test-refresh-token",
          token_type: "bearer",
          user: citizenUser,
        });
      }
      if (requestBody.email === "officer@niyamguard.local" && requestBody.password === "Officer@12345") {
        return jsonResponse({
          success: true,
          access_token: "test-access-token",
          refresh_token: "test-refresh-token",
          token_type: "bearer",
          user: officerUser,
        });
      }
      return jsonResponse({ detail: "Invalid email or password." }, 401);
    }
    if (url.endsWith("/api/auth/logout")) {
      return jsonResponse({ success: true });
    }
    if (url.endsWith("/api/auth/me")) {
      return jsonResponse({ success: true, user: overrides.user || adminUser });
    }
    if (url.endsWith("/api/auth/users")) {
      if ((options.method || "GET").toUpperCase() === "POST") {
        const requestBody = JSON.parse(options.body);
        return jsonResponse({
          success: true,
          user: {
            id: "user_created",
            email: requestBody.email,
            role: requestBody.role,
            is_active: requestBody.is_active,
            created_at: "2026-07-09T00:10:00+00:00",
            updated_at: "2026-07-09T00:10:00+00:00",
          },
        });
      }
      return jsonResponse({ success: true, users: [overrides.user || adminUser] });
    }
    if (url.endsWith("/api/audit/events")) {
      return jsonResponse({ success: true, events: overrides.auditEvents || auditEvents });
    }
    if (url.endsWith("/api/audit/verify")) {
      return jsonResponse({ success: true, valid: true, checked_events: 2 });
    }
    if (url.endsWith("/api/ops/status")) {
      return jsonResponse(overrides.opsStatus || readinessReport.ops);
    }
    if (url.endsWith("/api/admin/readiness")) {
      return jsonResponse(overrides.readinessReport || readinessReport);
    }
    if (url.endsWith("/api/virtual-gov/status")) {
      return jsonResponse(overrides.virtualGovStatus || virtualGovStatus);
    }
    if (url.endsWith("/api/virtual-gov/scenarios")) {
      return jsonResponse({ success: true, scenarios: overrides.virtualGovScenarios || virtualGovScenarios });
    }
    if (url.endsWith("/api/virtual-gov/run")) {
      return jsonResponse(overrides.virtualGovResult || virtualGovResult);
    }
    if (url.endsWith("/api/sources")) {
      return jsonResponse({ success: true, sources: overrides.sources || sources });
    }
    if (url.includes("/api/sources/") && url.endsWith("/sync")) {
      return jsonResponse({ success: true, job: { id: "sync_0001", new_documents_found: 1, status: "success" } });
    }
    if (url.endsWith("/api/circulars/sync-all")) {
      return jsonResponse({ success: true, results: [{ success: true }] });
    }
    if (url.endsWith("/api/circulars")) {
      return jsonResponse({ success: true, circulars: overrides.circularDocuments || circularDocuments });
    }
    if (url.includes("/api/circulars/") && url.endsWith("/extract-rules")) {
      return jsonResponse({ success: true, candidates: overrides.ruleCandidates || ruleCandidates });
    }
    if (url.endsWith("/api/rule-candidates")) {
      return jsonResponse({ success: true, candidates: overrides.ruleCandidates || ruleCandidates });
    }
    if (url.includes("/api/rule-candidates/") && url.endsWith("/approve")) {
      return jsonResponse({ success: true, candidate: { ...ruleCandidates[0], status: "approved" } });
    }
    if (url.endsWith("/api/policy-updates/history")) {
      return jsonResponse({ success: true, events: overrides.policyHistory || policyHistory });
    }
    if (url.endsWith("/api/policy-updates/versions")) {
      return jsonResponse({ success: true, versions: overrides.ruleVersions || ruleVersions });
    }
    if (url.includes("/api/policy-updates/") && url.endsWith("/publish")) {
      return jsonResponse({
        success: true,
        rule_version: ruleVersions[0],
        publication_event: policyHistory[0],
        knowledge_update: knowledgeEvents[0],
        propagation_plan: { id: "plan_version_rule_001_2", task_ids: propagationTasks.map((task) => task.id) },
        compliance_run: complianceRuns[0],
      });
    }
    if (url.endsWith("/api/knowledge/update-events")) {
      return jsonResponse({ success: true, events: overrides.knowledgeEvents || knowledgeEvents });
    }
    if (url.endsWith("/api/knowledge/reindex")) {
      return jsonResponse({ success: true, events: overrides.knowledgeEvents || knowledgeEvents });
    }
    if (url.endsWith("/api/propagation/tasks")) {
      return jsonResponse({ success: true, tasks: overrides.propagationTasks || propagationTasks });
    }
    if (url.includes("/api/propagation/tasks/") && url.endsWith("/apply-demo-patch")) {
      return jsonResponse({ success: true, task: { ...propagationTasks[0], status: "auto_patched" } });
    }
    if (url.endsWith("/api/scheduler/status")) {
      return jsonResponse({ success: true, scheduler: overrides.schedulerStatus || schedulerStatus });
    }
    if (url.endsWith("/api/scheduler/run-now")) {
      return jsonResponse({ success: true, results: [{ success: true }] });
    }
    if (url.includes("/api/compliance/rerun-for-rule/")) {
      return jsonResponse({ success: true, run: complianceRuns[0] });
    }
    if (url.endsWith("/api/compliance/runs")) {
      return jsonResponse({ success: true, runs: overrides.complianceRuns || complianceRuns });
    }
    if (url.endsWith("/api/mock-systems/reset-demo")) {
      return jsonResponse({ success: true, systems: mockSystems });
    }
    if (url.endsWith("/api/mock-systems/apply-demo-patch")) {
      return jsonResponse({
        success: true,
        systems: {
          ...mockSystems,
          meeseva: { ...mockSystems.meeseva, displayed_value: "6 months", sync_status: "updated", source_circular: "GO-138" },
          public_faq: { ...mockSystems.public_faq, faq_value: "6 months", form_hint_value: "6 months", sync_status: "updated", source_circular: "GO-138" },
        },
      });
    }
    if (url.endsWith("/api/mock-systems/meeseva")) {
      return jsonResponse({ success: true, system: overrides.mockSystems?.meeseva || mockSystems.meeseva });
    }
    if (url.endsWith("/api/mock-systems/public-faq")) {
      return jsonResponse({ success: true, system: overrides.mockSystems?.public_faq || mockSystems.public_faq });
    }
    if (url.endsWith("/api/mock-systems")) {
      return jsonResponse({ success: true, systems: overrides.mockSystems || mockSystems });
    }
    if (url.endsWith("/api/demo/run-self-update-scenario")) {
      return jsonResponse({
        success: true,
        steps: {
          publication: { success: true },
          patches: [{ success: true }],
          mock_systems: {
            ...mockSystems,
            meeseva: { ...mockSystems.meeseva, displayed_value: "6 months", sync_status: "updated", source_circular: "GO-138" },
            public_faq: { ...mockSystems.public_faq, faq_value: "6 months", form_hint_value: "6 months", sync_status: "updated", source_circular: "GO-138" },
          },
        },
      });
    }
    if (url.endsWith("/api/demo/run-full-end-to-end")) {
      return jsonResponse(overrides.fullDemoResult || fullDemoResult);
    }
    if (url.endsWith("/api/scheme-finder/recommend")) {
      return jsonResponse(overrides.schemeFinderResponse || schemeFinderResponse);
    }
    if (url.endsWith("/api/portal/services")) {
      return jsonResponse({ success: true, services: overrides.portalServices || portalServices });
    }
    if (url.endsWith("/api/portal/services/income_certificate")) {
      return jsonResponse({
        success: true,
        service: { ...(overrides.portalServices || portalServices)[0], form: overrides.portalForm || portalForm },
      });
    }
    if (url.endsWith("/api/portal/services/income_certificate/form")) {
      return jsonResponse({ success: true, form: overrides.portalForm || portalForm });
    }
    if (url.endsWith("/api/admin/services")) {
      return jsonResponse({ success: true, services: overrides.portalServices || portalServices });
    }
    if (url.endsWith("/api/admin/forms")) {
      return jsonResponse({ success: true, forms: [overrides.portalForm || portalForm] });
    }
    if (url.endsWith("/api/admin/certificates")) {
      return jsonResponse({ success: true, certificates: [overrides.portalCertificate || portalCertificate] });
    }
    if (url.endsWith("/api/applications")) {
      if ((options.method || "GET").toUpperCase() === "POST") {
        const requestBody = JSON.parse(options.body);
        return jsonResponse({
          success: true,
          application: {
            ...portalApplication,
            status: "draft",
            current_stage: "Draft",
            form_values_json: requestBody.form_values,
            documents: [],
            payments: [],
            certificate: null,
          },
        }, 201);
      }
      return jsonResponse({ success: true, applications: [overrides.portalApplication || portalApplication] });
    }
    if (url.endsWith("/api/applications/app_portal_001")) {
      return jsonResponse({ success: true, application: overrides.portalApplication || portalApplication });
    }
    if (url.includes("/api/applications/app_portal_001/documents")) {
      return jsonResponse({ success: true, document: { id: "doc_uploaded", document_type: "aadhaar", file_name: "aadhaar.pdf" } }, 201);
    }
    if (url.endsWith("/api/applications/app_portal_001/submit")) {
      return jsonResponse({ success: true, application: { ...portalApplication, status: "payment_pending", current_stage: "Payment pending" } });
    }
    if (url.endsWith("/api/payments/app_portal_001/create")) {
      return jsonResponse({ success: true, payment: { id: "pay_001", amount: 35, payment_status: "created" } }, 201);
    }
    if (url.endsWith("/api/payments/pay_001/simulate-success")) {
      return jsonResponse({ success: true, payment: { id: "pay_001", amount: 35, payment_status: "paid" } });
    }
    if (url.endsWith("/api/officer/pending") || url.endsWith("/api/officer/applications")) {
      return jsonResponse({ success: true, applications: [overrides.portalApplication || portalApplication] });
    }
    if (url.endsWith("/api/officer/applications/app_portal_001/approve")) {
      return jsonResponse({
        success: true,
        application: {
          ...portalApplication,
          status: "certificate_issued",
          current_stage: "Certificate issued",
          certificate: portalCertificate,
        },
      });
    }
    if (url.endsWith("/api/officer/applications/app_portal_001/reject")) {
      return jsonResponse({ success: true, application: { ...portalApplication, status: "rejected", current_stage: "Rejected" } });
    }
    if (url.endsWith("/api/officer/applications/app_portal_001/request-documents")) {
      return jsonResponse({ success: true, application: { ...portalApplication, status: "documents_required", current_stage: "Documents requested" } });
    }
    if (url.endsWith("/api/track/NGSP-2026-INC-000001")) {
      return jsonResponse({
        success: true,
        tracking: {
          application_number: "NGSP-2026-INC-000001",
          service_name: "Income Certificate",
          status: "under_review",
          current_stage: "Officer review",
          due_date: "2026-07-16",
          sla: { status: "within_sla" },
          history: [
            { id: "hist_1", status: "draft", note: "Application draft created.", created_at: "2026-07-09T00:00:00+00:00" },
            { id: "hist_2", status: "under_review", note: "Payment completed.", created_at: "2026-07-09T00:05:00+00:00" },
          ],
        },
      });
    }
    if (url.endsWith("/api/certificates/verify/hash_demo")) {
      return jsonResponse({
        success: true,
        valid: true,
        message: "Certificate is valid.",
        certificate: portalCertificate,
        service_name: "Income Certificate",
        applicant_name: "Ravi Kumar",
      });
    }
    if (url.endsWith("/api/citizen/profile")) {
      return jsonResponse({
        success: true,
        profile: {
          id: "profile_001",
          user_id: "user_citizen",
          full_name: "Ravi Kumar",
          mobile: "9876543210",
          email: "citizen@niyamguard.local",
          district: "Hyderabad",
        },
      });
    }
    if (url.endsWith("/api/citizen/documents")) {
      return jsonResponse({ success: true, documents: [{ id: "citdoc_1", document_type: "aadhaar", file_name: "aadhaar.pdf", file_size: 2048 }] });
    }
    if (url.endsWith("/api/notifications")) {
      return jsonResponse({ success: true, notifications: [{ id: "not_1", title: "Application submitted", message: "NGSP-2026-INC-000001 is under review." }] });
    }
    if (url.endsWith("/api/demo/run")) {
      return jsonResponse({ success: true, summary: { findings: 4, priority_scores: 4, conflicts: 1 } });
    }
    if (url.includes("/api/reports/export") || url.includes("/api/demo/reports/export")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        headers: { get: () => "attachment; filename=test.csv" },
        json: () => Promise.resolve({ success: true }),
        blob: () => Promise.resolve(new Blob(["report"], { type: "text/csv" })),
      });
    }
    if (url.endsWith("/api/chat")) {
      return jsonResponse(overrides.chat || chatAnswer);
    }
    if (url.endsWith("/api/hybrid/answer")) {
      return jsonResponse(overrides.hybridDemoAnswer || hybridDemoAnswer);
    }
    if (url.endsWith("/api/ai/status")) {
      return jsonResponse(overrides.aiStatus || aiStatus);
    }
    if (url.endsWith("/api/ai/verified-explanation")) {
      return jsonResponse(overrides.verifiedAIExplanation || verifiedAIExplanation);
    }
    if (url.includes("/api/ai/finding/") && url.endsWith("/impact-summary")) {
      return jsonResponse(overrides.aiImpactSummary || aiImpactSummary);
    }
    if (url.endsWith("/api/dataset/status")) {
      return jsonResponse(overrides.datasetStatus || datasetStatus);
    }
    if (url.includes("/api/dataset/demo-flow")) {
      return jsonResponse(overrides.datasetFlow || datasetFlow);
    }
    if (url.endsWith("/api/dataset/qa")) {
      return jsonResponse(overrides.datasetAnswer || datasetAnswer);
    }
    if (url.endsWith("/api/forms")) {
      return jsonResponse({ success: true, forms: overrides.services || services });
    }
    if (url.endsWith("/api/compliance/run")) {
      return jsonResponse({ success: true, findings: complianceFindings });
    }
    if (url.endsWith("/api/integration/health")) {
      return jsonResponse({
        module: "niyamguard_government_core",
        status: "online",
        version: "1.0.0",
        features: [
          "verified_knowledge_base",
          "connected_systems_registry",
          "compliance_verification",
          "cascade_tracing",
          "priority_dashboard",
          "conflict_detection",
          "reports_export",
          "public_rule_api",
        ],
        counts: {
          verified_rules: 2,
          connected_systems: 5,
          findings: 4,
        },
      });
    }
    if (url.endsWith("/api/dashboard/summary")) {
      return jsonResponse({ success: true, summary: adminSummary });
    }
    if (url.includes("/api/public/rules/latest")) {
      return jsonResponse(overrides.publicRule || publicRule);
    }
    if (url.endsWith("/api/dashboard/recalculate-priority")) {
      return jsonResponse({ success: true, priority_findings: priorityFindings });
    }
    if (url.endsWith("/api/conflicts/scan")) {
      return jsonResponse({ success: true, conflicts });
    }
    if (url.endsWith("/api/admin/summary")) {
      return jsonResponse({ success: true, summary: adminSummary });
    }
    if (url.endsWith("/api/admin/module-status")) {
      return jsonResponse({
        success: true,
        modules: [
          { name: "central_verified_knowledge_base", status: "ready" },
          { name: "connected_systems_registry", status: "ready" },
          { name: "compliance_verification_engine", status: "ready" },
          { name: "cascade_tracing_impact_analysis", status: "ready" },
          { name: "priority_dashboard", status: "ready" },
          { name: "cross_circular_conflict_detection", status: "ready" },
          { name: "government_admin_apis", status: "ready" },
          { name: "reports_export_module", status: "ready" },
          { name: "public_verified_rule_apis", status: "ready" },
        ],
      });
    }
    if (url.endsWith("/api/connected-systems")) {
      return jsonResponse({ success: true, systems: connectedSystems });
    }
    if (url.endsWith("/api/compliance/findings")) {
      return jsonResponse({ success: true, findings: complianceFindings });
    }
    if (url.endsWith("/api/dashboard/priority-findings")) {
      return jsonResponse({ success: true, priority_findings: priorityFindings });
    }
    if (url.endsWith("/api/conflicts")) {
      return jsonResponse({ success: true, conflicts });
    }
    if (url.endsWith("/api/knowledge/rules")) {
      return jsonResponse({ success: true, rules: knowledgeRules });
    }
    if (url.endsWith("/api/reports/summary")) {
      return jsonResponse({
        success: true,
        summary: {
          circulars: 2,
          verified_rules: 2,
          connected_systems: 5,
          compliance_findings: 4,
          conflicts: 1,
          priority_scores: 4,
        },
      });
    }
    if (url.includes("/api/cascade/finding/")) {
      return jsonResponse({
        success: true,
        trace: {
          id: "trace_find_rule_001_sys_meeseva_portal",
          impact_summary: "Portal mismatch can cause wrong approval or rejection risk.",
          nodes_json: [
            { id: "node_1", label: "Circular Changed" },
            { id: "node_2", label: "Portal Not Updated" },
            { id: "node_3", label: "Citizen Applies Under Wrong Rule" },
          ],
          edges_json: [{ from: "node_1", to: "node_2" }],
        },
      });
    }
    if (url.includes("/api/services/search")) {
      return jsonResponse({ success: true, services: overrides.services || services });
    }
    if (url.endsWith("/api/services")) {
      return jsonResponse({ success: true, services: overrides.services || services });
    }
    if (url.endsWith("/api/forms/income-certificate")) {
      return jsonResponse({ success: true, form: incomeForm });
    }
    if (url.endsWith("/api/forms/income_certificate")) {
      return jsonResponse({ success: true, form: overrides.form || incomeForm });
    }
    if (url.endsWith("/api/forms/birth_certificate")) {
      return jsonResponse({ success: true, form: { ...incomeForm, form_id: "birth_certificate", service_name: "Birth Certificate" } });
    }
    if (url.endsWith("/api/sessions")) {
      const requestBody = JSON.parse(options.body);
      return jsonResponse({
        success: true,
        session_id:
          requestBody.form_id === "catalog" ? "catalog-session" : "session-123",
        form_id: requestBody.form_id,
        language: requestBody.language,
      }, 201);
    }
    if (url.endsWith("/api/tts/health")) {
      return jsonResponse({
        success: true,
        available_providers: ["browser", "gtts"],
        default_provider: "gtts",
        supported_languages: {
          telugu: "te-IN",
          hindi: "hi-IN",
          english: "en-IN",
        },
      });
    }
    if (url.endsWith("/api/tts/speak")) {
      if (overrides.ttsError) {
        return jsonResponse(
          {
            success: false,
            message:
              "TTS provider failed. Text response is available, but voice audio could not be generated.",
          },
          503,
        );
      }
      const requestBody = JSON.parse(options.body);
      return audioResponse("fake-mp3", {
        languageCode: requestBody.language_code,
      });
    }
    if (url.endsWith("/api/stt/transcribe")) {
      return jsonResponse(
        overrides.stt || {
          success: true,
          transcript: "purpose lo scholarship ani rayacha",
          detected_language: "telugu",
          language_code: "te-IN",
          confidence: 0.85,
          provider: "browser-fallback",
        },
      );
    }
    if (url.endsWith("/api/location/reverse")) {
      return jsonResponse(
        overrides.location || {
          success: true,
          detected_language: "english",
          language_code: "en-IN",
          reply:
            "Location permission received, but exact mandal lookup is not available in this MVP. Please enter a pincode or village name.",
          matches: [],
          auto_fill: false,
          should_submit: false,
        },
      );
    }
    if (url.endsWith("/api/assistant/ask")) {
      const requestBody = JSON.parse(options.body);
      const defaultResponse =
        requestBody.form_id === "catalog"
          ? {
              success: true,
              field: null,
              reply:
                "It looks like you may need the Income Certificate form.",
              suggested_form_id: "income_certificate",
              suggested_form_name: "Income Certificate",
              related_values: {},
              location_matches: [],
              warning: null,
              detected_language: "english",
              language_code: "en-IN",
              auto_fill: false,
              should_submit: false,
            }
          : {
              success: true,
              field: "monthly_income",
              reply:
                "You can enter 15000 in Monthly Income. If Annual Income is asked, enter 180000.",
              suggested_value: "15000",
              related_values: { annual_income: "180000" },
              location_matches: [],
              warning: null,
              detected_language: "english",
              language_code: "en-IN",
              auto_fill: false,
              should_submit: false,
            };
      return maybeDelay(
        (typeof overrides.ask === "function"
          ? overrides.ask(requestBody)
          : overrides.ask) || defaultResponse,
      );
    }
    if (url.endsWith("/api/assistant/summary")) {
      return jsonResponse(
        overrides.summary || {
          success: true,
          summary: "Please review your details.",
          missing_fields: [],
          missing_documents: [],
          warnings: [],
          detected_language: "english",
          language_code: "en-IN",
          auto_fill: false,
          should_submit: false,
        },
      );
    }
    if (url.endsWith("/api/assistant/validate")) {
      const requestBody = JSON.parse(options.body);
      return jsonResponse({
        success: true,
        field: requestBody.field,
        valid: true,
        message: `${requestBody.field} is valid.`,
        auto_fill: false,
        should_submit: false,
      });
    }
    return jsonResponse({ detail: "Not found" }, 404);
  });
  vi.stubGlobal("fetch", fetchMock);
  return { fetchMock };
}
