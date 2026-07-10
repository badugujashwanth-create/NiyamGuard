import { useCallback, useEffect, useMemo, useState } from "react";

import {
  askAssistant,
  askChat,
  createSession,
  generateSummary,
  getLatestPublicRule,
  reverseLocation,
} from "../../services/api";
import VoiceAssistantPanel from "./VoiceAssistantPanel";

function message(role, text) {
  return {
    id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    role,
    text,
  };
}

function detectQuestionLanguage(text) {
  const normalized = text.toLowerCase();
  if (/[\u0c00-\u0c7f]/.test(text) || /\b(entha|enti|aa|kavali|cheppandi|lo|kosam)\b/.test(normalized)) {
    return { detected_language: "telugu", language_code: "te-IN" };
  }
  if (/[\u0900-\u097f]/.test(text) || /\b(kya|kitne|hai|abhi|bataiye|anusaar|ke liye)\b/.test(normalized)) {
    return { detected_language: "hindi", language_code: "hi-IN" };
  }
  return { detected_language: "english", language_code: "en-IN" };
}

function isIncomeValidityQuestion(text, formId) {
  const normalized = text.toLowerCase();
  const mentionsValidity =
    /\b(validity|valid|months?|rule|entha)\b/.test(normalized) || /validity|valid/.test(normalized);
  const mentionsIncomeCertificate =
    /\b(income certificate|certificate|income)\b/.test(normalized) ||
    formId === "income_certificate";
  return mentionsValidity && mentionsIncomeCertificate;
}

function valueFromRuleResponse(ruleResponse) {
  const answer = ruleResponse?.answer || "";
  const match = answer.match(/currently\s+(.+?)\.?$/i);
  return match?.[1]?.replace(/\.$/, "") || "source not available";
}

function formatVerifiedRuleReply(ruleResponse, language) {
  const source = ruleResponse.source || {};
  const circular = source.circular_number || "source not available";
  const department = source.department || "department not available";
  const value = valueFromRuleResponse(ruleResponse);
  if (!ruleResponse?.verified) {
    if (language.detected_language === "telugu") {
      return "Verified rule source dorakaledu. Dayachesi official government source nunchi verify cheyyandi.";
    }
    if (language.detected_language === "hindi") {
      return "Verified rule source available nahi hai. Kripya official government source se verify karein.";
    }
    return "Verified rule source is not available. Please verify from the official government source.";
  }
  if (language.detected_language === "telugu") {
    return `ప్రస్తుత verified rule ప్రకారం Income Certificate validity ${value}. Source: ${circular}, ${department} Department.`;
  }
  if (language.detected_language === "hindi") {
    return `Verified rule के अनुसार Income Certificate validity अभी ${value} है. Source: ${circular}, ${department} Department.`;
  }
  return `According to the verified rule, Income Certificate validity is currently ${value}. Source: ${circular}, ${department} Department.`;
}

function sourceCardFromRule(ruleResponse) {
  const source = ruleResponse?.source;
  if (!source) return null;
  return {
    circular: source.circular_number,
    department: source.department,
    rule: "Income Certificate Validity",
    currentValue: valueFromRuleResponse(ruleResponse),
    confidence: source.confidence,
    effectiveDate: source.effective_date,
    sourceType: "verified_rule",
    verified: true,
    provider: "deterministic",
    whySelected: "Matched income certificate validity against the latest verified public rule.",
  };
}

function titleCase(value = "") {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function isCitizenKnowledgeQuestion(text, formId) {
  const normalized = text.toLowerCase();
  const asksFormFieldHelp =
    /\b(purpose|monthly income|field|box|mandal|pincode|what should i enter|rayacha|likhna)\b/.test(
      normalized,
    ) && !/\b(document|documents|docs|eligib|process|apply|validity|fee|timeline|old rule|new rule)\b/.test(normalized);
  if (asksFormFieldHelp) return false;
  const hasIntent =
    /\b(document|documents|docs|proof|eligib|qualify|process|apply|steps|validity|valid|fee|cost|timeline|days|old rule|new rule|compare|which service|which form)\b/.test(
      normalized,
    ) || /\b(enti|entha|kavali|kaise|kya)\b/.test(normalized);
  const hasKnownService =
    /\b(income certificate|residence certificate|caste certificate|community certificate|ews|scholarship|post matric|pension|old age|widow|disability|birth certificate|death certificate|family member|ration card|food security)\b/.test(
      normalized,
    ) || formId !== "catalog";
  return hasIntent && hasKnownService;
}

function sourceCardFromChat(chatResponse) {
  const firstReference = chatResponse?.source?.references?.[0] || {};
  return {
    circular:
      firstReference.circular_number ||
      firstReference.source_label ||
      firstReference.label ||
      chatResponse?.source?.label ||
      "NiyamGuard Knowledge Base",
    department: firstReference.department || "Citizen Services Knowledge",
    rule: titleCase(chatResponse?.intent || "Citizen Knowledge"),
    currentValue:
      firstReference.current_value ||
      titleCase(chatResponse?.scheme_or_service || chatResponse?.source?.type || "Guidance"),
    confidence: chatResponse?.confidence,
    effectiveDate: firstReference.effective_date,
    sourceType: chatResponse?.source?.type,
    method: chatResponse?.method,
    verified: Boolean(chatResponse?.verified),
    provider: chatResponse?.provider,
    fallback: Boolean(chatResponse?.fallback),
    whySelected: `Matched this question to ${titleCase(chatResponse?.intent || "knowledge")} guidance.`,
  };
}

export default function VoiceFormAssistant({
  serviceId,
  serviceName,
  formFields = [],
  requiredDocuments = [],
  activeField = "",
  activeDocument = "",
  onFieldFocus,
}) {
  const [sessionId, setSessionId] = useState("");
  const [sessionStatus, setSessionStatus] = useState("loading");
  const [messages, setMessages] = useState([]);
  const [assistantReply, setAssistantReply] = useState(null);
  const [speechCommand, setSpeechCommand] = useState(null);
  const [asking, setAsking] = useState(false);
  const [lastDetectedLanguage, setLastDetectedLanguage] = useState("english");
  const [lastLanguageCode, setLastLanguageCode] = useState("en-IN");
  const [error, setError] = useState("");

  const formId = serviceId || "income_certificate";

  useEffect(() => {
    let active = true;
    async function init() {
      setSessionStatus("loading");
      try {
        const session = await createSession("auto", formId);
        if (!active) return;
        setSessionId(session.session_id);
        setSessionStatus("ready");
      } catch (initError) {
        if (active) {
          setError(initError.message);
          setSessionStatus("error");
        }
      }
    }
    void init();
    return () => {
      active = false;
    };
  }, [formId]);

  const contextSummary = useMemo(
    () => ({
      service: serviceName || titleCase(formId),
      fields: formFields.map((field) => field.label || field.key).join(", "),
      documents: requiredDocuments.map((doc) => doc.label || doc.key).join(", "),
    }),
    [formFields, formId, requiredDocuments, serviceName],
  );

  function applyAssistantResponse(response) {
    const safeResponse = {
      ...response,
      suggested_value: response.auto_fill === false ? response.suggested_value : null,
      detected_language: response.detected_language || "english",
      language_code: response.language_code || "en-IN",
    };
    setAssistantReply(safeResponse);
    setLastDetectedLanguage(safeResponse.detected_language);
    setLastLanguageCode(safeResponse.language_code);
    setMessages((current) => [...current, message("assistant", safeResponse.reply)]);
    setSpeechCommand({
      id: `${Date.now()}-${Math.random()}`,
      text: safeResponse.reply,
      languageCode: safeResponse.language_code,
      detectedLanguage: safeResponse.detected_language,
    });
    return safeResponse;
  }

  const handleAsk = useCallback(
    async (text) => {
      if (!sessionId) {
        setError("The assistant session is not ready.");
        return null;
      }
      setAsking(true);
      setError("");
      setMessages((current) => [...current, message("user", text)]);
      try {
        if (isIncomeValidityQuestion(text, formId)) {
          const language = detectQuestionLanguage(text);
          const ruleResponse = await getLatestPublicRule("income_certificate", "validity");
          return applyAssistantResponse({
            success: Boolean(ruleResponse.success),
            reply: formatVerifiedRuleReply(ruleResponse, language),
            detected_language: language.detected_language,
            language_code: language.language_code,
            verified_rule: true,
            verified_source: sourceCardFromRule(ruleResponse),
            auto_fill: false,
          });
        }
        if (isCitizenKnowledgeQuestion(text, formId)) {
          const chatResponse = await askChat({
            message: text,
            language: "auto",
            context: { service_id: formId, form_id: formId, form_context: contextSummary },
            profile: {},
          });
          return applyAssistantResponse({
            success: Boolean(chatResponse.success),
            reply: chatResponse.answer,
            detected_language: chatResponse.language || "english",
            language_code: chatResponse.language_code || "en-IN",
            verified_rule: true,
            verified_source: sourceCardFromChat(chatResponse),
            auto_fill: false,
          });
        }
        const response = await askAssistant({
          sessionId,
          formId,
          message: text,
          currentField: activeField,
          currentDocument: activeDocument,
          lastVisibleSection: activeDocument ? "documents" : "details",
          language: "auto",
        });
        return applyAssistantResponse(response);
      } catch (askError) {
        setError(askError.message);
        const errorReply = "I could not contact the guidance service. Please try again.";
        setAssistantReply({ reply: errorReply, warning: askError.message });
        setMessages((current) => [...current, message("assistant", errorReply)]);
        return null;
      } finally {
        setAsking(false);
      }
    },
    [activeDocument, activeField, contextSummary, formId, sessionId],
  );

  async function handleUseLocation({ latitude, longitude }) {
    try {
      const response = await reverseLocation({
        latitude,
        longitude,
        language: lastDetectedLanguage || "auto",
      });
      return applyAssistantResponse(response);
    } catch (locationError) {
      setError(locationError.message);
      return null;
    }
  }

  return (
    <aside className="voice-form-assistant" aria-label="Voice Form Assistant">
      <div className="voice-form-assistant-heading">
        <p className="eyebrow">Voice Form Assistant</p>
        <h3>Help while filling this form</h3>
        <p>
          Ask by voice or text: &quot;What should I enter here?&quot;, &quot;Which documents are required?&quot;,
          &quot;Income certificate validity entha?&quot;
        </p>
        <ul className="voice-form-context">
          <li>Service: {contextSummary.service}</li>
          {contextSummary.documents ? <li>Documents: {contextSummary.documents}</li> : null}
        </ul>
      </div>
      {error ? <div className="global-error" role="alert">{error}</div> : null}
      <VoiceAssistantPanel
        activeDocument={activeDocument}
        activeField={activeField}
        asking={asking}
        assistantReply={assistantReply}
        formId={formId}
        lastDetectedLanguage={lastDetectedLanguage}
        lastLanguageCode={lastLanguageCode}
        messages={messages}
        onAsk={handleAsk}
        onFieldFocus={onFieldFocus}
        onUseLocation={handleUseLocation}
        sessionId={sessionId}
        sessionStatus={sessionStatus}
        speechCommand={speechCommand}
        title="Voice Form Assistant"
      />
    </aside>
  );
}
