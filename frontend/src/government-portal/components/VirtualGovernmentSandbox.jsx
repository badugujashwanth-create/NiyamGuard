import { useEffect, useState } from "react";

import SpotlightCard from "../../shared/react-bits/SpotlightCard";
import {
  createSandboxCircular,
  downloadSandboxCircularPdf,
  publishSandboxCircular,
  generateSandboxCircularPdf,
  getPortalServices,
  getSandboxStatus,
  listSandboxCirculars,
} from "../../services/api";

const initialPayload = {
  department: "Revenue Department",
  circular_number: `GO-SBX-${new Date().getFullYear()}`,
  title: "Income Certificate Validity Update",
  service_affected: "Income Certificate",
  rule_key: "validity",
  old_value: "12 months",
  new_value: "6 months",
  effective_date: "",
  body:
    "The Revenue Department hereby notifies that Income Certificate validity is revised from 12 months to 6 months for scholarship and fee reimbursement applications.",
};

const ruleTemplates = [
  {
    key: "validity",
    label: "Validity period",
    oldValue: "12 months",
    newValue: "6 months",
    title: (service) => `${service.name} Validity Update`,
    body: (service, oldValue, newValue) =>
      `The ${service.department || service.category} hereby notifies that ${service.name} validity is revised from ${oldValue} to ${newValue}.`,
  },
  {
    key: "required_document",
    label: "Required document",
    oldValue: "Existing document list",
    newValue: "Aadhaar Card and current address proof required",
    title: (service) => `${service.name} Document Requirement Update`,
    body: (service, oldValue, newValue) =>
      `The ${service.department || service.category} updates ${service.name} document requirements from ${oldValue} to ${newValue}.`,
  },
  {
    key: "eligibility_age",
    label: "Eligibility age",
    oldValue: "60 years",
    newValue: "65 years",
    title: (service) => `${service.name} Eligibility Age Update`,
    body: (service, oldValue, newValue) =>
      `The ${service.department || service.category} revises ${service.name} eligibility age from ${oldValue} to ${newValue}.`,
  },
  {
    key: "income_limit",
    label: "Income limit",
    oldValue: "200000 rupees",
    newValue: "250000 rupees",
    title: (service) => `${service.name} Income Limit Update`,
    body: (service, oldValue, newValue) =>
      `The ${service.department || service.category} revises ${service.name} income limit from ${oldValue} to ${newValue}.`,
  },
  {
    key: "processing_time",
    label: "Processing time",
    oldValue: "30 days",
    newValue: "21 days",
    title: (service) => `${service.name} Processing Time Update`,
    body: (service, oldValue, newValue) =>
      `The ${service.department || service.category} revises ${service.name} processing time from ${oldValue} to ${newValue}.`,
  },
];

function fieldLabel(key) {
  return key.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function CircularRows({ circulars, onPublish, onGeneratePdf, onOpenPdf, runningId }) {
  return (
    <div className="admin-table-wrap">
      <table className="admin-table">
        <thead>
          <tr>
            <th>Circular ID</th>
            <th>Service affected</th>
            <th>What Changed</th>
            <th>Status</th>
            <th>Date</th>
            <th>Files</th>
          </tr>
        </thead>
        <tbody>
          {circulars.length ? circulars.map((circular) => (
            <tr key={circular.id}>
              <td>{circular.circular_number}</td>
              <td>{circular.service_affected}</td>
              <td>{circular.old_value} to {circular.new_value}</td>
              <td>{circular.delivery_status || circular.status}</td>
              <td>{circular.effective_date}</td>
              <td>
                <div className="admin-report-actions">
                  {circular.pdf_url ? (
                    <button
                      className="button button-secondary"
                      disabled={runningId === `open-${circular.id}`}
                      onClick={() => void onOpenPdf(circular.id)}
                      type="button"
                    >
                      Open PDF
                    </button>
                  ) : (
                    <button
                      className="button button-secondary"
                      disabled={runningId === circular.id}
                      onClick={() => void onGeneratePdf(circular.id)}
                      type="button"
                    >
                      Generate PDF
                    </button>
                  )}
                  <button
                    className="button button-primary"
                    disabled={!circular.pdf_url || runningId === circular.id}
                    onClick={() => void onPublish(circular.id)}
                    type="button"
                  >
                    Publish to NiyamGuard
                  </button>
                </div>
              </td>
            </tr>
          )) : (
            <tr><td colSpan="6">No sandbox circulars generated yet.</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default function VirtualGovernmentSandbox({ embedded = false }) {
  const [payload, setPayload] = useState(initialPayload);
  const [services, setServices] = useState([]);
  const [selectedServiceId, setSelectedServiceId] = useState("income_certificate");
  const [status, setStatus] = useState(null);
  const [circulars, setCirculars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [runningId, setRunningId] = useState("");
  const [error, setError] = useState("");
  const [lastPublish, setLastPublish] = useState(null);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [statusResponse, circularResponse] = await Promise.all([
        getSandboxStatus(),
        listSandboxCirculars(),
      ]);
      const serviceResponse = await getPortalServices();
      setStatus(statusResponse);
      setCirculars(circularResponse.circulars || []);
      setServices(serviceResponse.services || []);
    } catch (loadError) {
      setError(loadError.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  function updateField(key, value) {
    setPayload((current) => ({ ...current, [key]: value }));
  }

  function applyTemplate(serviceId, ruleKey = payload.rule_key) {
    const service = services.find((item) => item.service_id === serviceId) || services[0];
    const template = ruleTemplates.find((item) => item.key === ruleKey) || ruleTemplates[0];
    if (!service) return;
    setSelectedServiceId(service.service_id);
    setPayload((current) => {
      const oldValue = template.oldValue;
      const newValue = template.newValue;
      return {
        ...current,
        department: service.department || service.category,
        title: template.title(service),
        service_affected: service.name,
        rule_key: template.key,
        old_value: oldValue,
        new_value: newValue,
        body: template.body(service, oldValue, newValue),
      };
    });
  }

  async function createAndGenerate(event) {
    event.preventDefault();
    setError("");
    setLastPublish(null);
    setRunningId("new");
    try {
      const createResponse = await createSandboxCircular({
        ...payload,
        effective_date: payload.effective_date || null,
      });
      const circularId = createResponse.circular.id;
      setRunningId(circularId);
      await generateSandboxCircularPdf(circularId);
      await load();
    } catch (createError) {
      setError(createError.message);
    } finally {
      setRunningId("");
    }
  }

  async function generatePdf(circularId) {
    setError("");
    setRunningId(circularId);
    try {
      await generateSandboxCircularPdf(circularId);
      await load();
    } catch (pdfError) {
      setError(pdfError.message);
    } finally {
      setRunningId("");
    }
  }

  async function publishCircular(circularId) {
    setError("");
    setRunningId(circularId);
    try {
      const response = await publishSandboxCircular(circularId);
      setLastPublish(response);
      await load();
    } catch (publishError) {
      setError(publishError.message);
    } finally {
      setRunningId("");
    }
  }

  async function openPdf(circularId) {
    setError("");
    setRunningId(`open-${circularId}`);
    try {
      const blob = await downloadSandboxCircularPdf(circularId);
      const url = window.URL.createObjectURL(blob);
      window.open(url, "_blank", "noopener,noreferrer");
      window.setTimeout(() => window.URL.revokeObjectURL(url), 60_000);
    } catch (pdfError) {
      setError(pdfError.message);
    } finally {
      setRunningId("");
    }
  }

  const Shell = embedded ? "section" : "main";

  return (
    <Shell className="admin-main sandbox-page">
      <header className="admin-header">
        <div>
          <p className="eyebrow">Synthetic circular generator</p>
          <h1>Virtual Government Sandbox</h1>
        </div>
      </header>

      {error ? <div className="global-error" role="alert">{error}</div> : null}
      {loading ? <p className="admin-loading">Loading sandbox circulars...</p> : null}

      <section className="admin-section">
        <div className="admin-card-grid">
          <SpotlightCard as="article" className="admin-stat-card">
            <span>Circulars</span>
            <strong>{status?.circular_count || circulars.length || 0}</strong>
            <p>Generated in the sandbox holding area.</p>
          </SpotlightCard>
          <SpotlightCard as="article" className="admin-stat-card">
            <span>Latest state</span>
            <strong>{status?.latest_status || "none"}</strong>
            <p>Published circulars enter the government review pipeline.</p>
          </SpotlightCard>
        </div>
      </section>

      <section className="admin-section">
        <div className="admin-page-summary">
          <div>
            <h2>Generate Circular</h2>
            <p>Create a sandbox circular PDF, review it, then publish it to the government inbox.</p>
          </div>
        </div>
        <form className="admin-form-grid" onSubmit={createAndGenerate}>
          <label htmlFor="sandbox-service">
            Service
            <select
              id="sandbox-service"
              onChange={(event) => applyTemplate(event.target.value)}
              value={selectedServiceId}
            >
              {services.map((service) => (
                <option key={service.service_id} value={service.service_id}>
                  {service.name} - {service.department || service.category}
                </option>
              ))}
            </select>
          </label>
          <label htmlFor="sandbox-rule-template">
            Field Changed
            <select
              id="sandbox-rule-template"
              onChange={(event) => applyTemplate(selectedServiceId, event.target.value)}
              value={payload.rule_key}
            >
              {ruleTemplates.map((template) => (
                <option key={template.key} value={template.key}>{template.label}</option>
              ))}
            </select>
          </label>
          {Object.entries(payload).filter(([key]) => !["service_affected", "rule_key"].includes(key)).map(([key, value]) => (
            <label className={key === "body" ? "admin-form-wide" : ""} htmlFor={`sandbox-${key}`} key={key}>
              {fieldLabel(key)}
              {key === "body" ? (
                <textarea id={`sandbox-${key}`} onChange={(event) => updateField(key, event.target.value)} required value={value} />
              ) : (
                <input id={`sandbox-${key}`} onChange={(event) => updateField(key, event.target.value)} required type={key === "effective_date" ? "date" : "text"} value={value} />
              )}
            </label>
          ))}
          <div className="admin-form-wide admin-report-actions">
            <button className="button button-primary" disabled={Boolean(runningId)} type="submit">
              {runningId === "new" ? "Generating..." : "Generate PDF"}
            </button>
          </div>
        </form>
      </section>

      <section className="admin-section">
        <div className="admin-page-summary">
          <div>
            <h2>Sandbox Holding Area</h2>
            <p>Generated circulars remain in the sandbox until Publish to NiyamGuard is selected.</p>
          </div>
        </div>
        <CircularRows
          circulars={circulars}
          onPublish={publishCircular}
          onGeneratePdf={generatePdf}
          onOpenPdf={openPdf}
          runningId={runningId}
        />
      </section>

      {lastPublish ? (
        <section className="admin-section">
          <div className="admin-page-summary">
            <div>
              <h2>Government Delivery</h2>
              <p>{lastPublish.message || "Circular was delivered to the government inbox."}</p>
            </div>
            {lastPublish.circular?.pdf_url ? (
              <button className="button button-primary" onClick={() => void openPdf(lastPublish.circular.id)} type="button">
                Open PDF
              </button>
            ) : null}
          </div>
          <p>Government document: {lastPublish.government_document?.circular_number || "Delivered"}</p>
        </section>
      ) : null}
    </Shell>
  );
}
