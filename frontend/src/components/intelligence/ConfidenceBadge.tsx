interface ConfidenceBadgeProps {
  confidence: number;
}

export default function ConfidenceBadge({ confidence }: ConfidenceBadgeProps) {
  const pct = Math.round(confidence * 100);
  let color = 'bg-red-100 text-red-800';
  if (pct >= 80) color = 'bg-green-100 text-green-800';
  else if (pct >= 60) color = 'bg-yellow-100 text-yellow-800';
  else if (pct >= 40) color = 'bg-orange-100 text-orange-800';

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${color}`}>
      {pct}%
    </span>
  );
}
