import { useState } from "react";
import { sendMessage } from "../api";
import BirthDetailsForm from "./BirthDetailsForm";
import ChartLoader from "./ChartLoader";
import MessageInput from "./MessageInput";
import MessageList from "./MessageList";
import NatalChart from "./NatalChart";

export default function ChatContainer() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [userProfile, setUserProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState("en");
  const [chartSvg, setChartSvg] = useState(null);

  const handleBirthSubmit = async (profile) => {
    setUserProfile(profile);
    setLanguage(profile.preferred_language);
    setLoading(true);
    try {
      const res = await sendMessage({
        sessionId,
        message: null,
        userProfile: profile,
        preferredLanguage: profile.preferred_language,
      });
      setSessionId(res.session_id);
      setMessages([{ role: "assistant", content: res.response }]);
      if (res.chart_svg) {
        setChartSvg(res.chart_svg);
      }
    } catch (err) {
      setMessages([{ role: "assistant", content: `Error: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  const doSend = async (text) => {
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);

    try {
      const res = await sendMessage({
        sessionId,
        message: text,
        userProfile,
        preferredLanguage: language,
      });
      setSessionId(res.session_id);
      setMessages((prev) => [...prev, { role: "assistant", content: res.response }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const showForm = !userProfile;

  return (
    <div className={`chat-container ${!showForm ? "chat-container--with-chart" : ""}`}>
      {showForm ? (
        <>
          <header className="chat-header">
            <div className="logo">
              <span className="logo-icon">✦</span>
              <span className="logo-text">tara</span>
            </div>
          </header>
          <div className="chat-body">
            <div className="form-wrapper">
              <BirthDetailsForm onSubmit={handleBirthSubmit} />
            </div>
          </div>
        </>
      ) : (
        <>
          <div className="chat-panel">
            <header className="chat-header">
              <div className="logo">
                <span className="logo-icon">✦</span>
                <span className="logo-text">tara</span>
              </div>
            </header>
            <div className="chat-body">
              <MessageList messages={messages} />
              {loading && (
                <div className="loading-indicator">
                  <span className="loading-dot" />
                  <span className="loading-dot" />
                  <span className="loading-dot" />
                </div>
              )}
            </div>
            <MessageInput onSend={doSend} loading={loading} language={language} />
          </div>
          <div className="chart-panel">
            {chartSvg ? (
              <NatalChart svgString={chartSvg} />
            ) : (
              <ChartLoader />
            )}
          </div>
        </>
      )}
    </div>
  );
}
