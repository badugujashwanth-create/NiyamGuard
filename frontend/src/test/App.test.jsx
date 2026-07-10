import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "../App";
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
  await user.click(screen.getByText("Having trouble? Type instead"));
  return screen.getByLabelText("Type your question");
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

  it("landing page shows only the two main portal choices", async () => {
    installApiMock();
    window.history.pushState({}, "", "/");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "NiyamGuard" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Open Citizen Portal" })).toHaveAttribute("href", "/citizen");
    expect(screen.getByRole("link", { name: "Open Government Portal" })).toHaveAttribute("href", "/government");
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
      name: "NiyamGuard Voice Assistant",
    });
    const mainControls = within(assistant.querySelector(".voice-controls")).getAllByRole(
      "button",
    );
    expect(mainControls.map((button) => button.textContent)).toEqual(["Start", "Stop", "Use Text Instead"]);
    expect(screen.queryByText("Force Backend Voice")).not.toBeInTheDocument();
    expect(screen.queryByText("Speak Again")).not.toBeInTheDocument();
    expect(screen.queryByText("Raw JSON")).not.toBeInTheDocument();
    expect(screen.getByText("Having trouble? Type instead").closest("details")).not.toHaveAttribute("open");
    await user.click(screen.getByRole("button", { name: "Use Text Instead" }));
    expect(screen.getByText("Having trouble? Type instead").closest("details")).toHaveAttribute("open");
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
      language: "auto",
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
    expect(screen.getAllByRole("link", { name: "Apply Income Certificate" })[0]).toHaveAttribute("href", "/apply/income_certificate");
    expect(screen.getAllByRole("link", { name: "Track Application" })[0]).toHaveAttribute("href", "/track");
    expect(screen.getAllByRole("link", { name: "Verify Certificate" })[0]).toHaveAttribute("href", "/verify-certificate");
    expect(screen.getByRole("complementary", { name: "NiyamGuard Voice Assistant" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Apply for Certificates with Voice Assistant" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "income certificate validity entha" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Start Voice Assistant" })).toHaveAttribute("href", "#citizen-voice-assistant");
    expect(screen.queryByText("Compliance Drift")).not.toBeInTheDocument();
    expect(screen.queryByText("Audit Trail")).not.toBeInTheDocument();
    expect(screen.queryByText("Virtual Government Sandbox")).not.toBeInTheDocument();

    await user.click(screen.getAllByRole("button", { name: "Ask Assistant" })[0]);
    expect(await screen.findByTestId("citizen-hybrid-output")).toHaveTextContent("Income Certificate validity is 6 months");
    expect(fetchMock.mock.calls.some(([url]) => url.endsWith("/api/hybrid/answer"))).toBe(true);
  });

  it("legacy demo route still opens the original demo dashboard", async () => {
    const { fetchMock } = installApiMock();
    const user = userEvent.setup();
    window.history.pushState({}, "", "/demo");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "NiyamGuard AI Demo" })).toBeInTheDocument();
    expect(screen.getByText("Government Admin Portal")).toBeInTheDocument();
    expect(screen.getByText("Run Compliance Demo")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Full virtual government flow" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Run Full Virtual Government Demo" }));
    expect(await screen.findByText("Certificate Generated")).toBeInTheDocument();
    expect(fetchMock.mock.calls.some(([url]) => url.endsWith("/api/virtual-gov/run"))).toBe(true);
  });

  it("government portal runs the backend full demo flow", async () => {
    const { fetchMock } = installApiMock();
    const user = userEvent.setup();
    window.history.pushState({}, "", "/government");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "NiyamGuard Government Portal" })).toBeInTheDocument();
    expect(screen.getByText(/Demo and pilot testing only/)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Circulars & Policy Updates" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Self-Updating Policy Engine" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Compliance Drift" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Connected Systems / Propagation" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Virtual Government Sandbox" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Officer Review" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Certificates" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Audit Trail" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Reports" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Hybrid Answer Engine / Ollama" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Readiness & Ops" })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Run Full End-to-End Demo" }));

    expect(await screen.findByText("Circular Published")).toBeInTheDocument();
    expect(screen.getByTestId("demo-application-number")).toHaveTextContent("NGSP-2026-INC-000001");
    expect(screen.getByTestId("demo-certificate-number")).toHaveTextContent("NGCERT-2026-INC-000001");
    expect(screen.getByTestId("demo-verification-hash")).toHaveTextContent("hash_demo");
    expect(screen.getByTestId("ollama-output")).toHaveTextContent("GO-138 means");
    expect(screen.getByText("Ollama Explanation Generated or Fallback Active")).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: "Explain GO-138 using Local AI" }).length).toBeGreaterThan(0);
    expect(fetchMock.mock.calls.some(([url]) => url.endsWith("/api/demo/run-full-end-to-end"))).toBe(true);
  });

  it("login page renders", async () => {
    installApiMock();
    window.history.pushState({}, "", "/login");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "NiyamGuard Admin Login" })).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toHaveValue("admin@niyamguard.local");
    expect(screen.getByText(/Demo admin:/)).toBeInTheDocument();
  });

  it("protects admin routes when unauthenticated", async () => {
    installApiMock();
    window.history.pushState({}, "", "/admin");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "NiyamGuard Admin Login" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/login");
  });

  it("admin login succeeds and opens the dashboard", async () => {
    installApiMock();
    const user = userEvent.setup();
    window.history.pushState({}, "", "/login");
    render(<App />);

    await user.click(await screen.findByRole("button", { name: "Sign In" }));

    expect(await screen.findByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
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

    expect(await screen.findByText(/Income Certificate validity 6 months/)).toBeInTheDocument();
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
    expect(fetchMock.mock.calls.some(([url]) => url.endsWith("/api/chat"))).toBe(true);
  });

  it("admin dashboard renders", async () => {
    installApiMock();
    seedAdminSession();
    window.history.pushState({}, "", "/admin");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
    expect(screen.getByText("NiyamGuard compares verified circular rules against portals, forms, SOPs, and FAQs to detect policy drift before citizens are harmed.")).toBeInTheDocument();
    expect(screen.getByText("Verified Rules").closest("article")).toHaveTextContent("2");
    expect(screen.getByText("Connected Systems").closest("article")).toHaveTextContent("5");
    expect(screen.getByText("Compliance Findings").closest("article")).toHaveTextContent("4");
    expect(screen.getByText("Drifted Systems").closest("article")).toHaveTextContent("3");
    expect(screen.getByText("Open Conflicts").closest("article")).toHaveTextContent("1");
    expect(screen.getByText("High Priority Findings")).toBeInTheDocument();
  });

  it("admin compliance page renders", async () => {
    installApiMock();
    seedAdminSession();
    const user = userEvent.setup();
    window.history.pushState({}, "", "/admin/compliance");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Compliance" })).toBeInTheDocument();
    expect(screen.getByText("Compliance Findings")).toBeInTheDocument();
    expect(screen.getByText("3 drifted systems")).toBeInTheDocument();
    expect(screen.getByText("1 compliant system")).toBeInTheDocument();
    expect(screen.getByText("MeeSeva Income Certificate Portal")).toBeInTheDocument();
    expect(screen.getByText("Officer SOP Manual")).toBeInTheDocument();
    expect(screen.getByText("Public FAQ")).toBeInTheDocument();
    expect(screen.getByText("Simplified Citizen Form")).toBeInTheDocument();
    expect(screen.getByText("Update portal validation rule from 12 months to 6 months.")).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: "Generate AI Summary" }).length).toBeGreaterThan(0);
    await user.click(screen.getAllByRole("button", { name: "Generate AI Summary" })[0]);
    expect(await screen.findByText("AI Impact Summary")).toBeInTheDocument();
    expect(screen.getAllByText("Fallback").length).toBeGreaterThan(0);
    expect(screen.queryByText(/"findings"/)).not.toBeInTheDocument();
  });

  it("admin conflict page renders", async () => {
    installApiMock();
    seedAdminSession();
    window.history.pushState({}, "", "/admin/conflicts");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Conflicts" })).toBeInTheDocument();
    expect(screen.getByText(/old GO-112 saying 12 months/)).toBeInTheDocument();
    expect(screen.getByText("GO-138: 6 months")).toBeInTheDocument();
    expect(screen.getByText("GO-112: 12 months")).toBeInTheDocument();
    expect(screen.getByText(/keep GO-138 active and supersede GO-112/)).toBeInTheDocument();
  });

  it("admin scale and impact pages render", async () => {
    installApiMock();
    seedAdminSession();
    const user = userEvent.setup();
    window.history.pushState({}, "", "/admin/scale-view");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Scale View" })).toBeInTheDocument();
    expect(screen.getByText("Multi-District / Department Scale View")).toBeInTheDocument();
    expect(screen.getByText(/Demo operational data for MVP/)).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Impact" }));
    expect(await screen.findByRole("heading", { name: "Impact" })).toBeInTheDocument();
    expect(screen.getByText("Citizen Impact Dashboard")).toBeInTheDocument();
    expect(screen.getByText(/Portal validity mismatch affects citizens immediately/)).toBeInTheDocument();
  });

  it("admin knowledge base page renders", async () => {
    installApiMock();
    seedAdminSession();
    window.history.pushState({}, "", "/admin/knowledge-base");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Knowledge Base" })).toBeInTheDocument();
    expect(screen.getAllByText("Income Certificate Validity").length).toBeGreaterThan(0);
  });

  it("admin self-update policy pages render from live API data", async () => {
    installApiMock();
    seedAdminSession();
    const user = userEvent.setup();
    window.history.pushState({}, "", "/admin/sources");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Sources" })).toBeInTheDocument();
    expect(screen.getByText("Revenue Department Demo Circular Feed")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Rule Candidates" }));
    expect(await screen.findByRole("heading", { name: "Rule Candidates" })).toBeInTheDocument();
    expect(screen.getByText("Extracted Rule Candidates")).toBeInTheDocument();
    expect(screen.getByText("Income Certificate validity changed from 12 months to 6 months.")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Policy Updates" }));
    expect(await screen.findByRole("heading", { name: "Policy Updates" })).toBeInTheDocument();
    expect(screen.getByText("Published Policy Updates")).toBeInTheDocument();
    expect(screen.getByText("Knowledge Updates")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Propagation" }));
    expect(await screen.findByRole("heading", { name: "Propagation" })).toBeInTheDocument();
    expect(screen.getByText("Mock MeeSeva Portal")).toBeInTheDocument();
    expect(screen.getByText("task_version_rule_001_2_sys_meeseva_portal")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Scheduler" }));
    expect(await screen.findByRole("heading", { name: "Scheduler" })).toBeInTheDocument();
    expect(screen.getByText("Self-Update Scheduler")).toBeInTheDocument();
  });

  it("mock connected system pages render stale dataset state", async () => {
    installApiMock();
    window.history.pushState({}, "", "/mock/meeseva");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Mock MeeSeva Portal" })).toBeInTheDocument();
    expect(screen.getByText("Certificate validity rule")).toBeInTheDocument();
    expect(screen.getAllByText("12 months").length).toBeGreaterThan(0);
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

  it("officer portal opens pending application review", async () => {
    installApiMock();
    seedAdminSession(officerUser);
    const user = userEvent.setup();
    window.history.pushState({}, "", "/officer/pending");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Officer Review" })).toBeInTheDocument();
    expect(screen.getByText("NGSP-2026-INC-000001")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Open" }));
    expect(await screen.findByRole("button", { name: "Approve and Issue" })).toBeInTheDocument();
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

  it("admin service portal pages render seeded service data", async () => {
    installApiMock();
    seedAdminSession();
    window.history.pushState({}, "", "/admin/services");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Services" })).toBeInTheDocument();
    expect(screen.getByText("Service Definitions")).toBeInTheDocument();
    expect(screen.getByText("Residence Certificate")).toBeInTheDocument();
    expect(screen.getAllByText("7 days").length).toBeGreaterThan(0);
  });

  it("admin regulatory AI dataset page renders and answers QA", async () => {
    installApiMock();
    seedAdminSession();
    const user = userEvent.setup();
    window.history.pushState({}, "", "/admin/regulatory-ai");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Regulatory AI" })).toBeInTheDocument();
    expect(screen.getByText("Regulatory AI Dataset Explorer")).toBeInTheDocument();
    expect(screen.getByText("Regulatory circulars").closest("article")).toHaveTextContent("220");
    expect(screen.getByText("Internal policies").closest("article")).toHaveTextContent("314");
    expect(screen.getByText("Obligations").closest("article")).toHaveTextContent("758");
    expect(screen.getByText("IRDAI circular on data privacy requirements for mutual funds entities")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Ask Dataset" }));
    expect(await screen.findByText(/Intent: explain_risk_score/)).toBeInTheDocument();
    expect(screen.getByText("policy_qa_pair")).toBeInTheDocument();
  });

  it("admin readiness page renders and runs the sandbox", async () => {
    installApiMock();
    seedAdminSession();
    const user = userEvent.setup();
    window.history.pushState({}, "", "/admin/readiness");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Readiness" })).toBeInTheDocument();
    expect(screen.getByText("Government Pilot Readiness")).toBeInTheDocument();
    expect(screen.getByText("Verified source-backed answers")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Run Sandbox Scenario" }));
    expect(await screen.findByText("NGSP-2026-INC-000001")).toBeInTheDocument();
    expect(screen.getAllByText("certificate_issued").length).toBeGreaterThan(0);
  });

  it("virtual government sandbox page runs the public scenario", async () => {
    installApiMock();
    const user = userEvent.setup();
    window.history.pushState({}, "", "/virtual-gov");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Virtual Government Sandbox" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Run Sandbox Scenario" }));
    expect(await screen.findByText("Income certificate regulation-to-certificate sandbox")).toBeInTheDocument();
    expect(screen.getByText("NGCERT-2026-INC-000001")).toBeInTheDocument();
  });

  it("admin reports page renders", async () => {
    installApiMock();
    seedAdminSession();
    window.history.pushState({}, "", "/admin/reports");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Reports" })).toBeInTheDocument();
    expect(screen.getAllByText("Export Compliance CSV").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Export Conflicts CSV").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Export Rules JSON").length).toBeGreaterThan(0);
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

    expect(await screen.findByRole("heading", { name: "NiyamGuard Admin Login" })).toBeInTheDocument();
  });
});
