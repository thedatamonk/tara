const API_URL = "http://localhost:8000";

export async function sendMessage({ sessionId, message, userProfile, preferredLanguage }) {
  const body = {
    preferred_language: preferredLanguage || "en",
  };
  if (message) body.message = message;
  if (sessionId) body.session_id = sessionId;
  if (userProfile) body.user_profile = userProfile;

  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || "Request failed");
  }

  return res.json();
}
