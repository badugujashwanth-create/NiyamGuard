import { useEffect, useMemo, useState } from "react";

import {
  approvePortalApplication,
  createPortalApplication,
  createPortalPayment,
  getAccessToken,
  getCitizenDocuments,
  getCitizenProfile,
  getOfficerApplications,
  getOfficerPendingApplications,
  getPortalApplication,
  getPortalApplications,
  getPortalNotifications,
  getPortalService,
  getPortalServices,
  rejectPortalApplication,
  requestPortalDocuments,
  simulatePortalPaymentSuccess,
  submitPortalApplication,
  trackPortalApplication,
  updatePortalApplication,
  updateCitizenProfile,
  uploadPortalDocument,
  verifyPortalCertificate,
} from "../../services/api";

function titleCase(value = "") {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function statusTone(status = "") {
  if (["certificate_issued", "approved", "paid", "valid", "within_sla"].includes(status)) return "green";
  if (["rejected", "revoked", "failed", "overdue"].includes(status)) return "red";
  if (["payment_pending", "documents_required", "due_soon"].includes(status)) return "blue";
  return "neutral";
}

function Pill({ children, tone = "neutral" }) {
  return <span className={`portal-pill portal-pill-${tone}`}>{children}</span>;
}

function navigateTo(path) {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new Event("popstate"));
}

function RequiresLogin({ path }) {
  return (
    <section className="portal-panel">
      <h2>Sign in required</h2>
      <p>Use the demo citizen or officer account to continue this service workflow.</p>
      <a className="button button-primary" href={`/login?next=${encodeURIComponent(path)}`}>Sign In</a>
    </section>
  );
}

function FieldInput({ field, value, onChange }) {
  const type = field.type === "textarea" ? "textarea" : "input";
  const common = {
    id: field.key,
    onChange: (event) => onChange(field.key, event.target.value),
    required: Boolean(field.required),
    value: value || "",
  };
  return (
    <label className={field.type === "textarea" ? "portal-field portal-field-wide" : "portal-field"} htmlFor={field.key}>
      <span>{field.label}{field.required ? " *" : ""}</span>
      {type === "textarea" ? (
        <textarea {...common} rows="3" />
      ) : (
        <input {...common} type={field.type === "number" ? "number" : field.type === "date" ? "date" : "text"} />
      )}
    </label>
  );
}

function ServiceCard({ service }) {
  return (
    <article className="portal-card">
      <div>
        <div className="portal-card-heading">
          <span>{service.category}</span>
          <Pill tone={service.fee_amount ? "blue" : "green"}>
            {service.fee_amount ? `Rs ${service.fee_amount}` : "No fee"}
          </Pill>
        </div>
        <h3>{service.name}</h3>
        <p>{service.description}</p>
      </div>
      <dl>
        <div><dt>SLA</dt><dd>{service.processing_days} days</dd></div>
        <div><dt>Documents</dt><dd>{service.required_documents_json.length}</dd></div>
      </dl>
      <div className="portal-actions">
        <button className="button button-secondary" onClick={() => navigateTo(`/services/${service.service_id}`)} type="button">
          Details
        </button>
        <button className="button button-primary" onClick={() => navigateTo(`/apply/${service.service_id}`)} type="button">
          Apply
        </button>
      </div>
    </article>
  );
}

function ServicesPage() {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    getPortalServices()
      .then((response) => {
        if (active) setServices(response.services || []);
      })
      .catch((loadError) => {
        if (active) setError(loadError.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  return (
    <section className="portal-section">
      <div className="portal-summary">
        <div>
          <p className="eyebrow">Public service portal</p>
          <h2>Services</h2>
          <p>Apply through the synthetic NiyamGuard Service Portal and track each stage from draft to certificate.</p>
        </div>
        <Pill tone="green">{services.length} services</Pill>
      </div>
      {loading ? <p className="portal-loading">Loading services...</p> : null}
      {error ? <div className="global-error" role="alert">{error}</div> : null}
      <div className="portal-grid">
        {services.map((service) => <ServiceCard key={service.service_id} service={service} />)}
      </div>
    </section>
  );
}

function ServiceDetailPage({ serviceId }) {
  const [service, setService] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    getPortalService(serviceId)
      .then((response) => {
        if (active) setService(response.service);
      })
      .catch((loadError) => {
        if (active) setError(loadError.message);
      });
    return () => {
      active = false;
    };
  }, [serviceId]);

  if (error) return <div className="global-error" role="alert">{error}</div>;
  if (!service) return <p className="portal-loading">Loading service...</p>;
  return (
    <section className="portal-section">
      <div className="portal-summary">
        <div>
          <p className="eyebrow">{service.category}</p>
          <h2>{service.name}</h2>
          <p>{service.description}</p>
        </div>
        <button className="button button-primary" onClick={() => navigateTo(`/apply/${service.service_id}`)} type="button">
          Apply Now
        </button>
      </div>
      <div className="portal-two-column">
        <section className="portal-panel">
          <h3>Eligibility</h3>
          <ul>{service.eligibility_json.map((item) => <li key={item}>{item}</li>)}</ul>
        </section>
        <section className="portal-panel">
          <h3>Required Documents</h3>
          <ul>
            {service.required_documents_json.map((item) => (
              <li key={item.key}>{item.label} {item.required ? "(required)" : "(optional)"}</li>
            ))}
          </ul>
        </section>
      </div>
      <section className="portal-panel">
        <h3>Form Fields</h3>
        <div className="portal-field-preview">
          {service.form.fields_json.map((field) => (
            <span key={field.key}>{field.label}</span>
          ))}
        </div>
      </section>
    </section>
  );
}

function ApplyPage({ serviceId, path }) {
  const [service, setService] = useState(null);
  const [values, setValues] = useState({});
  const [application, setApplication] = useState(null);
  const [files, setFiles] = useState({});
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    getPortalService(serviceId)
      .then((response) => {
        if (active) setService(response.service);
      })
      .catch((loadError) => {
        if (active) setError(loadError.message);
      });
    return () => {
      active = false;
    };
  }, [serviceId]);

  if (!getAccessToken()) return <RequiresLogin path={path} />;
  if (error) return <div className="global-error" role="alert">{error}</div>;
  if (!service) return <p className="portal-loading">Loading application form...</p>;

  function updateValue(key, value) {
    setValues((current) => ({ ...current, [key]: value }));
  }

  async function handleCreateDraft(event) {
    event.preventDefault();
    setError("");
    setStatus(application ? "Updating draft..." : "Creating draft...");
    try {
      const payload = {
        service_id: service.service_id,
        form_values: values,
        district: values.district,
        mandal: values.mandal,
      };
      const response = application
        ? await updatePortalApplication(application.id, payload)
        : await createPortalApplication(payload);
      setApplication(response.application);
      setStatus(`Draft saved: ${response.application.application_number}`);
    } catch (createError) {
      setError(createError.message);
      setStatus("");
    }
  }

  async function handleUpload(documentType) {
    if (!application || !files[documentType]) return;
    setStatus(`Uploading ${documentType}...`);
    try {
      await uploadPortalDocument(application.id, documentType, files[documentType]);
      const refreshed = await getPortalApplication(application.id);
      setApplication(refreshed.application);
      setStatus("Document uploaded.");
    } catch (uploadError) {
      setError(uploadError.message);
      setStatus("");
    }
  }

  async function handleSubmitApplication() {
    if (!application) return;
    setStatus("Submitting application...");
    setError("");
    try {
      const response = await submitPortalApplication(application.id);
      setApplication(response.application);
      setStatus(`Submitted. Current stage: ${response.application.current_stage}`);
      if (response.application.status === "payment_pending") {
        navigateTo(`/payment/${response.application.id}`);
      }
    } catch (submitError) {
      setError(submitError.message);
      setStatus("");
    }
  }

  const uploadedTypes = new Set((application?.documents || []).map((item) => item.document_type));

  return (
    <section className="portal-section">
      <div className="portal-summary">
        <div>
          <p className="eyebrow">Citizen application</p>
          <h2>{service.name}</h2>
          <p>Complete the form, create a draft, upload documents, and submit it into officer review.</p>
        </div>
        {application ? <Pill tone={statusTone(application.status)}>{titleCase(application.status)}</Pill> : null}
      </div>
      {error ? <div className="global-error" role="alert">{error}</div> : null}
      {status ? <p className="portal-status">{status}</p> : null}
      <form className="portal-form" onSubmit={handleCreateDraft}>
        <div className="portal-form-grid">
          {service.form.fields_json.map((field) => (
            <FieldInput key={field.key} field={field} onChange={updateValue} value={values[field.key]} />
          ))}
        </div>
        <button className="button button-primary" type="submit">
          {application ? "Update Draft Values" : "Create Draft"}
        </button>
      </form>
      {application ? (
        <section className="portal-panel">
          <h3>Document Upload</h3>
          <div className="portal-documents">
            {service.required_documents_json.map((document) => (
              <div className="portal-document-row" key={document.key}>
                <div>
                  <strong>{document.label}</strong>
                  <span>{document.required ? "Required" : "Optional"} · PDF/JPG/PNG · 5 MB</span>
                </div>
                <input
                  aria-label={`Upload ${document.label}`}
                  onChange={(event) => setFiles((current) => ({ ...current, [document.key]: event.target.files?.[0] }))}
                  type="file"
                />
                <button className="button button-secondary" onClick={() => void handleUpload(document.key)} type="button">
                  {uploadedTypes.has(document.key) ? "Uploaded" : "Upload"}
                </button>
              </div>
            ))}
          </div>
          <button className="button button-primary" onClick={() => void handleSubmitApplication()} type="button">
            Submit Application
          </button>
        </section>
      ) : null}
    </section>
  );
}

function ApplicationsPage({ path }) {
  const [applications, setApplications] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!getAccessToken()) return;
    let active = true;
    Promise.all([getPortalApplications(), getPortalNotifications()])
      .then(([applicationResponse, notificationResponse]) => {
        if (!active) return;
        setApplications(applicationResponse.applications || []);
        setNotifications(notificationResponse.notifications || []);
      })
      .catch((loadError) => {
        if (active) setError(loadError.message);
      });
    return () => {
      active = false;
    };
  }, []);

  if (!getAccessToken()) return <RequiresLogin path={path} />;
  return (
    <section className="portal-section">
      <div className="portal-summary">
        <div>
          <p className="eyebrow">Citizen workspace</p>
          <h2>My Applications</h2>
          <p>Track submitted applications, pending payments, SLA state, evidence, and issued certificates.</p>
        </div>
        <Pill tone="blue">{applications.length} records</Pill>
      </div>
      {error ? <div className="global-error" role="alert">{error}</div> : null}
      <div className="portal-two-column">
        <section className="portal-panel">
          <h3>Applications</h3>
          <ApplicationList applications={applications} />
        </section>
        <section className="portal-panel">
          <h3>Notifications</h3>
          <ul className="portal-list">
            {notifications.length ? notifications.map((item) => (
              <li key={item.id}>
                <strong>{item.title}</strong>
                <span>{item.message}</span>
              </li>
            )) : <li><span>No notifications yet.</span></li>}
          </ul>
        </section>
      </div>
    </section>
  );
}

function ApplicationList({ applications, openPathPrefix = "/applications" }) {
  if (!applications.length) return <p className="empty-state">No applications found.</p>;
  return (
    <div className="portal-table-wrap">
      <table className="portal-table">
        <thead>
          <tr>
            <th>Application</th>
            <th>Service</th>
            <th>Status</th>
            <th>SLA</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {applications.map((application) => (
            <tr key={application.id}>
              <td>{application.application_number}</td>
              <td>{application.service?.name || titleCase(application.service_id)}</td>
              <td><Pill tone={statusTone(application.status)}>{titleCase(application.status)}</Pill></td>
              <td><Pill tone={statusTone(application.sla?.status)}>{titleCase(application.sla?.status || "not_started")}</Pill></td>
              <td>
                <button className="button button-secondary" onClick={() => navigateTo(`${openPathPrefix}/${application.id}`)} type="button">
                  Open
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ApplicationDetailPage({ applicationId, path }) {
  const [application, setApplication] = useState(null);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  async function refresh() {
    const response = await getPortalApplication(applicationId);
    setApplication(response.application);
  }

  useEffect(() => {
    if (!getAccessToken()) return;
    let active = true;
    getPortalApplication(applicationId)
      .then((response) => {
        if (active) setApplication(response.application);
      })
      .catch((loadError) => {
        if (active) setError(loadError.message);
      });
    return () => {
      active = false;
    };
  }, [applicationId]);

  if (!getAccessToken()) return <RequiresLogin path={path} />;
  if (error) return <div className="global-error" role="alert">{error}</div>;
  if (!application) return <p className="portal-loading">Loading application...</p>;

  return (
    <section className="portal-section">
      <div className="portal-summary">
        <div>
          <p className="eyebrow">{application.service?.name}</p>
          <h2>{application.application_number}</h2>
          <p>{application.current_stage}</p>
        </div>
        <Pill tone={statusTone(application.status)}>{titleCase(application.status)}</Pill>
      </div>
      {status ? <p className="portal-status">{status}</p> : null}
      <div className="portal-two-column">
        <section className="portal-panel">
          <h3>Application Details</h3>
          <PortalDefinitionList rows={[
            ["Status", titleCase(application.status)],
            ["Fee", application.service?.fee_amount ? `Rs ${application.service.fee_amount}` : "No fee"],
            ["Fee status", titleCase(application.fee_status)],
            ["Due date", application.due_date || "Not submitted"],
            ["SLA", titleCase(application.sla?.status || "not_started")],
          ]} />
          {application.status === "payment_pending" ? (
            <button className="button button-primary" onClick={() => navigateTo(`/payment/${application.id}`)} type="button">
              Pay Fee
            </button>
          ) : null}
        </section>
        <section className="portal-panel">
          <h3>Evidence</h3>
          <ul className="portal-list">
            {application.documents.map((document) => (
              <li key={document.id}>
                <strong>{titleCase(document.document_type)}</strong>
                <span>{document.file_name}</span>
                <Pill tone="blue">{document.verification_status}</Pill>
              </li>
            ))}
          </ul>
        </section>
      </div>
      {application.certificate ? (
        <section className="portal-panel">
          <h3>Certificate</h3>
          <PortalDefinitionList rows={[
            ["Certificate number", application.certificate.certificate_number],
            ["Status", titleCase(application.certificate.status)],
            ["Issued", application.certificate.issued_at],
            ["Expires", application.certificate.expires_at || "Not time limited"],
            ["Verification hash", application.certificate.verification_hash],
          ]} />
          <button
            className="button button-secondary"
            onClick={() => navigateTo(`/verify-certificate?query=${application.certificate.verification_hash}`)}
            type="button"
          >
            Verify Certificate
          </button>
        </section>
      ) : null}
      <button className="button button-secondary" onClick={() => void refresh().then(() => setStatus("Application refreshed."))} type="button">
        Refresh
      </button>
    </section>
  );
}

function PaymentPage({ applicationId, path }) {
  const [application, setApplication] = useState(null);
  const [payment, setPayment] = useState(null);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!getAccessToken()) return;
    let active = true;
    getPortalApplication(applicationId)
      .then((response) => {
        if (active) setApplication(response.application);
      })
      .catch((loadError) => {
        if (active) setError(loadError.message);
      });
    return () => {
      active = false;
    };
  }, [applicationId]);

  if (!getAccessToken()) return <RequiresLogin path={path} />;
  if (error) return <div className="global-error" role="alert">{error}</div>;
  if (!application) return <p className="portal-loading">Loading payment...</p>;

  async function handleCreatePayment() {
    setStatus("Creating sandbox payment...");
    const response = await createPortalPayment(application.id);
    setPayment(response.payment);
    setStatus("Sandbox payment ready.");
  }

  async function handleSuccess() {
    if (!payment) return;
    setStatus("Marking payment as successful...");
    await simulatePortalPaymentSuccess(payment.id);
    const refreshed = await getPortalApplication(application.id);
    setApplication(refreshed.application);
    setStatus("Payment successful. Application is under officer review.");
  }

  return (
    <section className="portal-section">
      <div className="portal-summary">
        <div>
          <p className="eyebrow">Payment sandbox</p>
          <h2>{application.application_number}</h2>
          <p>No real money is collected. This simulates a government fee gateway callback.</p>
        </div>
        <Pill tone={statusTone(application.fee_status)}>{titleCase(application.fee_status)}</Pill>
      </div>
      {status ? <p className="portal-status">{status}</p> : null}
      <section className="portal-panel">
        <PortalDefinitionList rows={[
          ["Service", application.service?.name],
          ["Amount", `Rs ${application.service?.fee_amount || 0}`],
          ["Current status", titleCase(application.status)],
          ["Fee status", titleCase(application.fee_status)],
        ]} />
        <div className="portal-actions">
          <button className="button button-secondary" onClick={() => void handleCreatePayment()} type="button">
            Create Sandbox Payment
          </button>
          <button className="button button-primary" disabled={!payment} onClick={() => void handleSuccess()} type="button">
            Simulate Success
          </button>
        </div>
      </section>
    </section>
  );
}

function TrackPage() {
  const [query, setQuery] = useState("");
  const [tracking, setTracking] = useState(null);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setTracking(null);
    try {
      const response = await trackPortalApplication(query.trim());
      setTracking(response.tracking);
    } catch (trackError) {
      setError(trackError.message);
    }
  }

  return (
    <section className="portal-section">
      <div className="portal-summary">
        <div>
          <p className="eyebrow">Public tracking</p>
          <h2>Track Application</h2>
          <p>Enter a NiyamGuard demo application number to view its current stage and SLA state.</p>
        </div>
      </div>
      <form className="portal-search-form" onSubmit={handleSubmit}>
        <label htmlFor="track-number">
          Application number
          <input id="track-number" onChange={(event) => setQuery(event.target.value)} value={query} />
        </label>
        <button className="button button-primary" type="submit">Track</button>
      </form>
      {error ? <div className="global-error" role="alert">{error}</div> : null}
      {tracking ? <TrackingResult tracking={tracking} /> : null}
    </section>
  );
}

function TrackingResult({ tracking }) {
  return (
    <section className="portal-panel">
      <h3>{tracking.application_number}</h3>
      <PortalDefinitionList rows={[
        ["Service", tracking.service_name],
        ["Status", titleCase(tracking.status)],
        ["Stage", tracking.current_stage],
        ["Due date", tracking.due_date || "Not submitted"],
        ["SLA", titleCase(tracking.sla?.status || "not_started")],
      ]} />
      <ul className="portal-list">
        {tracking.history.map((item) => (
          <li key={item.id}>
            <strong>{titleCase(item.status)}</strong>
            <span>{item.note || "Status updated"}</span>
            <em>{item.created_at}</em>
          </li>
        ))}
      </ul>
    </section>
  );
}

function VerifyCertificatePage() {
  const initial = new URLSearchParams(window.location.search).get("query") || "";
  const [query, setQuery] = useState(initial);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setResult(null);
    try {
      const response = await verifyPortalCertificate(query.trim());
      setResult(response);
    } catch (verifyError) {
      setError(verifyError.message);
    }
  }

  return (
    <section className="portal-section">
      <div className="portal-summary">
        <div>
          <p className="eyebrow">Public verification</p>
          <h2>Verify Certificate</h2>
          <p>Use the certificate number or verification hash printed on a demo certificate.</p>
        </div>
      </div>
      <form className="portal-search-form" onSubmit={handleSubmit}>
        <label htmlFor="certificate-query">
          Certificate number or hash
          <input id="certificate-query" onChange={(event) => setQuery(event.target.value)} value={query} />
        </label>
        <button className="button button-primary" type="submit">Verify</button>
      </form>
      {error ? <div className="global-error" role="alert">{error}</div> : null}
      {result ? (
        <section className="portal-panel">
          <h3>{result.valid ? "Certificate is valid" : "Not found in available dataset"}</h3>
          <p>{result.message}</p>
          {result.certificate ? (
            <PortalDefinitionList rows={[
              ["Certificate", result.certificate.certificate_number],
              ["Service", result.service_name],
              ["Applicant", result.applicant_name],
              ["Issued", result.certificate.issued_at],
              ["Status", titleCase(result.certificate.status)],
            ]} />
          ) : null}
        </section>
      ) : null}
    </section>
  );
}

function ProfilePage({ path }) {
  const [profile, setProfile] = useState(null);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!getAccessToken()) return;
    getCitizenProfile()
      .then((response) => setProfile(response.profile))
      .catch((loadError) => setError(loadError.message));
  }, []);

  if (!getAccessToken()) return <RequiresLogin path={path} />;
  if (error) return <div className="global-error" role="alert">{error}</div>;
  if (!profile) return <p className="portal-loading">Loading profile...</p>;

  async function handleSubmit(event) {
    event.preventDefault();
    const response = await updateCitizenProfile(profile);
    setProfile(response.profile);
    setStatus("Profile saved.");
  }

  return (
    <section className="portal-section">
      <div className="portal-summary">
        <div>
          <p className="eyebrow">Citizen profile</p>
          <h2>Profile</h2>
          <p>Profile data can prefill future demo applications.</p>
        </div>
      </div>
      {status ? <p className="portal-status">{status}</p> : null}
      <form className="portal-form" onSubmit={handleSubmit}>
        <div className="portal-form-grid">
          {["full_name", "mobile", "email", "date_of_birth", "district", "mandal", "village", "pincode", "address_line1"].map((key) => (
            <label className={key === "address_line1" ? "portal-field portal-field-wide" : "portal-field"} htmlFor={key} key={key}>
              <span>{titleCase(key)}</span>
              <input
                id={key}
                onChange={(event) => setProfile((current) => ({ ...current, [key]: event.target.value }))}
                value={profile[key] || ""}
              />
            </label>
          ))}
        </div>
        <button className="button button-primary" type="submit">Save Profile</button>
      </form>
    </section>
  );
}

function DocumentsPage({ path }) {
  const [documents, setDocuments] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!getAccessToken()) return;
    getCitizenDocuments()
      .then((response) => setDocuments(response.documents || []))
      .catch((loadError) => setError(loadError.message));
  }, []);

  if (!getAccessToken()) return <RequiresLogin path={path} />;
  return (
    <section className="portal-section">
      <div className="portal-summary">
        <div>
          <p className="eyebrow">Citizen documents</p>
          <h2>Document Vault</h2>
          <p>Uploaded application documents are listed from local demo storage.</p>
        </div>
        <Pill tone="blue">{documents.length} files</Pill>
      </div>
      {error ? <div className="global-error" role="alert">{error}</div> : null}
      <section className="portal-panel">
        <ul className="portal-list">
          {documents.length ? documents.map((document) => (
            <li key={document.id}>
              <strong>{titleCase(document.document_type)}</strong>
              <span>{document.file_name}</span>
              <em>{Math.round(document.file_size / 1024)} KB</em>
            </li>
          )) : <li><span>No uploaded documents yet.</span></li>}
        </ul>
      </section>
    </section>
  );
}

function OfficerPage({ path, applicationId }) {
  const [applications, setApplications] = useState([]);
  const [selected, setSelected] = useState(null);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const statusFilter = useMemo(() => {
    if (path.includes("/approved")) return "certificate_issued";
    if (path.includes("/rejected")) return "rejected";
    return "";
  }, [path]);

  async function load() {
    const response = path.includes("/pending")
      ? await getOfficerPendingApplications()
      : await getOfficerApplications(statusFilter);
    setApplications(response.applications || []);
    if (applicationId) {
      const applicationResponse = await getPortalApplication(applicationId);
      setSelected(applicationResponse.application);
    } else {
      setSelected(null);
    }
  }

  useEffect(() => {
    if (!getAccessToken()) return;
    let active = true;
    load()
      .catch((loadError) => {
        if (active) setError(loadError.message);
      });
    return () => {
      active = false;
    };
  }, [path, applicationId, statusFilter]);

  if (!getAccessToken()) return <RequiresLogin path={path} />;
  return (
    <section className="portal-section">
      <div className="portal-summary">
        <div>
          <p className="eyebrow">Officer workspace</p>
          <h2>Officer Review</h2>
          <p>Review submitted applications, request documents, approve certificates, and see SLA risk.</p>
        </div>
        <Pill tone="blue">{applications.length} applications</Pill>
      </div>
      {error ? <div className="global-error" role="alert">{error}</div> : null}
      {status ? <p className="portal-status">{status}</p> : null}
      <div className="portal-actions">
        <button className="button button-secondary" onClick={() => navigateTo("/officer/pending")} type="button">Pending</button>
        <button className="button button-secondary" onClick={() => navigateTo("/officer/approved")} type="button">Approved</button>
        <button className="button button-secondary" onClick={() => navigateTo("/officer/rejected")} type="button">Rejected</button>
      </div>
      <div className="portal-two-column">
        <section className="portal-panel">
          <h3>Queue</h3>
          <ApplicationList applications={applications} openPathPrefix="/officer/applications" />
        </section>
        {selected ? (
          <section className="portal-panel">
            <h3>{selected.application_number}</h3>
            <PortalDefinitionList rows={[
              ["Service", selected.service?.name],
              ["Applicant", selected.form_values_json?.applicant_name],
              ["Status", titleCase(selected.status)],
              ["SLA", titleCase(selected.sla?.status || "not_started")],
              ["Fee", titleCase(selected.fee_status)],
            ]} />
            <ul className="portal-list">
              {selected.documents.map((document) => (
                <li key={document.id}>
                  <strong>{titleCase(document.document_type)}</strong>
                  <span>{document.file_name}</span>
                </li>
              ))}
            </ul>
            <div className="portal-actions">
              <button
                className="button button-secondary"
                onClick={() => void requestPortalDocuments(selected.id, "Please upload clearer evidence.", ["address_proof"]).then(load).then(() => setStatus("Documents requested."))}
                type="button"
              >
                Request Documents
              </button>
              <button
                className="button button-secondary"
                onClick={() => void rejectPortalApplication(selected.id, "Evidence did not satisfy demo review.").then(load).then(() => setStatus("Application rejected."))}
                type="button"
              >
                Reject
              </button>
              <button
                className="button button-primary"
                onClick={() => void approvePortalApplication(selected.id, "Evidence accepted.").then(load).then(() => setStatus("Certificate issued."))}
                type="button"
              >
                Approve and Issue
              </button>
            </div>
          </section>
        ) : (
          <section className="portal-panel">
            <h3>Select an application</h3>
            <p>Open a queue record to review evidence and make a decision.</p>
          </section>
        )}
      </div>
    </section>
  );
}

function PortalDefinitionList({ rows }) {
  return (
    <dl className="portal-definition-list">
      {rows.map(([label, value]) => (
        <div key={label}>
          <dt>{label}</dt>
          <dd>{value || "Not found in available dataset"}</dd>
        </div>
      ))}
    </dl>
  );
}

export default function ServicePortal({ path }) {
  const segments = path.split("/").filter(Boolean);
  const first = segments[0] || "services";
  const second = segments[1];
  const third = segments[2];

  function renderPage() {
    if (first === "services" && second) return <ServiceDetailPage serviceId={second} />;
    if (first === "services") return <ServicesPage />;
    if (first === "apply" && second) return <ApplyPage path={path} serviceId={second} />;
    if (first === "applications" && second) return <ApplicationDetailPage applicationId={second} path={path} />;
    if (first === "applications") return <ApplicationsPage path={path} />;
    if (first === "track") return <TrackPage />;
    if (first === "verify-certificate") return <VerifyCertificatePage />;
    if (first === "payment" && second) return <PaymentPage applicationId={second} path={path} />;
    if (first === "citizen" && second === "profile") return <ProfilePage path={path} />;
    if (first === "citizen" && second === "documents") return <DocumentsPage path={path} />;
    if (first === "officer" && second === "applications" && third) return <OfficerPage applicationId={third} path={path} />;
    if (first === "officer") return <OfficerPage path={path} />;
    return <ServicesPage />;
  }

  return (
    <div className="portal-shell">
      <header className="portal-header">
        <div className="brand">
          <span className="brand-emblem" aria-hidden="true">NG</span>
          <div>
            <p>NiyamGuard Service Portal</p>
            <h1>Public Services</h1>
          </div>
        </div>
        <nav className="portal-nav" aria-label="Service portal">
          <button onClick={() => navigateTo("/services")} type="button">Services</button>
          <button onClick={() => navigateTo("/applications")} type="button">Applications</button>
          <button onClick={() => navigateTo("/track")} type="button">Track</button>
          <button onClick={() => navigateTo("/verify-certificate")} type="button">Verify</button>
          <button onClick={() => navigateTo("/officer")} type="button">Officer</button>
        </nav>
      </header>
      <main className="portal-main">
        {renderPage()}
      </main>
      <footer>
        Synthetic NiyamGuard demo portal. No official submission, payment, or certificate is sent to a government system.
      </footer>
    </div>
  );
}
