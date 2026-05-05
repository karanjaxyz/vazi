import { Link } from 'react-router-dom';
import { useProjects } from '../../hooks/use-api';
import { formatDistanceToNow } from 'date-fns';

export default function ProjectsPage() {
  const { data: projects, isLoading } = useProjects();

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <h1 className="font-serif text-3xl">Projects</h1>
        <Link
          to="/projects/new"
          className="px-5 py-2.5 bg-accent text-bg rounded-lg text-sm font-semibold hover:opacity-90 transition-opacity"
        >
          New project
        </Link>
      </div>

      {isLoading ? (
        <div className="text-text-muted text-sm">Loading...</div>
      ) : !projects?.length ? (
        <div className="border border-border rounded-xl p-12 text-center">
          <p className="text-text-secondary mb-2">No projects yet</p>
          <p className="text-sm text-text-muted mb-6">Create your first project to start tracking AI visibility.</p>
          <Link
            to="/projects/new"
            className="inline-flex px-5 py-2.5 bg-accent text-bg rounded-lg text-sm font-semibold hover:opacity-90 transition-opacity"
          >
            Create project
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {projects.map((project) => (
            <Link
              key={project.id}
              to={`/projects/${project.id}`}
              className="block border border-border rounded-xl p-5 hover:border-border-light transition-colors"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="font-semibold">{project.name}</h2>
                  <p className="text-sm text-text-muted mt-1">
                    Tracking "{project.brand_name}" · Created {formatDistanceToNow(new Date(project.created_at))} ago
                  </p>
                </div>
                <div className={`w-2 h-2 rounded-full ${project.is_active ? 'bg-green' : 'bg-text-muted'}`} />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
