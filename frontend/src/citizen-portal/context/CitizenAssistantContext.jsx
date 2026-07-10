import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import {
  askAssistant,
  askChat,
  createSession,
  getLatestPublicRule,
  reverseLocation,
} from "../../services/api";

function message(role, text) {
  return {
    id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    role,
    text,
  };
}

function titleCase(value = "") {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
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

function valueFromRuleResponse(ruleResponse) {
  const answer = ruleResponse?.answer || "";
  const match = answer.match(/currently\s+(.+?)\.?$/i);
  return match?.[1]?.replace(/\.$/, "") || "source not available";
}

function formatVerifiedRuleReply(ruleResponse) {
  const source = ruleResponse?.source || {};
  const circular = source.circular_number || "source not available";
  const department = source.department || "department not available";
  const value = valueFromRuleResponse(ruleResponse);
  if (!ruleResponse?.verified) {
    return "Verified rule source is not available. Please verify from the official government source.";
  }
  return `According to the verified rule, Income Certificate validity ${value}. Source: ${circular}, ${department} Department.`;
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

function isIncomeValidityQuestion(text, formId) {
  const normalized = text.toLowerCase();
  const mentionsValidity =
    /\b(validity|valid|months?|rule|entha)\b/.test(normalized) || /validity|valid/.test(normalized);
  const mentionsIncomeCertificate =
    /\b(income certificate|certificate|income)\b/.test(normalized) ||
    formId === "income_certificate";
  return mentionsValidity && mentionsIncomeCertificate;
}

function isFormFieldHelp(text) {
  return /\b(purpose|monthly income|annual income|field|box|mandal|pincode|what should i enter|what should i upload|rayacha|likhna)\b/i.test(
    text,
  );
}

function isCitizenKnowledgeQuestion(text, formId, mode) {
  const normalized = text.toLowerCase();
  if (mode === "form" && isFormFieldHelp(text)) return false;

  const hasIntent =
    /\b(document|documents|docs|proof|eligib|qualify|process|apply|steps|validity|valid|fee|cost|timeline|days|old rule|new rule|compare|which service|which form|status|track|tracking|application|certificate|verify|verification|hash|payment|sla)\b/.test(
      normalized,
    ) || /\b(enti|entha|kavali|kaise|kya)\b/.test(normalized);
  const hasKnownService =
    /\b(income certificate|residence certificate|caste certificate|community certificate|ews|scholarship|post matric|pension|old age|widow|disability|birth certificate|death certificate|family member|ration card|food security|certificate|application)\b/.test(
      normalized,
    ) || (formId && formId !== "catalog");

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
    lastUpdated: firstReference.last_updated,
    sourceType: chatResponse?.source?.type,
    sourceSourceType: firstReference.source_type,
    method: chatResponse?.method,
    sourceCount: chatResponse?.sources?.length || chatResponse?.source?.references?.length || 0,
    verified: Boolean(chatResponse?.verified),
    provider: chatResponse?.provider,
    fallback: Boolean(chatResponse?.fallback),
    whySelected: `Matched this question to ${titleCase(chatResponse?.intent || "knowledge")} guidance for ${titleCase(chatResponse?.scheme_or_service || "citizen services")}.`,
  };
}

export function defaultCitizenAssistantContextForPath(path = "/citizen") {
  const segments = path.split("/").filter(Boolean);
  const first = segments[0] || "citizen";
  const second = segments[1];

  if (path === "/citizen") {
    return {
      mode: "landing",
      routePath: path,
      formId: "income_certificate",
      serviceName: "Citizen Portal",
      lastVisibleSection: "landing",
    };
  }
  if (path.startsWith("/citizen/assistant")) {
    return {
      mode: "catalog",
      routePath: path,
      formId: "catalog",
      serviceName: "Guided Service Catalog",
      lastVisibleSection: "catalog",
    };
  }
  if (path.startsWith("/scheme-finder")) {
    return {
      mode: "scheme_finder",
      routePath: path,
      formId: "catalog",
      serviceName: "Scheme Finder",
      lastVisibleSection: "scheme_finder",
    };
  }
  if (first === "apply") {
    return {
      mode: "form",
      routePath: path,
      formId: second || "income_certificate",
      serviceName: titleCase(second || "income_certificate"),
      lastVisibleSection: "details",
    };
  }
  if (first === "verify-certificate") {
    return {
      mode: "verification",
      routePath: path,
      formId: "income_certificate",
      serviceName: "Certificate Verification",
      lastVisibleSection: "verification",
    };
  }
  if (first === "track") {
    return {
      mode: "tracking",
      routePath: path,
      formId: "income_certificate",
      serviceName: "Application Tracking",
      lastVisibleSection: "tracking",
    };
  }
  if (first === "applications") {
    return {
      mode: "applications",
      routePath: path,
      formId: "income_certificate",
      serviceName: "My Applications",
      lastVisibleSection: "applications",
    };
  }
  if (first === "payment") {
    return {
      mode: "payment",
      routePath: path,
      formId: "income_certificate",
      serviceName: "Payment Sandbox",
      lastVisibleSection: "payment",
    };
  }
  if (first === "services") {
    return {
      mode: second ? "service_detail" : "service_catalog",
      routePath: path,
      formId: second || "catalog",
      serviceName: second ? titleCase(second) : "Service Catalog",
      lastVisibleSection: "services",
    };
  }
  if (first === "citizen" && second === "profile") {
    return {
      mode: "profile",
      routePath: path,
      formId: "income_certificate",
      serviceName: "Citizen Profile",
      lastVisibleSection: "profile",
    };
  }
  if (first === "citizen" && second === "documents") {
    return {
      mode: "documents",
      routePath: path,
      formId: "income_certificate",
      serviceName: "Document Vault",
      lastVisibleSection: "documents",
    };
  }
  return {
    mode: "general",
    routePath: path,
    formId: "income_certificate",
    serviceName: "Citizen Services",
    lastVisibleSection: "general",
  };
}

function introForContext(pageContext) {
  if (pageContext.mode === "form") {
    return `Namaste. I am NiyamGuard Voice Assistant. I can help with the ${pageContext.serviceName || titleCase(pageContext.formId)} form, including fields, documents, and verified rules.`;
  }
  if (pageContext.mode === "verification") {
    return "Namaste. I am NiyamGuard Voice Assistant. I can help explain certificate numbers, verification hashes, validity, and how to verify a certificate.";
  }
  if (pageContext.mode === "tracking" || pageContext.mode === "applications") {
    return "Namaste. I am NiyamGuard Voice Assistant. I can help explain application status, documents, timelines, and certificate validity.";
  }
  if (pageContext.mode === "scheme_finder") {
    return "Namaste. I am NiyamGuard Voice Assistant. I can help explain services and documents while the Scheme Finder gives recommendations.";
  }
  return "Namaste. I am NiyamGuard Voice Assistant. I can help you find services, apply for certificates, track applications, and verify certificates.";
}

function placeholderForContext(pageContext) {
  if (pageContext.mode === "form") return "Example: What should I enter for monthly income?";
  if (pageContext.mode === "verification") return "Example: What does verification hash mean?";
  if (pageContext.mode === "tracking" || pageContext.mode === "applications") return "Example: How do I track my application status?";
  if (pageContext.mode === "scheme_finder") return "Example: Which documents are needed for scholarship?";
  return "Example: How do I apply for income certificate?";
}

const CitizenAssistantContext = createContext(null);

export function CitizenAssistantProvider({ children }) {
  const [pageContext, setPageContext] = useState(() => defaultCitizenAssistantContextForPath(window.location.pathname));
  const [sessionId, setSessionId] = useState("");
  const [sessionStatus, setSessionStatus] = useState("loading");
  const [messages, setMessages] = useState([]);
  const [assistantReply, setAssistantReply] = useState(null);
  const [speechCommand, setSpeechCommand] = useState(null);
  const [asking, setAsking] = useState(false);
  const [lastDetectedLanguage, setLastDetectedLanguage] = useState("english");
  const [lastLanguageCode, setLastLanguageCode] = useState("en-IN");
  const [error, setError] = useState("");

  const formId = pageContext.formId || "income_certificate";

  const setRoutePath = useCallback((path) => {
    setPageContext(defaultCitizenAssistantContextForPath(path));
  }, []);

  const updatePageContext = useCallback((context) => {
    setPageContext((current) => ({
      ...current,
      ...context,
      formId: context.formId || current.formId || "income_certificate",
    }));
  }, []);

  useEffect(() => {
    let active = true;
    async function initializeSession() {
      setSessionStatus("loading");
      setError("");
      try {
        const session = await createSession("auto", formId);
        if (!active) return;
        setSessionId(session.session_id);
        setSessionStatus("ready");
      } catch (initError) {
        if (!active) return;
        setSessionId("");
        setSessionStatus("error");
        setError(initError.message);
      }
    }
    void initializeSession();
    return () => {
      active = false;
    };
  }, [formId]);

  const applyAssistantResponse = useCallback((response) => {
    const safeResponse = {
      ...response,
      suggested_value: response?.auto_fill === false ? response.suggested_value : null,
      detected_language: response?.detected_language || response?.language || "english",
      language_code: response?.language_code || "en-IN",
      reply: response?.reply || response?.answer || "No answer returned.",
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
  }, []);

  const ask = useCallback(
    async (text) => {
      const cleaned = text.trim();
      if (!cleaned) return null;
      if (!sessionId) {
        setError("The assistant session is not ready.");
        return null;
      }
      setAsking(true);
      setError("");
      setMessages((current) => [...current, message("user", cleaned)]);
      try {
        if (isIncomeValidityQuestion(cleaned, formId)) {
          const language = detectQuestionLanguage(cleaned);
          const ruleResponse = await getLatestPublicRule("income_certificate", "validity");
          return applyAssistantResponse({
            success: Boolean(ruleResponse.success),
            field: null,
            reply: formatVerifiedRuleReply(ruleResponse, language),
            suggested_value: null,
            related_values: {},
            location_matches: [],
            warning: ruleResponse.source
              ? null
              : "Source not available. Please verify from official government source.",
            detected_language: language.detected_language,
            language_code: language.language_code,
            auto_fill: false,
            should_submit: false,
            verified_rule: true,
            verified_source: sourceCardFromRule(ruleResponse),
          });
        }

        const useCatalogAssistant =
          formId === "catalog" &&
          ["catalog", "service_catalog", "service_detail"].includes(pageContext.mode);
        const useFormAssistant = pageContext.mode === "form" && !isCitizenKnowledgeQuestion(cleaned, formId, pageContext.mode);

        if (useCatalogAssistant || useFormAssistant) {
          const response = await askAssistant({
            sessionId,
            formId,
            message: cleaned,
            currentField: pageContext.activeField,
            currentDocument: pageContext.activeDocument,
            lastVisibleSection: pageContext.lastVisibleSection,
            language: "auto",
          });
          return applyAssistantResponse(response);
        }

        const chatResponse = await askChat({
          message: cleaned,
          language: "auto",
          context: {
            route: pageContext.routePath,
            page_mode: pageContext.mode,
            service_id: formId === "catalog" ? undefined : formId,
            form_id: formId,
            service_name: pageContext.serviceName,
            active_field: pageContext.activeField,
            active_document: pageContext.activeDocument,
          },
          profile: {},
        });
        return applyAssistantResponse({
          success: Boolean(chatResponse.success),
          field: null,
          reply: chatResponse.answer,
          suggested_value: null,
          related_values: {},
          location_matches: [],
          warning: chatResponse.fallback
            ? "No verified source was available for this question."
            : null,
          detected_language: chatResponse.language || "english",
          language_code: chatResponse.language_code || "en-IN",
          auto_fill: false,
          should_submit: false,
          verified_rule: true,
          verified_source: sourceCardFromChat(chatResponse),
        });
      } catch (askError) {
        setError(askError.message);
        return applyAssistantResponse({
          success: false,
          reply: "I could not contact the guidance service. Please try again.",
          warning: askError.message,
          detected_language: "english",
          language_code: "en-IN",
          auto_fill: false,
        });
      } finally {
        setAsking(false);
      }
    },
    [applyAssistantResponse, formId, pageContext, sessionId],
  );

  const clear = useCallback(async () => {
    setMessages([]);
    setAssistantReply(null);
    setSpeechCommand(null);
    setLastDetectedLanguage("english");
    setLastLanguageCode("en-IN");
    setSessionStatus("loading");
    try {
      const session = await createSession("auto", formId);
      setSessionId(session.session_id);
      setSessionStatus("ready");
    } catch (clearError) {
      setError(clearError.message);
      setSessionStatus("error");
    }
  }, [formId]);

  const useLocation = useCallback(
    async ({ latitude, longitude }) => {
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
    },
    [applyAssistantResponse, lastDetectedLanguage],
  );

  const value = useMemo(
    () => ({
      ask,
      asking,
      assistantReply,
      clear,
      error,
      formId,
      introText: introForContext(pageContext),
      lastDetectedLanguage,
      lastLanguageCode,
      messages,
      pageContext,
      placeholder: placeholderForContext(pageContext),
      publishAssistantReply: applyAssistantResponse,
      sessionId,
      sessionStatus,
      setRoutePath,
      speechCommand,
      updatePageContext,
      useLocation,
    }),
    [
      ask,
      asking,
      assistantReply,
      clear,
      error,
      formId,
      lastDetectedLanguage,
      lastLanguageCode,
      messages,
      pageContext,
      applyAssistantResponse,
      sessionId,
      sessionStatus,
      setRoutePath,
      speechCommand,
      updatePageContext,
      useLocation,
    ],
  );

  return (
    <CitizenAssistantContext.Provider value={value}>
      {children}
    </CitizenAssistantContext.Provider>
  );
}

export function useCitizenAssistant() {
  const context = useContext(CitizenAssistantContext);
  if (!context) {
    throw new Error("useCitizenAssistant must be used inside CitizenAssistantProvider");
  }
  return context;
}

export function useCitizenAssistantPageContext(pageContext) {
  const { updatePageContext } = useCitizenAssistant();
  const serializedContext = JSON.stringify(pageContext);
  useEffect(() => {
    updatePageContext(pageContext);
  }, [serializedContext, updatePageContext]);
}
