/**
 * Alert component for displaying notifications, warnings, and error messages
 */

import React from 'react';

interface AlertProps {
  children: React.ReactNode;
  variant?: 'success' | 'error' | 'warning' | 'info';
  className?: string;
  onClose?: () => void;
}

const variantStyles = {
  success: 'bg-green-50 text-green-800 border-green-200',
  error: 'bg-red-50 text-red-800 border-red-200',
  warning: 'bg-yellow-50 text-yellow-800 border-yellow-200',
  info: 'bg-blue-50 text-blue-800 border-blue-200',
};

const iconMap = {
  success: '✓',
  error: '✕',
  warning: '⚠',
  info: 'ℹ',
};

export const Alert: React.FC<AlertProps> = ({ 
  children, 
  variant = 'info', 
  className = '', 
  onClose 
}) => {
  return (
    <div 
      className={`
        relative p-4 border rounded-lg flex items-start gap-3
        ${variantStyles[variant]}
        ${className}
      `}
      role="alert"
    >
      <span className="text-lg font-semibold mt-0.5">
        {iconMap[variant]}
      </span>
      <div className="flex-1">
        {children}
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="text-current hover:opacity-70 ml-2"
          aria-label="Close alert"
        >
          ✕
        </button>
      )}
    </div>
  );
};