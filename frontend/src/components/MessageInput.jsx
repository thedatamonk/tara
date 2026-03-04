import { useState } from "react";

export default function MessageInput({ onSend, loading, language }) {
  const [text, setText] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim() || loading) return;
    onSend(text.trim());
    setText("");
  };

  const placeholder = language === "hi"
    ? "अपना प्रश्न पूछें..."
    : "Ask about your stars...";

  return (
    <form className="message-input" onSubmit={handleSubmit}>
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={placeholder}
        disabled={loading}
      />
      <button type="submit" disabled={loading || !text.trim()}>
        {loading ? "⟳" : "→"}
      </button>
    </form>
  );
}
