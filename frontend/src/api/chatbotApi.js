import { request } from "./client";

export function askChatbot({ message, language = "auto", mode, context = {}, profile = {} }) {
  return request("/api/chatbot/ask", {
    method: "POST",
    body: JSON.stringify({ message, language, mode, context, profile }),
  });
}
