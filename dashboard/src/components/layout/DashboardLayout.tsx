import { NavLink, Outlet, useParams } from 'react-router-dom';
import { useAuthStore } from '../../stores/auth';
import { useProjects } from '../../hooks/use-api';

const navItems = [
  { label: 'Overview', path: '' },
  { label: 'Mentions', path: 'mentions' },
  { label: 'Competitors', path: 'competitors' },
  { label: 'Trends', path: 'trends' },
  { label: 'Sources', path: 'sources' },
  { label: 'Runs', path: 'runs' },
  { label: 'Settings', path: 'settings' },
];

export default function DashboardLayout() {
  const { signOut } = useAuthStore();
  const { projectId } = useParams();
  const { data: projects } = useProjects();

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-60 bg-bg-warm border-r border-border flex flex-col shrink-0">
        {/* Logo */}
        <div className="px-5 h-16 flex items-center border-b border-border">
          <a href="/" className="font-serif text-xl text-text">
            Vazi<span className="text-accent">.</span>
          </a>
        </div>

        {/* Project selector */}
        <div className="px-3 py-3 border-b border-border">
          <select
            className="w-full bg-bg border border-border rounded-lg px-3 py-2 text-sm text-text-secondary focus:outline-none focus:border-accent"
            value={projectId || ''}
            onChange={(e) => {
              if (e.target.value) window.location.href = `/projects/${e.target.value}`;
            }}
          >
            <option value="">Select project</option>
            {projects?.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>

        {/* Nav links */}
        {projectId && (
          <nav className="flex-1 px-3 py-3 space-y-0.5 overflow-y-auto">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={`/projects/${projectId}/${item.path}`}
                end={item.path === ''}
                className={({ isActive }) =>
                  `block px-3 py-2 rounded-lg text-sm transition-colors ${
                    isActive
                      ? 'bg-accent-dim text-accent font-medium'
                      : 'text-text-muted hover:text-text-secondary hover:bg-bg-card'
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        )}

        {/* Bottom */}
        <div className="p-3 border-t border-border space-y-1">
          <NavLink
            to="/settings"
            className="block px-3 py-2 rounded-lg text-sm text-text-muted hover:text-text-secondary hover:bg-bg-card transition-colors"
          >
            Account
          </NavLink>
          <button
            onClick={signOut}
            className="w-full text-left px-3 py-2 rounded-lg text-sm text-text-muted hover:text-red hover:bg-bg-card transition-colors"
          >
            Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
