import { useEffect, useRef, useState } from "react";

import { useSpeechRecognition } from "../hooks/useSpeechRecognition";
import { useSpeechSynthesis } from "../hooks/useSpeechSynthesis";
import AssistantTranscript from "./AssistantTranscript";

export default function VoiceAssistantPanel({
  fields,
  currentField,
  onCurrentFieldChange,
  language,
  onLanguageChange,
  messages,
  assistantReply,
  speechCommand,
  onAsk,
  onClear,
  sessionStatus,
  asking,
}) {
  const [textMessage, setTextMessage] = useState("");
  const lastSpeechCommandRef = useRef(null);
  const {
    supported: synthesisSupported,
    isSpeaking,
    error: synthesisError,
    speak,
    cancel,
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
    language,
    onFinalTranscript: sendMessage,
  });

  function speakWithoutMicrophoneFeedback(text) {
    const shouldResumeListening = isActive;
    if (shouldResumeListening) pause();
    const started = speak(text, language, () => {
      if (shouldResumeListening) resume();
    });
    if (!started && shouldResumeListening) resume();
  }

  useEffect(() => {
    if (
      !speechCommand?.text ||
      lastSpeechCommandRef.current === speechCommand.id
    ) {
      return;
    }
    lastSpeechCommandRef.current = speechCommand.id;
    speakWithoutMicrophoneFeedback(speechCommand.text);
  }, [speechCommand]);

  async function clearConversation() {
    stop();
    cancel();
    clearTranscript();
    setTextMessage("");
    await onClear();
  }

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
        <span>It will not submit or fill the form automatically.</span>
      </div>

      <div className="assistant-selectors">
        <label>
          Current field
          <select
            value={currentField}
            onChange={(event) => onCurrentFieldChange(event.target.value)}
          >
            <option value="">Not selected</option>
            {fields.map((field) => (
              <option key={field.key} value={field.key}>
                {field.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Language
          <select
            value={language}
            onChange={(event) => {
              stop();
              cancel();
              onLanguageChange(event.target.value);
            }}
          >
            <option value="english">English</option>
            <option value="telugu">Telugu-friendly</option>
            <option value="hindi">Hindi-friendly</option>
            <option value="mixed">Mixed</option>
          </select>
        </label>
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
              ? "Listening continuously…"
              : "Voice help active…"
            : "Start Voice Help"}
        </button>
        <button
          className="button button-stop"
          disabled={!isActive}
          onClick={stop}
          type="button"
        >
          Stop Voice Help
        </button>
      </div>

      {!recognitionSupported ? (
        <p className="support-message">
          Voice recognition is not available in this browser. Use the text box
          below. Chrome or Edge generally provides browser speech recognition.
        </p>
      ) : null}
      {speechError ? (
        <p className="support-message support-error" role="alert">
          {speechError}
        </p>
      ) : null}
      {isActive && !speechError ? (
        <p className="support-message voice-active-message" aria-live="polite">
          Voice help stays active until you click Stop. It pauses while the
          assistant speaks, then listens again.
        </p>
      ) : null}
      {synthesisError ? (
        <p className="support-message support-error" role="alert">
          {synthesisError}
        </p>
      ) : null}

      <form
        className="text-question"
        onSubmit={(event) => {
          event.preventDefault();
          sendMessage(textMessage);
        }}
      >
        <label htmlFor="assistant-question">Type your question</label>
        <div>
          <input
            id="assistant-question"
            onChange={(event) => setTextMessage(event.target.value)}
            placeholder="Example: What should I enter for purpose?"
            value={textMessage}
          />
          <button
            className="button button-primary"
            disabled={!textMessage.trim() || asking || sessionStatus !== "ready"}
            type="submit"
          >
            {asking ? "Asking…" : "Ask"}
          </button>
        </div>
      </form>

      {assistantReply ? (
        <section className="latest-reply" aria-live="polite">
          <div className="section-heading">
            <h3>Assistant reply</h3>
            {synthesisSupported ? (
              <button
                className="text-button"
                onClick={() => {
                  if (isSpeaking) {
                    cancel();
                    if (isActive) resume();
                  } else {
                    speakWithoutMicrophoneFeedback(assistantReply.reply);
                  }
                }}
                type="button"
              >
                {isSpeaking ? "Stop speaking" : "Speak again"}
              </button>
            ) : null}
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
