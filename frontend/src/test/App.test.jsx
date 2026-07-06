import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "../App";
import { installApiMock } from "./fixtures";

class FakeRecognition {
  static instances = [];

  constructor() {
    this.startCalls = 0;
    FakeRecognition.instances.push(this);
  }

  start() {
    this.startCalls += 1;
    this.onstart?.();
  }

  stop() {
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
    await user.type(question, "monthly income fifteen thousand");
    await user.click(screen.getByRole("button", { name: "Ask" }));

    expect(
      await screen.findAllByText(/You can enter 15000 in Monthly Income/),
    ).not.toHaveLength(0);
    expect(screen.getByText("15000", { selector: ".suggestion strong" }))
      .toBeInTheDocument();
    expect(incomeInput).toHaveValue(null);

    await user.type(incomeInput, "15000");
    expect(incomeInput).toHaveValue(15000);
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
    expect(window.speechSynthesis.resume).toHaveBeenCalled();

    window.speechSynthesis.speak.mock.calls[0][0].onend();
    await waitFor(() => expect(recognition.startCalls).toBeGreaterThan(1));
    expect(
      screen.getByRole("button", { name: "Listening continuously…" }),
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
