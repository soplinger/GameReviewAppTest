/**
 * FeedPage - Social feed showing friend reviews with pagination
 */

import React, { useState } from 'react';
import { useFeed } from '../../services/feedService';
import { FeedCard } from '../../components/feed/FeedCard';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Alert } from '../../components/ui/Alert';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import { useNavigate } from 'react-router-dom';

export const FeedPage: React.FC = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const navigate = useNavigate();
  
  const {
    data: feedData,
    isLoading,
    error,
    refetch
  } = useFeed({
    page: currentPage,
    page_size: 10,
  });

  const handleUserClick = (userId: number) => {
    // TODO: Navigate to user profile when that route exists
    console.log('Navigate to user:', userId);
  };

  const handleGameClick = (gameId: number) => {
    navigate(`/games/${gameId}`);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const renderPagination = () => {
    if (!feedData || feedData.total_pages <= 1) return null;

    const { page, total_pages } = feedData;
    const maxVisiblePages = 5;
    
    let startPage = Math.max(1, page - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(total_pages, startPage + maxVisiblePages - 1);
    
    if (endPage - startPage + 1 < maxVisiblePages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    const pages = [];
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }

    return (
      <div className="flex justify-center items-center space-x-2 mt-8">
        <Button
          variant="outline"
          size="sm"
          onClick={() => handlePageChange(page - 1)}
          disabled={page <= 1}
        >
          Previous
        </Button>
        
        {startPage > 1 && (
          <>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handlePageChange(1)}
            >
              1
            </Button>
            {startPage > 2 && <span className="px-2 text-gray-500">...</span>}
          </>
        )}
        
        {pages.map((pageNum) => (
          <Button
            key={pageNum}
            variant={pageNum === page ? 'primary' : 'outline'}
            size="sm"
            onClick={() => handlePageChange(pageNum)}
          >
            {pageNum}
          </Button>
        ))}
        
        {endPage < total_pages && (
          <>
            {endPage < total_pages - 1 && <span className="px-2 text-gray-500">...</span>}
            <Button
              variant="outline"
              size="sm"
              onClick={() => handlePageChange(total_pages)}
            >
              {total_pages}
            </Button>
          </>
        )}
        
        <Button
          variant="outline"
          size="sm"
          onClick={() => handlePageChange(page + 1)}
          disabled={page >= total_pages}
        >
          Next
        </Button>
      </div>
    );
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Feed</h1>
        <p className="text-gray-600">
          See what your friends are saying about games
        </p>
      </div>

      {/* Error handling */}
      {error && (
        <Alert variant="error" className="mb-6">
          <div>
            <p>Failed to load feed. Please try again.</p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => refetch()}
              className="mt-2"
            >
              Retry
            </Button>
          </div>
        </Alert>
      )}

      {/* Loading state */}
      {isLoading && (
        <div className="flex justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      )}

      {/* Feed content */}
      {feedData && !isLoading && (
        <>
          {feedData.reviews.length > 0 ? (
            <>
              <div className="space-y-6">
                {feedData.reviews.map((review) => (
                  <FeedCard
                    key={review.id}
                    review={review}
                    onUserClick={handleUserClick}
                    onGameClick={handleGameClick}
                  />
                ))}
              </div>
              
              {/* Pagination */}
              {renderPagination()}
              
              {/* Feed stats */}
              <div className="text-center text-sm text-gray-500 mt-8 pt-6 border-t border-gray-200">
                <p>
                  Showing {feedData.reviews.length} of {feedData.total} reviews
                  {feedData.total_pages > 1 && (
                    <span> • Page {feedData.page} of {feedData.total_pages}</span>
                  )}
                </p>
              </div>
            </>
          ) : (
            /* Empty state */
            <Card className="p-12 text-center">
              <div className="space-y-4">
                <div className="w-16 h-16 mx-auto bg-gray-100 rounded-full flex items-center justify-center">
                  <svg 
                    className="w-8 h-8 text-gray-400" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path 
                      strokeLinecap="round" 
                      strokeLinejoin="round" 
                      strokeWidth={2} 
                      d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" 
                    />
                  </svg>
                </div>
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Your feed is empty
                  </h3>
                  <p className="text-gray-600 mb-6">
                    Add friends to see their game reviews here, or check back when your friends post new reviews.
                  </p>
                  <div className="flex justify-center space-x-4">
                    <Button
                      onClick={() => navigate('/friends')}
                      className="flex items-center space-x-2"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                      </svg>
                      <span>Find Friends</span>
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => navigate('/games')}
                      className="flex items-center space-x-2"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                      <span>Browse Games</span>
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  );
};