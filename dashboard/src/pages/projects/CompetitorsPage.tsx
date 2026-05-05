import { useParams } from 'react-router-dom';
import { useCompetitors } from '../../hooks/use-api';

export default function CompetitorsPage() {
  const { projectId } = useParams();
  const { data, isLoading } = useCompetitors(projectId!);

  if (isLoading) return <div className="p-8 text-text-muted text-sm">Loading...</div>;
  if (!data?.scores.length) return <div className="p-8 text-text-muted text-sm">No data yet. Run a scan first.</div>;

  return (
    <div className="p-8">
      <h1 className="font-serif text-2xl mb-6">Competitor Comparison</h1>

      <div className="border border-border rounded-xl overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border text-left">
              <th className="px-5 py-3 text-[11px] text-text-muted uppercase tracking-wide font-medium">Brand</th>
              <th className="px-5 py-3 text-[11px] text-text-muted uppercase tracking-wide font-medium">Mentions</th>
              <th className="px-5 py-3 text-[11px] text-text-muted uppercase tracking-wide font-medium">% of Queries</th>
              <th className="px-5 py-3 text-[11px] text-text-muted uppercase tracking-wide font-medium">Avg Position</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {data.scores.map((score) => (
              <tr key={score.name} className={score.is_target ? 'bg-accent-dim' : ''}>
                <td className="px-5 py-3 text-sm font-medium">
                  {score.name}
                  {score.is_target && <span className="ml-2 text-[10px] text-accent font-semibold">YOU</span>}
                </td>
                <td className="px-5 py-3 text-sm font-mono text-text-secondary">{score.mention_count}</td>
                <td className="px-5 py-3 text-sm font-mono text-text-secondary">{score.mention_pct}%</td>
                <td className="px-5 py-3 text-sm font-mono text-text-secondary">#{score.avg_position}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
