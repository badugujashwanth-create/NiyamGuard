import { useCallback, useEffect, useRef, useState } from "react";

const LANGUAGE_CODES = {
  english: "en-IN",
  telugu: "te-IN",
  hindi: "hi-IN",
  mixed: "en-IN",
};

export function useSpeechRecognition({ language = "english", onFinalTranscript }) {
  const recognitionRef = useRef(null);
  const finalCallbackRef = useRef(onFinalTranscript);
  const shouldListenRef = useRef(false);
  const pausedRef = useRef(false);
  const restartTimerRef = useRef(null);
  const [isListening, setIsListening] = useState(false);
  const [isActive, setIsActive] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState("");

  finalCallbackRef.current = onFinalTranscript;

  const Recognition =
    typeof window !== "undefined"
      ? window.SpeechRecognition || window.webkitSpeechRecognition
      : undefined;
  const supported = Boolean(Recognition);

  useEffect(() => {
    if (!supported) return undefined;

    const recognition = new Recognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = LANGUAGE_CODES[language] || "en-IN";

    const beginRecognition = () => {
      if (
        !recognitionRef.current ||
        !shouldListenRef.current ||
        pausedRef.current
      ) {
        return;
      }
      try {
        recognition.start();
      } catch (startError) {
        if (startError?.name !== "InvalidStateError") {
          setError("Voice recognition could not restart. Click Start Voice Help.");
          shouldListenRef.current = false;
          setIsActive(false);
        }
      }
    };

    recognition.onstart = () => {
      setError("");
      setIsListening(true);
    };
    recognition.onresult = (event) => {
      let combinedTranscript = "";
      let finalTranscript = "";
      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const result = event.results[index];
        const text = result[0]?.transcript || "";
        combinedTranscript += text;
        if (result.isFinal) finalTranscript += text;
      }
      const cleanedTranscript = combinedTranscript.trim();
      setTranscript(cleanedTranscript);
      if (finalTranscript.trim()) {
        finalCallbackRef.current?.(finalTranscript.trim());
      }
    };
    recognition.onerror = (event) => {
      if (event.error === "aborted") return;
      const messages = {
        "not-allowed": "Microphone permission was denied. Use the text box instead.",
        "service-not-allowed":
          "Browser speech recognition is blocked. Check browser permissions or use the text box.",
        "no-speech": "No speech was heard. Please try again or use the text box.",
        "audio-capture": "No microphone was found. Use the text box instead.",
        network:
          "The browser speech service is unavailable. Check your connection or use the text box.",
      };
      setError(messages[event.error] || "Voice recognition stopped unexpectedly.");
      setIsListening(false);
      if (
        ["not-allowed", "service-not-allowed", "audio-capture", "network"].includes(
          event.error,
        )
      ) {
        shouldListenRef.current = false;
        pausedRef.current = false;
        setIsActive(false);
      }
    };
    recognition.onend = () => {
      setIsListening(false);
      if (shouldListenRef.current && !pausedRef.current) {
        clearTimeout(restartTimerRef.current);
        restartTimerRef.current = window.setTimeout(beginRecognition, 250);
      }
    };
    recognitionRef.current = recognition;

    return () => {
      shouldListenRef.current = false;
      pausedRef.current = false;
      clearTimeout(restartTimerRef.current);
      recognition.abort();
      recognitionRef.current = null;
    };
  }, [Recognition, language, supported]);

  const start = useCallback(() => {
    if (!recognitionRef.current || shouldListenRef.current) return;
    setError("");
    setTranscript("");
    shouldListenRef.current = true;
    pausedRef.current = false;
    setIsActive(true);
    try {
      recognitionRef.current.start();
    } catch {
      shouldListenRef.current = false;
      setIsActive(false);
      setError("Voice recognition is already active. Please wait and try again.");
    }
  }, []);

  const stop = useCallback(() => {
    shouldListenRef.current = false;
    pausedRef.current = false;
    clearTimeout(restartTimerRef.current);
    setIsActive(false);
    setIsListening(false);
    try {
      recognitionRef.current?.stop();
    } catch {
      // The recognizer was already stopped.
    }
  }, []);

  const pause = useCallback(() => {
    if (!shouldListenRef.current) return;
    pausedRef.current = true;
    clearTimeout(restartTimerRef.current);
    setIsListening(false);
    try {
      recognitionRef.current?.stop();
    } catch {
      // The recognizer was between browser-managed recognition cycles.
    }
  }, []);

  const resume = useCallback(() => {
    if (!shouldListenRef.current || !recognitionRef.current) return;
    pausedRef.current = false;
    clearTimeout(restartTimerRef.current);
    restartTimerRef.current = window.setTimeout(() => {
      if (!shouldListenRef.current || pausedRef.current) return;
      try {
        recognitionRef.current?.start();
      } catch (startError) {
        if (startError?.name !== "InvalidStateError") {
          setError("Voice recognition could not resume. Click Start Voice Help.");
          shouldListenRef.current = false;
          setIsActive(false);
        }
      }
    }, 250);
  }, []);

  const clearTranscript = useCallback(() => {
    setTranscript("");
    setError("");
  }, []);

  return {
    supported,
    isListening,
    isActive,
    transcript,
    error,
    start,
    stop,
    pause,
    resume,
    clearTranscript,
  };
}
