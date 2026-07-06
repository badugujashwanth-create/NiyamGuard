import { useCallback, useEffect, useState } from "react";

const LANGUAGE_CODES = {
  english: "en-IN",
  telugu: "te-IN",
  hindi: "hi-IN",
  mixed: "en-IN",
};

export function useSpeechSynthesis() {
  const supported =
    typeof window !== "undefined" &&
    "speechSynthesis" in window &&
    typeof window.SpeechSynthesisUtterance !== "undefined";
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voices, setVoices] = useState([]);
  const [error, setError] = useState("");

  const cancel = useCallback(() => {
    if (!supported) return;
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  }, [supported]);

  useEffect(() => {
    if (!supported) return undefined;
    const loadVoices = () => {
      setVoices(window.speechSynthesis.getVoices?.() || []);
    };
    loadVoices();
    window.speechSynthesis.addEventListener?.("voiceschanged", loadVoices);
    return () => {
      window.speechSynthesis.removeEventListener?.("voiceschanged", loadVoices);
    };
  }, [supported]);

  const speak = useCallback(
    (text, language = "english", onComplete) => {
      if (!supported || !text) return false;
      window.speechSynthesis.cancel();
      window.speechSynthesis.resume?.();
      setError("");
      const utterance = new window.SpeechSynthesisUtterance(text);
      const languageCode = LANGUAGE_CODES[language] || "en-IN";
      const languagePrefix = languageCode.split("-")[0].toLowerCase();
      utterance.lang = languageCode;
      utterance.voice =
        voices.find(
          (voice) => voice.lang?.toLowerCase() === languageCode.toLowerCase(),
        ) ||
        voices.find((voice) =>
          voice.lang?.toLowerCase().startsWith(languagePrefix),
        ) ||
        null;
      utterance.rate = 0.9;
      utterance.pitch = 1;
      utterance.volume = 1;
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => {
        setIsSpeaking(false);
        onComplete?.();
      };
      utterance.onerror = (event) => {
        setIsSpeaking(false);
        if (event.error !== "canceled" && event.error !== "interrupted") {
          setError(
            "The browser could not speak this reply. Check device volume and browser audio permissions.",
          );
        }
        onComplete?.();
      };
      window.speechSynthesis.speak(utterance);
      return true;
    },
    [supported, voices],
  );

  useEffect(() => cancel, [cancel]);

  return { supported, isSpeaking, error, speak, cancel };
}
