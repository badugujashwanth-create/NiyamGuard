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
    if (url.endsWith("/api/ai/status")) {
      return jsonResponse(overrides.aiStatus || aiStatus);
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
