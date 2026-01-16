import { useState, useEffect } from 'react';
import { oauthService, LinkedAccount } from '../services/oauthService';
import { FaSteam, FaPlaystation, FaXbox } from 'react-icons/fa';

interface PlatformConfig {
  name: string;
  icon: JSX.Element;
  color: string;
  bgColor: string;
}

const PLATFORMS: Record<string, PlatformConfig> = {
  steam: {
    name: 'Steam',
    icon: <FaSteam className="text-2xl" />,
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10 hover:bg-blue-500/20'
  },
  playstation: {
    name: 'PlayStation',
    icon: <FaPlaystation className="text-2xl" />,
    color: 'text-blue-600',
    bgColor: 'bg-blue-600/10 hover:bg-blue-600/20'
  },
  xbox: {
    name: 'Xbox',
    icon: <FaXbox className="text-2xl" />,
    color: 'text-green-500',
    bgColor: 'bg-green-500/10 hover:bg-green-500/20'
  }
};

export default function LinkedAccountsPage() {
  const [linkedAccounts, setLinkedAccounts] = useState<LinkedAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [unlinking, setUnlinking] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [syncStatus, setSyncStatus] = useState<string | null>(null);

  useEffect(() => {
    loadLinkedAccounts();

    // Listen for OAuth completion events
    const handleOAuthComplete = () => {
      loadLinkedAccounts();
      setSyncStatus('Account linked successfully! Syncing library...');
      handleSyncAll();
    };

    window.addEventListener('oauth-complete', handleOAuthComplete as EventListener);

    return () => {
      window.removeEventListener('oauth-complete', handleOAuthComplete as EventListener);
    };
  }, []);

  const loadLinkedAccounts = async () => {
    try {
      setLoading(true);
      setError(null);
      const accounts = await oauthService.getLinkedAccounts();
      setLinkedAccounts(accounts);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load linked accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleLinkAccount = async (platform: 'steam' | 'playstation' | 'xbox') => {
    try {
      setError(null);
      await oauthService.linkAccount(platform);
    } catch (err: any) {
      setError(err.response?.data?.detail || `Failed to link ${platform} account`);
    }
  };

  const handleUnlinkAccount = async (platform: 'steam' | 'playstation' | 'xbox') => {
    if (!confirm(`Are you sure you want to unlink your ${platform} account? This will remove all imported games.`)) {
      return;
    }

    try {
      setUnlinking(platform);
      setError(null);
      await oauthService.unlinkAccount(platform);
      await loadLinkedAccounts();
      setSyncStatus(`${platform} account unlinked successfully`);
    } catch (err: any) {
      setError(err.response?.data?.detail || `Failed to unlink ${platform} account`);
    } finally {
      setUnlinking(null);
    }
  };

  const handleSyncAccount = async (platform: 'steam' | 'playstation' | 'xbox') => {
    try {
      setSyncing(true);
      setError(null);
      setSyncStatus(`Syncing ${platform} library...`);
      
      const result = await oauthService.syncLibrary(platform);
      
      setSyncStatus(
        `Synced ${result.total_games} games from ${platform} ` +
        `(${result.new_games} new, ${result.updated_games} updated)`
      );

      if (result.errors.length > 0) {
        setError(`Sync completed with errors: ${result.errors.join(', ')}`);
      }

      await loadLinkedAccounts();
    } catch (err: any) {
      setError(err.response?.data?.detail || `Failed to sync ${platform} library`);
      setSyncStatus(null);
    } finally {
      setSyncing(false);
    }
  };

  const handleSyncAll = async () => {
    try {
      setSyncing(true);
      setError(null);
      setSyncStatus('Syncing all platforms...');
      
      const result = await oauthService.syncLibrary();
      
      setSyncStatus(
        `Synced ${result.total_games} games from ${result.synced_platforms.join(', ')} ` +
        `(${result.new_games} new, ${result.updated_games} updated)`
      );

      if (result.errors.length > 0) {
        setError(`Sync completed with errors: ${result.errors.join(', ')}`);
      }

      await loadLinkedAccounts();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to sync libraries');
      setSyncStatus(null);
    } finally {
      setSyncing(false);
    }
  };

  const isLinked = (platform: string) => {
    return linkedAccounts.some(acc => acc.platform === platform);
  };

  const getLinkedAccount = (platform: string) => {
    return linkedAccounts.find(acc => acc.platform === platform);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Linked Gaming Accounts
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Connect your gaming platforms to import your library and track playtime
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}

      {syncStatus && (
        <div className="mb-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
          <p className="text-green-800 dark:text-green-200">{syncStatus}</p>
        </div>
      )}

      {linkedAccounts.length > 0 && (
        <div className="mb-6 flex justify-end">
          <button
            onClick={handleSyncAll}
            disabled={syncing}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {syncing ? 'Syncing...' : 'Sync All Platforms'}
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {Object.entries(PLATFORMS).map(([platformKey, config]) => {
          const linked = isLinked(platformKey);
          const account = getLinkedAccount(platformKey);

          return (
            <div
              key={platformKey}
              className={`${config.bgColor} border border-gray-200 dark:border-gray-700 rounded-lg p-6 transition-colors`}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className={config.color}>{config.icon}</div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {config.name}
                  </h3>
                </div>
                {linked && (
                  <span className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 text-xs font-medium rounded">
                    Connected
                  </span>
                )}
              </div>

              {linked && account ? (
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                      Username
                    </p>
                    <p className="text-gray-900 dark:text-white font-medium">
                      {account.platform_username}
                    </p>
                  </div>

                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                      Connected
                    </p>
                    <p className="text-gray-900 dark:text-white text-sm">
                      {new Date(account.connected_at).toLocaleDateString()}
                    </p>
                  </div>

                  {account.last_synced_at && (
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                        Last Synced
                      </p>
                      <p className="text-gray-900 dark:text-white text-sm">
                        {new Date(account.last_synced_at).toLocaleDateString()}
                      </p>
                    </div>
                  )}

                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleSyncAccount(platformKey as any)}
                      disabled={syncing}
                      className="flex-1 px-3 py-2 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700 disabled:opacity-50"
                    >
                      Sync
                    </button>
                    <button
                      onClick={() => handleUnlinkAccount(platformKey as any)}
                      disabled={unlinking === platformKey}
                      className="flex-1 px-3 py-2 bg-red-600 text-white text-sm rounded hover:bg-red-700 disabled:opacity-50"
                    >
                      {unlinking === platformKey ? 'Unlinking...' : 'Unlink'}
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  onClick={() => handleLinkAccount(platformKey as any)}
                  className="w-full px-4 py-2 bg-gray-900 dark:bg-gray-700 text-white rounded-lg hover:bg-gray-800 dark:hover:bg-gray-600 transition-colors"
                >
                  Link {config.name} Account
                </button>
              )}
            </div>
          );
        })}
      </div>

      {linkedAccounts.length > 0 && (
        <div className="mt-8 text-center">
          <a
            href="/library"
            className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 font-medium"
          >
            View Your Game Library →
          </a>
        </div>
      )}
    </div>
  );
}
