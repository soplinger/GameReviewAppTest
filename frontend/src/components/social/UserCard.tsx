/**
 * UserCard component for displaying user information with friendship actions
 */

import React from 'react';
import { UserWithFriendship } from '../../services/socialService';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { Avatar } from '../ui/Avatar';

interface UserCardProps {
  user: UserWithFriendship;
  onSendFriendRequest?: (userId: number) => void;
  onRemoveFriend?: (userId: number) => void;
  onUserClick?: (userId: number) => void;
  isLoading?: boolean;
  showActions?: boolean;
  className?: string;
}

export const UserCard: React.FC<UserCardProps> = ({
  user,
  onSendFriendRequest,
  onRemoveFriend,
  onUserClick,
  isLoading = false,
  showActions = true,
  className = '',
}) => {
  const getFriendshipStatusDisplay = () => {
    switch (user.friendship_status) {
      case 'friends':
        return {
          text: 'Friends',
          color: 'text-green-600',
          bgColor: 'bg-green-50',
        };
      case 'pending_sent':
        return {
          text: 'Request Sent',
          color: 'text-yellow-600',
          bgColor: 'bg-yellow-50',
        };
      case 'pending_received':
        return {
          text: 'Request Received',
          color: 'text-blue-600',
          bgColor: 'bg-blue-50',
        };
      case 'blocked':
        return {
          text: 'Blocked',
          color: 'text-red-600',
          bgColor: 'bg-red-50',
        };
      default:
        return null;
    }
  };

  const canSendFriendRequest = () => {
    return user.friendship_status === 'none' && onSendFriendRequest;
  };

  const canRemoveFriend = () => {
    return user.friendship_status === 'friends' && onRemoveFriend;
  };

  const handleUserClick = () => {
    if (onUserClick) {
      onUserClick(user.id);
    }
  };

  const handleSendFriendRequest = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onSendFriendRequest) {
      onSendFriendRequest(user.id);
    }
  };

  const handleRemoveFriend = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onRemoveFriend) {
      onRemoveFriend(user.id);
    }
  };

  const statusDisplay = getFriendshipStatusDisplay();

  return (
    <Card 
      className={`p-4 hover:shadow-md transition-shadow ${
        onUserClick ? 'cursor-pointer' : ''
      } ${className}`}
      onClick={handleUserClick}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3 min-w-0 flex-1">
          <Avatar
            src={user.avatar_url}
            alt={user.username}
            size="md"
          />
          
          <div className="min-w-0 flex-1">
            <div className="flex items-center space-x-2">
              <h4 className="font-medium text-gray-900 truncate">
                {user.username}
              </h4>
              {statusDisplay && (
                <span 
                  className={`px-2 py-1 text-xs font-medium rounded-full ${statusDisplay.color} ${statusDisplay.bgColor}`}
                >
                  {statusDisplay.text}
                </span>
              )}
            </div>
            
            {user.bio && (
              <p className="text-sm text-gray-600 truncate mt-1">
                {user.bio}
              </p>
            )}
            
            <p className="text-xs text-gray-500">
              Joined {new Date(user.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        {showActions && (
          <div className="flex items-center space-x-2 ml-3">
            {canSendFriendRequest() && (
              <Button
                size="sm"
                onClick={handleSendFriendRequest}
                disabled={isLoading}
                className="shrink-0"
              >
                {isLoading ? 'Sending...' : 'Add Friend'}
              </Button>
            )}

            {canRemoveFriend() && (
              <Button
                size="sm"
                variant="outline"
                onClick={handleRemoveFriend}
                disabled={isLoading}
                className="shrink-0 text-red-600 border-red-300 hover:bg-red-50"
              >
                {isLoading ? 'Removing...' : 'Remove'}
              </Button>
            )}

            {user.friendship_status === 'pending_sent' && (
              <span className="text-xs text-gray-500 shrink-0">
                Pending...
              </span>
            )}

            {user.friendship_status === 'pending_received' && (
              <span className="text-xs text-blue-600 shrink-0">
                Respond to request
              </span>
            )}
          </div>
        )}
      </div>
    </Card>
  );
};