import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useMyReviews, useDeleteReview, useUpdateReview } from '../../services/reviewService';
import { ReviewCard } from '../../components/reviews/ReviewCard';
import { ReviewForm } from '../../components/reviews/ReviewForm';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { Spinner } from '../../components/ui/Spinner';
import type { ReviewUpdate } from '../../types/api';
import { FaSteam, FaPlaystation, FaXbox, FaSync } from 'react-icons/fa';
import { oauthService } from '../../services/oauthService';

export const ProfilePage = () => {
  const { user } = useAuth();
  const [page, setPage] = useState(1);
  const [editingReviewId, setEditingReviewId] = useState<number | null>(null);
  const [linkedAccounts, setLinkedAccounts] = useState<any[]>([]);
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncingPlatform, setSyncingPlatform] = useState<string | null>(null);

  const { data, isLoading, error } = useMyReviews(page, 10);
  const deleteReview = useDeleteReview();
  const updateReview = useUpdateReview();

  useEffect(() => {
    loadLinkedAccounts();
    
    const handleOAuthComplete = () => {
      loadLinkedAccounts();
    };
    
    window.addEventListener('oauth-complete', handleOAuthComplete);
    return () => window.removeEventListener('oauth-complete', handleOAuthComplete);
  }, []);

  const loadLinkedAccounts = async () => {
    try {
      const accounts = await oauthService.getLinkedAccounts();
      setLinkedAccounts(accounts);
    } catch (err) {
      console.error('Failed to load linked accounts:', err);
    }
  };

  const handleLinkAccount = async (platform: string) => {
    try {
      await oauthService.linkAccount(platform);
    } catch (err) {
      console.error('Failed to link account:', err);
    }
  };

  const handleUnlinkAccount = async (platform: string) => {
    if (!window.confirm(`Are you sure you want to unlink your ${platform} account?`)) {
      return;
    }
    
    try {
      await oauthService.unlinkAccount(platform);
      await loadLinkedAccounts();
    } catch (err) {
      console.error('Failed to unlink account:', err);
    }
  };

  const handleSyncLibrary = async (platform?: string) => {
    setIsSyncing(true);
    setSyncingPlatform(platform || 'all');
    
    try {
      // Start sync job
      const response = await oauthService.syncLibrary(platform);
      const jobId = response.job_id;
      
      // Poll for job status
      const pollInterval = setInterval(async () => {
        try {
          const status = await oauthService.getSyncJobStatus(jobId);
          
          if (status.status === 'completed') {
            clearInterval(pollInterval);
            setIsSyncing(false);
            setSyncingPlatform(null);
            alert(`Successfully synced ${status.synced_games} games from ${platform || 'all platforms'}!`);
          } else if (status.status === 'failed') {
            clearInterval(pollInterval);
            setIsSyncing(false);
            setSyncingPlatform(null);
            alert(`Sync failed: ${status.error || 'Unknown error'}`);
          }
          // Keep polling if status is 'pending' or 'running'
        } catch (pollError) {
          console.error('Failed to check sync status:', pollError);
        }
      }, 2000); // Poll every 2 seconds
      
      // Set timeout to stop polling after 5 minutes
      setTimeout(() => {
        clearInterval(pollInterval);
        if (isSyncing) {
          setIsSyncing(false);
          setSyncingPlatform(null);
          alert('Sync is taking longer than expected. Check back later for results.');
        }
      }, 300000); // 5 minutes
      
    } catch (err) {
      console.error('Failed to start sync:', err);
      alert(`Failed to start sync: ${err instanceof Error ? err.message : 'Unknown error'}`);
      setIsSyncing(false);
      setSyncingPlatform(null);
    }
  };

  const handleDelete = async (reviewId: number) => {
    if (window.confirm('Are you sure you want to delete this review?')) {
      await deleteReview.mutateAsync(reviewId);
    }
  };

  const handleUpdate = async (reviewId: number, data: ReviewUpdate) => {
    await updateReview.mutateAsync({ id: reviewId, data });
    setEditingReviewId(null);
  };

  if (!user) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-yellow-50 text-yellow-600 p-4 rounded-lg">
          Please log in to view your profile.
        </div>
      </div>
    );
  }

  const editingReview = editingReviewId
    ? data?.reviews.find((r) => r.id === editingReviewId)
    : null;

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Profile Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="flex items-center gap-4">
          {user.avatar_url ? (
            <img
              src={user.avatar_url}
              alt={user.username}
              className="w-20 h-20 rounded-full"
            />
          ) : (
            <div className="w-20 h-20 rounded-full bg-primary-600 flex items-center justify-center text-white text-3xl font-bold">
              {user.username.charAt(0).toUpperCase()}
            </div>
          )}
          <div>
            <h1 className="text-3xl font-bold">{user.username}</h1>
            <p className="text-gray-600">{user.email}</p>
            {user.bio && <p className="text-gray-700 mt-2">{user.bio}</p>}
          </div>
        </div>

        {data && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="flex gap-8">
              <div>
                <p className="text-2xl font-bold">{data.total}</p>
                <p className="text-gray-600">Reviews</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Linked Gaming Accounts */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-2xl font-bold mb-4">Gaming Accounts</h2>
        <p className="text-gray-600 mb-6">
          Link your gaming accounts to automatically import your game library and playtime.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {/* Steam */}
          {(() => {
            const account = linkedAccounts.find((a) => a.platform === 'STEAM');
            return (
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center gap-3 mb-3">
                  <FaSteam className="text-3xl text-blue-600" />
                  <div>
                    <h3 className="font-semibold">Steam</h3>
                    {account && (
                      <p className="text-sm text-gray-600">{account.platform_username}</p>
                    )}
                  </div>
                </div>
                {account ? (
                  <div className="space-y-2">
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => handleSyncLibrary('steam')}
                      disabled={isSyncing}
                      className="w-full"
                    >
                      {isSyncing && syncingPlatform === 'steam' ? (
                        <><Spinner size="sm" /> Syncing...</>
                      ) : (
                        <><FaSync /> Sync Library</>
                      )}
                    </Button>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handleUnlinkAccount('steam')}
                      className="w-full"
                    >
                      Unlink
                    </Button>
                  </div>
                ) : (
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => handleLinkAccount('steam')}
                    className="w-full"
                  >
                    Link Account
                  </Button>
                )}
              </div>
            );
          })()}

          {/* PlayStation */}
          {(() => {
            const account = linkedAccounts.find((a) => a.platform === 'PLAYSTATION');
            return (
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center gap-3 mb-3">
                  <FaPlaystation className="text-3xl text-blue-800" />
                  <div>
                    <h3 className="font-semibold">PlayStation</h3>
                    {account && (
                      <p className="text-sm text-gray-600">{account.platform_username}</p>
                    )}
                  </div>
                </div>
                {account ? (
                  <div className="space-y-2">
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => handleSyncLibrary('playstation')}
                      disabled={isSyncing}
                      className="w-full"
                    >
                      {isSyncing && syncingPlatform === 'playstation' ? (
                        <><Spinner size="sm" /> Syncing...</>
                      ) : (
                        <><FaSync /> Sync Library</>
                      )}
                    </Button>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handleUnlinkAccount('playstation')}
                      className="w-full"
                    >
                      Unlink
                    </Button>
                  </div>
                ) : (
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => handleLinkAccount('playstation')}
                    className="w-full"
                  >
                    Link Account
                  </Button>
                )}
              </div>
            );
          })()}

          {/* Xbox */}
          {(() => {
            const account = linkedAccounts.find((a) => a.platform === 'XBOX');
            return (
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center gap-3 mb-3">
                  <FaXbox className="text-3xl text-green-600" />
                  <div>
                    <h3 className="font-semibold">Xbox</h3>
                    {account && (
                      <p className="text-sm text-gray-600">{account.platform_username}</p>
                    )}
                  </div>
                </div>
                {account ? (
                  <div className="space-y-2">
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => handleSyncLibrary('xbox')}
                      disabled={isSyncing}
                      className="w-full"
                    >
                      {isSyncing && syncingPlatform === 'xbox' ? (
                        <><Spinner size="sm" /> Syncing...</>
                      ) : (
                        <><FaSync /> Sync Library</>
                      )}
                    </Button>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handleUnlinkAccount('xbox')}
                      className="w-full"
                    >
                      Unlink
                    </Button>
                  </div>
                ) : (
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => handleLinkAccount('xbox')}
                    className="w-full"
                  >
                    Link Account
                  </Button>
                )}
              </div>
            );
          })()}
        </div>

        {linkedAccounts.length > 0 && (
          <div className="text-center">
            <Button
              variant="secondary"
              onClick={() => handleSyncLibrary()}
              disabled={isSyncing}
            >
              {isSyncing && syncingPlatform === 'all' ? (
                <><Spinner size="sm" /> Syncing All Platforms...</>
              ) : (
                <><FaSync /> Sync All Platforms</>
              )}
            </Button>
          </div>
        )}
      </div>

      {/* Edit Review Form */}
      {editingReview && (
        <Card className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Edit Review</h2>
          <ReviewForm
            initialData={{
              rating: editingReview.rating,
              title: editingReview.title,
              content: editingReview.content,
              playtime_hours: editingReview.playtime_hours,
              platform: editingReview.platform,
              is_recommended: editingReview.is_recommended,
            }}
            gameId={editingReview.game_id}
            onSubmit={(data) => handleUpdate(editingReview.id, data as ReviewUpdate)}
            onCancel={() => setEditingReviewId(null)}
            isEditing={true}
          />
        </Card>
      )}

      {/* Reviews Section */}
      <div>
        <h2 className="text-2xl font-bold mb-6">My Reviews</h2>

        {isLoading && (
          <div className="flex justify-center py-8">
            <Spinner size="lg" />
          </div>
        )}

        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-lg">
            Failed to load reviews
          </div>
        )}

        {data && data.reviews.length > 0 ? (
          <>
            <div className="space-y-4 mb-6">
              {data.reviews.map((review) =>
                editingReviewId === review.id ? null : (
                  <ReviewCard
                    key={review.id}
                    review={review}
                    showGameInfo={true}
                    onEdit={() => setEditingReviewId(review.id)}
                    onDelete={() => handleDelete(review.id)}
                  />
                )
              )}
            </div>

            {/* Pagination */}
            {data.total_pages > 1 && (
              <div className="flex justify-center gap-2">
                <Button
                  variant="secondary"
                  onClick={() => setPage((p) => p - 1)}
                  disabled={page <= 1}
                >
                  Previous
                </Button>
                <span className="flex items-center px-4">
                  Page {page} of {data.total_pages}
                </span>
                <Button
                  variant="secondary"
                  onClick={() => setPage((p) => p + 1)}
                  disabled={page >= data.total_pages}
                >
                  Next
                </Button>
              </div>
            )}
          </>
        ) : (
          !isLoading && (
            <Card variant="bordered">
              <p className="text-center text-gray-600 py-8">
                You haven't written any reviews yet.
              </p>
            </Card>
          )
        )}
      </div>
    </div>
  );
};
