import { useParams } from 'react-router-dom';
import { useOverview, useMentions, useTriggerRun } from '../../hooks/use-api';

function MetricCard({ label, value, delta, color }: {
  label: string; value: string; delta?: string; color?: string;
}) {
  return (
    <div className="bg-bg-card border border-border rounded-xl p-5">
      <div className="text-[11px] text-text-muted uppercase tracking-wide mb-2">{label}</div>
      <div className={`font-serif text-3xl tracking-tight ${color || ''}`}>{value}</div>
      {delta && <div className="text-xs text-green font-medium mt-1">{delta}</div>}
    </div>
  );
}

export default function OverviewPage() {
  const { projectId } = useParams();
  const { data: overview, isLoading } = useOverview(projectId!);
  const { data: mentions } = useMentions(projectId!);
  const triggerRun = useTriggerRun(projectId!);

  if (isLoading) {
    return <div className="p-8 text-text-muted text-sm">Loading...</div>;
  }

  if (!overview) {
    return (
      <div className="p-8">
        <div className="border border-border rounded-xl p-12 text-center">
          <p className="text-text-secondary mb-2">No data yet</p>
          <p className="text-sm text-text-muted mb-6">Run your first monitoring scan to see results.</p>
          <button
            onClick={() => triggerRun.mutate()}
            disabled={triggerRun.isPending}
            className="px-5 py-2.5 bg-accent text-bg rounded-lg text-sm font-semibold hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {triggerRun.isPending ? 'Starting...' : 'Run first scan'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="font-serif text-2xl">Overview</h1>
        <button
          onClick={() => triggerRun.mutate()}
          disabled={triggerRun.isPending}
          className="px-4 py-2 border border-border rounded-lg text-sm text-text-secondary hover:border-border-light hover:text-text transition-all disabled:opacity-50"
        >
          {triggerRun.isPending ? 'Running...' : 'Run scan'}
        </button>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-8">
        <MetricCard
          label="Visibility Score"
          value={`${overview.visibility_score}`}
        />
        <MetricCard
          label="Mentions"
          value={`${overview.total_mentions}`}
          delta={`of ${overview.total_queries} queries`}
        />
        <MetricCard
          label="Competitor Gap"
          value={overview.competitor_gap >= 0 ? `+${overview.competitor_gap}` : `${overview.competitor_gap}`}
          color={overview.competitor_gap >= 0 ? 'text-green' : 'text-red'}
        />
        <MetricCard
          label="Sentiment"
          value={`${overview.sentiment_positive_pct}%`}
          delta="Positive"
          color="text-accent"
        />
      </div>

      {/* Mention breakdown */}
      {mentions && (
        <div className="border border-border rounded-xl overflow-hidden">
          <div className="px-5 py-3 border-b border-border">
            <h2 className="text-sm font-medium text-text-secondary">
              Mentions by query — {mentions.total_mentioned}/{mentions.total_queries} queries
            </h2>
          </div>
          <div className="divide-y divide-border">
            {mentions.mentions.map((m) => (
              <div key={m.query_id} className="px-5 py-3 flex items-center justify-between">
                <span className="text-sm font-mono text-text-secondary truncate mr-4">
                  {m.query_text}
                </span>
                <div className="flex gap-1.5 shrink-0">
                  {Object.entries(m.providers).map(([provider, mentioned]) => (
                    <span
                      key={provider}
                      className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        mentioned
                          ? 'bg-accent-dim text-accent'
                          : 'bg-bg-card text-text-muted'
                      }`}
                    >
                      {provider} {mentioned ? '✓' : '✗'}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
