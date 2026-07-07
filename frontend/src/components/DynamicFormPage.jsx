import { useMemo, useState } from "react";

import DocumentUploadSection from "./DocumentUploadSection";
import DynamicFieldRenderer from "./DynamicFieldRenderer";
import SafetyNotice from "./SafetyNotice";

function initialValidationState() {
  return {};
}

export default function DynamicFormPage({
  backendReady,
  form,
  language,
  loadingSummary,
  onBack,
  onDocumentChange,
  onFieldFocus,
  onReview,
  onValueChange,
  uploadedDocuments,
  values,
}) {
  const [validation, setValidation] = useState(initialValidationState);
  const [submitNotice, setSubmitNotice] = useState("");

  const requiredCount = form.fields.filter((field) => field.required).length;
  const completedRequired = useMemo(
    () =>
      form.fields.filter((field) => {
        if (!field.required) return false;
        const value = values[field.key];
        return typeof value === "boolean" ? value : Boolean(value?.toString().trim());
      }).length,
    [form.fields, values],
  );

  function setFieldValidation(field, result) {
    setValidation((current) => ({ ...current, [field]: result }));
  }

  function handleSubmit(event) {
    event.preventDefault();
    setSubmitNotice("Demo only. No government application was submitted.");
  }

  return (
    <section className="form-card" aria-labelledby="form-title">
      <div className="card-header">
        <div>
          <p className="eyebrow">{form.department}</p>
          <h2 id="form-title">{form.service_name} Application</h2>
          <p className="form-description">{form.description}</p>
        </div>
        <span className="manual-badge">Manual entry only</span>
      </div>

      <SafetyNotice />

      <div className="form-status-line">
        <span>
          Required details completed: {completedRequired}/{requiredCount}
        </span>
        <button className="text-button" onClick={onBack} type="button">
          Back to services
        </button>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          {form.fields.map((field) => (
            <DynamicFieldRenderer
              field={field}
              key={field.key}
              language={language}
              onFocus={onFieldFocus}
              onValidation={setFieldValidation}
              onValueChange={(key, value) => {
                onValueChange(key, value);
                setValidation((current) => ({ ...current, [key]: null }));
                setSubmitNotice("");
              }}
              validation={validation[field.key]}
              value={values[field.key]}
            />
          ))}
        </div>

        <DocumentUploadSection
          documents={form.required_documents}
          language={language}
          onDocumentChange={(key, value) => {
            onDocumentChange(key, value);
            setSubmitNotice("");
          }}
          onDocumentFocus={onFieldFocus}
          uploadedDocuments={uploadedDocuments}
        />

        <div className="form-actions">
          <button
            className="button button-secondary"
            disabled={!backendReady || loadingSummary}
            onClick={onReview}
            type="button"
          >
            {loadingSummary ? "Preparing review..." : "Review My Details"}
          </button>
          <button className="button button-primary" type="submit">
            Submit Manually (Demo)
          </button>
        </div>
        <p className="submit-notice" aria-live="polite">
          {submitNotice}
        </p>
      </form>
    </section>
  );
}
