import { useEffect, useRef } from "react";

export default function MessageList({ messages }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) return null;

  return (
    <div className="message-list">
      {messages.map((msg, i) => (
        <div key={i} className={`message ${msg.role}`}>
          <div className="message-avatar">
            {msg.role === "user" ? "◯" : "✦"}
          </div>
          <div className="message-content">
            <div className="message-role">
              {msg.role === "user" ? "You" : "Nakshatra"}
            </div>
            <div className="message-text">{msg.content}</div>
          </div>
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
}
