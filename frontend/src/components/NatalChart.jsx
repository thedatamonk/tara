export default function NatalChart({ svgString }) {
  if (!svgString) return null;
  return (
    <div
      className="natal-chart"
      dangerouslySetInnerHTML={{ __html: svgString }}
    />
  );
}
