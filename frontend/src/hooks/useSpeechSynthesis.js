import { useCallback, useEffect, useRef, useState } from "react";

import { requestTtsAudio } from "../services/api";

const BACKEND_FAILURE_MESSAGE =
  "Could not generate voice output for this language. Please check internet or TTS provider. Text guidance is still visible.";
const BACKEND_FALLBACK_MESSAGE =
  "Browser voice for this language was not found. Using backend voice output.";
const FORCE_BACKEND_TTS =
  String(import.meta.env.VITE_FORCE_BACKEND_TTS).toLowerCase() === "true";

function normalizedLanguageCode(languageCode) {
  return ["te-IN", "hi-IN", "en-IN", "en-US"].includes(languageCode)
    ? languageCode
    : "en-IN";
}

export function useSpeechSynthesis() {
  const browserSupported =
    typeof window !== "undefined" &&
    typeof window.speechSynthesis !== "undefined" &&
    typeof window.SpeechSynthesisUtterance === "function";
  const utteranceRef = useRef(null);
  const audioRef = useRef(null);
  const objectUrlRef = useRef("");
  const voicesRef = useRef([]);
  const operationRef = useRef(0);
  const [voices, setVoices] = useState([]);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [error, setError] = useState("");
  const [lastVoiceWarning, setLastVoiceWarning] = useState("");
  const [lastVoiceMode, setLastVoiceMode] = useState("");
  const [lastVoiceName, setLastVoiceName] = useState("");
  const [lastProvider, setLastProvider] = useState("");

  const refreshVoices = useCallback(() => {
    if (browserSupported) {
      const availableVoices = window.speechSynthesis.getVoices?.() || [];
      voicesRef.current = availableVoices;
      setVoices(availableVoices);
      console.log(
        "Available speech voices:",
        availableVoices.map((voice) => ({
          name: voice.name,
          lang: voice.lang,
        })),
      );
    }
  }, [browserSupported]);

  useEffect(() => {
    if (!browserSupported) return undefined;
    refreshVoices();
    window.speechSynthesis.addEventListener?.(
      "voiceschanged",
      refreshVoices,
    );
    return () => {
      window.speechSynthesis.removeEventListener?.(
        "voiceschanged",
        refreshVoices,
      );
    };
  }, [browserSupported, refreshVoices]);

  const findVoice = useCallback((languageCode = "en-IN") => {
    const requested = normalizedLanguageCode(languageCode).toLowerCase();
    const prefix = requested.split("-")[0];
    const availableVoices =
      window.speechSynthesis?.getVoices?.() || voicesRef.current;
    return (
      availableVoices.find(
        (voice) => voice.lang?.toLowerCase() === requested,
      ) ||
      availableVoices.find((voice) =>
        voice.lang?.toLowerCase().startsWith(`${prefix}-`),
      ) ||
      null
    );
  }, []);

  const hasVoiceForLanguage = useCallback(
    (languageCode) => Boolean(findVoice(languageCode)),
    [findVoice],
  );

  const clearAudio = useCallback(() => {
    const currentAudio = audioRef.current;
    if (currentAudio) {
      currentAudio.onplay = null;
      currentAudio.onended = null;
      currentAudio.onerror = null;
      currentAudio.pause?.();
      audioRef.current = null;
    }
    if (objectUrlRef.current) {
      URL.revokeObjectURL?.(objectUrlRef.current);
      objectUrlRef.current = "";
    }
  }, []);

  const stop = useCallback(() => {
    operationRef.current += 1;
    const utterance = utteranceRef.current;
    if (utterance) {
      utterance.onstart = null;
      utterance.onend = null;
      utterance.onerror = null;
      utteranceRef.current = null;
    }
    window.speechSynthesis?.cancel?.();
    clearAudio();
    setIsSpeaking(false);
  }, [clearAudio]);

  const speak = useCallback(
    async (text, options = {}) => {
      const cleanedText = text?.trim();
      if (!cleanedText) {
        return { spoken: false, reason: "empty_text" };
      }

      stop();
      const operationId = operationRef.current;
      const languageCode = normalizedLanguageCode(options.languageCode);
      const detectedLanguage = options.detectedLanguage || "english";
      const onComplete = options.onComplete;
      const forceBackendTts =
        FORCE_BACKEND_TTS ||
        options.forceBackendTts === true ||
        options.preferBackendTts === true;
      setError("");
      setLastVoiceWarning("");

      const finish = () => {
        if (operationRef.current !== operationId) return;
        setIsSpeaking(false);
        onComplete?.();
      };

      const playBackend = async (missingBrowserVoice = false) => {
        if (missingBrowserVoice) {
          setLastVoiceWarning(BACKEND_FALLBACK_MESSAGE);
        }
        try {
          const result = await requestTtsAudio({
            text: cleanedText,
            languageCode,
            detectedLanguage,
            provider: options.provider || "auto",
          });
          if (operationRef.current !== operationId) {
            return { spoken: false, reason: "canceled" };
          }

          const objectUrl = URL.createObjectURL(result.blob);
          objectUrlRef.current = objectUrl;
          const audio = new Audio(objectUrl);
          audioRef.current = audio;
          audio.onplay = () => {
            if (operationRef.current !== operationId) return;
            console.log("Speech started");
            setIsSpeaking(true);
          };
          audio.onended = () => {
            if (operationRef.current !== operationId) return;
            console.log("Speech ended");
            clearAudio();
            finish();
          };
          audio.onerror = () => {
            if (operationRef.current !== operationId) return;
            console.error("Speech error", "backend-audio-playback");
            clearAudio();
            setError(BACKEND_FAILURE_MESSAGE);
            finish();
          };
          setLastVoiceMode("backend");
          setLastProvider(result.provider || "edge_tts");
          setLastVoiceName("");
          setIsSpeaking(true);
          console.log("Speaking assistant reply");
          await audio.play();
          return {
            spoken: true,
            mode: "backend",
            voiceFound: false,
            voiceName: null,
            provider: result.provider || "edge_tts",
            languageCode,
          };
        } catch (backendError) {
          if (operationRef.current !== operationId) {
            return { spoken: false, reason: "canceled" };
          }
          console.error("Speech error", backendError);
          clearAudio();
          setIsSpeaking(false);
          setLastVoiceMode("failed");
          setLastProvider("");
          setError(BACKEND_FAILURE_MESSAGE);
          onComplete?.();
          return {
            spoken: false,
            mode: "failed",
            voiceFound: false,
            languageCode,
            reason: "backend_failed",
          };
        }
      };

      const selectedVoice = browserSupported
        ? findVoice(languageCode)
        : null;
      if (forceBackendTts || !selectedVoice) {
        return playBackend(!selectedVoice);
      }

      const utterance = new window.SpeechSynthesisUtterance(cleanedText);
      utterance.lang = languageCode;
      utterance.voice = selectedVoice;
      utterance.rate = 0.9;
      utterance.pitch = 1;
      utterance.volume = 1;
      utteranceRef.current = utterance;
      utterance.onstart = () => {
        if (operationRef.current !== operationId) return;
        console.log("Speech started");
        setIsSpeaking(true);
      };
      utterance.onend = () => {
        if (operationRef.current !== operationId) return;
        console.log("Speech ended");
        utteranceRef.current = null;
        finish();
      };
      utterance.onerror = (event) => {
        if (operationRef.current !== operationId) return;
        if (event.error === "canceled" || event.error === "interrupted") {
          finish();
          return;
        }
        console.error("Speech error", event.error);
        utteranceRef.current = null;
        void playBackend(false);
      };

      try {
        setLastVoiceMode("browser");
        setLastProvider("browser");
        setLastVoiceName(selectedVoice.name || "");
        setIsSpeaking(true);
        console.log("Speaking assistant reply");
        window.speechSynthesis.cancel();
        window.speechSynthesis.resume?.();
        window.speechSynthesis.speak(utterance);
        return {
          spoken: true,
          mode: "browser",
          voiceFound: true,
          voiceName: selectedVoice.name || null,
          provider: "browser",
          languageCode,
        };
      } catch (speechError) {
        console.error("Speech error", speechError);
        utteranceRef.current = null;
        return playBackend(false);
      }
    },
    [browserSupported, clearAudio, findVoice, stop],
  );

  useEffect(() => stop, [stop]);

  return {
    speak,
    stop,
    cancel: stop,
    isSpeaking,
    isSupported: browserSupported || typeof Audio !== "undefined",
    supported: browserSupported || typeof Audio !== "undefined",
    browserSupported,
    voices,
    refreshVoices,
    hasVoiceForLanguage,
    lastVoiceWarning,
    voiceWarning: lastVoiceWarning,
    error,
    lastVoiceMode,
    lastVoiceName,
    lastProvider,
  };
}
