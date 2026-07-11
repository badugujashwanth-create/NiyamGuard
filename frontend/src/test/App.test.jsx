import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "../app/App";
import { setAuthSession } from "../services/api";
import { adminUser, citizenUser, installApiMock, officerUser } from "./fixtures";

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
      "à°…à°µà±à°¨à±. à°ˆ certificate scholarship à°•à±‹à°¸à°‚ à°•à°¾à°µà°¾à°²à°‚à°Ÿà±‡ Purpose à°¬à°¾à°•à±à°¸à±â€Œà°²à±‹ Scholarship à°…à°¨à°¿ à°®à±€à°°à±‡ à°Ÿà±ˆà°ªà± à°šà±‡à°¯à°‚à°¡à°¿.",
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
      "à¤¹à¤¾à¤à¥¤ à¤¯à¤¹ certificate scholarship à¤•à¥‡ à¤²à¤¿à¤ à¤šà¤¾à¤¹à¤¿à¤ à¤¤à¥‹ Purpose box à¤®à¥‡à¤‚ Scholarship à¤¸à¥à¤µà¤¯à¤‚ à¤²à¤¿à¤–à¥‡à¤‚.",
    detected_language: "hindi",
    language_code: "hi-IN",
  };
}

async function openIncomeForm(user) {
  await screen.findByRole("heading", { name: "Choose a simplified service form" });
  await user.click(screen.getAllByRole("button", { name: "Start Application" })[0]);
  return screen.findByRole("heading", { name: "Income Certificate Application" });
}

async function openTextFallback(user) {
  return screen.getByLabelText("Message");
}

function seedAdminSession(user = adminUser) {
  setAuthSession({
    accessToken: "test-access-token",
    refreshToken: "test-refresh-token",
    user,
  });
}

describe("NiyamGuard frontend", () => {
  beforeEach(() => {
    window.history.pushState({}, "", "/citizen/assistant");
    seedAdminSession(citizenUser);
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
    Object.defineProperty(window, "MediaRecorder", {
      configurable: true,
      value: undefined,
    });
    Object.defineProperty(window, "scrollTo", {
      configurable: true,
      value: vi.fn(),
    });
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
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: { writeText: vi.fn() },
    });
  });

  it("landing page exposes each isolated portal and public verification", async () => {
    installApiMock();
    window.history.pushState({}, "", "/");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "NiyamGuard" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Open Citizen Portal" })).toHaveAttribute("href", "/citizen");
    expect(screen.getByRole("link", { name: "Open Government Portal" })).toHaveAttribute("href", "/government");
    expect(screen.getByRole("link", { name: "Open Admin Portal" })).toHaveAttribute("href", "/admin");
    expect(screen.getByRole("link", { name: "Verify a Certificate" })).toHaveAttribute("href", "/verify-certificate");
    expect(screen.queryByText(/old demo/i)).not.toBeInTheDocument();
    expect(screen.queryByText("Run Full End-to-End Demo")).not.toBeInTheDocument();
  });

  it("opens on the service catalog and hides technical selectors", async () => {
    const { fetchMock } = installApiMock();
    render(<App />);

    expect(
      await screen.findByRole("heading", { name: "Choose a simplified service form" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Income Certificate")).toBeInTheDocument();
    expect(screen.getAllByText("Ready form").length).toBeGreaterThan(0);
    expect(screen.getByText("Catalog only / coming soon")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Detailed guided form coming soon" }),
    ).toBeDisabled();
    expect(screen.queryByLabelText("Language")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Current field")).not.toBeInTheDocument();
    expect(navigator.geolocation.getCurrentPosition).not.toHaveBeenCalled();

    const sessionCall = fetchMock.mock.calls.find(([url]) =>
      url.endsWith("/api/sessions"),
    );
    expect(JSON.parse(sessionCall[1].body)).toEqual({
      form_id: "catalog",
      language: "auto",
    });
  });

  it("searches services from the catalog", async () => {
    const { fetchMock } = installApiMock();
    const user = userEvent.setup();
    render(<App />);

    await user.type(await screen.findByLabelText("Search services"), "income");
    expect(
      fetchMock.mock.calls.some(([url]) => url.includes("/api/services/search?q=income")),
    ).toBe(true);
  });

  it("lets the catalog assistant suggest a ready service", async () => {
    installApiMock();
    const user = userEvent.setup();
    render(<App />);

    await user.type(
      await screen.findByLabelText("Ask assistant about services"),
      "Scholarship kosam income certificate kavali",
    );
    await user.click(screen.getAllByRole("button", { name: "Ask Assistant" })[0]);

    expect(
      await screen.findByText(/may need the Income Certificate form/i),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Start Income Certificate" })).toBeInTheDocument();
  });

  it("does not open catalog-only suggestions", async () => {
    installApiMock({
      ask: {
        success: true,
        field: null,
        reply:
          "It looks like you may need Loan Eligibility Card. I can explain general requirements, but the detailed guided form is coming soon.",
        suggested_form_id: "loan_eligibility_card",
        suggested_form_name: "Loan Eligibility Card",
        related_values: {},
        location_matches: [],
        warning: null,
        detected_language: "english",
        language_code: "en-IN",
        auto_fill: false,
        should_submit: false,
      },
    });
    const user = userEvent.setup();
    render(<App />);

    await user.type(
      await screen.findByLabelText("Ask assistant about services"),
      "I need a loan eligibility card",
    );
    await user.click(screen.getAllByRole("button", { name: "Ask Assistant" })[0]);

    expect(await screen.findByText("Detailed guided form coming soon.")).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Start Loan Eligibility Card" }),
    ).not.toBeInTheDocument();
  });

  it("renders the selected dynamic form and document section", async () => {
    installApiMock();
    const user = userEvent.setup();
    render(<App />);

    await openIncomeForm(user);
    expect(screen.getByLabelText(/Monthly Income/)).toBeInTheDocument();
    expect(screen.getByText("Upload guidance")).toBeInTheDocument();
    expect(screen.getByLabelText("Upload Income Proof")).toBeInTheDocument();
  });

  it("shows voice controls with a visible text fallback", async () => {
    installApiMock();
    const user = userEvent.setup();
    render(<App />);
    await openIncomeForm(user);

    const assistant = screen.getByRole("complementary", {
      name: "NiyamGuard Chatbot",
    });
    const mainControls = within(assistant.querySelector(".voice-controls")).getAllByRole(
      "button",
    );
    expect(mainControls.map((button) => button.textContent)).toEqual(["Start", "Stop", "Type"]);
    expect(screen.queryByText("Force Backend Voice")).not.toBeInTheDocument();
    expect(screen.queryByText("Speak Again")).not.toBeInTheDocument();
    expect(screen.queryByText("Raw JSON")).not.toBeInTheDocument();
    expect(screen.getByLabelText("Message")).toBeVisible();
    await user.click(screen.getByRole("button", { name: "Type" }));
    expect(screen.getByLabelText("Message")).toHaveFocus();
  });

  it("validates uploaded files locally", async () => {
    installApiMock();
    const user = userEvent.setup();
    render(<App />);
    await openIncomeForm(user);

    fireEvent.change(screen.getByLabelText("Upload Income Proof"), {
      target: {
        files: [new File(["bad"], "income.txt", { type: "text/plain" })],
      },
    });
    expect(await screen.findByText(/File type .txt is not accepted/)).toBeInTheDocument();

    await user.upload(
      screen.getByLabelText("Upload Aadhaar Card"),
      new File([new Uint8Array(1024 * 1024 * 6)], "aadhaar.pdf", {
        type: "application/pdf",
      }),
    );
    expect(await screen.findByText(/File is too large/)).toBeInTheDocument();
  });

  it("sends selected form id and focused field context", async () => {
    const { fetchMock } = installApiMock();
    const user = userEvent.setup();
    render(<App />);
    await openIncomeForm(user);

    await user.click(screen.getByLabelText(/Monthly Income/));
    const input = await openTextFallback(user);
    await user.type(input, "what should I enter here");
    await user.click(screen.getByRole("button", { name: "Ask" }));

    await waitFor(() =>
      expect(fetchMock.mock.calls.some(([url]) => url.endsWith("/api/assistant/ask"))).toBe(true),
    );
    const askCall = fetchMock.mock.calls.findLast(([url]) =>
      url.endsWith("/api/assistant/ask"),
    );
    expect(JSON.parse(askCall[1].body)).toMatchObject({
      form_id: "income_certificate",
      current_field: "monthly_income",
      current_document: null,
      last_visible_section: "details",
      language: "english",
    });
  });

  it("sends focused document context for upload guidance", async () => {
    const { fetchMock } = installApiMock();
    const user = userEvent.setup();
    render(<App />);
    await openIncomeForm(user);

    fireEvent.focus(screen.getByLabelText("Upload Income Proof"));
    const input = await openTextFallback(user);
    await user.type(input, "what should I upload here");
    await user.click(screen.getByRole("button", { name: "Ask" }));

    await waitFor(() =>
      expect(fetchMock.mock.calls.some(([url]) => url.endsWith("/api/assistant/ask"))).toBe(true),
    );
    const askCall = fetchMock.mock.calls.findLast(([url]) =>
      url.endsWith("/api/assistant/ask"),
    );
    expect(JSON.parse(askCall[1].body)).toMatchObject({
      form_id: "income_certificate",
      current_document: "income_proof",
      last_visible_section: "documents",
    });
  });

  it("speaks the introduction before starting browser fallback recognition", async () => {
    installApiMock();
    const user = userEvent.setup();
    render(<App />);
    await openIncomeForm(user);

    await user.click(screen.getByRole("button", { name: "Start" }));
    expect(screen.getByRole("status")).toHaveTextContent("Speaking...");
    expect(window.speechSynthesis.speak).toHaveBeenCalledOnce();
    expect(window.speechSynthesis.speak.mock.calls[0][0].text).toContain(
      "Namaste. I am NiyamGuard Voice Assistant",
    );
    const recognition = FakeRecognition.instances.at(-1);
    expect(recognition.startCalls).toBe(0);
    window.speechSynthesis.speak.mock.calls[0][0].onend();
    await waitFor(() => expect(recognition.startCalls).toBe(1));
    expect(screen.getByRole("status")).toHaveTextContent("Listening...");
  });

  it("uses the citizen-selected Telugu language for recognition and assistant routing", async () => {
    const { fetchMock } = installApiMock();
    const user = userEvent.setup();
    render(<App />);
    await openIncomeForm(user);

    await user.selectOptions(screen.getByLabelText("Voice language"), "te-IN");
    await waitFor(() => expect(FakeRecognition.instances.at(-1).lang).toBe("te-IN"));

    const input = await openTextFallback(user);
    await user.type(input, "monthly income fifteen thousand");
    await user.click(screen.getByRole("button", { name: "Ask" }));

    await waitFor(() =>
      expect(fetchMock.mock.calls.some(([url]) => url.endsWith("/api/assistant/ask"))).toBe(true),
    );
    const askCall = fetchMock.mock.calls.findLast(([url]) => url.endsWith("/api/assistant/ask"));
    expect(JSON.parse(askCall[1].body).language).toBe("telugu");
  });

  it("moves through listening, thinking, and speaking states for voice input", async () => {
    const { fetchMock } = installApiMock({ askDelayMs: 40 });
    const user = userEvent.setup();
    render(<App />);
    await openIncomeForm(user);

    await user.click(screen.getByRole("button", { name: "Start" }));
    window.speechSynthesis.speak.mock.calls[0][0].onend();
    const recognition = FakeRecognition.instances.at(-1);
    await waitFor(() => expect(recognition.startCalls).toBe(1));
    recognition.emitFinal("monthly income fifteen thousand");

    expect(await screen.findByText("Thinking...")).toBeInTheDocument();
    await waitFor(() =>
      expect(fetchMock.mock.calls.some(([url]) => url.endsWith("/api/assistant/ask"))).toBe(true),
    );
    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("Speaking..."));
    expect(await screen.findAllByText(/You can enter 15000/)).not.toHaveLength(0);
  });

  it("citizen apply form shows the Voice Form Assistant", async () => {
    installApiMock();
    const user = userEvent.setup();
    render(<App />);
    await openIncomeForm(user);
    expect(screen.getByRole("heading", { name: "NiyamGuard Chatbot" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Start" })).toBeInTheDocument();
  });

  it("asking mandalam renders direct mandal guidance", async () => {
    installApiMock({
      ask: {
        success: true,
        field: "mandal",
        reply: "A mandal is the local administrative area. Enter the mandal shown on your address proof.",
        detected_language: "english",
        language_code: "en-IN",
        auto_fill: false,
        should_submit: false,
      },
    });
    const user = userEvent.setup();
    render(<App />);
    await openIncomeForm(user);
    const input = await openTextFallback(user);
    await user.type(input, "mandalam");
    await user.click(screen.getByRole("button", { name: "Ask" }));
    expect(await screen.findAllByText(/local administrative area/)).not.toHaveLength(0);
  });

  it("asking occupation with a name renders a correction", async () => {
    installApiMock({
      ask: {
        success: true,
        field: "occupation",
        reply: "Occupation means your job or main work, not your name. Use Student, Employee, Farmer, Business, Homemaker, Unemployed, or Other.",
        detected_language: "english",
        language_code: "en-IN",
        auto_fill: false,
        should_submit: false,
      },
    });
    const user = userEvent.setup();
    render(<App />);
    await openIncomeForm(user);
    const input = await openTextFallback(user);
    await user.type(input, "occupation lag raha hai Imran Ali");
    await user.click(screen.getByRole("button", { name: "Ask" }));
    expect(await screen.findAllByText(/not your name/)).not.toHaveLength(0);
  });

  it("sends the real final voice transcript through citizen knowledge routing", async () => {
    const { fetchMock } = installApiMock();
    const user = userEvent.setup();
    render(<App />);
    await openIncomeForm(user);

    await user.click(screen.getByRole("button", { name: "Start" }));
    window.speechSynthesis.speak.mock.calls[0][0].onend();
    const recognition = FakeRecognition.instances.at(-1);
    await waitFor(() => expect(recognition.startCalls).toBe(1));
    recognition.emitFinal("scholarship documents enti");

    await waitFor(() => expect(fetchMock.mock.calls.some(([url]) => url.endsWith("/api/chat"))).toBe(true));
    const chatCall = fetchMock.mock.calls.find(([url]) => url.endsWith("/api/chat"));
    expect(JSON.parse(chatCall[1].body).message).toBe("scholarship documents enti");
    expect(await screen.findAllByText(/For Post-Matric Scholarship/)).not.toHaveLength(0);
  });

  it("uses a matching English browser voice without backend TTS", async () => {
    const { fetchMock } = installApiMock();
    const user = userEvent.setup();
    render(<App />);
    await openIncomeForm(user);

    const incomeInput = screen.getByLabelText(/Monthly Income/);
    const input = await openTextFallback(user);
    await user.type(input, "monthly income fifteen thousand");
    await user.click(screen.getByRole("button", { name: "Ask" }));

    expect(await screen.findAllByText(/You can enter 15000/)).not.toHaveLength(0);
    await waitFor(() => expect(window.speechSynthesis.speak).toHaveBeenCalledOnce());
    expect(window.speechSynthesis.speak.mock.calls[0][0].lang).toBe("en-IN");
    expect(incomeInput).toHaveValue(null);
    expect(fetchMock.mock.calls.some(([url]) => url.endsWith("/api/tts/speak"))).toBe(false);
  });

  it("uses backend TTS for Telugu and does not auto-fill", async () => {
    const { fetchMock } = installApiMock({ ask: teluguPurposeResponse() });
    const user = userEvent.setup();
    render(<App />);
    await openIncomeForm(user);

    const purposeInput = screen.getByLabelText(/Purpose of Certificate/);
    const input = await openTextFallback(user);
    await user.type(input, "purpose lo scholarship ani rayacha");
    await user.click(screen.getByRole("button", { name: "Ask" }));

    expect(await screen.findAllByText(/à°…à°µà±à°¨à±/)).not.toHaveLength(0);
    await waitFor(() => expect(FakeAudio.instances).toHaveLength(1));
    const ttsCall = fetchMock.mock.calls.find(([url]) => url.endsWith("/api/tts/speak"));
    expect(JSON.parse(ttsCall[1].body)).toMatchObject({
      language_code: "te-IN",
      detected_language: "telugu",
    });
    expect(purposeInput).toHaveValue("");
  });

  it("uses backend TTS for Hindi and does not auto-fill", async () => {
    const { fetchMock } = installApiMock({ ask: hindiPurposeResponse() });
    const user = userEvent.setup();
    render(<App />);
    await openIncomeForm(user);

    const input = await openTextFallback(user);
    await user.type(input, "purpose mein scholarship likhna hai kya");
    await user.click(screen.getByRole("button", { name: "Ask" }));

    expect(await screen.findAllByText(/à¤¹à¤¾à¤/)).not.toHaveLength(0);
    await waitFor(() => expect(FakeAudio.instances).toHaveLength(1));
    const ttsCall = fetchMock.mock.calls.find(([url]) => url.endsWith("/api/tts/speak"));
    expect(JSON.parse(ttsCall[1].body).language_code).toBe("hi-IN");
    expect(screen.getByLabelText(/Purpose of Certificate/)).toHaveValue("");
  });

  it("sends manually entered values and document status for review", async () => {
    const { fetchMock } = installApiMock();
    const user = userEvent.setup();
    render(<App />);
    await openIncomeForm(user);

    await user.type(screen.getByLabelText(/Purpose of Certificate/), "Scholarship");
    await user.upload(
      screen.getByLabelText("Upload Aadhaar Card"),
      new File(["pdf"], "aadhaar.pdf", { type: "application/pdf" }),
    );
    await user.click(screen.getByRole("button", { name: "Review My Details" }));

    expect(await screen.findAllByText("Please review your details.")).not.toHaveLength(0);
    const summaryCall = fetchMock.mock.calls.find(([url]) =>
      url.endsWith("/api/assistant/summary"),
    );
    expect(JSON.parse(summaryCall[1].body)).toMatchObject({
      form_id: "income_certificate",
      language: "auto",
      form_values: expect.objectContaining({ purpose: "Scholarship" }),
      uploaded_documents: expect.objectContaining({
        aadhaar: expect.objectContaining({ name: "aadhaar.pdf", uploaded: true }),
      }),
    });
  });

  it("keeps demo submit manual and never calls a submission endpoint", async () => {
    const { fetchMock } = installApiMock();
    const user = userEvent.setup();
    render(<App />);
    await openIncomeForm(user);

    fireEvent.submit(
      screen.getByRole("button", { name: "Submit Manually (Demo)" }).closest("form"),
    );
    expect(screen.getByText("Demo only. No government application was submitted.")).toBeInTheDocument();
    expect(fetchMock.mock.calls.some(([url]) => /submit/i.test(url))).toBe(false);
  });

  it("does not request geolocation until the user clicks the optional location button", async () => {
    const { fetchMock } = installApiMock();
    const user = userEvent.setup();
    navigator.geolocation.getCurrentPosition.mockImplementation((success) =>
      success({ coords: { latitude: 17.444, longitude: 78.377 } }),
    );
    render(<App />);
    await openIncomeForm(user);

    expect(navigator.geolocation.getCurrentPosition).not.toHaveBeenCalled();
    await user.click(screen.getByText("Need mandal or location help?"));
    await user.click(screen.getByRole("button", { name: "Use My Location to Help Find Mandal" }));
    expect(navigator.geolocation.getCurrentPosition).toHaveBeenCalledOnce();
    await waitFor(() =>
      expect(fetchMock.mock.calls.some(([url]) => url.endsWith("/api/location/reverse"))).toBe(true),
    );
    expect(screen.getByLabelText(/District/)).toHaveValue("");
    expect(screen.getByLabelText(/Mandal/)).toHaveValue("");
  });

  it("offers mandal help without changing district or mandal fields", async () => {
    const locationReply = {
      success: true,
      field: "mandal",
      reply:
        "à°®à±€ pincode à°ªà±à°°à°•à°¾à°°à°‚ à°œà°¿à°²à±à°²à°¾ Rangareddy, à°®à°‚à°¡à°²à°‚ Serilingampally à°‰à°‚à°¡à°µà°šà±à°šà±. à°¦à°¯à°šà±‡à°¸à°¿ confirm à°šà±‡à°¯à°‚à°¡à°¿.",
      suggested_value: null,
      related_values: { district: "Rangareddy", mandal: "Serilingampally" },
      location_matches: [],
      warning: null,
      detected_language: "telugu",
      language_code: "te-IN",
      auto_fill: false,
      should_submit: false,
    };
    installApiMock({ ask: locationReply });
    const user = userEvent.setup();
    render(<App />);
    await openIncomeForm(user);

    await user.click(screen.getByText("Need mandal or location help?"));
    await user.type(screen.getByLabelText("Pincode"), "500032");
    await user.click(screen.getByRole("button", { name: "Find mandal" }));
    expect(await screen.findAllByText(/Serilingampally/)).not.toHaveLength(0);
    expect(screen.getByLabelText(/District/)).toHaveValue("");
    expect(screen.getByLabelText(/Mandal/)).toHaveValue("");
  });

  it("keeps text visible when backend TTS fails", async () => {
    installApiMock({ ask: teluguPurposeResponse(), ttsError: true });
    const user = userEvent.setup();
    vi.spyOn(console, "error").mockImplementation(() => {});
    render(<App />);
    await openIncomeForm(user);

    const input = await openTextFallback(user);
    await user.type(input, "purpose lo scholarship ani rayacha");
    await user.click(screen.getByRole("button", { name: "Ask" }));

    expect(await screen.findAllByText(/à°…à°µà±à°¨à±/)).not.toHaveLength(0);
    expect(
      await screen.findByText(
        "Could not generate voice output for this language. Please check internet or TTS provider. Text guidance is still visible.",
      ),
    ).toBeInTheDocument();
  });

  it("citizen portal shows only citizen-facing features and answers from the hybrid engine", async () => {
    const { fetchMock } = installApiMock();
    const user = userEvent.setup();
    window.history.pushState({}, "", "/citizen");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Citizen Portal" })).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: "Open Services" })[0]).toHaveAttribute("href", "/services");
    expect(screen.getAllByRole("link", { name: "Track Application" })[0]).toHaveAttribute("href", "/track");
    expect(screen.getAllByRole("link", { name: "Verify Certificate" })[0]).toHaveAttribute("href", "/verify-certificate");
    expect(screen.getByRole("complementary", { name: "NiyamGuard Chatbot" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Apply for Services with Voice Assistant" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Start Voice Assistant" })).toHaveAttribute("href", "#citizen-voice-assistant");
    expect(screen.queryByText("Compliance Drift")).not.toBeInTheDocument();
    expect(screen.queryByText("Audit Trail")).not.toBeInTheDocument();
    expect(screen.queryByText("Virtual Government Sandbox")).not.toBeInTheDocument();

    await user.click(screen.getAllByRole("button", { name: "Ask Assistant" })[0]);
    expect(await screen.findByTestId("citizen-hybrid-output")).toHaveTextContent("Income Certificate validity is 6 months");
    expect(fetchMock.mock.calls.some(([url]) => url.endsWith("/api/hybrid/answer"))).toBe(true);
  });

  it("does not expose the legacy mixed demo route to an admin", async () => {
    installApiMock();
    seedAdminSession();
    window.history.pushState({}, "", "/demo");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/admin");
    expect(screen.queryByRole("heading", { name: "NiyamGuard AI Demo" })).not.toBeInTheDocument();
  });

  it("government portal exposes circular upload from overview", async () => {
    installApiMock();
    seedAdminSession(officerUser);
    window.history.pushState({}, "", "/government");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Policy Operations" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Upload New Circular" })).toBeInTheDocument();
    expect(screen.getByLabelText("Circular document")).toHaveAttribute("type", "file");
    expect(screen.getByRole("button", { name: "Upload & Extract" })).toBeDisabled();
    expect(screen.getByText("Circulars").closest("article")).toBeInTheDocument();
    expect(screen.getByText("Rule Candidates").closest("article")).toBeInTheDocument();
    expect(screen.getByText("Open Mismatches").closest("article")).toBeInTheDocument();
  });

  it("login page renders", async () => {
    installApiMock();
    window.localStorage.clear();
    window.history.pushState({}, "", "/login");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "NiyamGuard Login" })).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toHaveValue("citizen@niyamguard.local");
    expect(screen.getByText(/separate demo accounts/i)).toBeInTheDocument();
  });

  it("protects admin routes when unauthenticated", async () => {
    installApiMock();
    window.localStorage.clear();
    window.history.pushState({}, "", "/admin");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "NiyamGuard Login" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/login");
  });

  it("redirects a citizen away from government and admin portals", async () => {
    installApiMock();
    seedAdminSession(citizenUser);
    window.history.pushState({}, "", "/government");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Citizen Portal" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/citizen");
    expect(screen.queryByRole("heading", { name: "Policy Operations" })).not.toBeInTheDocument();
  });

  it("redirects an officer away from the admin portal", async () => {
    installApiMock();
    seedAdminSession(officerUser);
    window.history.pushState({}, "", "/admin");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Policy Operations" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/government");
    expect(screen.queryByText("NiyamGuard Admin")).not.toBeInTheDocument();
  });

  it("redirects an admin away from citizen and officer modules", async () => {
    installApiMock();
    seedAdminSession(adminUser);
    window.history.pushState({}, "", "/government/applications");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/admin");
    expect(screen.queryByRole("heading", { name: "Officer Review" })).not.toBeInTheDocument();
  });

  it("admin login succeeds and opens the separate admin portal", async () => {
    installApiMock();
    const user = userEvent.setup();
    window.localStorage.clear();
    window.history.pushState({}, "", "/login");
    render(<App />);

    await user.click(await screen.findByRole("button", { name: "Admin" }));
    await user.click(screen.getByRole("button", { name: "Sign In" }));

    expect(await screen.findByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/admin");
    expect(screen.getByText("NiyamGuard Admin")).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Policy Operations" })).not.toBeInTheDocument();
    expect(screen.getByText("admin@niyamguard.local")).toBeInTheDocument();
  });

  it("citizen assistant answers validity questions from verified public rule API", async () => {
    const { fetchMock } = installApiMock();
    const user = userEvent.setup();
    render(<App />);
    await openIncomeForm(user);

    const input = await openTextFallback(user);
    await user.type(input, "income certificate validity entha");
    await user.click(screen.getByRole("button", { name: "Ask" }));

    expect(await screen.findByText(/Income Certificate validity is currently 6 months/)).toBeInTheDocument();
    expect(screen.getByText("Verified Source")).toBeInTheDocument();
    expect(screen.getByText("GO-138")).toBeInTheDocument();
    expect(screen.getAllByText("Revenue").length).toBeGreaterThan(0);
    expect(screen.getByText("91%")).toBeInTheDocument();
    expect(
      fetchMock.mock.calls.some(([url]) =>
        url.includes("/api/public/rules/latest?service_id=income_certificate&rule_key=validity"),
      ),
    ).toBe(true);
    expect(
      fetchMock.mock.calls.some(([url]) => url.endsWith("/api/assistant/ask")),
    ).toBe(false);
    expect(screen.queryByText(/"source"/)).not.toBeInTheDocument();
  });

  it("citizen assistant answers scheme document questions from sourced chat knowledge", async () => {
    const { fetchMock } = installApiMock();
    const user = userEvent.setup();
    render(<App />);
    await openIncomeForm(user);

    const input = await openTextFallback(user);
    await user.type(input, "scholarship documents enti");
    await user.click(screen.getByRole("button", { name: "Ask" }));

    expect(await screen.findByText(/For Post-Matric Scholarship/)).toBeInTheDocument();
    expect(screen.getByText("Verified Source")).toBeInTheDocument();
    expect(screen.getByText("Citizen Services Knowledge")).toBeInTheDocument();
    expect(screen.getByText("78%")).toBeInTheDocument();
    expect(screen.getByText("RAG Source")).toBeInTheDocument();
    expect(screen.getByText("Seed Demo Data")).toBeInTheDocument();
    expect(screen.getByText("Fallback")).toBeInTheDocument();
    const chatCall = fetchMock.mock.calls.find(([url]) => url.endsWith("/api/chat"));
    expect(chatCall).toBeDefined();
    expect(JSON.parse(chatCall[1].body).message).toBe("scholarship documents enti");
  });

  it("admin dashboard renders", async () => {
    installApiMock();
    seedAdminSession();
    window.history.pushState({}, "", "/admin");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
    expect(screen.getByText("System-wide administration for NiyamGuard accounts, runtime readiness, sandbox operations, and audit integrity.")).toBeInTheDocument();
    expect(screen.getByText("Verified Rules").closest("article")).toHaveTextContent("2");
    expect(screen.getByText("Connected Systems").closest("article")).toHaveTextContent("5");
    expect(screen.getByText("Compliance Findings").closest("article")).toHaveTextContent("4");
    expect(screen.getByText("Drifted Systems").closest("article")).toHaveTextContent("3");
    expect(screen.getByText("Open Conflicts").closest("article")).toHaveTextContent("1");
    expect(screen.getByText("Module Readiness")).toBeInTheDocument();
    expect(screen.queryByText("High Priority Findings")).not.toBeInTheDocument();
  });

  it("redirects an admin away from former officer-only module routes", async () => {
    installApiMock();
    seedAdminSession();
    window.history.pushState({}, "", "/admin/compliance");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/admin");
    expect(screen.queryByText("Compliance Findings")).not.toBeInTheDocument();
  });

  it("admin navigation stays limited to current admin workspaces", async () => {
    installApiMock();
    seedAdminSession();
    window.history.pushState({}, "", "/admin");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Sandbox" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "System Audit" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Users" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Impact" })).not.toBeInTheDocument();
  });

  it("scheme finder recommends possible citizen services", async () => {
    installApiMock();
    const user = userEvent.setup();
    window.history.pushState({}, "", "/scheme-finder");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Find services that may match your need" })).toBeInTheDocument();
    await user.click(screen.getByLabelText("Student"));
    await user.click(screen.getByRole("button", { name: "Find Possible Services" }));
    expect(await screen.findByText("Income Certificate")).toBeInTheDocument();
    expect(screen.getByText(/You may be eligible/)).toBeInTheDocument();
    expect(screen.getByText("Verified GO-138 public rule plus local form catalog")).toBeInTheDocument();
  });

  it("service portal lists seeded public services", async () => {
    installApiMock();
    window.history.pushState({}, "", "/services");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Services" })).toBeInTheDocument();
    expect(screen.getByText("Income Certificate")).toBeInTheDocument();
    expect(screen.getByText("Residence Certificate")).toBeInTheDocument();
    expect(screen.getByText("Rs 35")).toBeInTheDocument();
  });

  it("citizen can create a service portal application draft", async () => {
    installApiMock();
    seedAdminSession(citizenUser);
    const user = userEvent.setup();
    window.history.pushState({}, "", "/apply/income_certificate");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Income Certificate" })).toBeInTheDocument();
    await user.type(screen.getByLabelText(/Applicant Full Name/), "Ravi Kumar");
    await user.type(screen.getByLabelText(/Mobile Number/), "9876543210");
    await user.type(screen.getByLabelText(/^District/), "Hyderabad");
    await user.type(screen.getByLabelText(/^Mandal/), "Ameerpet");
    await user.type(screen.getByLabelText(/^Address/), "House 1, Ameerpet");
    await user.type(screen.getByLabelText(/^Purpose/), "Scholarship");
    await user.type(screen.getByLabelText(/Annual Income/), "180000");
    await user.type(screen.getByLabelText(/Occupation/), "Student family");
    await user.click(screen.getByRole("button", { name: "Create Draft" }));

    expect(await screen.findByText(/Draft saved: NGSP-2026-INC-000001/)).toBeInTheDocument();
    expect(screen.getByText("Document Upload")).toBeInTheDocument();
  });

  it("keeps application review inside the government portal layout", async () => {
    installApiMock();
    seedAdminSession(officerUser);
    const user = userEvent.setup();
    window.history.pushState({}, "", "/officer/pending");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Policy Operations" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/government/applications/pending");
    expect((await screen.findAllByRole("heading", { name: "Officer Review" })).length).toBeGreaterThan(0);
    expect(screen.getByRole("button", { name: "Circular Intake" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Application Review" })).toHaveClass("active");
    expect(screen.getByText("NGSP-2026-INC-000001")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Open" }));
    expect(await screen.findByRole("button", { name: "Approve and Issue" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/government/applications/app_portal_001");
  });

  it("public tracking and certificate verification render dataset-backed results", async () => {
    installApiMock();
    const user = userEvent.setup();
    window.history.pushState({}, "", "/track");
    render(<App />);

    await user.type(await screen.findByLabelText("Application number"), "NGSP-2026-INC-000001");
    await user.click(screen.getAllByRole("button", { name: "Track" }).at(-1));
    expect(await screen.findByText("Officer review")).toBeInTheDocument();

    window.history.pushState({}, "", "/verify-certificate");
    window.dispatchEvent(new Event("popstate"));
    await user.type(await screen.findByLabelText("Certificate number or hash"), "hash_demo");
    await user.click(screen.getAllByRole("button", { name: "Verify" }).at(-1));
    expect(await screen.findByText("Certificate is valid")).toBeInTheDocument();
    expect(screen.getByText("NGCERT-2026-INC-000001")).toBeInTheDocument();
  });

  it("sandbox generates PDF, opens it, and publishes to the government inbox", async () => {
    const { fetchMock } = installApiMock();
    seedAdminSession();
    const user = userEvent.setup();
    window.history.pushState({}, "", "/virtual-gov");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Virtual Government Sandbox" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/admin/sandbox");
    expect(screen.getByText("Sandbox Holding Area")).toBeInTheDocument();
    expect(await screen.findByRole("button", { name: "Open PDF" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Publish to NiyamGuard" }));
    expect(await screen.findByRole("heading", { name: "Government Delivery" })).toBeInTheDocument();
    expect(screen.getByText(/Circular published to the NiyamGuard Government Circular Inbox/)).toBeInTheDocument();
    expect(fetchMock.mock.calls.some(([url]) => url.endsWith("/api/sandbox/circulars/sbx_go_138/publish"))).toBe(true);
  });

  it("admin audit page renders", async () => {
    installApiMock();
    seedAdminSession();
    window.history.pushState({}, "", "/admin/audit");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Audit" })).toBeInTheDocument();
    expect(screen.getByText("Audit Log")).toBeInTheDocument();
    expect(screen.getByText("Hash chain verified")).toBeInTheDocument();
    expect(screen.getByText("Login Success")).toBeInTheDocument();
  });

  it("admin users page renders", async () => {
    installApiMock();
    seedAdminSession();
    window.history.pushState({}, "", "/admin/users");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Users" })).toBeInTheDocument();
    expect(screen.getByText("User Management")).toBeInTheDocument();
    expect(screen.getAllByText("admin@niyamguard.local").length).toBeGreaterThan(0);
    expect(screen.getByRole("button", { name: "Create User" })).toBeInTheDocument();
  });

  it("admin logout clears the session", async () => {
    installApiMock();
    seedAdminSession();
    const user = userEvent.setup();
    window.history.pushState({}, "", "/admin");
    render(<App />);

    await screen.findByRole("heading", { name: "Dashboard" });
    await user.click(screen.getByRole("button", { name: "Logout" }));

    expect(await screen.findByRole("heading", { name: "NiyamGuard Login" })).toBeInTheDocument();
  });
});
