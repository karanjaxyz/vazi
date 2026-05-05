import { useParams } from 'react-router-dom';
import { useRuns } from '../../hooks/use-api';
import { formatDistanceToNow } from 'date-fns';

const statusColors: Record<string, string> = {
  completed: 'bg-green/10 text-green',
  running: 'bg-accent-dim text-accent',
  pending: 'bg-bg-card text-text-muted',
  failed: 'bg-red/10 text-red',
};

export default function RunsPage() {
  const { projectId } = useParams();
  const { data, isLoading } = useRuns(projectId!);

  if (isLoading) return <div className="p-8 text-text-muted text-sm">Loading...</div>;
  if (!data?.runs.length) return <div className="p-8 text-text-muted text-sm">No runs yet.</div>;

  return (
    <div className="p-8">
      <h1 className="font-serif text-2xl mb-6">Run History</h1>
      <div className="border border-border rounded-xl overflow-hidden">
        <div className="divide-y divide-border">
          {data.runs.map((run) => (
            <div key={run.id} className="px-5 py-4 flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${statusColors[run.status] || ''}`}>
                    {run.status}
                  </span>
                  {run.completed_at && (
                    <span className="text-xs text-text-muted">
                      {formatDistanceToNow(new Date(run.completed_at))} ago
                    </span>
                  )}
                </div>
              </div>
              <div className="text-sm font-mono text-text-secondary">
                {run.mention_count} mentions · {run.query_count} queries
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
