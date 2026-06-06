import React from 'react';

const NewsEyeLogo = ({ size = 32, className = "" }) => {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 100 100" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Outer Shield Shape */}
      <path 
        d="M50 5L15 20V45C15 67.5 30 88 50 95C70 88 85 67.5 85 45V20L50 5Z" 
        fill="#1e293b" 
        stroke="#3b82f6" 
        strokeWidth="4"
      />
      
      {/* Eye Outline */}
      <path 
        d="M25 50C25 50 35 35 50 35C65 35 75 50 75 50C75 50 65 65 50 65C35 65 25 50 25 50Z" 
        stroke="#60a5fa" 
        strokeWidth="3"
        strokeLinecap="round"
      />
      
      {/* Eye Pupil (Central Node) */}
      <circle cx="50" cy="50" r="8" fill="#3b82f6" />
      
      {/* Data/Network Nodes */}
      <circle cx="50" cy="50" r="14" stroke="#3b82f6" strokeWidth="1" strokeDasharray="2 2" />
      
      {/* Network Connections */}
      <line x1="50" y1="42" x2="50" y2="35" stroke="#60a5fa" strokeWidth="2" />
      <line x1="50" y1="58" x2="50" y2="65" stroke="#60a5fa" strokeWidth="2" />
      <line x1="42" y1="50" x2="35" y2="50" stroke="#60a5fa" strokeWidth="2" />
      <line x1="58" y1="50" x2="65" y2="50" stroke="#60a5fa" strokeWidth="2" />
      
      {/* Accent Glow */}
      <circle cx="50" cy="50" r="4" fill="white" fillOpacity="0.4" />
    </svg>
  );
};

export default NewsEyeLogo;
