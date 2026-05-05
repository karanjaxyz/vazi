import { useParams } from 'react-router-dom';
import { useMentions } from '../../hooks/use-api';

export default function MentionsPage() {
  const { projectId } = useParams();
  const { data, isLoading } = useMentions(projectId!);

  if (isLoading) return <div className="p-8 text-text-muted text-sm">Loading...</div>;
  if (!data?.mentions.length) return <div className="p-8 text-text-muted text-sm">No data yet. Run a scan first.</div>;

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="font-serif text-2xl">Mentions</h1>
        <p className="text-sm text-text-muted">
          Mentioned in {data.total_mentioned} of {data.total_queries} queries
        </p>
      </div>

      <div className="border border-border rounded-xl overflow-hidden">
        {/* Header */}
        <div className="px-5 py-3 border-b border-border grid grid-cols-[1fr_auto_80px] gap-4 items-center">
          <span className="text-[11px] text-text-muted uppercase tracking-wide font-medium">Query</span>
          <span className="text-[11px] text-text-muted uppercase tracking-wide font-medium">Providers</span>
          <span className="text-[11px] text-text-muted uppercase tracking-wide font-medium text-right">Sentiment</span>
        </div>

        {/* Rows */}
        <div className="divide-y divide-border">
          {data.mentions.map((m) => {
            const mentioned = Object.values(m.providers).some(Boolean);
            return (
              <div
                key={m.query_id}
                className={`px-5 py-3 grid grid-cols-[1fr_auto_80px] gap-4 items-center ${
                  !mentioned ? 'opacity-40' : ''
                }`}
              >
                <span className="text-sm font-mono text-text-secondary truncate">{m.query_text}</span>
                <div className="flex gap-1.5">
                  {Object.entries(m.providers).map(([provider, isMentioned]) => (
                    <span
                      key={provider}
                      className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        isMentioned
                          ? 'bg-accent-dim text-accent'
                          : 'bg-bg-card text-text-muted'
                      }`}
                    >
                      {provider}
                    </span>
                  ))}
                </div>
                <span className={`text-xs font-medium text-right ${
                  m.sentiment === 'positive' ? 'text-green' :
                  m.sentiment === 'negative' ? 'text-red' :
                  'text-text-muted'
                }`}>
                  {m.sentiment || '—'}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
