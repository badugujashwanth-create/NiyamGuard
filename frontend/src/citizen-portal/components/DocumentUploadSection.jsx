function documentHelp(document, language) {
  return document.help?.[language] || document.help?.english || "";
}

function formatFileSize(bytes) {
  if (!bytes) return "";
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export default function DocumentUploadSection({
  documents,
  language,
  uploadedDocuments,
  onDocumentChange,
  onDocumentFocus,
}) {
  function handleFile(document, file) {
    if (!file) {
      onDocumentChange(document.key, null);
      return;
    }
    const extension = file.name.split(".").pop()?.toLowerCase() || "";
    const allowed = document.accepted_file_types.map((item) =>
      item.toLowerCase(),
    );
    const maxBytes = document.max_size_mb * 1024 * 1024;
    let error = "";
    if (!allowed.includes(extension)) {
      error = `File type .${extension || "unknown"} is not accepted.`;
    } else if (file.size > maxBytes) {
      error = `File is too large. Max size is ${document.max_size_mb} MB.`;
    }

    onDocumentChange(document.key, {
      name: file.name,
      size: file.size,
      type: file.type,
      uploaded: !error,
      error,
    });
  }

  if (!documents?.length) return null;

  return (
    <section className="document-section" aria-labelledby="document-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Required documents</p>
          <h3 id="document-title">Upload guidance</h3>
        </div>
        <span>Demo/local only</span>
      </div>
      <div className="document-list">
        {documents.map((document) => {
          const status = uploadedDocuments[document.key];
          const accept = document.accepted_file_types
            .map((item) => `.${item}`)
            .join(",");
          return (
            <article className="document-item" key={document.key}>
              <div>
                <h4>
                  {document.label}
                  {document.required ? <span aria-label="required"> *</span> : null}
                </h4>
                <p>{documentHelp(document, language)}</p>
                <small>
                  Accepted: {document.accepted_file_types.join(", ")}. Max{" "}
                  {document.max_size_mb} MB. Examples:{" "}
                  {(document.examples || []).join(", ") || document.label}.
                </small>
              </div>
              <label className="file-control">
                <span>Select file manually</span>
                <input
                  accept={accept}
                  aria-label={`Upload ${document.label}`}
                  onChange={(event) =>
                    handleFile(document, event.target.files?.[0] || null)
                  }
                  onFocus={() => onDocumentFocus(`document:${document.key}`)}
                  type="file"
                />
              </label>
              {status ? (
                <p
                  className={`document-status ${
                    status.error ? "validation-invalid" : "validation-valid"
                  }`}
                  role="status"
                >
                  {status.error ||
                    `${status.name} selected manually (${formatFileSize(status.size)})`}
                </p>
              ) : null}
            </article>
          );
        })}
      </div>
    </section>
  );
}
