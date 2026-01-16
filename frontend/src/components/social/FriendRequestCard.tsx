/**
 * FriendRequestCard component for displaying friend requests with accept/decline actions
 */

import React from 'react';
import { FriendshipResponse, useRespondToFriendRequest } from '../../services/socialService';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { Avatar } from '../ui/Avatar';
import { Alert } from '../ui/Alert';

interface FriendRequestCardProps {
  friendship: FriendshipResponse;
  type: 'sent' | 'received';
  className?: string;
}

export const FriendRequestCard: React.FC<FriendRequestCardProps> = ({
  friendship,
  type,
  className = '',
}) => {
  const respondToRequestMutation = useRespondToFriendRequest();

  const displayUser = type === 'received' ? friendship.requester : friendship.addressee;

  const handleAccept = async () => {
    try {
      await respondToRequestMutation.mutateAsync({
        friendshipId: friendship.id,
        action: 'accept',
      });
    } catch (error) {
      console.error('Failed to accept friend request:', error);
    }
  };

  const handleDecline = async () => {
    try {
      await respondToRequestMutation.mutateAsync({
        friendshipId: friendship.id,
        action: 'decline',
      });
    } catch (error) {
      console.error('Failed to decline friend request:', error);
    }
  };

  const getStatusDisplay = () => {
    if (type === 'sent') {
      switch (friendship.status) {
        case 'pending':
          return {
            text: 'Pending',
            color: 'text-yellow-600',
            bgColor: 'bg-yellow-50',
          };
        case 'accepted':
          return {
            text: 'Accepted',
            color: 'text-green-600',
            bgColor: 'bg-green-50',
          };
        case 'declined':
          return {
            text: 'Declined',
            color: 'text-red-600',
            bgColor: 'bg-red-50',
          };
        default:
          return null;
      }
    }
    return null;
  };

  const statusDisplay = getStatusDisplay();
  const canRespond = type === 'received' && friendship.status === 'pending';
  const isLoading = respondToRequestMutation.isPending;

  return (
    <Card className={`p-4 ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3 min-w-0 flex-1">
          <Avatar
            src={displayUser.avatar_url}
            alt={displayUser.username}
            size="md"
          />
          
          <div className="min-w-0 flex-1">
            <div className="flex items-center space-x-2">
              <h4 className="font-medium text-gray-900 truncate">
                {displayUser.username}
              </h4>
              {statusDisplay && (
                <span 
                  className={`px-2 py-1 text-xs font-medium rounded-full ${statusDisplay.color} ${statusDisplay.bgColor}`}
                >
                  {statusDisplay.text}
                </span>
              )}
            </div>
            
            {displayUser.bio && (
              <p className="text-sm text-gray-600 truncate mt-1">
                {displayUser.bio}
              </p>
            )}
            
            <p className="text-xs text-gray-500">
              {type === 'received' 
                ? `Sent request ${new Date(friendship.created_at).toLocaleDateString()}`
                : `Request sent ${new Date(friendship.created_at).toLocaleDateString()}`
              }
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 ml-3">
          {canRespond && (
            <>
              <Button
                size="sm"
                onClick={handleAccept}
                disabled={isLoading}
                className="shrink-0 bg-green-600 hover:bg-green-700"
              >
                {isLoading ? 'Accepting...' : 'Accept'}
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={handleDecline}
                disabled={isLoading}
                className="shrink-0 text-red-600 border-red-300 hover:bg-red-50"
              >
                {isLoading ? 'Declining...' : 'Decline'}
              </Button>
            </>
          )}
          
          {type === 'sent' && friendship.status === 'pending' && (
            <span className="text-xs text-gray-500 shrink-0">
              Waiting for response...
            </span>
          )}
        </div>
      </div>

      {respondToRequestMutation.error && (
        <Alert variant="error" className="mt-3">
          Failed to respond to friend request. Please try again.
        </Alert>
      )}
    </Card>
  );
};