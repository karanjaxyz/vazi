import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  useProject,
  useUpdateProject,
  useDeleteProject,
  useAddCompetitor,
  useRemoveCompetitor,
  useAddQuery,
  useRemoveQuery,
} from '../../hooks/use-api';

export default function ProjectSettingsPage() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { data: project, isLoading } = useProject(projectId!);
  const updateProject = useUpdateProject(projectId!);
  const deleteProject = useDeleteProject(projectId!);
  const addCompetitor = useAddCompetitor(projectId!);
  const removeCompetitor = useRemoveCompetitor(projectId!);
  const addQuery = useAddQuery(projectId!);
  const removeQuery = useRemoveQuery(projectId!);

  const [competitorInput, setCompetitorInput] = useState('');
  const [queryInput, setQueryInput] = useState('');

  if (isLoading || !project) return <div className="p-8 text-text-muted text-sm">Loading...</div>;

  const handleDelete = async () => {
    if (!confirm('Delete this project and all its data? This cannot be undone.')) return;
    await deleteProject.mutateAsync();
    navigate('/');
  };

  return (
    <div className="p-8 max-w-2xl">
      <h1 className="font-serif text-2xl mb-8">Project Settings</h1>

      {/* Brand name */}
      <div className="mb-8 pb-8 border-b border-border">
        <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wide mb-4">Brand</h2>
        <div className="flex gap-2">
          <input
            type="text"
            defaultValue={project.brand_name}
            onBlur={(e) => {
              if (e.target.value !== project.brand_name) {
                updateProject.mutate({ brand_name: e.target.value });
              }
            }}
            className="flex-1 px-4 py-3 bg-bg-card border border-border rounded-lg text-sm text-text focus:outline-none focus:border-accent transition-colors"
          />
        </div>
      </div>

      {/* Competitors */}
      <div className="mb-8 pb-8 border-b border-border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wide">Competitors</h2>
          <span className="text-xs text-text-muted">{project.competitors.length}/5</span>
        </div>

        <div className="space-y-2 mb-4">
          {project.competitors.map((c) => (
            <div key={c.id} className="flex items-center justify-between px-3 py-2 bg-bg-card border border-border rounded-lg">
              <span className="text-sm">{c.name}</span>
              <button
                onClick={() => removeCompetitor.mutate(c.id)}
                className="text-text-muted hover:text-red transition-colors text-sm"
              >
                Remove
              </button>
            </div>
          ))}
        </div>

        {project.competitors.length < 5 && (
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Add competitor"
              value={competitorInput}
              onChange={(e) => setCompetitorInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && competitorInput.trim()) {
                  e.preventDefault();
                  addCompetitor.mutate({ name: competitorInput.trim() });
                  setCompetitorInput('');
                }
              }}
              className="flex-1 px-4 py-3 bg-bg-card border border-border rounded-lg text-sm text-text placeholder:text-text-muted focus:outline-none focus:border-accent transition-colors"
            />
            <button
              onClick={() => {
                if (competitorInput.trim()) {
                  addCompetitor.mutate({ name: competitorInput.trim() });
                  setCompetitorInput('');
                }
              }}
              className="px-4 py-3 border border-border rounded-lg text-sm text-text-secondary hover:border-border-light transition-colors"
            >
              Add
            </button>
          </div>
        )}
      </div>

      {/* Queries */}
      <div className="mb-8 pb-8 border-b border-border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wide">Tracked Queries</h2>
          <span className="text-xs text-text-muted">{project.queries.length}/20</span>
        </div>

        <div className="space-y-1.5 mb-4">
          {project.queries.map((q) => (
            <div key={q.id} className="flex items-center justify-between px-3 py-2 bg-bg-card border border-border rounded-lg">
              <span className="text-sm font-mono text-text-secondary">{q.text}</span>
              <button
                onClick={() => removeQuery.mutate(q.id)}
                className="text-text-muted hover:text-red transition-colors text-sm"
              >
                Remove
              </button>
            </div>
          ))}
        </div>

        {project.queries.length < 20 && (
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Add query"
              value={queryInput}
              onChange={(e) => setQueryInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && queryInput.trim()) {
                  e.preventDefault();
                  addQuery.mutate({ text: queryInput.trim() });
                  setQueryInput('');
                }
              }}
              className="flex-1 px-4 py-3 bg-bg-card border border-border rounded-lg text-sm text-text placeholder:text-text-muted focus:outline-none focus:border-accent transition-colors"
            />
            <button
              onClick={() => {
                if (queryInput.trim()) {
                  addQuery.mutate({ text: queryInput.trim() });
                  setQueryInput('');
                }
              }}
              className="px-4 py-3 border border-border rounded-lg text-sm text-text-secondary hover:border-border-light transition-colors"
            >
              Add
            </button>
          </div>
        )}
      </div>

      {/* Danger zone */}
      <div>
        <h2 className="text-sm font-semibold text-red uppercase tracking-wide mb-4">Danger Zone</h2>
        <button
          onClick={handleDelete}
          className="px-4 py-2.5 border border-red/30 rounded-lg text-sm text-red hover:bg-red/10 transition-colors"
        >
          Delete project
        </button>
      </div>
    </div>
  );
}
