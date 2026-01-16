/**
 * GameSyncPanel - Admin panel for syncing games from IGDB
 */

import React, { useState } from 'react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { LoadingSpinner } from '../ui/LoadingSpinner';

interface GameSyncPanelProps {
  onSyncPopular: (limit: number) => void;
  onSyncBySearch: (query: string, limit: number) => void;
  onSyncByGenre: (genre: string, limit: number) => void;
  onSyncRecent: (limit: number, daysBack: number) => void;
  isLoading: boolean;
}

export const GameSyncPanel: React.FC<GameSyncPanelProps> = ({
  onSyncPopular,
  onSyncBySearch,
  onSyncByGenre,
  onSyncRecent,
  isLoading,
}) => {
  const [popularLimit, setPopularLimit] = useState(20);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchLimit, setSearchLimit] = useState(10);
  const [genre, setGenre] = useState('');
  const [genreLimit, setGenreLimit] = useState(15);
  const [recentLimit, setRecentLimit] = useState(25);
  const [recentDays, setRecentDays] = useState(90);

  const popularGenres = [
    'Action', 'Adventure', 'RPG', 'Strategy', 'Shooter', 'Sports',
    'Racing', 'Fighting', 'Puzzle', 'Simulation', 'Horror', 'Platformer'
  ];

  return (
    <Card className="p-6 mb-8 bg-gradient-to-r from-blue-50 to-indigo-50">
      <h3 className="text-lg font-semibold mb-4 text-gray-800">
        🎮 IGDB Game Sync Center
      </h3>
      <p className="text-sm text-gray-600 mb-6">
        Expand your game database by syncing popular, recent, or specific games from IGDB.
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Popular Games Sync */}
        <div className="space-y-3">
          <h4 className="font-medium text-gray-700">📈 Sync Popular Games</h4>
          <div className="flex items-end gap-2">
            <Input
              label="Limit"
              type="number"
              value={popularLimit}
              onChange={(e) => setPopularLimit(parseInt(e.target.value) || 20)}
              min="1"
              max="100"
              className="w-20"
            />
            <Button
              onClick={() => onSyncPopular(popularLimit)}
              disabled={isLoading}
              size="sm"
            >
              {isLoading ? <LoadingSpinner size="sm" /> : 'Sync Popular'}
            </Button>
          </div>
          <p className="text-xs text-gray-500">
            Get the most highly-rated and popular games
          </p>
        </div>

        {/* Search-based Sync */}
        <div className="space-y-3">
          <h4 className="font-medium text-gray-700">🔍 Sync by Search</h4>
          <div className="flex items-end gap-2">
            <Input
              label="Search Term"
              placeholder="zelda, mario, etc."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1"
            />
            <Input
              label="Limit"
              type="number"
              value={searchLimit}
              onChange={(e) => setSearchLimit(parseInt(e.target.value) || 10)}
              min="1"
              max="50"
              className="w-20"
            />
            <Button
              onClick={() => onSyncBySearch(searchQuery, searchLimit)}
              disabled={isLoading || !searchQuery}
              size="sm"
            >
              {isLoading ? <LoadingSpinner size="sm" /> : 'Sync Search'}
            </Button>
          </div>
        </div>

        {/* Genre-based Sync */}
        <div className="space-y-3">
          <h4 className="font-medium text-gray-700">🎯 Sync by Genre</h4>
          <div className="flex items-end gap-2">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Genre
              </label>
              <select
                value={genre}
                onChange={(e) => setGenre(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Select a genre...</option>
                {popularGenres.map((g) => (
                  <option key={g} value={g}>{g}</option>
                ))}
              </select>
            </div>
            <Input
              label="Limit"
              type="number"
              value={genreLimit}
              onChange={(e) => setGenreLimit(parseInt(e.target.value) || 15)}
              min="1"
              max="50"
              className="w-20"
            />
            <Button
              onClick={() => onSyncByGenre(genre, genreLimit)}
              disabled={isLoading || !genre}
              size="sm"
            >
              {isLoading ? <LoadingSpinner size="sm" /> : 'Sync Genre'}
            </Button>
          </div>
        </div>

        {/* Recent Games Sync */}
        <div className="space-y-3">
          <h4 className="font-medium text-gray-700">📅 Sync Recent Releases</h4>
          <div className="flex items-end gap-2">
            <Input
              label="Limit"
              type="number"
              value={recentLimit}
              onChange={(e) => setRecentLimit(parseInt(e.target.value) || 25)}
              min="1"
              max="100"
              className="w-20"
            />
            <Input
              label="Days Back"
              type="number"
              value={recentDays}
              onChange={(e) => setRecentDays(parseInt(e.target.value) || 90)}
              min="1"
              max="365"
              className="w-24"
            />
            <Button
              onClick={() => onSyncRecent(recentLimit, recentDays)}
              disabled={isLoading}
              size="sm"
            >
              {isLoading ? <LoadingSpinner size="sm" /> : 'Sync Recent'}
            </Button>
          </div>
          <p className="text-xs text-gray-500">
            Get games released in the last {recentDays} days
          </p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <p className="text-sm font-medium text-gray-700 mb-3">🚀 Quick Actions:</p>
        <div className="flex flex-wrap gap-2">
          {popularGenres.slice(0, 6).map((g) => (
            <Button
              key={g}
              variant="outline"
              size="sm"
              onClick={() => onSyncByGenre(g, 10)}
              disabled={isLoading}
            >
              {g} (10)
            </Button>
          ))}
        </div>
      </div>

      {isLoading && (
        <div className="mt-4 flex items-center gap-2 text-blue-600">
          <LoadingSpinner size="sm" />
          <span className="text-sm">Syncing games from IGDB...</span>
        </div>
      )}
    </Card>
  );
};