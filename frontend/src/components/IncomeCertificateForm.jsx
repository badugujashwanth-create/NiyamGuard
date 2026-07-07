import { useState } from "react";

import { validateInput } from "../services/api";

function inputType(field) {
  if (field.type === "number") return "number";
  if (field.type === "phone" || field.type === "aadhaar") return "text";
  return "text";
}

export default function IncomeCertificateForm({
  fields,
  values,
  onValueChange,
  onFieldFocus,
  onReview,
  loadingSummary,
  backendReady,
  language = "english",
}) {
  const [validation, setValidation] = useState({});
  const [submitNotice, setSubmitNotice] = useState("");

  async function handleBlur(field) {
    const value = values[field.key];
    if (!value?.toString().trim()) {
      setValidation((current) => ({ ...current, [field.key]: null }));
      return;
    }
    try {
      const result = await validateInput(field.key, value);
      setValidation((current) => ({ ...current, [field.key]: result }));
    } catch (error) {
      setValidation((current) => ({
        ...current,
        [field.key]: {
          valid: false,
          message: error.message,
        },
      }));
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    setSubmitNotice(
      "Demo only. No government application was submitted. On a real portal, review every value and use its submit button yourself.",
    );
  }

  const reviewLabel =
    language === "telugu"
      ? "వివరాలు చెక్ చేయండి"
      : language === "hindi"
        ? "विवरण जाँचें"
        : "Review My Details";

  return (
    <section className="form-card" aria-labelledby="form-title">
      <div className="card-header">
        <div>
          <p className="eyebrow">Citizen service form</p>
          <h2 id="form-title">Income Certificate Application</h2>
        </div>
        <span className="manual-badge">Manual entry only</span>
      </div>

      <p className="form-introduction">
        Enter your details yourself. Focus a field before asking the assistant so
        it can give more relevant guidance.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          {fields.map((field) => {
            const validationResult = validation[field.key];
            const sharedProps = {
              id: field.key,
              name: field.key,
              value: values[field.key] || "",
              required: field.required,
              onChange: (event) => {
                onValueChange(field.key, event.target.value);
                setValidation((current) => ({ ...current, [field.key]: null }));
                setSubmitNotice("");
              },
              onFocus: () => onFieldFocus(field.key),
              onBlur: () => handleBlur(field),
              "aria-describedby": `${field.key}-help ${field.key}-validation`,
            };

            return (
              <div
                className={`form-field ${field.type === "textarea" ? "field-wide" : ""}`}
                key={field.key}
              >
                <label htmlFor={field.key}>
                  {field.label}
                  {field.required ? <span aria-label="required"> *</span> : null}
                </label>
                {field.type === "textarea" ? (
                  <textarea {...sharedProps} rows="4" />
                ) : (
                  <input
                    {...sharedProps}
                    type={inputType(field)}
                    inputMode={
                      ["phone", "aadhaar", "number"].includes(field.type)
                        ? "numeric"
                        : undefined
                    }
                    min={field.type === "number" ? "1" : undefined}
                    autoComplete="off"
                  />
                )}
                <small id={`${field.key}-help`}>{field.help}</small>
                <div
                  className={`validation-message ${
                    validationResult?.valid ? "validation-valid" : "validation-invalid"
                  }`}
                  id={`${field.key}-validation`}
                  aria-live="polite"
                >
                  {validationResult?.message || ""}
                </div>
              </div>
            );
          })}
        </div>

        <div className="form-actions">
          <button
            className="button button-secondary"
            disabled={!backendReady || loadingSummary}
            onClick={onReview}
            type="button"
          >
            {loadingSummary ? "Preparing review…" : reviewLabel}
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
