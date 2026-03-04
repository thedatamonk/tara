import { useState, useRef, useEffect, useCallback } from "react";

const NOMINATIM_URL = "https://nominatim.openstreetmap.org/search";

function debounce(fn, ms) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  };
}

export default function LocationSearch({ value, onChange, placeholder, label }) {
  const [query, setQuery] = useState(value || "");
  const [results, setResults] = useState([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeIdx, setActiveIdx] = useState(-1);
  const wrapperRef = useRef(null);

  const search = useCallback(
    debounce(async (q) => {
      if (q.length < 2) {
        setResults([]);
        return;
      }
      setLoading(true);
      try {
        const params = new URLSearchParams({
          q,
          format: "json",
          countrycodes: "in",
          limit: "8",
          addressdetails: "1",
        });
        const res = await fetch(`${NOMINATIM_URL}?${params}`, {
          headers: { "Accept-Language": "en" },
        });
        const data = await res.json();
        const places = data.map((item) => ({
          display: item.display_name.split(",").slice(0, 3).join(",").trim(),
          full: item.display_name,
          lat: item.lat,
          lon: item.lon,
        }));
        setResults(places);
        setOpen(places.length > 0);
        setActiveIdx(-1);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 350),
    []
  );

  const handleInput = (e) => {
    const v = e.target.value;
    setQuery(v);
    search(v);
    if (!v) {
      onChange("");
      setResults([]);
      setOpen(false);
    }
  };

  const handleSelect = (place) => {
    setQuery(place.display);
    onChange(place.display);
    setOpen(false);
    setResults([]);
  };

  const handleKeyDown = (e) => {
    if (!open || results.length === 0) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIdx((i) => Math.min(i + 1, results.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIdx((i) => Math.max(i - 1, 0));
    } else if (e.key === "Enter" && activeIdx >= 0) {
      e.preventDefault();
      handleSelect(results[activeIdx]);
    } else if (e.key === "Escape") {
      setOpen(false);
    }
  };

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
    <div className="field location-field" ref={wrapperRef}>
      <label>{label}</label>
      <div className="location-input-wrap">
        <input
          type="text"
          value={query}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          onFocus={() => results.length > 0 && setOpen(true)}
          placeholder={placeholder}
          autoComplete="off"
        />
        {loading && <span className="location-spinner" />}
        <span className="location-icon">⌕</span>
      </div>
      {open && (
        <ul className="location-dropdown">
          {results.map((place, i) => (
            <li
              key={i}
              className={i === activeIdx ? "active" : ""}
              onMouseEnter={() => setActiveIdx(i)}
              onMouseDown={() => handleSelect(place)}
            >
              <span className="location-pin">◉</span>
              <span className="location-name">{place.display}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
