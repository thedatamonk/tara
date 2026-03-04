import { useState, useRef, useEffect } from "react";

const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

const MONTHS_SHORT = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

function daysInMonth(month, year) {
  return new Date(year, month, 0).getDate();
}

function range(start, end) {
  const arr = [];
  for (let i = start; i <= end; i++) arr.push(i);
  return arr;
}

export default function DatePicker({ value, onChange, label }) {
  const currentYear = new Date().getFullYear();
  const years = range(1940, currentYear).reverse();

  const [day, setDay] = useState("");
  const [month, setMonth] = useState("");
  const [year, setYear] = useState("");
  const [open, setOpen] = useState(false);
  const wrapperRef = useRef(null);

  // Parse initial value
  useEffect(() => {
    if (value && !day) {
      const [y, m, d] = value.split("-");
      setYear(y);
      setMonth(m);
      setDay(d);
    }
  }, [value]);

  const maxDay = month && year ? daysInMonth(parseInt(month), parseInt(year)) : 31;
  const days = range(1, maxDay);

  const emit = (d, m, y) => {
    if (d && m && y) {
      const dd = String(d).padStart(2, "0");
      const mm = String(m).padStart(2, "0");
      onChange(`${y}-${mm}-${dd}`);
      setOpen(false);
    }
  };

  const handleDay = (d) => { setDay(d); emit(d, month, year); };
  const handleMonth = (m) => {
    setMonth(m);
    // Clamp day if needed
    const newMax = daysInMonth(parseInt(m), parseInt(year) || 2000);
    const clampedDay = day && parseInt(day) > newMax ? String(newMax) : day;
    if (clampedDay !== day) setDay(clampedDay);
    emit(clampedDay, m, year);
  };
  const handleYear = (y) => { setYear(y); emit(day, month, y); };

  const displayText = day && month && year
    ? `${parseInt(day)} ${MONTHS_SHORT[parseInt(month) - 1]} ${year}`
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
    <div className="field date-field" ref={wrapperRef}>
      <label>{label}</label>
      <button
        type="button"
        className="picker-trigger"
        onClick={() => setOpen(!open)}
      >
        <span className={displayText ? "picker-value" : "picker-placeholder"}>
          {displayText || "Select date"}
        </span>
        <span className="picker-caret">▾</span>
      </button>
      {open && (
        <div className="date-dropdown">
          <div className="date-columns">
            <div className="date-col">
              <div className="date-col-label">Day</div>
              <div className="date-scroll">
                {days.map((d) => (
                  <button
                    key={d}
                    type="button"
                    className={String(d) === String(parseInt(day)) ? "selected" : ""}
                    onClick={() => handleDay(String(d))}
                  >
                    {d}
                  </button>
                ))}
              </div>
            </div>
            <div className="date-col date-col-month">
              <div className="date-col-label">Month</div>
              <div className="date-scroll">
                {MONTHS.map((m, i) => (
                  <button
                    key={m}
                    type="button"
                    className={String(i + 1) === String(parseInt(month)) ? "selected" : ""}
                    onClick={() => handleMonth(String(i + 1))}
                  >
                    {m}
                  </button>
                ))}
              </div>
            </div>
            <div className="date-col">
              <div className="date-col-label">Year</div>
              <div className="date-scroll">
                {years.map((y) => (
                  <button
                    key={y}
                    type="button"
                    className={String(y) === String(year) ? "selected" : ""}
                    onClick={() => handleYear(String(y))}
                  >
                    {y}
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
