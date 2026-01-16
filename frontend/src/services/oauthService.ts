import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface LinkedAccount {
  id: number;
  platform: 'steam' | 'playstation' | 'xbox';
  platform_user_id: string;
  platform_username: string;
  connected_at: string;
  last_synced_at: string | null;
}

export interface OAuthInitiateResponse {
  authorization_url: string;
  state: string | null;
}

export interface LibrarySyncResponse {
  synced_platforms: string[];
  total_games: number;
  new_games: number;
  updated_games: number;
  errors: string[];
}

export interface GameLibraryEntry {
  id: number;
  user_id: number;
  game_id: number;
  linked_account_id: number;
  playtime_hours: number;
  achievements_count: number;
  last_played_at: string | null;
  imported_at: string;
  game?: {
    id: number;
    name: string;
    slug: string;
    cover_image_url: string | null;
    release_date: string | null;
    rating: number | null;
  };
}

export interface GameLibraryListResponse {
  items: GameLibraryEntry[];
  total: number;
  skip: number;
  limit: number;
}

class OAuthService {
  /**
   * Initiate OAuth flow for a gaming platform
   */
  async initiateOAuth(platform: 'steam' | 'playstation' | 'xbox'): Promise<OAuthInitiateResponse> {
    const response = await axios.get(`${API_BASE_URL}/oauth/${platform}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    return response.data;
  }

  /**
   * Open OAuth authorization in new window
   */
  openOAuthWindow(authUrl: string, platform: string): void {
    const width = 600;
    const height = 700;
    const left = window.screen.width / 2 - width / 2;
    const top = window.screen.height / 2 - height / 2;

    const authWindow = window.open(
      authUrl,
      `${platform}_oauth`,
      `width=${width},height=${height},left=${left},top=${top},toolbar=no,location=no,status=no,menubar=no`
    );

    // Poll for window closure
    const pollTimer = setInterval(() => {
      if (authWindow?.closed) {
        clearInterval(pollTimer);
        // Refresh linked accounts after OAuth
        window.dispatchEvent(new CustomEvent('oauth-complete', { detail: { platform } }));
      }
    }, 500);
  }

  /**
   * Link a gaming platform account
   */
  async linkAccount(platform: 'steam' | 'playstation' | 'xbox'): Promise<void> {
    const { authorization_url } = await this.initiateOAuth(platform);
    this.openOAuthWindow(authorization_url, platform);
  }

  /**
   * Get all linked accounts for current user
   */
  async getLinkedAccounts(): Promise<LinkedAccount[]> {
    const response = await axios.get(`${API_BASE_URL}/oauth/accounts/me`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    return response.data;
  }

  /**
   * Unlink a gaming platform account
   */
  async unlinkAccount(platform: 'steam' | 'playstation' | 'xbox'): Promise<void> {
    await axios.delete(`${API_BASE_URL}/oauth/accounts/${platform}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`
      }
    });
  }

  /**
   * Sync game library from linked platforms
   */
  async syncLibrary(platform?: 'steam' | 'playstation' | 'xbox'): Promise<LibrarySyncResponse> {
    const params = platform ? { platform } : {};
    const response = await axios.post(
      `${API_BASE_URL}/oauth/library/sync`,
      null,
      {
        params,
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      }
    );
    return response.data;
  }

  /**
   * Get user's game library
   */
  async getGameLibrary(
    skip: number = 0,
    limit: number = 50,
    platform?: 'steam' | 'playstation' | 'xbox'
  ): Promise<GameLibraryListResponse> {
    const params: any = { skip, limit };
    if (platform) {
      params.platform = platform;
    }

    const response = await axios.get(`${API_BASE_URL}/oauth/library/me`, {
      params,
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    return response.data;
  }

  /**
   * Get playtime for a specific game
   */
  async getGamePlaytime(gameId: number): Promise<number> {
    const response = await axios.get(
      `${API_BASE_URL}/oauth/library/games/${gameId}/playtime`,
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      }
    );
    return response.data.playtime_hours;
  }

  /**
   * Get suggested playtime for review (from review endpoint)
   */
  async getSuggestedPlaytime(gameId: number): Promise<number | null> {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/reviews/games/${gameId}/suggested-playtime`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      );
      return response.data.suggested_playtime_hours;
    } catch (error) {
      // Return null if no playtime available
      return null;
    }
  }
}

export const oauthService = new OAuthService();
