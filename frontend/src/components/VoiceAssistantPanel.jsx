import { useCallback, useEffect, useRef, useState } from "react";

import { useSpeechRecognition } from "../hooks/useSpeechRecognition";
import { useSpeechSynthesis } from "../hooks/useSpeechSynthesis";
import { transcribeAudio } from "../services/api";

const INTRO_TEXT =
  "Namaste. I am NiyamGuard Voice Assistant. I will help you fill this form step by step. You can speak in Telugu, Hindi, or English. Tell me where you need help.";

const STATE_LABELS = {
  idle: "Stopped",
  intro_speaking: "Speaking...",
  listening: "Listening...",
  processing: "Thinking...",
  speaking: "Speaking...",
  stopped: "Stopped",
  error: "Could not hear clearly, please repeat",
};

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
}) {
  const [assistantState, setAssistantState] = useState("idle");
  const [textMessage, setTextMessage] = useState("");
  const [lastHeard, setLastHeard] = useState("");
  const [statusMessage, setStatusMessage] = useState("Stopped");
  const [locationStatus, setLocationStatus] = useState("");
  const [pincode, setPincode] = useState("");
  const activeRef = useRef(false);
  const introSpokenRef = useRef(false);
  const mediaStreamRef = useRef(null);
  const recorderRef = useRef(null);
  const recordTimerRef = useRef(null);
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

  async function processTranscript(transcript, source = "voice") {
    const cleaned = transcript.trim();
    if (!cleaned || cleaned.length < 3 || cleaned === processingTranscriptRef.current) {
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
    processingTranscriptRef.current = cleaned;
    failedAttemptsRef.current = 0;
    setLastHeard(cleaned);
    setAssistantState("processing");
    setStatusMessage("Thinking...");
    pauseBrowserRecognition();
    await onAsk(cleaned, { source });
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
  } = useSpeechRecognition({
    languageCode: lastLanguageCode,
    onFinalTranscript: (transcript) => {
      if (useBrowserFallbackRef.current && activeRef.current) {
        void processTranscript(transcript, "browser-fallback");
      }
    },
  });

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
  }, []);

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
        if (!activeRef.current || useBrowserFallbackRef.current) return;
        const audioBlob = new Blob(chunksRef.current, { type: "audio/webm" });
        chunksRef.current = [];
        setAssistantState("processing");
        setStatusMessage("Thinking...");
        try {
          const stt = await transcribeAudio({
            audioBlob,
            languageHint: "auto",
            formId,
            sessionId,
          });
          if (!stt.transcript || stt.confidence < 0.3) {
            await processTranscript("", "backend-stt");
            return;
          }
          await processTranscript(stt.transcript, "backend-stt");
        } catch {
          useBrowserFallbackRef.current = true;
          startBrowserFallback();
        }
      };
      setAssistantState("listening");
      setStatusMessage("Listening...");
      recorder.start();
      clearTimeout(recordTimerRef.current);
      recordTimerRef.current = window.setTimeout(() => {
        if (recorder.state !== "inactive") recorder.stop();
      }, 4500);
    } catch {
      useBrowserFallbackRef.current = true;
      startBrowserFallback();
    }
  }

  function startBrowserFallback() {
    if (!activeRef.current) return;
    if (!browserRecognitionSupported) {
      setAssistantState("error");
      setStatusMessage("Microphone listening is unavailable. Use the typing fallback below.");
      return;
    }
    useBrowserFallbackRef.current = true;
    setAssistantState("listening");
    setStatusMessage("Listening...");
    startBrowserRecognition();
  }

  function startListening() {
    if (!activeRef.current) return;
    if (useBrowserFallbackRef.current) {
      startBrowserFallback();
      return;
    }
    void startBackendRecording();
  }

  async function startVoiceHelp() {
    if (sessionStatus !== "ready") return;
    activeRef.current = true;
    setStatusMessage("Speaking...");
    setAssistantState("intro_speaking");
    clearTranscript();
    processingTranscriptRef.current = "";
    if (!introSpokenRef.current) {
      introSpokenRef.current = true;
      await speakAndMaybeResume(INTRO_TEXT, "en-IN", "english");
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

  useEffect(
    () => () => {
      activeRef.current = false;
      stopAllListening();
      stopSpeaking();
      mediaStreamRef.current?.getTracks?.().forEach((track) => track.stop());
    },
    [stopAllListening, stopSpeaking],
  );

  const latestUserMessage = lastHeard || browserTranscript;
  const latestAssistantText = assistantReply?.reply || "";

  return (
    <aside className="assistant-card simple-assistant" aria-labelledby="assistant-title">
      <div className="assistant-header">
        <div className="assistant-mark" aria-hidden="true">
          NG
        </div>
        <div>
          <p className="eyebrow">Voice guidance</p>
          <h2 id="assistant-title">NiyamGuard Voice Assistant</h2>
        </div>
      </div>

      <div className="assistant-status" role="status" aria-live="polite">
        {statusMessage || STATE_LABELS[assistantState]}
      </div>

      <div className="voice-controls">
        <button
          className="button button-voice"
          disabled={activeRef.current || sessionStatus !== "ready"}
          onClick={() => void startVoiceHelp()}
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
      </div>

      <div className="assistant-brief">
        <p>
          <span>Last thing you said</span>
          {latestUserMessage || "Nothing heard yet."}
        </p>
        <p>
          <span>Assistant answer</span>
          {latestAssistantText || "Start voice help and ask a question."}
        </p>
      </div>

      {assistantReply?.warning ? (
        <p className="reply-warning">{assistantReply.warning}</p>
      ) : null}

      {assistantReply?.verified_rule ? (
        <VerifiedSourceCard source={assistantReply.verified_source} />
      ) : null}

      {synthesisError || lastVoiceWarning || browserSpeechError ? (
        <p className="support-message support-error">
          {synthesisError || lastVoiceWarning || browserSpeechError}
        </p>
      ) : null}

      <details className="trouble-panel">
        <summary>Having trouble? Type instead</summary>
        <form className="text-question" onSubmit={sendTypedMessage}>
          <label htmlFor="assistant-question">Type your question</label>
          <div>
            <input
              id="assistant-question"
              onChange={(event) => setTextMessage(event.target.value)}
              placeholder="Example: What should I enter for monthly income?"
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
      </details>

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
          <dd>{source.rule || "Income Certificate Validity"}</dd>
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
      </dl>
    </div>
  );
}
