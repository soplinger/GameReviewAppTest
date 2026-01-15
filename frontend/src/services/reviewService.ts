import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../lib/api';
import type { Review, ReviewCreate, ReviewUpdate, PaginatedResponse } from '../types/api';

// Review API calls
const reviewApi = {
  create: async (data: ReviewCreate): Promise<Review> => {
    const response = await apiClient.post('/api/v1/reviews/', data);
    return response.data;
  },

  update: async (id: number, data: ReviewUpdate): Promise<Review> => {
    const response = await apiClient.put(`/api/v1/reviews/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/v1/reviews/${id}`);
  },

  getById: async (id: number): Promise<Review> => {
    const { data } = await apiClient.get(`/api/v1/reviews/${id}`);
    return data;
  },

  getByGame: async (params: {
    game_id: number;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Review>> => {
    const { data } = await apiClient.get('/api/v1/reviews/', { params });
    return data;
  },

  getByUser: async (params: {
    user_id: number;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Review>> => {
    const { data } = await apiClient.get('/api/v1/reviews/', { params });
    return data;
  },

  getMyReviews: async (params: {
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Review>> => {
    const { data } = await apiClient.get('/api/v1/reviews/users/me/reviews', { params });
    return data;
  },

  markHelpful: async (id: number): Promise<Review> => {
    const { data } = await apiClient.post(`/api/v1/reviews/${id}/helpful`);
    return data;
  },
};

// React Query hooks
export const useCreateReview = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: reviewApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] });
      queryClient.invalidateQueries({ queryKey: ['games'] });
    },
  });
};

export const useUpdateReview = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ReviewUpdate }) =>
      reviewApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] });
      queryClient.invalidateQueries({ queryKey: ['games'] });
    },
  });
};

export const useDeleteReview = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: reviewApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] });
      queryClient.invalidateQueries({ queryKey: ['games'] });
    },
  });
};

export const useReview = (id: number | null) => {
  return useQuery({
    queryKey: ['reviews', id],
    queryFn: () => reviewApi.getById(id!),
    enabled: !!id,
  });
};

export const useGameReviews = (gameId: number | null, page = 1, pageSize = 20) => {
  return useQuery({
    queryKey: ['reviews', 'game', gameId, page, pageSize],
    queryFn: () => reviewApi.getByGame({ game_id: gameId!, page, page_size: pageSize }),
    enabled: !!gameId,
  });
};

export const useUserReviews = (userId: number | null, page = 1, pageSize = 20) => {
  return useQuery({
    queryKey: ['reviews', 'user', userId, page, pageSize],
    queryFn: () => reviewApi.getByUser({ user_id: userId!, page, page_size: pageSize }),
    enabled: !!userId,
  });
};

export const useMyReviews = (page = 1, pageSize = 20) => {
  return useQuery({
    queryKey: ['reviews', 'me', page, pageSize],
    queryFn: () => reviewApi.getMyReviews({ page, page_size: pageSize }),
  });
};

export const useMarkHelpful = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: reviewApi.markHelpful,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] });
    },
  });
};
