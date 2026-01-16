/**
 * TypeScript types for API requests and responses
 */

/**
 * User types
 */
export interface User {
  id: number;
  username: string;
  email: string;
  bio?: string;
  avatar_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_login?: string;
}

export interface UserRegister {
  username: string;
  email: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserUpdate {
  username?: string;
  email?: string;
  bio?: string;
  avatar_url?: string;
  password?: string;
}

/**
 * Game types
 */
export interface Game {
  id: number;
  igdb_id?: number;
  rawg_id?: number;
  name: string;
  slug: string;
  summary?: string;
  storyline?: string;
  cover_url?: string;
  screenshots?: string[];
  artworks?: string[];
  videos?: string[];
  release_date?: string;
  rating?: number;
  rating_count?: number;
  metacritic_score?: number;
  platforms?: string[];
  genres?: string[];
  themes?: string[];
  game_modes?: string[];
  developers?: string[];
  publishers?: string[];
  websites?: string[];
  similar_games?: number[];
  last_synced_at: string;
  created_at: string;
  updated_at: string;
}

/**
 * Review types
 */
export interface Review {
  id: number;
  user_id: number;
  game_id: number;
  rating: number;
  title: string;
  content: string;
  playtime_hours?: number;
  platform?: string;
  is_recommended: boolean;
  helpful_count: number;
  created_at: string;
  updated_at: string;
  // Populated fields
  user?: User;
  game?: Game;
}

export interface ReviewCreate {
  game_id: number;
  rating: number;
  title: string;
  content: string;
  playtime_hours?: number;
  platform?: string;
  is_recommended: boolean;
}

export interface ReviewUpdate {
  rating?: number;
  title?: string;
  content?: string;
  playtime_hours?: number;
  platform?: string;
  is_recommended?: boolean;
}

/**
 * Friendship/Social types
 */
export interface Friendship {
  id: number;
  requester_id: number;
  addressee_id: number;
  status: 'pending' | 'accepted' | 'rejected' | 'blocked';
  created_at: string;
  updated_at: string;
  // Populated fields
  requester?: User;
  addressee?: User;
}

/**
 * Linked Account types
 */
export interface LinkedAccount {
  id: number;
  user_id: number;
  platform: 'steam' | 'psn' | 'xbox';
  platform_user_id: string;
  platform_username: string;
  linked_at: string;
}

/**
 * Feed types
 */
export interface FeedItem {
  id: string;
  type: 'review' | 'friendship' | 'game_release';
  created_at: string;
  data: Review | Friendship | Game;
}

/**
 * Pagination types
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/**
 * Error types
 */
export interface APIErrorResponse {
  detail: string;
  status_code?: number;
  errors?: Record<string, string[]>;
}
