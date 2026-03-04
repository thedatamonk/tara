import { useState } from "react";
import DatePicker from "./DatePicker";
import TimePicker from "./TimePicker";
import LocationSearch from "./LocationSearch";

const LANGUAGES = [
  { code: "en", label: "English", native: "EN" },
  { code: "hi", label: "हिन्दी", native: "हि" },
];

export default function BirthDetailsForm({ onSubmit }) {
  const [name, setName] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [birthTime, setBirthTime] = useState("");
  const [birthPlace, setBirthPlace] = useState("");
  const [language, setLanguage] = useState("en");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name || !birthDate || !birthTime || !birthPlace) return;
    onSubmit({
      name,
      birth_date: birthDate,
      birth_time: birthTime,
      birth_place: birthPlace,
      preferred_language: language,
    });
  };

  const labels = language === "hi"
    ? { name: "नाम", date: "जन्म तिथि", time: "जन्म समय", place: "जन्म स्थान", lang: "भाषा", submit: "शुरू करें" }
    : { name: "Name", date: "Date of Birth", time: "Time of Birth", place: "Place of Birth", lang: "Language", submit: "Begin Reading" };

  return (
    <form className="birth-form" onSubmit={handleSubmit}>
      <div className="form-header">
        <div className="form-icon">✦</div>
        <h2>{language === "hi" ? "अपना जन्म विवरण दर्ज करें" : "Enter Your Birth Details"}</h2>
        <p className="form-subtitle">
          {language === "hi"
            ? "सटीक कुंडली विश्लेषण के लिए"
            : "For an accurate natal chart reading"}
        </p>
      </div>
      <div className="form-fields">
        <div className="field">
          <label>{labels.name}</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder={language === "hi" ? "आपका नाम" : "Your name"}
            required
          />
        </div>

        <DatePicker
          value={birthDate}
          onChange={setBirthDate}
          label={labels.date}
        />

        <TimePicker
          value={birthTime}
          onChange={setBirthTime}
          label={labels.time}
        />

        <LocationSearch
          value={birthPlace}
          onChange={setBirthPlace}
          label={labels.place}
          placeholder={language === "hi" ? "शहर खोजें..." : "Search city..."}
        />

        <div className="field">
          <label>{labels.lang}</label>
          <div className="lang-selector">
            {LANGUAGES.map((lang) => (
              <button
                key={lang.code}
                type="button"
                className={`lang-option${language === lang.code ? " selected" : ""}`}
                onClick={() => setLanguage(lang.code)}
              >
                <span className="lang-native">{lang.native}</span>
                <span className="lang-label">{lang.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
      <button type="submit" className="submit-btn">{labels.submit}</button>
    </form>
  );
}
