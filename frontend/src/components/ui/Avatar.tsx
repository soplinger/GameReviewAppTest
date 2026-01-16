/**
 * Avatar component for displaying user profile pictures
 */

import React from 'react';

interface AvatarProps {
  src?: string | null;
  alt: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizeClasses = {
  sm: 'w-8 h-8 text-sm',
  md: 'w-12 h-12 text-base',
  lg: 'w-16 h-16 text-lg',
};

export const Avatar: React.FC<AvatarProps> = ({
  src,
  alt,
  size = 'md',
  className = '',
}) => {
  const baseClasses = `${sizeClasses[size]} rounded-full flex items-center justify-center font-medium ${className}`;

  if (src) {
    return (
      <img
        src={src}
        alt={alt}
        className={`${baseClasses} object-cover`}
      />
    );
  }

  // Fallback to initials
  const initials = alt
    .split(' ')
    .map(name => name.charAt(0))
    .join('')
    .toUpperCase()
    .slice(0, 2);

  return (
    <div className={`${baseClasses} bg-primary-600 text-white`}>
      {initials}
    </div>
  );
};