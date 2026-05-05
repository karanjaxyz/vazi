import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import AuthGuard from './components/layout/AuthGuard';
import DashboardLayout from './components/layout/DashboardLayout';

import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import ProjectsPage from './pages/projects/ProjectsPage';
import NewProjectPage from './pages/projects/NewProjectPage';
import OverviewPage from './pages/projects/OverviewPage';
import MentionsPage from './pages/projects/MentionsPage';
import CompetitorsPage from './pages/projects/CompetitorsPage';
import TrendsPage from './pages/projects/TrendsPage';
import SourcesPage from './pages/projects/SourcesPage';
import RunsPage from './pages/projects/RunsPage';
import SettingsPage from './pages/projects/SettingsPage';
import AccountPage from './pages/settings/AccountPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000, // 1 min before refetch
      retry: 1,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Public */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected */}
          <Route element={<AuthGuard />}>
            <Route element={<DashboardLayout />}>
              <Route path="/" element={<ProjectsPage />} />
              <Route path="/projects/new" element={<NewProjectPage />} />
              <Route path="/projects/:projectId" element={<OverviewPage />} />
              <Route path="/projects/:projectId/mentions" element={<MentionsPage />} />
              <Route path="/projects/:projectId/competitors" element={<CompetitorsPage />} />
              <Route path="/projects/:projectId/trends" element={<TrendsPage />} />
              <Route path="/projects/:projectId/sources" element={<SourcesPage />} />
              <Route path="/projects/:projectId/runs" element={<RunsPage />} />
              <Route path="/projects/:projectId/settings" element={<SettingsPage />} />
              <Route path="/settings" element={<AccountPage />} />
            </Route>
          </Route>

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
