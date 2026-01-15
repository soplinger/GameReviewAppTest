/**
 * Social service for friend management API calls
 * Provides React Query hooks for friend requests, user search, and friend management
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../lib/api';
import type { User } from '../types/auth';

// Types for social features
export interface FriendRequest {
  addressee_id: number;
}

export interface FriendshipResponse {
  id: number;
  requester_id: number;
  addressee_id: number;
  status: 'pending' | 'accepted' | 'declined' | 'blocked';
  created_at: string;
  updated_at: string;
  requester: User;
  addressee: User;
}

export interface UserSearchParams {
  query?: string;
  limit?: number;
  offset?: number;
}

export interface UserWithFriendship extends User {
  friendship_status: 'none' | 'pending_sent' | 'pending_received' | 'friends' | 'blocked';
  friendship_id?: number;
}

export interface UserSearchResponse {
  users: UserWithFriendship[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PendingRequestsResponse {
  sent_requests: FriendshipResponse[];
  received_requests: FriendshipResponse[];
}

// Query keys
export const socialKeys = {
  all: ['social'] as const,
  friends: () => [...socialKeys.all, 'friends'] as const,
  requests: () => [...socialKeys.all, 'requests'] as const,
  search: (params: UserSearchParams) => [...socialKeys.all, 'search', params] as const,
  status: (userId: number) => [...socialKeys.all, 'status', userId] as const,
};

// API functions
const socialApi = {
  // Send friend request
  sendFriendRequest: async (data: FriendRequest): Promise<FriendshipResponse> => {
    const response = await apiClient.post('/social/friends/request', data);
    return response.data;
  },

  // Respond to friend request (accept/decline)
  respondToFriendRequest: async (
    friendshipId: number, 
    action: 'accept' | 'decline'
  ): Promise<FriendshipResponse> => {
    const response = await apiClient.put(`/social/friends/${friendshipId}`, { action });
    return response.data;
  },

  // Remove friend
  removeFriend: async (friendId: number): Promise<void> => {
    await apiClient.delete(`/social/friends/${friendId}`);
  },

  // Get friends list
  getFriends: async (): Promise<User[]> => {
    const response = await apiClient.get('/social/friends');
    return response.data.friends;
  },

  // Get pending requests
  getPendingRequests: async (): Promise<PendingRequestsResponse> => {
    const response = await apiClient.get('/social/friends/requests');
    return response.data;
  },

  // Search users
  searchUsers: async (params: UserSearchParams): Promise<UserSearchResponse> => {
    const response = await apiClient.get('/social/users/search', { params });
    return response.data;
  },

  // Get friendship status with user
  getFriendshipStatus: async (userId: number): Promise<{ 
    status: string; 
    friendship_id?: number; 
  }> => {
    const response = await apiClient.get(`/social/friends/${userId}/status`);
    return response.data;
  },
};

// React Query hooks

/**
 * Hook to send a friend request
 */
export const useSendFriendRequest = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: socialApi.sendFriendRequest,
    onSuccess: () => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: socialKeys.requests() });
      queryClient.invalidateQueries({ queryKey: socialKeys.all });
    },
  });
};

/**
 * Hook to respond to friend request (accept/decline)
 */
export const useRespondToFriendRequest = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ 
      friendshipId, 
      action 
    }: { 
      friendshipId: number; 
      action: 'accept' | 'decline'; 
    }) => socialApi.respondToFriendRequest(friendshipId, action),
    onSuccess: () => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: socialKeys.friends() });
      queryClient.invalidateQueries({ queryKey: socialKeys.requests() });
    },
  });
};

/**
 * Hook to remove a friend
 */
export const useRemoveFriend = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: socialApi.removeFriend,
    onSuccess: () => {
      // Invalidate friends list
      queryClient.invalidateQueries({ queryKey: socialKeys.friends() });
    },
  });
};

/**
 * Hook to get friends list
 */
export const useFriends = () => {
  return useQuery({
    queryKey: socialKeys.friends(),
    queryFn: socialApi.getFriends,
  });
};

/**
 * Hook to get pending friend requests
 */
export const usePendingRequests = () => {
  return useQuery({
    queryKey: socialKeys.requests(),
    queryFn: socialApi.getPendingRequests,
  });
};

/**
 * Hook to search users with friendship status
 */
export const useUserSearch = (params: UserSearchParams) => {
  return useQuery({
    queryKey: socialKeys.search(params),
    queryFn: () => socialApi.searchUsers(params),
    enabled: !!params.query, // Only run when there's a search query
    staleTime: 30000, // 30 seconds
  });
};

/**
 * Hook to get friendship status with a specific user
 */
export const useFriendshipStatus = (userId: number) => {
  return useQuery({
    queryKey: socialKeys.status(userId),
    queryFn: () => socialApi.getFriendshipStatus(userId),
    enabled: !!userId, // Only run when userId is provided
  });
};