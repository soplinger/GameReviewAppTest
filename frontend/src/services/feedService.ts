/**
 * Feed service for social review feed functionality
 * Provides React Query hooks for fetching friends' reviews
 */

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import type { ReviewResponse } from './reviewService';

// Types for feed
export interface FeedResponse {
  reviews: ReviewResponse[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface FeedParams {
  page?: number;
  page_size?: number;
}

// Query keys
export const feedKeys = {
  all: ['feed'] as const,
  lists: () => [...feedKeys.all, 'list'] as const,
  list: (params: FeedParams) => [...feedKeys.lists(), params] as const,
};

// API functions
const feedApi = {
  // Get social feed
  getFeed: async (params: FeedParams = {}): Promise<FeedResponse> => {
    const response = await apiClient.get('/reviews/feed', {
      params: {
        page: params.page || 1,
        page_size: params.page_size || 20,
      },
    });
    return response.data;
  },
};

// React Query hooks

/**
 * Hook to get social feed with pagination
 */
export const useFeed = (params: FeedParams = {}) => {
  return useQuery({
    queryKey: feedKeys.list(params),
    queryFn: () => feedApi.getFeed(params),
    staleTime: 60000, // 1 minute
    gcTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to get social feed with infinite scroll support
 */
export const useInfiniteFeed = (pageSize: number = 20) => {
  return useQuery({
    queryKey: feedKeys.list({ page_size: pageSize }),
    queryFn: () => feedApi.getFeed({ page: 1, page_size: pageSize }),
    staleTime: 60000, // 1 minute
    select: (data) => ({
      ...data,
      hasNextPage: data.page < data.total_pages,
    }),
  });
};