/**
 * FriendsPage - Main page for managing friends and friend requests
 */

import React, { useState } from 'react';
import { 
  useFriends, 
  usePendingRequests, 
  useRemoveFriend 
} from '../../services/socialService';
import { UserSearch } from '../../components/social/UserSearch';
import { UserCard } from '../../components/social/UserCard';
import { FriendRequestCard } from '../../components/social/FriendRequestCard';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Alert } from '../../components/ui/Alert';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';

type TabType = 'friends' | 'requests' | 'search';

export const FriendsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('friends');

  const {
    data: friends,
    isLoading: friendsLoading,
    error: friendsError,
  } = useFriends();

  const {
    data: pendingRequests,
    isLoading: requestsLoading,
    error: requestsError,
  } = usePendingRequests();

  const removeFriendMutation = useRemoveFriend();

  const handleRemoveFriend = async (friendId: number) => {
    if (window.confirm('Are you sure you want to remove this friend?')) {
      try {
        await removeFriendMutation.mutateAsync(friendId);
      } catch (error) {
        console.error('Failed to remove friend:', error);
      }
    }
  };

  const renderTabButton = (tab: TabType, label: string, badge?: number) => (
    <Button
      key={tab}
      variant={activeTab === tab ? 'primary' : 'outline'}
      onClick={() => setActiveTab(tab)}
      className="relative"
    >
      {label}
      {badge !== undefined && badge > 0 && (
        <span className="ml-2 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-red-100 bg-red-600 rounded-full">
          {badge}
        </span>
      )}
    </Button>
  );

  const receivedRequestsCount = pendingRequests?.received_requests.length || 0;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Friends</h1>
        <p className="text-gray-600">
          Manage your friends and connect with other users
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="mb-6">
        <div className="flex space-x-2">
          {renderTabButton('friends', 'My Friends')}
          {renderTabButton('requests', 'Friend Requests', receivedRequestsCount)}
          {renderTabButton('search', 'Find Users')}
        </div>
      </div>

      {/* Error Alerts */}
      {friendsError && (
        <Alert variant="error" className="mb-6">
          Failed to load friends. Please refresh the page.
        </Alert>
      )}

      {requestsError && (
        <Alert variant="error" className="mb-6">
          Failed to load friend requests. Please refresh the page.
        </Alert>
      )}

      {removeFriendMutation.error && (
        <Alert variant="error" className="mb-6">
          Failed to remove friend. Please try again.
        </Alert>
      )}

      {/* Tab Content */}
      <div className="space-y-6">
        {/* Friends Tab */}
        {activeTab === 'friends' && (
          <Card className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              My Friends ({friends?.length || 0})
            </h2>
            
            {friendsLoading ? (
              <div className="flex justify-center py-8">
                <LoadingSpinner size="lg" />
              </div>
            ) : friends && friends.length > 0 ? (
              <div className="space-y-3">
                {friends.map((friend) => (
                  <UserCard
                    key={friend.id}
                    user={{
                      ...friend,
                      friendship_status: 'friends',
                    }}
                    onRemoveFriend={handleRemoveFriend}
                    isLoading={removeFriendMutation.isPending}
                    showActions={true}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-600 mb-4">
                  You don't have any friends yet
                </p>
                <Button
                  onClick={() => setActiveTab('search')}
                  className="mx-auto"
                >
                  Find Users to Add
                </Button>
              </div>
            )}
          </Card>
        )}

        {/* Friend Requests Tab */}
        {activeTab === 'requests' && (
          <div className="space-y-6">
            {requestsLoading ? (
              <div className="flex justify-center py-8">
                <LoadingSpinner size="lg" />
              </div>
            ) : (
              <>
                {/* Received Requests */}
                <Card className="p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">
                    Received Requests ({pendingRequests?.received_requests.length || 0})
                  </h2>
                  
                  {pendingRequests?.received_requests.length ? (
                    <div className="space-y-3">
                      {pendingRequests.received_requests.map((request) => (
                        <FriendRequestCard
                          key={request.id}
                          friendship={request}
                          type="received"
                        />
                      ))}
                    </div>
                  ) : (
                    <p className="text-center text-gray-600 py-4">
                      No pending friend requests
                    </p>
                  )}
                </Card>

                {/* Sent Requests */}
                <Card className="p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">
                    Sent Requests ({pendingRequests?.sent_requests.length || 0})
                  </h2>
                  
                  {pendingRequests?.sent_requests.length ? (
                    <div className="space-y-3">
                      {pendingRequests.sent_requests.map((request) => (
                        <FriendRequestCard
                          key={request.id}
                          friendship={request}
                          type="sent"
                        />
                      ))}
                    </div>
                  ) : (
                    <p className="text-center text-gray-600 py-4">
                      No sent friend requests
                    </p>
                  )}
                </Card>
              </>
            )}
          </div>
        )}

        {/* Search Tab */}
        {activeTab === 'search' && (
          <UserSearch />
        )}
      </div>
    </div>
  );
};