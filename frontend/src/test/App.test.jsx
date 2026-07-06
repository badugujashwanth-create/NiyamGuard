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
    this.onresult?.({
      resultIndex: 0,
      results: [result],
    });
  }
}

class FakeUtterance {
  constructor(text) {
    this.text = text;
  }
}

describe("NiyamGuard frontend", () => {
  beforeEach(() => {
    FakeRecognition.instances = [];
    window.SpeechRecognition = FakeRecognition;
    window.SpeechSynthesisUtterance = FakeUtterance;
    window.speechSynthesis = {
      cancel: vi.fn(),
      resume: vi.fn(),
      getVoices: vi.fn(() => [{ lang: "en-IN", name: "Test English" }]),
      speak: vi.fn((utterance) => utterance.onstart?.()),
    };
  });

  it("creates a backend session and displays the form", async () => {
    const { fetchMock } = installApiMock();
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Income Certificate Application" }))
      .toBeInTheDocument();
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/sessions"),
        expect.objectContaining({ method: "POST" }),
      ),
    );
  });

  it("supports text questions without auto-filling the form", async () => {
    installApiMock();
    const user = userEvent.setup();
    render(<App />);

    const incomeInput = await waitFor(() =>
      expect(document.getElementById("monthly_income")).toBeInTheDocument(),
    ).then(() => document.getElementById("monthly_income"));
    expect(incomeInput).toHaveValue(null);

    const question = screen.getByLabelText("Type your question");
    await user.type(
      question,
      "monthly income fifteen thousand what should I enter",
    );
    await user.click(screen.getByRole("button", { name: "Ask" }));

    expect(
      await screen.findAllByText(/You can enter 15000 in Monthly Income/),
    ).not.toHaveLength(0);
    expect(screen.getByText("15000", { selector: ".suggestion strong" }))
      .toBeInTheDocument();
    expect(incomeInput).toHaveValue(null);
    await waitFor(() => expect(window.speechSynthesis.speak).toHaveBeenCalledOnce());

    const spokenReply = window.speechSynthesis.speak.mock.calls[0][0];
    expect(spokenReply.text).toContain("You can enter 15000");
    expect(spokenReply.lang).toBe("en-IN");
    expect(spokenReply.rate).toBe(0.9);
    expect(spokenReply.pitch).toBe(1);
    expect(spokenReply.volume).toBe(1);
    expect(spokenReply.voice?.lang).toBe("en-IN");
    expect(window.speechSynthesis.resume).toHaveBeenCalled();

    await user.type(incomeInput, "15000");
    expect(incomeInput).toHaveValue(15000);
  });

  it("uses the backend Telugu language code for text and speech", async () => {
    installApiMock({
      ask: {
        success: true,
        field: "purpose",
        reply:
          "అవును. Purpose of Certificate ఫీల్డ్‌లో “Scholarship” అని టైప్ చేయండి.",
        suggested_value: "Scholarship",
        related_values: {},
        warning: null,
        detected_language: "telugu",
        language_code: "te-IN",
        auto_fill: false,
        should_submit: false,
      },
    });
    const user = userEvent.setup();
    render(<App />);

    await user.click(
      await screen.findByRole("button", {
        name: /Telugu purpose lo scholarship ani rayacha/,
      }),
    );
    expect(screen.getByLabelText("Type your question")).toHaveValue(
      "purpose lo scholarship ani rayacha",
    );
    await user.click(screen.getByRole("button", { name: "Ask" }));

    expect(await screen.findAllByText(/అవును/)).not.toHaveLength(0);
    await waitFor(() => expect(window.speechSynthesis.speak).toHaveBeenCalled());
    expect(window.speechSynthesis.speak.mock.calls[0][0].lang).toBe("te-IN");
    expect(document.getElementById("purpose")).toHaveValue("");
    expect(
      screen.getByText(
        "Your browser may not have a Telugu/Hindi voice installed. Text guidance is still available.",
      ),
    ).toBeInTheDocument();
  });

  it("uses the backend Hindi language code for speech", async () => {
    installApiMock({
      ask: {
        success: true,
        field: "purpose",
        reply:
          "हाँ। Purpose of Certificate field में “Scholarship” लिख सकते हैं।",
        suggested_value: "Scholarship",
        related_values: {},
        warning: null,
        detected_language: "hindi",
        language_code: "hi-IN",
        auto_fill: false,
        should_submit: false,
      },
    });
    const user = userEvent.setup();
    render(<App />);

    await user.type(
      await screen.findByLabelText("Type your question"),
      "purpose mein scholarship likhna hai kya",
    );
    await user.click(screen.getByRole("button", { name: "Ask" }));

    expect(await screen.findAllByText(/हाँ/)).not.toHaveLength(0);
    await waitFor(() => expect(window.speechSynthesis.speak).toHaveBeenCalled());
    expect(window.speechSynthesis.speak.mock.calls[0][0].lang).toBe("hi-IN");
    expect(document.getElementById("purpose")).toHaveValue("");
  });

  it("speaks the latest reply again and logs the speech lifecycle", async () => {
    installApiMock();
    const logSpy = vi.spyOn(console, "log").mockImplementation(() => {});
    const user = userEvent.setup();
    render(<App />);

    await user.type(
      await screen.findByLabelText("Type your question"),
      "monthly income fifteen thousand what should I enter",
    );
    await user.click(screen.getByRole("button", { name: "Ask" }));

    await waitFor(() => expect(window.speechSynthesis.speak).toHaveBeenCalledOnce());
    expect(logSpy).toHaveBeenCalledWith("Speaking assistant reply");
    expect(logSpy).toHaveBeenCalledWith("Speech started");

    const firstUtterance = window.speechSynthesis.speak.mock.calls[0][0];
    firstUtterance.onend();
    expect(logSpy).toHaveBeenCalledWith("Speech ended");

    await user.click(screen.getByRole("button", { name: "Speak again" }));
    await waitFor(() =>
      expect(window.speechSynthesis.speak).toHaveBeenCalledTimes(2),
    );
    expect(window.speechSynthesis.speak.mock.calls[1][0].text).toBe(
      firstUtterance.text,
    );
    expect(window.speechSynthesis.cancel).toHaveBeenCalledTimes(2);
  });

  it("shows live voice transcript, asks the backend, and speaks its reply", async () => {
    installApiMock();
    const user = userEvent.setup();
    render(<App />);

    const startButton = await screen.findByRole("button", {
      name: "Start Voice Help",
    });
    await user.click(startButton);
    expect(
      screen.getByRole("button", { name: "Listening continuously…" }),
    ).toBeInTheDocument();

    const recognition = FakeRecognition.instances.at(-1);
    expect(recognition.continuous).toBe(true);
    recognition.emitFinal(
      "monthly income fifteen thousand",
    );

    expect(
      await screen.findAllByText("monthly income fifteen thousand"),
    ).not.toHaveLength(0);
    await waitFor(() => expect(window.speechSynthesis.speak).toHaveBeenCalled());
    expect(window.speechSynthesis.speak.mock.calls[0][0].text).toContain(
      "You can enter 15000",
    );
    expect(recognition.stopCalls).toBeGreaterThan(0);

    window.speechSynthesis.speak.mock.calls[0][0].onend();
    await waitFor(() => expect(recognition.startCalls).toBeGreaterThan(1));
    expect(
      screen.getByRole("button", { name: "Listening continuously…" }),
    ).toBeInTheDocument();
  });

  it("does not resume recognition after voice help is stopped during speech", async () => {
    installApiMock();
    const user = userEvent.setup();
    render(<App />);

    await user.click(
      await screen.findByRole("button", { name: "Start Voice Help" }),
    );
    const recognition = FakeRecognition.instances.at(-1);
    recognition.emitFinal("monthly income fifteen thousand");

    await waitFor(() => expect(window.speechSynthesis.speak).toHaveBeenCalled());
    await user.click(screen.getByRole("button", { name: "Stop Voice Help" }));
    const startCallsAfterStop = recognition.startCalls;

    window.speechSynthesis.speak.mock.calls[0][0].onend();
    await new Promise((resolve) => window.setTimeout(resolve, 350));
    expect(recognition.startCalls).toBe(startCallsAfterStop);
  });

  it("reports and logs browser speech errors", async () => {
    installApiMock();
    const errorSpy = vi.spyOn(console, "error").mockImplementation(() => {});
    const user = userEvent.setup();
    render(<App />);

    await user.type(
      await screen.findByLabelText("Type your question"),
      "monthly income fifteen thousand",
    );
    await user.click(screen.getByRole("button", { name: "Ask" }));
    await waitFor(() => expect(window.speechSynthesis.speak).toHaveBeenCalled());

    window.speechSynthesis.speak.mock.calls[0][0].onerror({
      error: "synthesis-failed",
    });

    expect(errorSpy).toHaveBeenCalledWith("Speech error", "synthesis-failed");
    expect(
      await screen.findByText(
        "The browser could not speak this reply. Check device volume and browser audio permissions.",
      ),
    ).toBeInTheDocument();
  });

  it("warns when browser voice output is unavailable", async () => {
    installApiMock();
    window.speechSynthesis = undefined;
    window.SpeechSynthesisUtterance = undefined;

    render(<App />);

    expect(
      await screen.findByText(
        "Voice output is not supported in this browser. Please use Chrome or Edge.",
      ),
    ).toBeInTheDocument();
  });

  it("sends only manually typed values for review", async () => {
    const { fetchMock } = installApiMock();
    const user = userEvent.setup();
    render(<App />);

    const purposeInput = await waitFor(() =>
      expect(document.getElementById("purpose")).toBeInTheDocument(),
    ).then(() => document.getElementById("purpose"));
    await user.type(purposeInput, "Scholarship");
    await user.click(screen.getByRole("button", { name: "Review My Details" }));

    expect(
      await screen.findAllByText("Please review your details."),
    ).not.toHaveLength(0);
    const summaryCall = fetchMock.mock.calls.find(([url]) =>
      url.endsWith("/api/assistant/summary"),
    );
    expect(JSON.parse(summaryCall[1].body).form_values.purpose).toBe("Scholarship");
  });

  it("keeps submission manual and never calls a submission API", async () => {
    const { fetchMock } = installApiMock();
    render(<App />);
    await screen.findByRole("heading", { name: "Income Certificate Application" });

    fireEvent.submit(
      screen.getByRole("button", { name: "Submit Manually (Demo)" }).closest("form"),
    );
    expect(
      screen.getByText(/no government application was submitted/i),
    ).toBeInTheDocument();
    expect(
      fetchMock.mock.calls.some(([url]) => /submit/i.test(url)),
    ).toBe(false);
  });
});
