import { validateInput } from "../services/api";

function inputType(field) {
  if (field.type === "number") return "number";
  if (field.type === "date") return "date";
  if (field.type === "phone" || field.type === "aadhaar") return "text";
  return "text";
}

function helpText(field, language) {
  if (typeof field.help === "string") return field.help;
  return field.help?.[language] || field.help?.english || "";
}

export default function DynamicFieldRenderer({
  field,
  language,
  value,
  validation,
  onFocus,
  onValidation,
  onValueChange,
}) {
  async function handleBlur() {
    if (field.type === "checkbox" && !value) {
      onValidation(field.key, null);
      return;
    }
    if (field.type !== "checkbox" && !value?.toString().trim()) {
      onValidation(field.key, null);
      return;
    }
    try {
      const result = await validateInput(field.key, value);
      onValidation(field.key, result);
    } catch (error) {
      onValidation(field.key, { valid: false, message: error.message });
    }
  }

  const sharedProps = {
    id: field.key,
    name: field.key,
    required: field.required,
    onFocus: () => onFocus(field.key),
    onBlur: () => void handleBlur(),
    "aria-describedby": `${field.key}-help ${field.key}-validation`,
  };

  let control;
  if (field.type === "textarea" || field.type === "address_group") {
    control = (
      <textarea
        {...sharedProps}
        onChange={(event) => onValueChange(field.key, event.target.value)}
        rows="4"
        value={value || ""}
      />
    );
  } else if (field.type === "select") {
    control = (
      <select
        {...sharedProps}
        onChange={(event) => onValueChange(field.key, event.target.value)}
        value={value || ""}
      >
        <option value="">Select</option>
        {(field.options || []).map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    );
  } else if (field.type === "radio") {
    control = (
      <fieldset className="radio-group" onFocus={() => onFocus(field.key)}>
        <legend className="sr-only">{field.label}</legend>
        {(field.options || []).map((option) => (
          <label className="radio-control" key={option}>
            <input
              checked={value === option}
              name={field.key}
              onBlur={() => void handleBlur()}
              onChange={() => onValueChange(field.key, option)}
              type="radio"
              value={option}
            />
            <span>{option}</span>
          </label>
        ))}
      </fieldset>
    );
  } else if (field.type === "checkbox") {
    control = (
      <label className="checkbox-control">
        <input
          {...sharedProps}
          checked={Boolean(value)}
          onChange={(event) => onValueChange(field.key, event.target.checked)}
          type="checkbox"
        />
        <span>{field.label}</span>
      </label>
    );
  } else {
    control = (
      <input
        {...sharedProps}
        autoComplete="off"
        inputMode={
          ["phone", "aadhaar", "number"].includes(field.type)
            ? "numeric"
            : undefined
        }
        min={field.type === "number" ? "1" : undefined}
        onChange={(event) => onValueChange(field.key, event.target.value)}
        type={inputType(field)}
        value={value || ""}
      />
    );
  }

  return (
    <div
      className={`form-field ${
        ["textarea", "address_group"].includes(field.type) ? "field-wide" : ""
      }`}
    >
      {field.type !== "checkbox" ? (
        <label htmlFor={field.key}>
          {field.label}
          {field.required ? <span aria-label="required"> *</span> : null}
        </label>
      ) : null}
      {control}
      <small id={`${field.key}-help`}>{helpText(field, language)}</small>
      <div
        className={`validation-message ${
          validation?.valid ? "validation-valid" : "validation-invalid"
        }`}
        id={`${field.key}-validation`}
        aria-live="polite"
      >
        {validation?.message || ""}
      </div>
    </div>
  );
}
