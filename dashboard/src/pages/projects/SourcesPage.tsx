// Sources page
import { useParams } from 'react-router-dom';
import { useSources } from '../../hooks/use-api';

export default function SourcesPage() {
  const { projectId } = useParams();
  const { data, isLoading } = useSources(projectId!);

  if (isLoading) return <div className="p-8 text-text-muted text-sm">Loading...</div>;
  if (!data?.sources.length) return <div className="p-8 text-text-muted text-sm">No sources cited yet.</div>;

  return (
    <div className="p-8">
      <h1 className="font-serif text-2xl mb-6">Cited Sources</h1>
      <div className="border border-border rounded-xl overflow-hidden">
        <div className="divide-y divide-border">
          {data.sources.map((s) => (
            <div key={s.domain} className="px-5 py-3 flex items-center justify-between">
              <div>
                <span className="text-sm font-medium">{s.domain}</span>
                <div className="flex gap-1.5 mt-1">
                  {s.providers.map((p) => (
                    <span key={p} className="text-[10px] text-text-muted bg-bg-card px-1.5 py-0.5 rounded">{p}</span>
                  ))}
                </div>
              </div>
              <span className="text-sm font-mono text-text-secondary">{s.citation_count}×</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
