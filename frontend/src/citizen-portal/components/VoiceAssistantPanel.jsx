import { useCallback, useEffect, useRef, useState } from "react";

import { useSpeechRecognition } from "../../hooks/useSpeechRecognition";
import { useSpeechSynthesis } from "../../hooks/useSpeechSynthesis";
import { transcribeAudio } from "../../services/api";
import { SPEECH_FALLBACK_MESSAGE } from "../../services/speechService";
import AssistantTranscript from "./AssistantTranscript";

const INTRO_TEXT =
  "Namaste. I am NiyamGuard Voice Assistant. I will help you fill this form step by step. You can speak in Telugu, Hindi, or English. Tell me where you need help.";

const VOICE_LANGUAGES = [
  { code: "en-IN", language: "english", label: "English", whisper: "en" },
  { code: "te-IN", language: "telugu", label: "తెలుగు", whisper: "te" },
  { code: "hi-IN", language: "hindi", label: "हिन्दी", whisper: "hi" },
  { code: "auto", language: "auto", label: "Auto-detect", whisper: "auto" },
];

const LOCALIZED_INTROS = {
  telugu:
    "నమస్తే. నేను నియమ్‌గార్డ్ వాయిస్ అసిస్టెంట్‌ని. నేను మీకు దశలవారీగా సహాయం చేస్తాను. మీరు తెలుగులో మాట్లాడవచ్చు. మీకు ఏ సహాయం కావాలో చెప్పండి.",
  hindi:
    "नमस्ते। मैं नियमगार्ड वॉइस असिस्टेंट हूँ। मैं आपको चरण-दर-चरण सहायता दूँगा। आप हिन्दी में बोल सकते हैं। बताइए आपको किस विषय में मदद चाहिए।",
};

const DEFAULT_RECORDING_MS = 5500;
const PREFER_BROWSER_STT_FOR_TELUGU =
  String(import.meta.env.VITE_PREFER_BROWSER_STT_FOR_TELUGU || "true").toLowerCase() !== "false";

function recordingWindowMs() {
  const configured = Number(import.meta.env.VITE_STT_RECORDING_MS || DEFAULT_RECORDING_MS);
  return Number.isFinite(configured) ? Math.min(8000, Math.max(3000, configured)) : DEFAULT_RECORDING_MS;
}

const STATE_LABELS = {
  idle: "Stopped",
  intro_speaking: "Speaking...",
  listening: "Listening...",
  processing: "Thinking...",
  speaking: "Speaking...",
  stopped: "Stopped",
  error: "Could not hear clearly, please repeat",
};

function sourceBadges(source) {
  const badges = [];
  if (source?.method === "exact_rule_engine") badges.push("Exact Rule");
  if (source?.method === "decision_table") badges.push("Decision Table");
  if (source?.method === "rag_search") badges.push("RAG Search");
  if (source?.method === "local_llm") badges.push("Local LLM");
  if (source?.method === "safe_fallback") badges.push("Safe Fallback");
  if (source?.sourceType === "certificate_baseline") badges.push("Certificate Baseline");
  if (source?.sourceType === "verified_rule") badges.push("Verified Rule");
  if (source?.sourceType === "rag") badges.push("RAG Source");
  if (source?.sourceSourceType === "seed_demo" || /seed/i.test(source?.circular || "")) {
    badges.push("Seed Demo Data");
  }
  if (source?.provider === "ollama") badges.push("Ollama AI");
  if (source?.fallback || source?.provider === "fallback") badges.push("Fallback");
  return [...new Set(badges)];
}

export default function VoiceAssistantPanel({
  messages,
  assistantReply,
  speechCommand,
  onAsk,
  onUseLocation,
  sessionStatus,
  asking,
  lastDetectedLanguage = "english",
  lastLanguageCode = "en-IN",
  sessionId = "",
  formId = "income_certificate",
  activeField = "",
  activeDocument = "",
  introText = INTRO_TEXT,
  textPlaceholder = "Example: What should I enter for monthly income?",
}) {
  const [assistantState, setAssistantState] = useState("idle");
  const [textMessage, setTextMessage] = useState("");
  const [lastHeard, setLastHeard] = useState("");
  const [statusMessage, setStatusMessage] = useState("Stopped");
  const [selectedLanguageCode, setSelectedLanguageCode] = useState("en-IN");
  const [sttWarning, setSttWarning] = useState("");
  const [sttMetrics, setSttMetrics] = useState(null);
  const [locationStatus, setLocationStatus] = useState("");
  const [pincode, setPincode] = useState("");
  const activeRef = useRef(false);
  const introSpokenRef = useRef(false);
  const mediaStreamRef = useRef(null);
  const recorderRef = useRef(null);
  const recordTimerRef = useRef(null);
  const silenceMonitorRef = useRef(null);
  const audioContextRef = useRef(null);
  const chunksRef = useRef([]);
  const useBrowserFallbackRef = useRef(false);
  const processingTranscriptRef = useRef("");
  const lastSpeechCommandRef = useRef(null);
  const failedAttemptsRef = useRef(0);
  const resumeBrowserAfterSpeechRef = useRef(false);
  const {
    isSpeaking,
    error: synthesisError,
    lastVoiceWarning,
    speak,
    stop: stopSpeaking,
  } = useSpeechSynthesis();

  const selectedLanguage =
    VOICE_LANGUAGES.find((option) => option.code === selectedLanguageCode) || VOICE_LANGUAGES[0];
  const recognitionLanguageCode =
    selectedLanguage.code === "auto" ? lastLanguageCode || "en-IN" : selectedLanguage.code;

  async function processTranscript(transcript, source = "voice") {
    const cleaned = transcript.trim();
    if (!cleaned || cleaned.length < 3) {
      failedAttemptsRef.current += 1;
      setAssistantState("error");
      setStatusMessage(
        failedAttemptsRef.current >= 2
          ? "I could not hear clearly. Please repeat, or use the typing fallback below."
          : "I could not hear clearly. Please repeat.",
      );
      if (activeRef.current) window.setTimeout(startListening, 900);
      return;
    }
    if (cleaned === processingTranscriptRef.current) return;
    processingTranscriptRef.current = cleaned;
    failedAttemptsRef.current = 0;
    setLastHeard(cleaned);
    setAssistantState("processing");
    setStatusMessage("Thinking...");
    pauseBrowserRecognition();
    try {
      const response = await onAsk(cleaned, {
        source,
        language: selectedLanguage.language,
        languageCode: recognitionLanguageCode,
      });
      if (!response) {
        throw new Error("The assistant did not return a response.");
      }
    } catch (requestError) {
      setAssistantState("error");
      setStatusMessage(
        requestError?.message || "Assistant request failed. Review the error below and try again.",
      );
      if (activeRef.current) window.setTimeout(startListening, 1200);
    } finally {
      processingTranscriptRef.current = "";
    }
  }

  const {
    supported: browserRecognitionSupported,
    isListening: browserListening,
    transcript: browserTranscript,
    error: browserSpeechError,
    start: startBrowserRecognition,
    stop: stopBrowserRecognition,
    pause: pauseBrowserRecognition,
    resume: resumeBrowserRecognition,
    clearTranscript,
    support: speechSupport,
  } = useSpeechRecognition({
    languageCode: recognitionLanguageCode,
    onFinalTranscript: (transcript) => {
      if (useBrowserFallbackRef.current && activeRef.current) {
        void processTranscript(transcript, "browser-fallback");
      }
    },
  });

  const cleanupSilenceMonitor = useCallback(() => {
    clearInterval(silenceMonitorRef.current);
    silenceMonitorRef.current = null;
    const context = audioContextRef.current;
    audioContextRef.current = null;
    if (context && context.state !== "closed") {
      void context.close().catch(() => {});
    }
  }, []);

  const monitorRecordingSilence = useCallback((recorder, stream) => {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) return;
    try {
      const context = new AudioContextClass();
      const analyser = context.createAnalyser();
      analyser.fftSize = 1024;
      context.createMediaStreamSource(stream).connect(analyser);
      const samples = new Uint8Array(analyser.fftSize);
      const startedAt = performance.now();
      let heardVoice = false;
      let silenceStartedAt = null;
      audioContextRef.current = context;
      silenceMonitorRef.current = window.setInterval(() => {
        if (recorder.state === "inactive") return;
        analyser.getByteTimeDomainData(samples);
        const rms = Math.sqrt(
          samples.reduce((sum, sample) => {
            const normalized = (sample - 128) / 128;
            return sum + normalized * normalized;
          }, 0) / samples.length,
        );
        const now = performance.now();
        if (rms >= 0.022) {
          heardVoice = true;
          silenceStartedAt = null;
        } else if (heardVoice && now - startedAt >= 900) {
          silenceStartedAt ??= now;
          if (now - silenceStartedAt >= 850) recorder.stop();
        }
      }, 100);
    } catch {
      cleanupSilenceMonitor();
    }
  }, [cleanupSilenceMonitor]);

  const cleanupRecording = useCallback(() => {
    clearTimeout(recordTimerRef.current);
    recordTimerRef.current = null;
    if (recorderRef.current && recorderRef.current.state !== "inactive") {
      try {
        recorderRef.current.stop();
      } catch {
        // Recorder may already be stopping.
      }
    }
    recorderRef.current = null;
    cleanupSilenceMonitor();
  }, [cleanupSilenceMonitor]);

  const stopAllListening = useCallback(() => {
    cleanupRecording();
    stopBrowserRecognition();
  }, [cleanupRecording, stopBrowserRecognition]);

  const speakAndMaybeResume = useCallback(
    async (text, languageCode, detectedLanguage) => {
      stopAllListening();
      setAssistantState("speaking");
      setStatusMessage("Speaking...");
      resumeBrowserAfterSpeechRef.current = useBrowserFallbackRef.current;
      await speak(text, {
        languageCode: languageCode || "en-IN",
        detectedLanguage: detectedLanguage || "english",
        onComplete: () => {
          setAssistantState(activeRef.current ? "listening" : "stopped");
          setStatusMessage(activeRef.current ? "Listening..." : "Stopped");
          if (activeRef.current) {
            startListening();
          }
        },
      });
    },
    [speak, stopAllListening],
  );

  async function startBackendRecording() {
    if (!activeRef.current) return;
    if (!speechSupport.secureContext) {
      activeRef.current = false;
      setAssistantState("stopped");
      setStatusMessage("Voice input needs localhost or HTTPS. You can continue using text.");
      return;
    }
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
      useBrowserFallbackRef.current = true;
      startBrowserFallback();
      return;
    }

    try {
      if (!mediaStreamRef.current) {
        mediaStreamRef.current = await navigator.mediaDevices.getUserMedia({ audio: true });
      }
      chunksRef.current = [];
      const recorder = new MediaRecorder(mediaStreamRef.current, {
        mimeType: MediaRecorder.isTypeSupported?.("audio/webm") ? "audio/webm" : undefined,
      });
      recorderRef.current = recorder;
      recorder.ondataavailable = (event) => {
        if (event.data?.size) chunksRef.current.push(event.data);
      };
      recorder.onstop = async () => {
        cleanupSilenceMonitor();
        if (!activeRef.current || useBrowserFallbackRef.current) return;
        const audioBlob = new Blob(chunksRef.current, { type: "audio/webm" });
        chunksRef.current = [];
        setAssistantState("processing");
        setStatusMessage("Thinking...");
        try {
          const stt = await transcribeAudio({
            audioBlob,
            languageHint: selectedLanguage.whisper,
            formId,
            sessionId,
          });
          setSttWarning("");
          setSttMetrics({
            provider: stt.provider || "speech service",
            processingMs: stt.processing_ms ?? stt.timing_ms?.processing,
          });
          if (!stt.transcript || stt.confidence < 0.3) {
            await processTranscript("", "backend-stt");
            return;
          }
          await processTranscript(stt.transcript, "backend-stt");
        } catch (sttError) {
          setSttWarning(
            `${sttError?.message || "Local transcription failed."} Using browser speech recognition.`,
          );
          useBrowserFallbackRef.current = true;
          setSttMetrics({ provider: "browser speech recognition", processingMs: null });
          startBrowserFallback();
        }
      };
      setAssistantState("listening");
      setStatusMessage("Listening...");
      recorder.start();
      monitorRecordingSilence(recorder, mediaStreamRef.current);
      clearTimeout(recordTimerRef.current);
      recordTimerRef.current = window.setTimeout(() => {
        if (recorder.state !== "inactive") recorder.stop();
      }, recordingWindowMs());
    } catch (recordingError) {
      useBrowserFallbackRef.current = true;
      if (recordingError?.name === "NotAllowedError") {
        activeRef.current = false;
        setAssistantState("stopped");
        setStatusMessage("Microphone permission was denied. Use Text Instead.");
        return;
      }
      startBrowserFallback();
    }
  }

  function startBrowserFallback() {
    if (!activeRef.current) return;
    if (!browserRecognitionSupported) {
      activeRef.current = false;
      setAssistantState("stopped");
      setStatusMessage(SPEECH_FALLBACK_MESSAGE);
      return;
    }
    useBrowserFallbackRef.current = true;
    setAssistantState("listening");
    setStatusMessage("Listening...");
    startBrowserRecognition();
  }

  function startListening() {
    if (!activeRef.current) return;
    if (
      selectedLanguage.language === "telugu" &&
      PREFER_BROWSER_STT_FOR_TELUGU &&
      browserRecognitionSupported
    ) {
      useBrowserFallbackRef.current = true;
      setSttMetrics({ provider: "browser speech recognition (Telugu)", processingMs: null });
      startBrowserFallback();
      return;
    }
    if (useBrowserFallbackRef.current) {
      startBrowserFallback();
      return;
    }
    void startBackendRecording();
  }

  async function startVoiceHelp() {
    if (sessionStatus !== "ready") return;
    if (!speechSupport.supported) {
      setStatusMessage(speechSupport.reason || SPEECH_FALLBACK_MESSAGE);
      return;
    }
    activeRef.current = true;
    setStatusMessage("Speaking...");
    setAssistantState("intro_speaking");
    clearTranscript();
    processingTranscriptRef.current = "";
    if (!introSpokenRef.current) {
      introSpokenRef.current = true;
      const introduction = LOCALIZED_INTROS[selectedLanguage.language] || introText;
      await speakAndMaybeResume(
        introduction,
        recognitionLanguageCode,
        selectedLanguage.language === "auto" ? "english" : selectedLanguage.language,
      );
    } else {
      startListening();
    }
  }

  function stopVoiceHelp() {
    activeRef.current = false;
    setAssistantState("stopped");
    setStatusMessage("Stopped");
    stopAllListening();
    stopSpeaking();
  }

  async function sendTypedMessage(event) {
    event.preventDefault();
    const cleaned = textMessage.trim();
    if (!cleaned || asking || sessionStatus !== "ready") return;
    setTextMessage("");
    await processTranscript(cleaned, "typed-fallback");
  }

  function useMyLocation() {
    setLocationStatus(
      "Location is requested only after this click. It is used only to ask for mandal guidance.",
    );
    if (!navigator.geolocation) {
      setLocationStatus("Location is not supported. Please type your pincode.");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      async ({ coords }) => {
        setLocationStatus("Location received. Checking available guidance...");
        await onUseLocation({
          latitude: coords.latitude,
          longitude: coords.longitude,
        });
        setLocationStatus("Exact mandal lookup is not available in this MVP. Please enter pincode or village.");
      },
      () => setLocationStatus("Location permission was not provided. You can enter a pincode instead."),
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 },
    );
  }

  async function askPincode(event) {
    event.preventDefault();
    if (pincode.length !== 6) return;
    const text =
      lastDetectedLanguage === "hindi"
        ? `mera pincode ${pincode} hai. mujhe mandal bataiye`
        : lastDetectedLanguage === "telugu"
          ? `na pincode ${pincode}. na mandal cheppandi`
          : `My pincode is ${pincode}. Please help me find my mandal.`;
    setPincode("");
    await processTranscript(text, "typed-fallback");
  }

  useEffect(() => {
    if (!speechCommand?.text || lastSpeechCommandRef.current === speechCommand.id) {
      return;
    }
    lastSpeechCommandRef.current = speechCommand.id;
    void speakAndMaybeResume(
      speechCommand.text,
      speechCommand.languageCode,
      speechCommand.detectedLanguage,
    );
  }, [speechCommand, speakAndMaybeResume]);

  useEffect(() => {
    introSpokenRef.current = false;
  }, [introText]);

  useEffect(
    () => () => {
      activeRef.current = false;
      stopAllListening();
      stopSpeaking();
      mediaStreamRef.current?.getTracks?.().forEach((track) => track.stop());
    },
    [stopAllListening, stopSpeaking],
  );

  const voiceUnavailable = !speechSupport.supported;

  return (
    <aside className="assistant-card chatbot-card" aria-labelledby="assistant-title">
      <div className="assistant-header">
        <div className="assistant-mark" aria-hidden="true">
          NG
        </div>
        <div>
          <p className="eyebrow">Citizen assistant</p>
          <h2 id="assistant-title">NiyamGuard Chatbot</h2>
        </div>
      </div>

      <div className="assistant-status" role="status" aria-live="polite">
        {statusMessage || STATE_LABELS[assistantState]}
      </div>

      <label className="voice-language-control" htmlFor="assistant-voice-language">
        Voice language
        <select
          disabled={activeRef.current || assistantState === "speaking"}
          id="assistant-voice-language"
          onChange={(event) => {
            setSelectedLanguageCode(event.target.value);
            useBrowserFallbackRef.current = false;
            introSpokenRef.current = false;
            setSttWarning("");
          }}
          value={selectedLanguageCode}
        >
          {VOICE_LANGUAGES.map((option) => (
            <option key={option.code} value={option.code}>
              {option.label}
            </option>
          ))}
        </select>
      </label>

      <div className="voice-controls">
        <button
          className="button button-voice"
          disabled={voiceUnavailable || activeRef.current || sessionStatus !== "ready"}
          onClick={() => void startVoiceHelp()}
          title={voiceUnavailable ? speechSupport.reason || SPEECH_FALLBACK_MESSAGE : undefined}
          type="button"
        >
          Start
        </button>
        <button
          className="button button-stop"
          disabled={!activeRef.current && assistantState !== "speaking"}
          onClick={stopVoiceHelp}
          type="button"
        >
          Stop
        </button>
        <button
          className="button button-secondary"
          onClick={() => document.getElementById("assistant-question")?.focus()}
          type="button"
        >
          Type
        </button>
      </div>

      <AssistantTranscript messages={messages} liveTranscript={browserTranscript || lastHeard} />

      {assistantReply?.warning ? (
        <p className="reply-warning">{assistantReply.warning}</p>
      ) : null}

      {assistantReply?.verified_rule ? (
        <VerifiedSourceCard source={assistantReply.verified_source} />
      ) : null}

      {sttMetrics?.provider ? (
        <p className="support-message voice-provider-status">
          Listening provider: {sttMetrics.provider}
          {Number.isFinite(sttMetrics.processingMs)
            ? ` (${Math.round(sttMetrics.processingMs)} ms)`
            : ""}
        </p>
      ) : null}

      {sttWarning || synthesisError || lastVoiceWarning || browserSpeechError || (voiceUnavailable && speechSupport.reason) ? (
        <p className="support-message support-error">
          {sttWarning || synthesisError || lastVoiceWarning || browserSpeechError || speechSupport.reason}
        </p>
      ) : null}

      <details className="trouble-panel">
        <summary>Need mandal or location help?</summary>
        <form className="pincode-help simple-pincode" onSubmit={askPincode}>
          <label htmlFor="mandal-pincode">Pincode</label>
          <input
            id="mandal-pincode"
            inputMode="numeric"
            maxLength="6"
            onChange={(event) =>
              setPincode(event.target.value.replace(/\D/g, "").slice(0, 6))
            }
            placeholder="500032"
            value={pincode}
          />
          <button
            className="button button-secondary"
            disabled={pincode.length !== 6 || asking}
            type="submit"
          >
            Find mandal
          </button>
        </form>
        <button className="text-button" onClick={useMyLocation} type="button">
          Use My Location to Help Find Mandal
        </button>
        {locationStatus ? <p className="support-message">{locationStatus}</p> : null}
      </details>

      <form className="chatbot-composer text-question" onSubmit={sendTypedMessage}>
        <label htmlFor="assistant-question">Message</label>
        <div className="chatbot-composer-row">
          <input
            id="assistant-question"
            onChange={(event) => setTextMessage(event.target.value)}
            placeholder={textPlaceholder}
            value={textMessage}
          />
          <button
            className="button button-primary"
            disabled={!textMessage.trim() || asking || sessionStatus !== "ready"}
            type="submit"
          >
            Ask
          </button>
        </div>
      </form>
    </aside>
  );
}

function VerifiedSourceCard({ source }) {
  if (!source) {
    return (
      <div className="verified-source-card verified-source-missing">
        <h3>Verified Source</h3>
        <p>Source not available. Please verify from official government source.</p>
      </div>
    );
  }

  return (
    <div className="verified-source-card" aria-label="Verified Source">
      <h3>Verified Source</h3>
      <div className="source-badges" aria-label="Sources used">
        {sourceBadges(source).map((badge) => (
          <span key={badge}>{badge}</span>
        ))}
      </div>
      <dl>
        <div>
          <dt>Circular</dt>
          <dd>{source.circular || "Source not available"}</dd>
        </div>
        <div>
          <dt>Department</dt>
          <dd>{source.department || "Source not available"}</dd>
        </div>
        <div>
          <dt>Rule</dt>
          <dd>{source.rule || "Citizen Service Guidance"}</dd>
        </div>
        <div>
          <dt>Current Value</dt>
          <dd>{source.currentValue || "Source not available"}</dd>
        </div>
        <div>
          <dt>Confidence</dt>
          <dd>
            {source.confidence
              ? `${Math.round(Number(source.confidence) * 100)}%`
              : "Source not available"}
          </dd>
        </div>
        {source.effectiveDate ? (
          <div>
            <dt>Effective Date</dt>
            <dd>{source.effectiveDate}</dd>
          </div>
        ) : null}
        {source.lastUpdated ? (
          <div>
            <dt>Last Updated</dt>
            <dd>{source.lastUpdated}</dd>
          </div>
        ) : null}
        {source.whySelected ? (
          <div>
            <dt>Why Selected</dt>
            <dd>{source.whySelected}</dd>
          </div>
        ) : null}
      </dl>
    </div>
  );
}
