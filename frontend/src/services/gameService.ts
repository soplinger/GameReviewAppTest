import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api.ts';
import type {
  Game,
  Review,
  ReviewCreate,
  ReviewUpdate,
  PaginatedResponse,
} from '../types/api';

// Types for sync operations
export interface SyncResponse {
  success: boolean;
  message: string;
  count: number;
}

// Game API calls
const gameApi = {
  search: async (params: {
    query?: string;
    platform?: string;
    genre?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Game>> => {
    const { data } = await apiClient.get('/games/search', { params });
    return data;
  },

  hybridSearch: async (params: {
    query: string;
    auto_sync?: boolean;
    sync_limit?: number;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Game>> => {
    const { data } = await apiClient.get('/games/search/hybrid', { params });
    return data;
  },

  getPopular: async (params: {
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Game>> => {
    const { data } = await apiClient.get('/games/popular', { params });
    return data;
  },

  getRecent: async (params: {
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Game>> => {
    const { data } = await apiClient.get('/games/recent', { params });
    return data;
  },

  getById: async (id: number): Promise<Game> => {
    const { data } = await apiClient.get(`/games/${id}`);
    return data;
  },

  getBySlug: async (slug: string): Promise<Game> => {
    const { data } = await apiClient.get(`/games/slug/${slug}`);
    return data;
  },

  // Sync operations
  syncPopularGames: async (limit: number = 50): Promise<SyncResponse> => {
    const { data } = await apiClient.post('/games/sync/popular', null, {
      params: { limit },
    });
    return data;
  },

  syncGamesBySearch: async (query: string, limit: number = 10): Promise<SyncResponse> => {
    const { data } = await apiClient.post('/games/sync/search', null, {
      params: { query, limit },
    });
    return data;
  },

  syncGameById: async (igdbId: number): Promise<SyncResponse> => {
    const { data } = await apiClient.post(`/games/sync/game/${igdbId}`);
    return data;
  },

  syncGamesByGenre: async (genre: string, limit: number = 20): Promise<SyncResponse> => {
    const { data } = await apiClient.post(`/games/sync/genre/${encodeURIComponent(genre)}`, null, {
      params: { limit },
    });
    return data;
  },

  syncRecentGames: async (limit: number = 30, daysBack: number = 90): Promise<SyncResponse> => {
    const { data } = await apiClient.post('/games/sync/recent', null, {
      params: { limit, days_back: daysBack },
    });
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

export const useHybridSearchGames = (params: {
  query: string;
  auto_sync?: boolean;
  sync_limit?: number;
  page?: number;
  page_size?: number;
}) => {
  return useQuery({
    queryKey: ['games', 'hybrid-search', params],
    queryFn: () => gameApi.hybridSearch(params),
    enabled: !!params.query,
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

export const useGame = (idOrSlug: number | string | null | undefined) => {
  return useQuery({
    queryKey: ['games', idOrSlug],
    queryFn: async () => {
      if (!idOrSlug) throw new Error('Game ID or slug is required');
      // If it's a number or numeric string, use ID endpoint, otherwise use slug
      const isId = typeof idOrSlug === 'number' || /^\d+$/.test(String(idOrSlug));
      return isId ? gameApi.getById(Number(idOrSlug)) : gameApi.getBySlug(String(idOrSlug));
    },
    enabled: !!idOrSlug,
  });
};

export const useGameBySlug = (slug: string | null) => {
  return useQuery({
    queryKey: ['games', 'slug', slug],
    queryFn: () => gameApi.getBySlug(slug!),
    enabled: !!slug,
  });
};

// Sync mutations
export const useSyncPopularGames = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (limit: number = 50) => gameApi.syncPopularGames(limit),
    onSuccess: () => {
      // Invalidate games queries to refetch updated data
      queryClient.invalidateQueries({ queryKey: ['games'] });
    },
  });
};

export const useSyncGamesBySearch = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ query, limit }: { query: string; limit?: number }) =>
      gameApi.syncGamesBySearch(query, limit),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['games'] });
    },
  });
};

export const useSyncGameById = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (igdbId: number) => gameApi.syncGameById(igdbId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['games'] });
    },
  });
};

export const useSyncGamesByGenre = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ genre, limit }: { genre: string; limit?: number }) =>
      gameApi.syncGamesByGenre(genre, limit),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['games'] });
    },
  });
};

export const useSyncRecentGames = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ limit, daysBack }: { limit?: number; daysBack?: number } = {}) =>
      gameApi.syncRecentGames(limit, daysBack),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['games'] });
    },
  });
};
