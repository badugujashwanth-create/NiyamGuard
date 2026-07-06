import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "../App";
import { installApiMock } from "./fixtures";

class FakeRecognition {
  static instances = [];

  constructor() {
    this.startCalls = 0;
    this.stopCalls = 0;
    FakeRecognition.instances.push(this);
  }

  start() {
    this.startCalls += 1;
    this.onstart?.();
  }

  stop() {
    this.stopCalls += 1;
    this.onend?.();
  }

  abort() {}

  emitFinal(text) {
    const result = [{ transcript: text }];
    result.isFinal = true;
    this.onresult?.({ resultIndex: 0, results: [result] });
  }
}

class FakeUtterance {
  constructor(text) {
    this.text = text;
  }
}

class FakeAudio {
  static instances = [];

  constructor(source) {
    this.source = source;
    this.play = vi.fn(async () => {
      this.onplay?.();
    });
    this.pause = vi.fn();
    FakeAudio.instances.push(this);
  }
}

function teluguPurposeResponse() {
  return {
    success: true,
    field: "purpose",
    reply:
      "అవును. ఈ సర్టిఫికేట్ scholarship కోసం కావాలంటే, Purpose బాక్స్‌లో Scholarship అని మీరే టైప్ చేయండి.",
    suggested_value: "Scholarship",
    related_values: {},
    location_matches: [],
    warning: null,
    detected_language: "telugu",
    language_code: "te-IN",
    auto_fill: false,
    should_submit: false,
  };
}

function hindiPurposeResponse() {
  return {
    ...teluguPurposeResponse(),
    reply:
      "हाँ। यह certificate scholarship के लिए चाहिए तो Purpose box में Scholarship स्वयं लिखें।",
    detected_language: "hindi",
    language_code: "hi-IN",
  };
}

describe("NiyamGuard frontend", () => {
  beforeEach(() => {
    FakeRecognition.instances = [];
    FakeAudio.instances = [];
    window.SpeechRecognition = FakeRecognition;
    window.SpeechSynthesisUtterance = FakeUtterance;
    window.speechSynthesis = {
      cancel: vi.fn(),
      resume: vi.fn(),
      getVoices: vi.fn(() => [
        { lang: "en-IN", name: "Test English India" },
      ]),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      speak: vi.fn((utterance) => utterance.onstart?.()),
    };
    vi.stubGlobal("Audio", FakeAudio);
    Object.defineProperty(URL, "createObjectURL", {
      configurable: true,
      value: vi.fn(() => "blob:niyamguard-audio"),
    });
    Object.defineProperty(URL, "revokeObjectURL", {
      configurable: true,
      value: vi.fn(),
    });
    Object.defineProperty(navigator, "geolocation", {
      configurable: true,
      value: { getCurrentPosition: vi.fn() },
    });
  });

  it("creates an auto-language session and keeps technical selectors hidden", async () => {
    const { fetchMock } = installApiMock();
    render(<App />);

    expect(
      await screen.findByRole("heading", {
        name: "Income Certificate Application",
      }),
    ).toBeInTheDocument();
    expect(screen.queryByLabelText("Language")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Current field")).not.toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Start Voice Help" }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Type your question")).toBeInTheDocument();
    expect(navigator.geolocation.getCurrentPosition).not.toHaveBeenCalled();

    const sessionCall = fetchMock.mock.calls.find(([url]) =>
      url.endsWith("/api/sessions"),
    );
    expect(JSON.parse(sessionCall[1].body).language).toBe("auto");
  });

  it("sends language auto and the currently focused field", async () => {
    const { fetchMock } = installApiMock();
    const user = userEvent.setup();
    render(<App />);

    const incomeInput = await screen.findByLabelText(/Monthly Income/);
    await user.click(incomeInput);
    await user.type(
      screen.getByLabelText("Type your question"),
      "what should I enter here",
    );
    await user.click(screen.getByRole("button", { name: "Ask" }));

    await waitFor(() =>
      expect(
        fetchMock.mock.calls.some(([url]) =>
          url.endsWith("/api/assistant/ask"),
        ),
      ).toBe(true),
    );
    const askCall = fetchMock.mock.calls.find(([url]) =>
      url.endsWith("/api/assistant/ask"),
    );
    expect(JSON.parse(askCall[1].body)).toMatchObject({
      current_field: "monthly_income",
      language: "auto",
    });
  });

  it("uses a matching English browser voice without calling backend TTS", async () => {
    const { fetchMock } = installApiMock();
    const user = userEvent.setup();
    render(<App />);

    const incomeInput = await screen.findByLabelText(/Monthly Income/);
    await user.type(
      screen.getByLabelText("Type your question"),
      "monthly income fifteen thousand what should I enter",
    );
    await user.click(screen.getByRole("button", { name: "Ask" }));

    expect(
      await screen.findAllByText(/You can enter 15000 in Monthly Income/),
    ).not.toHaveLength(0);
    await waitFor(() =>
      expect(window.speechSynthesis.speak).toHaveBeenCalledOnce(),
    );
    const utterance = window.speechSynthesis.speak.mock.calls[0][0];
    expect(utterance.lang).toBe("en-IN");
    expect(utterance.voice.name).toBe("Test English India");
    expect(utterance.rate).toBe(0.9);
    expect(incomeInput).toHaveValue(null);
    expect(
      fetchMock.mock.calls.some(([url]) => url.endsWith("/api/tts/speak")),
    ).toBe(false);
  });

  it("uses backend MP3 for Telugu when no Telugu browser voice exists", async () => {
    const { fetchMock } = installApiMock({ ask: teluguPurposeResponse() });
    const user = userEvent.setup();
    render(<App />);

    const purposeInput = await screen.findByLabelText(/Purpose of Certificate/);
    await user.type(
      screen.getByLabelText("Type your question"),
      "purpose lo scholarship ani rayacha",
    );
    await user.click(screen.getByRole("button", { name: "Ask" }));

    expect(await screen.findAllByText(/అవును/)).not.toHaveLength(0);
    await waitFor(() => expect(FakeAudio.instances).toHaveLength(1));
    expect(FakeAudio.instances[0].play).toHaveBeenCalled();
    const ttsCall = fetchMock.mock.calls.find(([url]) =>
      url.endsWith("/api/tts/speak"),
    );
    expect(JSON.parse(ttsCall[1].body)).toMatchObject({
      language_code: "te-IN",
      detected_language: "telugu",
    });
    expect(
      screen.getByText(
        "Browser voice for this language was not found. Using backend voice output.",
      ),
    ).toBeInTheDocument();
    expect(purposeInput).toHaveValue("");
  });

  it("uses backend MP3 for Hindi when no Hindi browser voice exists", async () => {
    const { fetchMock } = installApiMock({ ask: hindiPurposeResponse() });
    const user = userEvent.setup();
    render(<App />);

    await user.type(
      await screen.findByLabelText("Type your question"),
      "purpose mein scholarship likhna hai kya",
    );
    await user.click(screen.getByRole("button", { name: "Ask" }));

    expect(await screen.findAllByText(/हाँ/)).not.toHaveLength(0);
    await waitFor(() => expect(FakeAudio.instances).toHaveLength(1));
    const ttsCall = fetchMock.mock.calls.find(([url]) =>
      url.endsWith("/api/tts/speak"),
    );
    expect(JSON.parse(ttsCall[1].body).language_code).toBe("hi-IN");
    expect(document.getElementById("purpose")).toHaveValue("");
  });

  it("Speak again replays the latest reply in its backend language", async () => {
    installApiMock({ ask: teluguPurposeResponse() });
    const user = userEvent.setup();
    render(<App />);

    await user.type(
      await screen.findByLabelText("Type your question"),
      "purpose lo scholarship ani rayacha",
    );
    await user.click(screen.getByRole("button", { name: "Ask" }));
    await waitFor(() => expect(FakeAudio.instances).toHaveLength(1));
    FakeAudio.instances[0].onended?.();

    await user.click(screen.getByRole("button", { name: "మళ్లీ వినండి" }));
    await waitFor(() => expect(FakeAudio.instances).toHaveLength(2));
    expect(FakeAudio.instances[1].play).toHaveBeenCalled();
  });

  it("can force backend voice from collapsed developer diagnostics", async () => {
    const { fetchMock } = installApiMock();
    const user = userEvent.setup();
    render(<App />);

    await user.type(
      await screen.findByLabelText("Type your question"),
      "monthly income fifteen thousand",
    );
    await user.click(screen.getByRole("button", { name: "Ask" }));
    await waitFor(() =>
      expect(window.speechSynthesis.speak).toHaveBeenCalledOnce(),
    );

    await user.click(screen.getByText("Developer Diagnostics"));
    await user.click(
      screen.getByRole("button", { name: "Force Backend Voice" }),
    );
    await waitFor(() =>
      expect(
        fetchMock.mock.calls.some(([url]) => url.endsWith("/api/tts/speak")),
      ).toBe(true),
    );
    expect(FakeAudio.instances).toHaveLength(1);
  });

  it("pauses recognition while speaking and resumes only while voice help is active", async () => {
    installApiMock();
    const user = userEvent.setup();
    render(<App />);

    await user.click(
      await screen.findByRole("button", { name: "Start Voice Help" }),
    );
    const recognition = FakeRecognition.instances.at(-1);
    recognition.emitFinal("monthly income fifteen thousand");

    await waitFor(() =>
      expect(window.speechSynthesis.speak).toHaveBeenCalled(),
    );
    expect(recognition.stopCalls).toBeGreaterThan(0);
    window.speechSynthesis.speak.mock.calls[0][0].onend();
    await waitFor(() => expect(recognition.startCalls).toBeGreaterThan(1));

    recognition.emitFinal("monthly income fifteen thousand");
    await waitFor(() =>
      expect(window.speechSynthesis.speak).toHaveBeenCalledTimes(2),
    );
    await user.click(screen.getByRole("button", { name: "Stop Voice Help" }));
    const startsAfterStop = recognition.startCalls;
    window.speechSynthesis.speak.mock.calls[1][0].onend();
    await new Promise((resolve) => window.setTimeout(resolve, 350));
    expect(recognition.startCalls).toBe(startsAfterStop);
  });

  it("falls back to backend audio when browser synthesis errors", async () => {
    const { fetchMock } = installApiMock();
    const user = userEvent.setup();
    const errorSpy = vi.spyOn(console, "error").mockImplementation(() => {});
    render(<App />);

    await user.type(
      await screen.findByLabelText("Type your question"),
      "monthly income fifteen thousand",
    );
    await user.click(screen.getByRole("button", { name: "Ask" }));
    await waitFor(() =>
      expect(window.speechSynthesis.speak).toHaveBeenCalled(),
    );
    window.speechSynthesis.speak.mock.calls[0][0].onerror({
      error: "synthesis-failed",
    });

    await waitFor(() =>
      expect(
        fetchMock.mock.calls.some(([url]) => url.endsWith("/api/tts/speak")),
      ).toBe(true),
    );
    expect(FakeAudio.instances).toHaveLength(1);
    expect(errorSpy).toHaveBeenCalledWith("Speech error", "synthesis-failed");
  });

  it("keeps text visible when backend TTS fails", async () => {
    installApiMock({ ask: teluguPurposeResponse(), ttsError: true });
    const user = userEvent.setup();
    vi.spyOn(console, "error").mockImplementation(() => {});
    render(<App />);

    await user.type(
      await screen.findByLabelText("Type your question"),
      "purpose lo scholarship ani rayacha",
    );
    await user.click(screen.getByRole("button", { name: "Ask" }));

    expect(await screen.findAllByText(/అవును/)).not.toHaveLength(0);
    expect(
      await screen.findByText(
        "Could not generate voice output for this language. Please check internet or TTS provider. Text guidance is still visible.",
      ),
    ).toBeInTheDocument();
  });

  it("offers mandal quick help, speaks the response, and never fills location fields", async () => {
    const locationReply = {
      success: true,
      field: "mandal",
      reply:
        "మీ pincode ప్రకారం జిల్లా Rangareddy, మండలం Serilingampally ఉండవచ్చు. దయచేసి confirm చేయండి.",
      suggested_value: null,
      related_values: {
        district: "Rangareddy",
        mandal: "Serilingampally",
      },
      location_matches: [],
      warning: null,
      detected_language: "telugu",
      language_code: "te-IN",
      auto_fill: false,
      should_submit: false,
    };
    const { fetchMock } = installApiMock({ ask: locationReply });
    const user = userEvent.setup();
    render(<App />);

    await user.click(
      await screen.findByRole("button", {
        name: "I don't know my mandal",
      }),
    );

    expect(await screen.findAllByText(/Serilingampally/)).not.toHaveLength(0);
    await waitFor(() => expect(FakeAudio.instances).toHaveLength(1));
    expect(document.getElementById("district")).toHaveValue("");
    expect(document.getElementById("mandal")).toHaveValue("");
    const askCall = fetchMock.mock.calls.find(([url]) =>
      url.endsWith("/api/assistant/ask"),
    );
    expect(JSON.parse(askCall[1].body)).toMatchObject({
      message: "na mandal teliyadu",
      language: "auto",
    });
  });

  it("requests geolocation only after the user clicks the optional button", async () => {
    const { fetchMock } = installApiMock();
    const user = userEvent.setup();
    navigator.geolocation.getCurrentPosition.mockImplementation((success) =>
      success({ coords: { latitude: 17.444, longitude: 78.377 } }),
    );
    render(<App />);

    await screen.findByRole("button", {
      name: "Use My Location to Help Find Mandal",
    });
    expect(navigator.geolocation.getCurrentPosition).not.toHaveBeenCalled();

    await user.click(
      screen.getByRole("button", {
        name: "Use My Location to Help Find Mandal",
      }),
    );
    expect(navigator.geolocation.getCurrentPosition).toHaveBeenCalledOnce();
    await waitFor(() =>
      expect(
        fetchMock.mock.calls.some(([url]) =>
          url.endsWith("/api/location/reverse"),
        ),
      ).toBe(true),
    );
    expect(document.getElementById("district")).toHaveValue("");
    expect(document.getElementById("mandal")).toHaveValue("");
  });

  it("sends only manually typed values for review", async () => {
    const { fetchMock } = installApiMock();
    const user = userEvent.setup();
    render(<App />);

    const purposeInput = await screen.findByLabelText(/Purpose of Certificate/);
    await user.type(purposeInput, "Scholarship");
    await user.click(screen.getByRole("button", { name: "Review My Details" }));

    expect(
      await screen.findAllByText("Please review your details."),
    ).not.toHaveLength(0);
    const summaryCall = fetchMock.mock.calls.find(([url]) =>
      url.endsWith("/api/assistant/summary"),
    );
    expect(JSON.parse(summaryCall[1].body)).toMatchObject({
      language: "auto",
      form_values: expect.objectContaining({ purpose: "Scholarship" }),
    });
  });

  it("keeps submission manual and never calls a submission API", async () => {
    const { fetchMock } = installApiMock();
    render(<App />);
    await screen.findByRole("heading", {
      name: "Income Certificate Application",
    });

    fireEvent.submit(
      screen
        .getByRole("button", { name: "Submit Manually (Demo)" })
        .closest("form"),
    );
    expect(
      screen.getByText(/No government application was submitted/i),
    ).toBeInTheDocument();
    expect(
      fetchMock.mock.calls.some(([url]) => /submit/i.test(url)),
    ).toBe(false);
  });
});
