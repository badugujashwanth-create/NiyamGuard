import { useCallback, useEffect, useRef, useState } from "react";

import { useSpeechRecognition } from "../hooks/useSpeechRecognition";
import { useSpeechSynthesis } from "../hooks/useSpeechSynthesis";
import { getTtsHealth } from "../services/api";
import AssistantTranscript from "./AssistantTranscript";

const SAMPLE_QUESTIONS = [
  ["Telugu", "purpose lo scholarship ani rayacha"],
  ["Telugu", "monthly income పదిహేను వేలు అయితే annual income ఎంత"],
  ["Hindi", "purpose mein scholarship likhna hai kya"],
  ["Hindi", "monthly income 15000 hai annual income kya hoga"],
  ["English", "monthly income fifteen thousand what should I enter"],
];

const VOICE_TESTS = [
  ["Test Telugu Voice", "నమస్తే. ఇది NiyamGuard Telugu voice test.", "te-IN", "telugu"],
  ["Test Hindi Voice", "नमस्ते. यह NiyamGuard Hindi voice test है.", "hi-IN", "hindi"],
  ["Test English Voice", "Hello. This is NiyamGuard English voice test.", "en-IN", "english"],
];

const UI_COPY = {
  english: {
    start: "Start Voice Help",
    listening: "Listening continuously…",
    active: "Voice help active…",
    stop: "Stop Voice Help",
    ask: "Ask",
    asking: "Asking…",
    speakAgain: "Speak again",
    locationTitle: "Need help finding your mandal?",
    unknownMandal: "I don't know my mandal",
    useLocation: "Use My Location to Help Find Mandal",
    privacy:
      "Location is optional and requested only after you click this button. It is never used to fill the form.",
  },
  telugu: {
    start: "Voice Help Start చేయండి",
    listening: "వింటున్నాను…",
    active: "Voice Help active…",
    stop: "Voice Help ఆపండి",
    ask: "అడగండి",
    asking: "అడుగుతోంది…",
    speakAgain: "మళ్లీ వినండి",
    locationTitle: "మీ మండలం తెలియదా?",
    unknownMandal: "నా మండలం తెలియదు",
    useLocation: "Locationతో మండలం కనుగొనండి",
    privacy:
      "మీ location ఉపయోగించి మండలం కనుగొనడానికి ప్రయత్నించవచ్చు. మీ అనుమతి లేకుండా location తీసుకోము; formను auto-fill చేయము.",
  },
  hindi: {
    start: "Voice Help शुरू करें",
    listening: "सुन रहा है…",
    active: "Voice Help चालू है…",
    stop: "Voice Help रोकें",
    ask: "पूछें",
    asking: "पूछ रहा है…",
    speakAgain: "फिर से सुनें",
    locationTitle: "अपना मंडल नहीं पता?",
    unknownMandal: "मुझे मंडल नहीं पता",
    useLocation: "Location से मंडल खोजने में मदद लें",
    privacy:
      "Location वैकल्पिक है और इस button पर click करने के बाद ही permission माँगी जाती है। Form अपने-आप नहीं भरा जाएगा।",
  },
};

export default function VoiceAssistantPanel({
  messages,
  assistantReply,
  speechCommand,
  onAsk,
  onClear,
  onUseLocation,
  sessionStatus,
  asking,
  lastDetectedLanguage = "english",
  lastLanguageCode = "en-IN",
}) {
  const [textMessage, setTextMessage] = useState("");
  const [pincode, setPincode] = useState("");
  const [locationStatus, setLocationStatus] = useState("");
  const [ttsHealth, setTtsHealth] = useState(null);
  const lastSpeechCommandRef = useRef(null);
  const resumeAfterSpeechRef = useRef(false);
  const copy = UI_COPY[lastDetectedLanguage] || UI_COPY.english;
  const {
    isSupported: voiceOutputSupported,
    browserSupported,
    isSpeaking,
    error: synthesisError,
    lastVoiceWarning,
    lastVoiceMode,
    lastVoiceName,
    lastProvider,
    voices,
    refreshVoices,
    speak,
    stop: stopSpeaking,
  } = useSpeechSynthesis();

  async function sendMessage(message) {
    const cleaned = message.trim();
    if (!cleaned || asking || sessionStatus !== "ready") return;
    setTextMessage("");
    await onAsk(cleaned);
  }

  const {
    supported: recognitionSupported,
    isListening,
    isActive,
    transcript,
    error: speechError,
    start,
    stop,
    pause,
    resume,
    clearTranscript,
  } = useSpeechRecognition({
    languageCode: lastLanguageCode,
    onFinalTranscript: sendMessage,
  });

  const speakWithoutMicrophoneFeedback = useCallback(
    async (text, languageCode, detectedLanguage, extraOptions = {}) => {
      const shouldResumeListening = isActive;
      resumeAfterSpeechRef.current = shouldResumeListening;
      if (shouldResumeListening) pause();
      return speak(text, {
        languageCode: languageCode || "en-IN",
        detectedLanguage: detectedLanguage || "english",
        ...extraOptions,
        onComplete: () => {
          if (resumeAfterSpeechRef.current) resume();
          resumeAfterSpeechRef.current = false;
        },
      });
    },
    [isActive, pause, resume, speak],
  );

  useEffect(() => {
    if (
      !speechCommand?.text ||
      lastSpeechCommandRef.current === speechCommand.id
    ) {
      return;
    }
    lastSpeechCommandRef.current = speechCommand.id;
    void speakWithoutMicrophoneFeedback(
      speechCommand.text,
      speechCommand.languageCode,
      speechCommand.detectedLanguage,
    );
  }, [speechCommand, speakWithoutMicrophoneFeedback]);

  useEffect(() => {
    let active = true;
    getTtsHealth()
      .then((health) => {
        if (active) setTtsHealth(health);
      })
      .catch(() => {
        if (active) setTtsHealth({ success: false });
      });
    return () => {
      active = false;
    };
  }, []);

  function stopVoiceHelp() {
    resumeAfterSpeechRef.current = false;
    stop();
  }

  async function clearConversation() {
    stopVoiceHelp();
    stopSpeaking();
    clearTranscript();
    setTextMessage("");
    setPincode("");
    setLocationStatus("");
    await onClear();
  }

  function useMyLocation() {
    setLocationStatus(
      "Location is requested only after this click. It is used only to ask for mandal guidance.",
    );
    if (!navigator.geolocation) {
      setLocationStatus(
        "Location is not supported in this browser. Please enter your pincode instead.",
      );
      return;
    }
    navigator.geolocation.getCurrentPosition(
      async ({ coords }) => {
        setLocationStatus("Location received. Checking available guidance…");
        await onUseLocation({
          latitude: coords.latitude,
          longitude: coords.longitude,
        });
        setLocationStatus(
          "For this MVP, confirm your location using a pincode or village name.",
        );
      },
      () => {
        setLocationStatus(
          "Location permission was not provided. You can enter a pincode instead.",
        );
      },
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 },
    );
  }

  function pincodeQuestion() {
    if (lastDetectedLanguage === "telugu") {
      return `na pincode ${pincode}. na mandal cheppandi`;
    }
    if (lastDetectedLanguage === "hindi") {
      return `mera pincode ${pincode} hai. mujhe mandal bataiye`;
    }
    return `My pincode is ${pincode}. Please help me find my mandal.`;
  }

  const groupedVoices = {
    telugu: voices.filter((voice) =>
      voice.lang?.toLowerCase().startsWith("te"),
    ),
    hindi: voices.filter((voice) =>
      voice.lang?.toLowerCase().startsWith("hi"),
    ),
    englishIndia: voices.filter(
      (voice) => voice.lang?.toLowerCase() === "en-in",
    ),
  };

  return (
    <aside className="assistant-card" aria-labelledby="assistant-title">
      <div className="assistant-header">
        <div className="assistant-mark" aria-hidden="true">
          NG
        </div>
        <div>
          <p className="eyebrow">Voice guidance</p>
          <h2 id="assistant-title">NiyamGuard Call Assistant</h2>
        </div>
        <span
          className={`status-dot status-${sessionStatus}`}
          title={`Assistant status: ${sessionStatus}`}
        />
      </div>

      <div className="safety-notice" role="note">
        <strong>AI only guides you.</strong>
        <span>It will not fill or submit the form automatically.</span>
      </div>

      <div className="voice-controls">
        <button
          className={`button button-voice ${isListening ? "button-listening" : ""}`}
          disabled={!recognitionSupported || isActive || sessionStatus !== "ready"}
          onClick={start}
          type="button"
        >
          <span aria-hidden="true">●</span>
          {isActive
            ? isListening
              ? copy.listening
              : copy.active
            : copy.start}
        </button>
        <button
          className="button button-stop"
          disabled={!isActive}
          onClick={stopVoiceHelp}
          type="button"
        >
          {copy.stop}
        </button>
      </div>

      {!recognitionSupported ? (
        <p className="support-message">
          Voice recognition is unavailable. Use the text box below.
        </p>
      ) : null}
      {!browserSupported && voiceOutputSupported ? (
        <p className="support-message">
          Browser voice is unavailable. Replies will use backend voice output.
        </p>
      ) : null}
      {speechError ? (
        <p className="support-message support-error" role="alert">
          {speechError}
        </p>
      ) : null}
      {isActive && !speechError ? (
        <p className="support-message voice-active-message" aria-live="polite">
          Voice help pauses while the assistant speaks and resumes only while
          Voice Help remains active.
        </p>
      ) : null}
      {synthesisError ? (
        <p className="support-message support-error" role="alert">
          {synthesisError}
        </p>
      ) : null}
      {lastVoiceWarning ? (
        <p className="support-message" role="status">
          {lastVoiceWarning}
        </p>
      ) : null}

      <form
        className="text-question"
        onSubmit={(event) => {
          event.preventDefault();
          void sendMessage(textMessage);
        }}
      >
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
            {asking ? copy.asking : copy.ask}
          </button>
        </div>
      </form>

      <section className="location-help" aria-labelledby="location-help-title">
        <h3 id="location-help-title">{copy.locationTitle}</h3>
        <button
          className="button button-secondary"
          disabled={asking || sessionStatus !== "ready"}
          onClick={() => void sendMessage("na mandal teliyadu")}
          type="button"
        >
          {copy.unknownMandal}
        </button>
        <div className="pincode-help">
          <label htmlFor="mandal-pincode">Pincode</label>
          <input
            id="mandal-pincode"
            inputMode="numeric"
            maxLength="6"
            onChange={(event) =>
              setPincode(event.target.value.replace(/\D/g, "").slice(0, 6))
            }
            placeholder="Example: 500032"
            value={pincode}
          />
          <button
            className="button button-secondary"
            disabled={pincode.length !== 6 || asking}
            onClick={() => void sendMessage(pincodeQuestion())}
            type="button"
          >
            Find possible mandal
          </button>
        </div>
        <button
          className="text-button"
          onClick={useMyLocation}
          type="button"
        >
          {copy.useLocation}
        </button>
        <p className="privacy-note">{copy.privacy}</p>
        {locationStatus ? (
          <p className="support-message" role="status">
            {locationStatus}
          </p>
        ) : null}
      </section>

      {assistantReply ? (
        <section className="latest-reply" aria-live="polite">
          <div className="section-heading">
            <h3>Assistant reply</h3>
            <button
              aria-busy={isSpeaking}
              className="text-button"
              onClick={() =>
                void speakWithoutMicrophoneFeedback(
                  assistantReply.reply,
                  assistantReply.language_code,
                  assistantReply.detected_language,
                )
              }
              type="button"
            >
              {copy.speakAgain}
            </button>
          </div>
          <p>{assistantReply.reply}</p>
          {assistantReply.suggested_value ? (
            <div className="suggestion">
              Suggested value to type manually:
              <strong>{assistantReply.suggested_value}</strong>
            </div>
          ) : null}
          {assistantReply.warning ? (
            <p className="reply-warning">{assistantReply.warning}</p>
          ) : null}
        </section>
      ) : null}

      <AssistantTranscript messages={messages} liveTranscript={transcript} />

      <details className="developer-diagnostics">
        <summary>Developer Diagnostics</summary>
        <h3>Voice Diagnostics</h3>
        <p>
          Voice mode: {lastVoiceMode || "Not used"} · Provider:{" "}
          {lastProvider || "Not used"}
        </p>
        <p>
          Detected language: {lastDetectedLanguage} · Language code:{" "}
          {lastLanguageCode}
        </p>
        <p>Voice name: {lastVoiceName || "Backend or unavailable"}</p>
        <p>
          Backend TTS:{" "}
          {ttsHealth?.success
            ? `${ttsHealth.default_provider} available`
            : "Unavailable"}
        </p>
        <p>
          Telugu voices: {groupedVoices.telugu.length} · Hindi voices:{" "}
          {groupedVoices.hindi.length} · English India voices:{" "}
          {groupedVoices.englishIndia.length}
        </p>
        <ul>
          {voices.map((voice) => (
            <li key={`${voice.name}-${voice.lang}`}>
              {voice.name} ({voice.lang})
            </li>
          ))}
        </ul>
        <div className="diagnostic-actions">
          <button onClick={refreshVoices} type="button">
            Check Available Voices
          </button>
          {assistantReply ? (
            <button
              onClick={() =>
                void speakWithoutMicrophoneFeedback(
                  assistantReply.reply,
                  assistantReply.language_code,
                  assistantReply.detected_language,
                  { forceBackendTts: true },
                )
              }
              type="button"
            >
              Force Backend Voice
            </button>
          ) : null}
          {VOICE_TESTS.map(([label, text, languageCode, detectedLanguage]) => (
            <button
              key={label}
              onClick={() =>
                void speakWithoutMicrophoneFeedback(
                  text,
                  languageCode,
                  detectedLanguage,
                )
              }
              type="button"
            >
              {label}
            </button>
          ))}
        </div>
        <div className="sample-questions">
          <p>Sample questions</p>
          <div>
            {SAMPLE_QUESTIONS.map(([language, text]) => (
              <button
                disabled={asking || sessionStatus !== "ready"}
                key={text}
                onClick={() => void sendMessage(text)}
                type="button"
              >
                <span>{language}</span>
                {text}
              </button>
            ))}
          </div>
        </div>
      </details>

      <button
        className="text-button clear-button"
        disabled={sessionStatus === "loading"}
        onClick={clearConversation}
        type="button"
      >
        Clear conversation
      </button>
    </aside>
  );
}
