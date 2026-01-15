import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../lib/api';
import type {
  Game,
  Review,
  ReviewCreate,
  ReviewUpdate,
  PaginatedResponse,
} from '../types/api';

// Game API calls
const gameApi = {
  search: async (params: {
    query?: string;
    platform?: string;
    genre?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Game>> => {
    const { data } = await apiClient.get('/api/v1/games/search', { params });
    return data;
  },

  getPopular: async (params: {
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Game>> => {
    const { data } = await apiClient.get('/api/v1/games/popular', { params });
    return data;
  },

  getRecent: async (params: {
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Game>> => {
    const { data } = await apiClient.get('/api/v1/games/recent', { params });
    return data;
  },

  getById: async (id: number): Promise<Game> => {
    const { data } = await apiClient.get(`/api/v1/games/${id}`);
    return data;
  },

  getBySlug: async (slug: string): Promise<Game> => {
    const { data } = await apiClient.get(`/api/v1/games/slug/${slug}`);
    return data;
  },
};

// React Query hooks for games
export const useSearchGames = (params: {
  query?: string;
  platform?: string;
  genre?: string;
  page?: number;
  page_size?: number;
}) => {
  return useQuery({
    queryKey: ['games', 'search', params],
    queryFn: () => gameApi.search(params),
    enabled: !!(params.query || params.platform || params.genre),
  });
};

export const usePopularGames = (params: { page?: number; page_size?: number } = {}) => {
  return useQuery({
    queryKey: ['games', 'popular', params],
    queryFn: () => gameApi.getPopular(params),
  });
};

export const useRecentGames = (params: { page?: number; page_size?: number } = {}) => {
  return useQuery({
    queryKey: ['games', 'recent', params],
    queryFn: () => gameApi.getRecent(params),
  });
};

export const useGame = (id: number | null) => {
  return useQuery({
    queryKey: ['games', id],
    queryFn: () => gameApi.getById(id!),
    enabled: !!id,
  });
};

export const useGameBySlug = (slug: string | null) => {
  return useQuery({
    queryKey: ['games', 'slug', slug],
    queryFn: () => gameApi.getBySlug(slug!),
    enabled: !!slug,
  });
};
