import { useMemo, useState } from "react";

import SafetyNotice from "./SafetyNotice";

export default function ServiceCatalog({
  services,
  loading,
  onAskCatalog,
  onSearch,
  onStart,
  assistantReply,
  asking,
}) {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("all");
  const [question, setQuestion] = useState("");

  const categories = useMemo(
    () => ["all", ...Array.from(new Set(services.map((item) => item.category)))],
    [services],
  );
  const visibleServices = useMemo(
    () =>
      services.filter(
        (service) => category === "all" || service.category === category,
      ),
    [category, services],
  );
  const suggestedService = assistantReply?.suggested_form_id
    ? services.find((service) => service.form_id === assistantReply.suggested_form_id)
    : null;
  const suggestedReady =
    suggestedService?.has_detailed_schema !== false &&
    suggestedService?.status !== "catalog_only";

  async function handleSearch(event) {
    const value = event.target.value;
    setQuery(value);
    await onSearch(value);
  }

  async function handleAsk(event) {
    event.preventDefault();
    const text = question.trim();
    if (!text) return;
    setQuestion("");
    await onAskCatalog(text);
  }

  return (
    <main className="catalog-page">
      <section className="catalog-header">
        <div>
          <p className="eyebrow">Citizen service catalog</p>
          <h2>Choose a simplified service form</h2>
          <p>
            Search for the certificate or service you need. The assistant can
            guide you, but you stay in control of every field and upload.
          </p>
        </div>
        <SafetyNotice />
      </section>

      <section className="catalog-tools" aria-label="Service search">
        <label>
          Search services
          <input
            onChange={(event) => void handleSearch(event)}
            placeholder="Example: income, scholarship, birth, residence"
            value={query}
          />
        </label>
        <label>
          Category
          <select
            onChange={(event) => setCategory(event.target.value)}
            value={category}
          >
            {categories.map((item) => (
              <option key={item} value={item}>
                {item === "all" ? "All categories" : item}
              </option>
            ))}
          </select>
        </label>
      </section>

      <section className="catalog-assistant" aria-labelledby="catalog-assistant-title">
        <div>
          <h3 id="catalog-assistant-title">Ask Assistant</h3>
          <p>Example: Scholarship kosam income certificate kavali</p>
        </div>
        <form onSubmit={(event) => void handleAsk(event)}>
          <input
            aria-label="Ask assistant about services"
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Tell the assistant what you need"
            value={question}
          />
          <button
            className="button button-primary"
            disabled={!question.trim() || asking}
            type="submit"
          >
            {asking ? "Asking..." : "Ask Assistant"}
          </button>
        </form>
        {assistantReply ? (
          <div className="catalog-reply" aria-live="polite">
            <p>{assistantReply.reply}</p>
            {assistantReply.suggested_form_id && suggestedReady ? (
              <button
                className="button button-secondary"
                onClick={() => onStart(assistantReply.suggested_form_id)}
                type="button"
              >
                Start {assistantReply.suggested_form_name}
              </button>
            ) : null}
            {assistantReply.suggested_form_id && !suggestedReady ? (
              <p className="coming-soon-note">
                Detailed guided form coming soon.
              </p>
            ) : null}
          </div>
        ) : null}
      </section>

      <section className="service-grid" aria-label="Available services">
        {loading ? <p className="empty-state">Loading services...</p> : null}
        {!loading && visibleServices.length === 0 ? (
          <p className="empty-state">No matching services found.</p>
        ) : null}
        {visibleServices.map((service) => (
          <article className="service-card" key={service.form_id}>
            <div>
              <div className="service-card-topline">
                <span>{service.category}</span>
                <strong
                  className={
                    service.status === "catalog_only"
                      ? "service-status service-status-coming"
                      : "service-status service-status-ready"
                  }
                >
                  {service.status === "catalog_only"
                    ? "Catalog only / coming soon"
                    : "Ready form"}
                </strong>
              </div>
              <h3>{service.service_name}</h3>
              <p>{service.description}</p>
              {service.common_use_cases?.length ? (
                <p className="service-use-cases">
                  Used for: {service.common_use_cases.join(", ")}
                </p>
              ) : null}
            </div>
            <div className="service-meta">
              <span>{service.department}</span>
              <span>
                {service.status === "catalog_only"
                  ? "Detailed form pending"
                  : `${service.required_document_count} documents`}
              </span>
            </div>
            <div className="service-actions">
              <button
                className="button button-primary"
                disabled={
                  service.status === "catalog_only" ||
                  service.has_detailed_schema === false
                }
                onClick={() => onStart(service.form_id)}
                type="button"
              >
                {service.status === "catalog_only"
                  ? "Detailed guided form coming soon"
                  : "Start Application"}
              </button>
              <button
                className="button button-secondary"
                onClick={() =>
                  void onAskCatalog(`I need help with ${service.service_name}`)
                }
                type="button"
              >
                Ask Assistant
              </button>
            </div>
          </article>
        ))}
      </section>
    </main>
  );
}
