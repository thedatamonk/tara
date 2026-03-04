const API_URL = "http://localhost:8000";

export async function createAstroChart(userProfile) {
  const res = await fetch(`${API_URL}/create_astro_chart`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_profile: userProfile }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || "Request failed");
  }

  return res.json();
}

export async function sendMessage({ sessionId, message, preferredLanguage }) {
  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      message,
      preferred_language: preferredLanguage || "en",
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || "Request failed");
  }

  return res.json();
}
