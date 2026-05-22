import type { DriftEvent } from '../../api/types';
import DriftDiff from './DriftDiff';

interface DriftTimelineProps {
  events: DriftEvent[];
  onAcknowledge?: (id: string) => void;
  isLoading?: boolean;
}

export default function DriftTimeline({ events, onAcknowledge, isLoading }: DriftTimelineProps) {
  if (isLoading) {
    return <div className="text-center py-8 text-gray-500">Loading drift events...</div>;
  }

  if (events.length === 0) {
    return <div className="text-center py-8 text-gray-500">No drift events detected</div>;
  }

  const grouped = events.reduce<Record<string, DriftEvent[]>>((acc, event) => {
    const date = new Date(event.detected_at).toLocaleDateString();
    if (!acc[date]) acc[date] = [];
    acc[date].push(event);
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      {Object.entries(grouped).map(([date, dayEvents]) => (
        <div key={date}>
          <h3 className="text-sm font-semibold text-gray-500 mb-3 sticky top-0 bg-gray-50 py-1 px-2 rounded">
            {date}
          </h3>
          <div className="space-y-3 pl-4 border-l-2 border-gray-200">
            {dayEvents.map((event) => (
              <div key={event.id} className="relative">
                <div className="absolute -left-[1.3rem] top-4 w-2.5 h-2.5 rounded-full border-2 border-white bg-purple-500" />
                <DriftDiff event={event} />
                {!event.acknowledged && onAcknowledge && (
                  <button
                    onClick={() => onAcknowledge(event.id)}
                    className="mt-1 text-xs text-blue-600 hover:text-blue-800"
                  >
                    Acknowledge
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
