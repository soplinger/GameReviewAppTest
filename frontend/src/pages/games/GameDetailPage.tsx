import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useGame } from '../../services/gameService';
import { useGameReviews, useCreateReview } from '../../services/reviewService';
import { ReviewCard } from '../../components/reviews/ReviewCard';
import { ReviewForm } from '../../components/reviews/ReviewForm';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { Spinner } from '../../components/ui/Spinner';
import { useAuth } from '../../contexts/AuthContext';
import type { ReviewCreate } from '../../types/api';

export const GameDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const gameId = id ? parseInt(id) : null;
  const { user } = useAuth();
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [reviewPage, setReviewPage] = useState(1);

  const { data: game, isLoading, error } = useGame(gameId);
  const {
    data: reviewsData,
    isLoading: reviewsLoading,
    error: reviewsError,
  } = useGameReviews(gameId, reviewPage);

  const createReview = useCreateReview();

  const handleCreateReview = async (data: ReviewCreate) => {
    await createReview.mutateAsync(data);
    setShowReviewForm(false);
  };

  const formatDate = (date: string | null) => {
    if (!date) return 'TBA';
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error || !game) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 text-red-600 p-4 rounded-lg">
          Game not found or failed to load.
        </div>
      </div>
    );
  }

  const userHasReview = reviewsData?.reviews.some((r) => r.user_id === user?.id);

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Game Header */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
        {/* Cover Image */}
        <div className="md:col-span-1">
          <div className="aspect-[3/4] bg-gray-200 rounded-lg overflow-hidden">
            {game.cover_url ? (
              <img
                src={game.cover_url}
                alt={game.name}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-gray-400">
                No Image
              </div>
            )}
          </div>
        </div>

        {/* Game Info */}
        <div className="md:col-span-2">
          <h1 className="text-4xl font-bold mb-4">{game.name}</h1>

          {/* Ratings */}
          <div className="flex flex-wrap gap-6 mb-6">
            {game.rating && (
              <div>
                <p className="text-sm text-gray-600">Metacritic</p>
                <div className="flex items-center gap-2">
                  <span className="text-2xl font-bold">{game.rating.toFixed(1)}</span>
                  <span className="text-yellow-500">★</span>
                </div>
              </div>
            )}
            {game.user_rating !== undefined && game.user_rating_count && (
              <div>
                <p className="text-sm text-gray-600">User Rating</p>
                <div className="flex items-center gap-2">
                  <span className="text-2xl font-bold">{game.user_rating.toFixed(1)}</span>
                  <span className="text-blue-500">★</span>
                  <span className="text-sm text-gray-500">
                    ({game.user_rating_count} reviews)
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Release Date */}
          <div className="mb-4">
            <span className="text-gray-600">Release Date: </span>
            <span className="font-medium">{formatDate(game.release_date)}</span>
          </div>

          {/* Genres */}
          {game.genres && game.genres.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-6">
              {game.genres.map((genre) => (
                <span
                  key={genre}
                  className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium"
                >
                  {genre}
                </span>
              ))}
            </div>
          )}

          {/* Summary */}
          {game.summary && (
            <div className="mb-6">
              <h2 className="text-xl font-bold mb-2">About</h2>
              <p className="text-gray-700">{game.summary}</p>
            </div>
          )}

          {/* Storyline */}
          {game.storyline && (
            <div className="mb-6">
              <h2 className="text-xl font-bold mb-2">Storyline</h2>
              <p className="text-gray-700">{game.storyline}</p>
            </div>
          )}

          {/* Platforms */}
          {game.platforms && game.platforms.length > 0 && (
            <div className="mb-4">
              <h3 className="font-semibold mb-2">Platforms</h3>
              <div className="flex flex-wrap gap-2">
                {game.platforms.map((platform) => (
                  <span
                    key={platform}
                    className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm"
                  >
                    {platform}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Developers & Publishers */}
          {(game.developers || game.publishers) && (
            <div className="grid grid-cols-2 gap-4 text-sm">
              {game.developers && game.developers.length > 0 && (
                <div>
                  <span className="text-gray-600">Developer: </span>
                  <span className="font-medium">{game.developers.join(', ')}</span>
                </div>
              )}
              {game.publishers && game.publishers.length > 0 && (
                <div>
                  <span className="text-gray-600">Publisher: </span>
                  <span className="font-medium">{game.publishers.join(', ')}</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Screenshots */}
      {game.screenshots && game.screenshots.length > 0 && (
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Screenshots</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {game.screenshots.slice(0, 8).map((screenshot, index) => (
              <div key={index} className="aspect-video bg-gray-200 rounded-lg overflow-hidden">
                <img
                  src={screenshot}
                  alt={`Screenshot ${index + 1}`}
                  className="w-full h-full object-cover"
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Reviews Section */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">Reviews</h2>
          {user && !userHasReview && !showReviewForm && (
            <Button onClick={() => setShowReviewForm(true)}>Write a Review</Button>
          )}
        </div>

        {/* Review Form */}
        {showReviewForm && gameId && (
          <Card className="mb-6">
            <h3 className="text-xl font-bold mb-4">Write Your Review</h3>
            <ReviewForm
              gameId={gameId}
              onSubmit={handleCreateReview}
              onCancel={() => setShowReviewForm(false)}
            />
          </Card>
        )}

        {/* Reviews List */}
        {reviewsLoading && (
          <div className="flex justify-center py-8">
            <Spinner size="lg" />
          </div>
        )}

        {reviewsError && (
          <div className="bg-red-50 text-red-600 p-4 rounded-lg">
            Failed to load reviews
          </div>
        )}

        {reviewsData && reviewsData.reviews.length > 0 ? (
          <>
            <div className="space-y-4 mb-6">
              {reviewsData.reviews.map((review) => (
                <ReviewCard key={review.id} review={review} showGameInfo={false} />
              ))}
            </div>

            {/* Pagination */}
            {reviewsData.total_pages > 1 && (
              <div className="flex justify-center gap-2">
                <Button
                  variant="secondary"
                  onClick={() => setReviewPage((p) => p - 1)}
                  disabled={reviewPage <= 1}
                >
                  Previous
                </Button>
                <span className="flex items-center px-4">
                  Page {reviewPage} of {reviewsData.total_pages}
                </span>
                <Button
                  variant="secondary"
                  onClick={() => setReviewPage((p) => p + 1)}
                  disabled={reviewPage >= reviewsData.total_pages}
                >
                  Next
                </Button>
              </div>
            )}
          </>
        ) : (
          !reviewsLoading && (
            <Card variant="bordered">
              <p className="text-center text-gray-600 py-8">
                No reviews yet. Be the first to review this game!
              </p>
            </Card>
          )
        )}
      </div>
    </div>
  );
};
