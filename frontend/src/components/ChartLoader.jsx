export default function ChartLoader() {
  return (
    <div className="chart-loader">
      <div className="chart-loader__wheel">
        <svg viewBox="0 0 120 120" className="chart-loader__svg">
          {/* Outer ring */}
          <circle
            cx="60" cy="60" r="54"
            fill="none"
            stroke="var(--gold-dim)"
            strokeWidth="0.5"
            opacity="0.3"
          />
          {/* Inner ring */}
          <circle
            cx="60" cy="60" r="36"
            fill="none"
            stroke="var(--gold-dim)"
            strokeWidth="0.5"
            opacity="0.2"
          />
          {/* Spinning arc */}
          <circle
            cx="60" cy="60" r="54"
            fill="none"
            stroke="var(--gold)"
            strokeWidth="1.5"
            strokeDasharray="85 255"
            strokeLinecap="round"
            className="chart-loader__arc"
          />
          {/* Cross lines */}
          <line x1="60" y1="6" x2="60" y2="114" stroke="var(--gold-dim)" strokeWidth="0.3" opacity="0.2" />
          <line x1="6" y1="60" x2="114" y2="60" stroke="var(--gold-dim)" strokeWidth="0.3" opacity="0.2" />
          {/* Center dot */}
          <circle cx="60" cy="60" r="2" fill="var(--gold)" opacity="0.6" />
        </svg>
      </div>
      <p className="chart-loader__text">Mapping the stars</p>
    </div>
  );
}
