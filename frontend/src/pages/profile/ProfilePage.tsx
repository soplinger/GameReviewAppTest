import { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useMyReviews, useDeleteReview, useUpdateReview } from '../../services/reviewService';
import { ReviewCard } from '../../components/reviews/ReviewCard';
import { ReviewForm } from '../../components/reviews/ReviewForm';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { Spinner } from '../../components/ui/Spinner';
import type { ReviewUpdate } from '../../types/api';

export const ProfilePage = () => {
  const { user } = useAuth();
  const [page, setPage] = useState(1);
  const [editingReviewId, setEditingReviewId] = useState<number | null>(null);

  const { data, isLoading, error } = useMyReviews(page, 10);
  const deleteReview = useDeleteReview();
  const updateReview = useUpdateReview();

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
