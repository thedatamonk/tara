import { useState, useRef, useEffect } from "react";

function range(start, end) {
  const arr = [];
  for (let i = start; i <= end; i++) arr.push(i);
  return arr;
}

const HOURS = range(1, 12);
const MINUTES = range(0, 59);
const PERIODS = ["AM", "PM"];

export default function TimePicker({ value, onChange, label }) {
  const [hour, setHour] = useState("");
  const [minute, setMinute] = useState("");
  const [period, setPeriod] = useState("AM");
  const [open, setOpen] = useState(false);
  const wrapperRef = useRef(null);

  // Parse initial value (HH:MM 24h)
  useEffect(() => {
    if (value && !hour) {
      const [h, m] = value.split(":").map(Number);
      const p = h >= 12 ? "PM" : "AM";
      const h12 = h === 0 ? 12 : h > 12 ? h - 12 : h;
      setHour(String(h12));
      setMinute(String(m));
      setPeriod(p);
    }
  }, [value]);

  const emit = (h, m, p) => {
    if (h && m !== "" && p) {
      let h24 = parseInt(h);
      if (p === "AM" && h24 === 12) h24 = 0;
      if (p === "PM" && h24 !== 12) h24 += 12;
      const hh = String(h24).padStart(2, "0");
      const mm = String(m).padStart(2, "0");
      onChange(`${hh}:${mm}`);
    }
  };

  const handleHour = (h) => { setHour(h); emit(h, minute, period); };
  const handleMinute = (m) => { setMinute(String(m)); emit(hour, m, period); };
  const handlePeriod = (p) => { setPeriod(p); emit(hour, minute, p); };

  const displayText = hour && minute !== ""
    ? `${hour}:${String(minute).padStart(2, "0")} ${period}`
    : "";

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="field time-field" ref={wrapperRef}>
      <label>{label}</label>
      <button
        type="button"
        className="picker-trigger"
        onClick={() => setOpen(!open)}
      >
        <span className={displayText ? "picker-value" : "picker-placeholder"}>
          {displayText || "Select time"}
        </span>
        <span className="picker-caret">▾</span>
      </button>
      {open && (
        <div className="time-dropdown">
          <div className="date-columns">
            <div className="date-col">
              <div className="date-col-label">Hour</div>
              <div className="date-scroll">
                {HOURS.map((h) => (
                  <button
                    key={h}
                    type="button"
                    className={String(h) === String(hour) ? "selected" : ""}
                    onClick={() => handleHour(String(h))}
                  >
                    {h}
                  </button>
                ))}
              </div>
            </div>
            <div className="date-col">
              <div className="date-col-label">Min</div>
              <div className="date-scroll">
                {MINUTES.map((m) => (
                  <button
                    key={m}
                    type="button"
                    className={String(m) === String(parseInt(minute)) ? "selected" : ""}
                    onClick={() => handleMinute(m)}
                  >
                    {String(m).padStart(2, "0")}
                  </button>
                ))}
              </div>
            </div>
            <div className="date-col date-col-period">
              <div className="date-col-label">  </div>
              <div className="date-scroll period-scroll">
                {PERIODS.map((p) => (
                  <button
                    key={p}
                    type="button"
                    className={p === period ? "selected" : ""}
                    onClick={() => handlePeriod(p)}
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
