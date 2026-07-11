import { request } from "./client";

export function askChat({ message, language = "auto", context = {}, profile = {} }) {
  return request(
    "/api/chat",
    {
      method: "POST",
      body: JSON.stringify({ message, language, context, profile }),
    },
  );
}
