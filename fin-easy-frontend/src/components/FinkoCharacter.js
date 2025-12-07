import React from 'react';
import { motion } from 'framer-motion';

const FinkoCharacter = ({ size = 'medium', animation = 'idle', className = '' }) => {
  // FINKO - MICO's cousin, designed for accounting/finance
  // Similar to MICO but with accounting theme (calculator, money, etc.)
  
  const sizeClasses = {
    small: 'w-16 h-16',
    medium: 'w-32 h-32',
    large: 'w-48 h-48'
  };

  const animations = {
    idle: {
      y: [0, -5, 0],
      transition: {
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut"
      }
    },
    calculating: {
      rotate: [0, 5, -5, 0],
      scale: [1, 1.05, 1],
      transition: {
        duration: 0.5,
        repeat: Infinity,
        ease: "easeInOut"
      }
    },
    celebrate: {
      scale: [1, 1.2, 1],
      rotate: [0, 10, -10, 0],
      transition: {
        duration: 0.6,
        repeat: 2
      }
    },
    pointing: {
      x: [0, 10, 0],
      transition: {
        duration: 0.8,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  return (
    <motion.div
      className={`${sizeClasses[size]} ${className}`}
      animate={animations[animation] || animations.idle}
    >
      <svg
        viewBox="0 0 200 200"
        className="w-full h-full"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* FINKO Body - Green with calculator/money theme */}
        <circle cx="100" cy="100" r="80" fill="#10b981" stroke="#059669" strokeWidth="3" />
        
        {/* Eyes */}
        <circle cx="80" cy="85" r="8" fill="#ffffff" />
        <circle cx="120" cy="85" r="8" fill="#ffffff" />
        <circle cx="80" cy="85" r="4" fill="#111827" />
        <circle cx="120" cy="85" r="4" fill="#111827" />
        
        {/* Smile */}
        <path
          d="M 70 110 Q 100 130 130 110"
          stroke="#ffffff"
          strokeWidth="4"
          fill="none"
          strokeLinecap="round"
        />
        
        {/* Calculator/Money symbol on chest */}
        <rect x="85" y="105" width="30" height="25" rx="3" fill="#ffffff" opacity="0.9" />
        <line x1="90" y1="112" x2="110" y2="112" stroke="#10b981" strokeWidth="2" />
        <line x1="90" y1="118" x2="110" y2="118" stroke="#10b981" strokeWidth="2" />
        <line x1="90" y1="124" x2="110" y2="124" stroke="#10b981" strokeWidth="2" />
        
        {/* Dollar sign */}
        <text x="100" y="125" fontSize="12" fill="#10b981" textAnchor="middle" fontWeight="bold">$</text>
        
        {/* Arms - pointing or calculating */}
        {animation === 'pointing' ? (
          <>
            <line x1="50" y1="100" x2="30" y2="80" stroke="#059669" strokeWidth="8" strokeLinecap="round" />
            <circle cx="30" cy="80" r="6" fill="#059669" />
          </>
        ) : (
          <>
            <line x1="50" y1="100" x2="40" y2="110" stroke="#059669" strokeWidth="8" strokeLinecap="round" />
            <line x1="150" y1="100" x2="160" y2="110" stroke="#059669" strokeWidth="8" strokeLinecap="round" />
          </>
        )}
        
        {/* Legs */}
        <line x1="85" y1="170" x2="85" y2="190" stroke="#059669" strokeWidth="8" strokeLinecap="round" />
        <line x1="115" y1="170" x2="115" y2="190" stroke="#059669" strokeWidth="8" strokeLinecap="round" />
        
        {/* Feet */}
        <ellipse cx="85" cy="190" rx="8" ry="4" fill="#059669" />
        <ellipse cx="115" cy="190" rx="8" ry="4" fill="#059669" />
      </svg>
    </motion.div>
  );
};

export default FinkoCharacter;

