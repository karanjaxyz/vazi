import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';

// --- Types ---

interface Project {
  id: string;
  name: string;
  brand_name: string;
  is_active: boolean;
  created_at: string;
  competitors: { id: string; name: string }[];
  queries: { id: string; text: string }[];
}

interface Overview {
  visibility_score: number;
  total_mentions: number;
  total_queries: number;
  competitor_gap: number;
  sentiment_positive_pct: number;
  last_run_at: string | null;
}

interface MentionsByQuery {
  query_id: string;
  query_text: string;
  providers: Record<string, boolean>;
  sentiment: string | null;
}

interface CompetitorScore {
  name: string;
  mention_count: number;
  mention_pct: number;
  avg_position: number;
  is_target: boolean;
}

interface TrendPoint {
  run_id: string;
  date: string;
  visibility_score: number;
  mention_count: number;
  sentiment_positive_pct: number;
}

interface Source {
  domain: string;
  citation_count: number;
  providers: string[];
}

interface Run {
  id: string;
  status: string;
  started_at: string | null;
  completed_at: string | null;
  query_count: number;
  mention_count: number;
}

// --- Projects ---

export function useProjects() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: () => api.get<Project[]>('/api/projects'),
  });
}

export function useProject(id: string) {
  return useQuery({
    queryKey: ['projects', id],
    queryFn: () => api.get<Project>(`/api/projects/${id}`),
    enabled: !!id,
  });
}

export function useCreateProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { name: string; brand_name: string; competitors: { name: string }[]; queries: { text: string }[] }) =>
      api.post<Project>('/api/projects', data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['projects'] }),
  });
}

export function useUpdateProject(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { name?: string; brand_name?: string; is_active?: boolean }) =>
      api.patch<Project>(`/api/projects/${id}`, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['projects'] });
      qc.invalidateQueries({ queryKey: ['projects', id] });
    },
  });
}

export function useDeleteProject(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.delete(`/api/projects/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['projects'] }),
  });
}

// --- Competitors & Queries ---

export function useAddCompetitor(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { name: string }) =>
      api.post(`/api/projects/${projectId}/competitors`, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['projects', projectId] }),
  });
}

export function useRemoveCompetitor(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (competitorId: string) =>
      api.delete(`/api/projects/${projectId}/competitors/${competitorId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['projects', projectId] }),
  });
}

export function useAddQuery(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { text: string }) =>
      api.post(`/api/projects/${projectId}/queries`, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['projects', projectId] }),
  });
}

export function useRemoveQuery(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (queryId: string) =>
      api.delete(`/api/projects/${projectId}/queries/${queryId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['projects', projectId] }),
  });
}

// --- Dashboard ---

export function useOverview(projectId: string) {
  return useQuery({
    queryKey: ['overview', projectId],
    queryFn: () => api.get<Overview>(`/api/projects/${projectId}/overview`),
    enabled: !!projectId,
  });
}

export function useMentions(projectId: string) {
  return useQuery({
    queryKey: ['mentions', projectId],
    queryFn: () => api.get<{ mentions: MentionsByQuery[]; total_mentioned: number; total_queries: number }>(`/api/projects/${projectId}/mentions`),
    enabled: !!projectId,
  });
}

export function useCompetitors(projectId: string) {
  return useQuery({
    queryKey: ['competitors', projectId],
    queryFn: () => api.get<{ scores: CompetitorScore[]; total_queries: number }>(`/api/projects/${projectId}/competitors`),
    enabled: !!projectId,
  });
}

export function useTrends(projectId: string) {
  return useQuery({
    queryKey: ['trends', projectId],
    queryFn: () => api.get<{ data: TrendPoint[] }>(`/api/projects/${projectId}/trends`),
    enabled: !!projectId,
  });
}

export function useSources(projectId: string) {
  return useQuery({
    queryKey: ['sources', projectId],
    queryFn: () => api.get<{ sources: Source[] }>(`/api/projects/${projectId}/sources`),
    enabled: !!projectId,
  });
}

export function useRuns(projectId: string) {
  return useQuery({
    queryKey: ['runs', projectId],
    queryFn: () => api.get<{ runs: Run[] }>(`/api/projects/${projectId}/runs`),
    enabled: !!projectId,
  });
}

// --- Admin ---

export function useTriggerRun(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.post(`/api/admin/run/${projectId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['runs', projectId] }),
  });
}
