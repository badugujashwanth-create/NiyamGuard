import { useCallback, useEffect, useRef, useState } from "react";

import { useSpeechRecognition } from "../../hooks/useSpeechRecognition";
import { useSpeechSynthesis } from "../../hooks/useSpeechSynthesis";
import { askHybridDemoQuestion } from "../../services/api";

const LANGUAGES = {
  english: { label: "English", code: "en-IN" },
  telugu: { label: "\u0c24\u0c46\u0c32\u0c41\u0c17\u0c41", code: "te-IN" },
  hindi: { label: "\u0939\u093f\u0902\u0926\u0940", code: "hi-IN" },
};

function responseText(response) {
  return response?.answer || response?.reply || "I could not find a guidance answer. Please try a different question.";
}

export default function CitizenAssistantDock() {
  const [open, setOpen] = useState(false);
  const [mode, setMode] = useState("chat");
  const [language, setLanguage] = useState("english");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [asking, setAsking] = useState(false);
  const voiceQuestionInFlight = useRef(false);
  const { error: synthesisError, isSpeaking, speak, stop: stopSpeaking } = useSpeechSynthesis();

  const askQuestion = useCallback(async (rawQuestion, shouldSpeak = false) => {
    const cleaned = rawQuestion.trim();
    if (!cleaned || asking) return;
    setAsking(true);
    setError("");
    setStatus("Finding verified guidance...");
    try {
      const response = await askHybridDemoQuestion(cleaned);
      const reply = responseText(response);
      setAnswer(reply);
      setStatus(response?.verified ? "Answer checked against a verified published rule." : "Guidance returned. Verify important details with the receiving department.");
      if (shouldSpeak) await speak(reply, { detectedLanguage: response?.language || language, languageCode: response?.language_code || LANGUAGES[language].code });
    } catch {
      setError("Guidance is temporarily unavailable. You can continue filling the form and try again.");
      setStatus("");
    } finally {
      setAsking(false);
    }
  }, [asking, language, speak]);

  const { error: speechError, isListening, start: startListening, stop: stopListening, support, transcript } = useSpeechRecognition({
    languageCode: LANGUAGES[language].code,
    onFinalTranscript: (spokenQuestion) => {
      if (voiceQuestionInFlight.current) return;
      voiceQuestionInFlight.current = true;
      stopListening();
      setQuestion(spokenQuestion);
      void askQuestion(spokenQuestion, true).finally(() => { voiceQuestionInFlight.current = false; });
    },
  });
  const voiceAvailable = support.secureContext && support.webSpeechSupported;

  useEffect(() => () => { stopListening(); stopSpeaking(); }, [stopListening, stopSpeaking]);
  function closeDock() { stopListening(); stopSpeaking(); setOpen(false); }

  return (
    <aside className="citizen-assistant-dock" aria-label="Citizen guidance assistant">
      {!open ? <button className="citizen-assistant-launcher" onClick={() => setOpen(true)} type="button">Need help?</button> : (
        <section className="citizen-assistant-popover" aria-live="polite">
          <header><div><p className="eyebrow">Citizen guidance</p><h2>How can we help?</h2></div><button aria-label="Close guidance assistant" className="citizen-assistant-close" onClick={closeDock} type="button">Close</button></header>
          <div className="citizen-assistant-tabs" role="tablist" aria-label="Guidance mode"><button aria-selected={mode === "chat"} onClick={() => setMode("chat")} role="tab" type="button">Chat</button><button aria-selected={mode === "voice"} onClick={() => setMode("voice")} role="tab" type="button">Voice</button></div>
          <label className="citizen-assistant-language" htmlFor="assistant-language">Language<select id="assistant-language" onChange={(event) => setLanguage(event.target.value)} value={language}>{Object.entries(LANGUAGES).map(([value, item]) => <option key={value} value={value}>{item.label}</option>)}</select></label>
          {mode === "chat" ? <form onSubmit={(event) => { event.preventDefault(); void askQuestion(question); }}><label htmlFor="citizen-assistant-question">Ask about forms, documents, eligibility, tracking, or verification</label><textarea id="citizen-assistant-question" onChange={(event) => setQuestion(event.target.value)} placeholder="For example: What documents do I need?" rows="3" value={question} /><button className="button button-primary" disabled={!question.trim() || asking} type="submit">{asking ? "Checking..." : "Ask"}</button></form> : (
            <section className="citizen-assistant-voice" aria-label="Live voice guidance"><p>Speak in English, Telugu, or Hindi. Your words stay visible before a response is read aloud.</p><div className="portal-actions"><button className="button button-primary" disabled={asking || !voiceAvailable || isListening} onClick={startListening} type="button">{isListening ? "Listening..." : "Start voice"}</button><button className="button button-secondary" disabled={!isListening} onClick={stopListening} type="button">Stop</button></div><p className="citizen-assistant-transcript" aria-live="polite">{transcript ? `Heard: ${transcript}` : isListening ? "Listening…" : "Select Start voice, then allow microphone access when your browser asks."}</p>{speechError ? <p className="support-message support-error">{speechError}</p> : null}{!voiceAvailable && !transcript ? <p className="support-message support-error">{support.reason || "Voice input is not available in this browser. You can continue using text."}</p> : null}{synthesisError ? <p className="support-message support-error">{synthesisError}</p> : null}{isSpeaking ? <p className="support-message">Reading the verified guidance aloud…</p> : null}</section>
          )}
          {status ? <p className="support-message">{status}</p> : null}{error ? <p className="support-message support-error">{error}</p> : null}{answer ? <section className="citizen-assistant-answer"><p className="eyebrow">Guidance answer</p><p>{answer}</p></section> : null}
        </section>
      )}
    </aside>
  );
}
