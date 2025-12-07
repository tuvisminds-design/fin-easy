import React from 'react';
import { motion } from 'framer-motion';

const FincoCharacter = ({ size = 'medium', animation = 'idle' }) => {
  const sizes = {
    small: 'w-16 h-16',
    medium: 'w-32 h-32',
    large: 'w-48 h-48'
  };

  const animations = {
    idle: {
      y: [0, -10, 0],
      transition: {
        duration: 2,
        repeat: Infinity,
        ease: 'easeInOut'
      }
    },
    pointing: {
      x: [0, 5, 0],
      transition: {
        duration: 0.5,
        repeat: Infinity,
        ease: 'easeInOut'
      }
    },
    celebrate: {
      scale: [1, 1.2, 1],
      rotate: [0, 10, -10, 0],
      transition: {
        duration: 0.6,
        repeat: Infinity,
        ease: 'easeInOut'
      }
    },
    talking: {
      scale: [1, 1.05, 1],
      transition: {
        duration: 0.3,
        repeat: Infinity,
        ease: 'easeInOut'
      }
    }
  };

  return (
    <motion.div
      className={`${sizes[size]} flex items-center justify-center`}
      animate={animations[animation] || animations.idle}
    >
      <svg
        viewBox="0 0 200 200"
        className="w-full h-full"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* FINCO Character - Green calculator/money character */}
        {/* Head */}
        <circle cx="100" cy="80" r="35" fill="#10b981" stroke="#059669" strokeWidth="2" />
        
        {/* Eyes */}
        <circle cx="90" cy="75" r="4" fill="white" />
        <circle cx="110" cy="75" r="4" fill="white" />
        <circle cx="90" cy="75" r="2" fill="#1f2937" />
        <circle cx="110" cy="75" r="2" fill="#1f2937" />
        
        {/* Smile */}
        <path
          d="M 85 90 Q 100 100 115 90"
          stroke="white"
          strokeWidth="3"
          fill="none"
          strokeLinecap="round"
        />
        
        {/* Calculator Body */}
        <rect x="60" y="120" width="80" height="60" rx="8" fill="#10b981" stroke="#059669" strokeWidth="2" />
        
        {/* Calculator Screen */}
        <rect x="70" y="130" width="60" height="15" rx="2" fill="#1f2937" />
        <text x="100" y="142" textAnchor="middle" fill="#10b981" fontSize="10" fontFamily="monospace">$0.00</text>
        
        {/* Calculator Buttons */}
        <circle cx="80" cy="155" r="4" fill="#059669" />
        <circle cx="100" cy="155" r="4" fill="#059669" />
        <circle cx="120" cy="155" r="4" fill="#059669" />
        <circle cx="80" cy="170" r="4" fill="#059669" />
        <circle cx="100" cy="170" r="4" fill="#059669" />
        <circle cx="120" cy="170" r="4" fill="#059669" />
        
        {/* Dollar Sign on Chest */}
        <text x="100" y="105" textAnchor="middle" fill="white" fontSize="24" fontFamily="Arial" fontWeight="bold">$</text>
      </svg>
    </motion.div>
  );
};

export default FincoCharacter;

