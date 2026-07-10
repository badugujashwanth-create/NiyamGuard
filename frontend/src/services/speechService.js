export const SPEECH_FALLBACK_MESSAGE =
  "Voice input is not available in this browser. You can continue using text.";

export function isLocalhost(hostname = "") {
  return ["localhost", "127.0.0.1", "::1", "[::1]"].includes(hostname);
}

export function isSecureSpeechContext(location = globalThis.window?.location) {
  if (!location) return false;
  return location.protocol === "https:" || isLocalhost(location.hostname);
}

export function getSpeechRecognitionConstructor(win = globalThis.window) {
  return win?.SpeechRecognition || win?.webkitSpeechRecognition || null;
}

export function getSpeechSupport({
  win = globalThis.window,
  location = globalThis.window?.location,
  navigatorRef = globalThis.navigator,
} = {}) {
  const recognition = getSpeechRecognitionConstructor(win);
  const secureContext = isSecureSpeechContext(location);
  const microphoneSupported = Boolean(navigatorRef?.mediaDevices?.getUserMedia);
  const webSpeechSupported = Boolean(recognition);
  const supported = secureContext && (webSpeechSupported || microphoneSupported);

  let reason = "";
  if (!secureContext) {
    reason = "Voice input needs localhost or HTTPS. You can continue using text.";
  } else if (!webSpeechSupported && !microphoneSupported) {
    reason = SPEECH_FALLBACK_MESSAGE;
  }

  return {
    supported,
    webSpeechSupported,
    microphoneSupported,
    secureContext,
    recognition,
    reason,
  };
}

export function speechErrorMessage(errorCode) {
  const messages = {
    "not-allowed": "Microphone permission was denied. Use Text Instead.",
    "service-not-allowed": SPEECH_FALLBACK_MESSAGE,
    "no-speech": "No speech was heard. Please try again or Use Text Instead.",
    "audio-capture": "No microphone was found. You can continue using text.",
    network: SPEECH_FALLBACK_MESSAGE,
    aborted: "",
  };
  return messages[errorCode] || SPEECH_FALLBACK_MESSAGE;
}
