/**
 * UserSearch component for searching and finding users to add as friends
 */

import React, { useState, useCallback } from 'react';
import { useUserSearch, useSendFriendRequest } from '../../services/socialService';
import { UserCard } from './UserCard';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { Alert } from '../ui/Alert';

interface UserSearchProps {
  onUserSelect?: (userId: number) => void;
  className?: string;
}

export const UserSearch: React.FC<UserSearchProps> = ({
  onUserSelect,
  className = '',
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');

  // Debounce search input
  const debouncedSearch = useCallback(
    (() => {
      let timeoutId: NodeJS.Timeout;
      return (query: string) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
          setDebouncedQuery(query);
        }, 300);
      };
    })(),
    []
  );

  React.useEffect(() => {
    debouncedSearch(searchQuery);
  }, [searchQuery, debouncedSearch]);

  const {
    data: searchResults,
    isLoading,
    error,
    refetch
  } = useUserSearch({
    query: debouncedQuery,
    limit: 10,
  });

  const sendFriendRequestMutation = useSendFriendRequest();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (debouncedQuery.trim()) {
      refetch();
    }
  };

  const handleSendFriendRequest = async (userId: number) => {
    try {
      await sendFriendRequestMutation.mutateAsync({
        addressee_id: userId,
      });
    } catch (error) {
      console.error('Failed to send friend request:', error);
    }
  };

  const clearSearch = () => {
    setSearchQuery('');
    setDebouncedQuery('');
  };

  return (
    <Card className={`p-6 ${className}`}>
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Search Users
          </h3>
          <form onSubmit={handleSearch} className="flex gap-2">
            <Input
              type="text"
              placeholder="Search by username..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1"
            />
            <Button
              type="submit"
              disabled={!searchQuery.trim() || isLoading}
              className="px-4"
            >
              {isLoading ? 'Searching...' : 'Search'}
            </Button>
            {searchQuery && (
              <Button
                type="button"
                variant="outline"
                onClick={clearSearch}
                className="px-3"
              >
                Clear
              </Button>
            )}
          </form>
        </div>

        {error && (
          <Alert variant="error">
            Failed to search users. Please try again.
          </Alert>
        )}

        {sendFriendRequestMutation.error && (
          <Alert variant="error">
            Failed to send friend request. Please try again.
          </Alert>
        )}

        {sendFriendRequestMutation.isSuccess && (
          <Alert variant="success">
            Friend request sent successfully!
          </Alert>
        )}

        {searchResults && searchResults.users.length > 0 && (
          <div className="space-y-3">
            <h4 className="font-medium text-gray-900">
              Found {searchResults.total} user{searchResults.total !== 1 ? 's' : ''}
            </h4>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {searchResults.users.map((user) => (
                <UserCard
                  key={user.id}
                  user={user}
                  onSendFriendRequest={handleSendFriendRequest}
                  onUserClick={onUserSelect}
                  isLoading={sendFriendRequestMutation.isPending}
                />
              ))}
            </div>
            
            {searchResults.total_pages > 1 && (
              <div className="text-center pt-2">
                <p className="text-sm text-gray-600">
                  Showing page {searchResults.page} of {searchResults.total_pages}
                </p>
                {/* TODO: Add pagination controls if needed */}
              </div>
            )}
          </div>
        )}

        {searchResults && searchResults.users.length === 0 && debouncedQuery && (
          <div className="text-center py-8">
            <p className="text-gray-600">
              No users found matching "{debouncedQuery}"
            </p>
            <p className="text-sm text-gray-500 mt-1">
              Try searching with a different username
            </p>
          </div>
        )}

        {!debouncedQuery && (
          <div className="text-center py-8">
            <p className="text-gray-600">
              Enter a username to search for users
            </p>
          </div>
        )}
      </div>
    </Card>
  );
};