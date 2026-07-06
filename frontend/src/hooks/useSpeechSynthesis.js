import { useCallback, useEffect, useRef, useState } from "react";

const SPEECH_ERROR_MESSAGE =
  "The browser could not speak this reply. Check device volume and browser audio permissions.";
const VOICE_WARNING_MESSAGE =
  "Your browser may not have a Telugu/Hindi voice installed. Text guidance is still available.";

export function useSpeechSynthesis() {
  const supported =
    typeof window !== "undefined" &&
    typeof window.speechSynthesis !== "undefined" &&
    typeof window.SpeechSynthesisUtterance === "function";
  const utteranceRef = useRef(null);
  const voicesRef = useRef([]);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [error, setError] = useState("");
  const [voiceWarning, setVoiceWarning] = useState("");

  useEffect(() => {
    if (!supported) return undefined;

    const loadVoices = () => {
      voicesRef.current = window.speechSynthesis.getVoices?.() || [];
    };

    loadVoices();
    window.speechSynthesis.addEventListener?.("voiceschanged", loadVoices);
    return () => {
      window.speechSynthesis.removeEventListener?.("voiceschanged", loadVoices);
    };
  }, [supported]);

  const cancel = useCallback(() => {
    if (!supported) return;

    const currentUtterance = utteranceRef.current;
    if (currentUtterance) {
      currentUtterance.onstart = null;
      currentUtterance.onend = null;
      currentUtterance.onerror = null;
      utteranceRef.current = null;
    }

    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  }, [supported]);

  const speak = useCallback(
    (text, languageCode = "en-IN", onComplete) => {
      const cleanedText = text?.trim();
      if (!supported || !cleanedText) return false;
      const requestedLanguageCode = ["en-IN", "te-IN", "hi-IN"].includes(
        languageCode,
      )
        ? languageCode
        : "en-IN";

      const previousUtterance = utteranceRef.current;
      if (previousUtterance) {
        previousUtterance.onstart = null;
        previousUtterance.onend = null;
        previousUtterance.onerror = null;
      }

      window.speechSynthesis.cancel();
      window.speechSynthesis.resume?.();
      setError("");

      const utterance = new window.SpeechSynthesisUtterance(cleanedText);
      utterance.lang = requestedLanguageCode;
      utterance.rate = 0.9;
      utterance.pitch = 1;
      utterance.volume = 1;
      const availableVoices =
        window.speechSynthesis.getVoices?.() || voicesRef.current;
      const languagePrefix = requestedLanguageCode
        .split("-")[0]
        .toLowerCase();
      const requestedVoice =
        availableVoices.find(
          (voice) =>
            voice.lang?.toLowerCase() === requestedLanguageCode.toLowerCase(),
        ) ||
        availableVoices.find((voice) =>
          voice.lang?.toLowerCase().startsWith(`${languagePrefix}-`),
        );
      if (requestedVoice) {
        utterance.voice = requestedVoice;
        setVoiceWarning("");
      } else if (requestedLanguageCode === "en-IN") {
        utterance.voice =
          availableVoices.find((voice) =>
            voice.lang?.toLowerCase().startsWith("en-"),
          ) ||
          availableVoices.find((voice) => voice.default) ||
          availableVoices[0] ||
          null;
        setVoiceWarning("");
      } else {
        // Keep the requested language code and let the browser try its own voice fallback.
        utterance.voice = null;
        setVoiceWarning(VOICE_WARNING_MESSAGE);
      }
      utteranceRef.current = utterance;

      utterance.onstart = () => {
        if (utteranceRef.current !== utterance) return;
        console.log("Speech started");
        setIsSpeaking(true);
      };
      utterance.onend = () => {
        if (utteranceRef.current !== utterance) return;
        console.log("Speech ended");
        utteranceRef.current = null;
        setIsSpeaking(false);
        onComplete?.();
      };
      utterance.onerror = (event) => {
        if (utteranceRef.current !== utterance) return;
        console.error("Speech error", event.error);
        utteranceRef.current = null;
        setIsSpeaking(false);
        if (event.error !== "canceled" && event.error !== "interrupted") {
          setError(SPEECH_ERROR_MESSAGE);
        }
        onComplete?.();
      };

      try {
        console.log("Speaking assistant reply");
        setIsSpeaking(true);
        window.speechSynthesis.speak(utterance);
        return true;
      } catch (speechError) {
        console.error("Speech error", speechError);
        utteranceRef.current = null;
        setIsSpeaking(false);
        setError(SPEECH_ERROR_MESSAGE);
        return false;
      }
    },
    [supported],
  );

  useEffect(() => cancel, [cancel]);

  return {
    supported,
    isSpeaking,
    error,
    voiceWarning,
    speak,
    cancel,
  };
}
