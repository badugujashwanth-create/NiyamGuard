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
import { adminUser, installApiMock } from "./fixtures";

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
    window.history.pushState({}, "", "/");
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

  it("shows only Start and Stop as main assistant controls", async () => {
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
    expect(mainControls.map((button) => button.textContent)).toEqual(["Start", "Stop"]);
    expect(screen.queryByText("Force Backend Voice")).not.toBeInTheDocument();
    expect(screen.queryByText("Speak Again")).not.toBeInTheDocument();
    expect(screen.queryByText("Raw JSON")).not.toBeInTheDocument();
    expect(
      screen.getByText("Having trouble? Type instead").closest("details"),
    ).not.toHaveAttribute("open");
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

  it("demo dashboard renders live presentation sections", async () => {
    installApiMock();
    window.history.pushState({}, "", "/demo");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "NiyamGuard AI Demo" })).toBeInTheDocument();
    expect(screen.getByText("Government Admin Portal")).toBeInTheDocument();
    expect(screen.getByText("Run Compliance Demo")).toBeInTheDocument();
    expect(screen.getByText(/GO-138 changed Income Certificate validity/)).toBeInTheDocument();
    expect(screen.queryByText(/"success"/)).not.toBeInTheDocument();
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

  it("admin knowledge base page renders", async () => {
    installApiMock();
    seedAdminSession();
    window.history.pushState({}, "", "/admin/knowledge-base");
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Knowledge Base" })).toBeInTheDocument();
    expect(screen.getAllByText("Income Certificate Validity").length).toBeGreaterThan(0);
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
