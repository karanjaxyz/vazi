import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCreateProject } from '../../hooks/use-api';

export default function NewProjectPage() {
  const navigate = useNavigate();
  const createProject = useCreateProject();

  const [name, setName] = useState('');
  const [brandName, setBrandName] = useState('');
  const [competitorInput, setCompetitorInput] = useState('');
  const [competitors, setCompetitors] = useState<string[]>([]);
  const [queryInput, setQueryInput] = useState('');
  const [queries, setQueries] = useState<string[]>([]);

  const addCompetitor = () => {
    const val = competitorInput.trim();
    if (val && competitors.length < 5 && !competitors.includes(val)) {
      setCompetitors([...competitors, val]);
      setCompetitorInput('');
    }
  };

  const addQuery = () => {
    const val = queryInput.trim();
    if (val && queries.length < 20 && !queries.includes(val)) {
      setQueries([...queries, val]);
      setQueryInput('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const project = await createProject.mutateAsync({
      name,
      brand_name: brandName,
      competitors: competitors.map((c) => ({ name: c })),
      queries: queries.map((q) => ({ text: q })),
    });
    navigate(`/projects/${project.id}`);
  };

  const inputClass = 'w-full px-4 py-3 bg-bg-card border border-border rounded-lg text-sm text-text placeholder:text-text-muted focus:outline-none focus:border-accent transition-colors';

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="font-serif text-3xl mb-2">New Project</h1>
      <p className="text-sm text-text-muted mb-8">Set up your brand, competitors, and queries to track.</p>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Basics */}
        <div className="space-y-4">
          <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wide">Basics</h2>
          <input
            type="text"
            placeholder="Project name (e.g. My SaaS)"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className={inputClass}
            required
          />
          <input
            type="text"
            placeholder="Brand name to track (e.g. Acme CRM)"
            value={brandName}
            onChange={(e) => setBrandName(e.target.value)}
            className={inputClass}
            required
          />
        </div>

        {/* Competitors */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wide">Competitors</h2>
            <span className="text-xs text-text-muted">{competitors.length}/5</span>
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Competitor name"
              value={competitorInput}
              onChange={(e) => setCompetitorInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addCompetitor())}
              className={inputClass}
              disabled={competitors.length >= 5}
            />
            <button
              type="button"
              onClick={addCompetitor}
              disabled={competitors.length >= 5}
              className="px-4 py-3 border border-border rounded-lg text-sm text-text-secondary hover:border-border-light transition-colors disabled:opacity-30 shrink-0"
            >
              Add
            </button>
          </div>

          {competitors.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {competitors.map((c) => (
                <span key={c} className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-bg-card border border-border rounded-lg text-sm">
                  {c}
                  <button
                    type="button"
                    onClick={() => setCompetitors(competitors.filter((x) => x !== c))}
                    className="text-text-muted hover:text-red transition-colors"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Queries */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wide">Queries</h2>
            <span className="text-xs text-text-muted">{queries.length}/20</span>
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              placeholder="e.g. best CRM for small business"
              value={queryInput}
              onChange={(e) => setQueryInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addQuery())}
              className={inputClass}
              disabled={queries.length >= 20}
            />
            <button
              type="button"
              onClick={addQuery}
              disabled={queries.length >= 20}
              className="px-4 py-3 border border-border rounded-lg text-sm text-text-secondary hover:border-border-light transition-colors disabled:opacity-30 shrink-0"
            >
              Add
            </button>
          </div>

          {queries.length > 0 && (
            <div className="space-y-1.5">
              {queries.map((q) => (
                <div key={q} className="flex items-center justify-between px-3 py-2 bg-bg-card border border-border rounded-lg">
                  <span className="text-sm font-mono text-text-secondary">{q}</span>
                  <button
                    type="button"
                    onClick={() => setQueries(queries.filter((x) => x !== q))}
                    className="text-text-muted hover:text-red transition-colors text-sm"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Submit */}
        <div className="flex items-center gap-4 pt-4 border-t border-border">
          <button
            type="submit"
            disabled={createProject.isPending || !name || !brandName}
            className="px-6 py-3 bg-accent text-bg rounded-lg text-sm font-semibold hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {createProject.isPending ? 'Creating...' : 'Create project'}
          </button>
          {createProject.isError && (
            <p className="text-sm text-red">{createProject.error.message}</p>
          )}
        </div>
      </form>
    </div>
  );
}
