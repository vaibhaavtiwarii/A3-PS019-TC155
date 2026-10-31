import React from 'react'

// Simplified SVG for Privexis logo (blue cybersecurity shield)
export default function PrivexisLogo() {
  return (
    <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Shield shape with blue gradient */}
      <path d="M10 20C10 10 20 5 30 5C40 5 40 15 30 25C20 35 10 30 10 20Z" fill="url(#shieldGradient)"/>

      {/* Shield border */}
      <path d="M10 20C10 10 20 5 30 5C40 5 40 15 30 25C20 35 10 30 10 20Z" stroke="#007BFF" strokeWidth="2" fill="none"/>

      {/* Cybernetic lines inside shield */}
      <path d="M15 10L25 20L15 30" stroke="#007BFF" strokeWidth="1.5" strokeLinecap="round"/>
      <path d="M20 15L25 20L20 25" stroke="#007BFF" strokeWidth="1.5" strokeLinecap="round"/>
      <path d="M25 15L30 20L25 25" stroke="#007BFF" strokeWidth="1.5" strokeLinecap="round"/>

      {/* Glowing blue dots for cybernetic effect */}
      <circle cx="12" cy="12" r="1" fill="#007BFF"/>
      <circle cx="28" cy="12" r="1" fill="#007BFF"/>
      <circle cx="28" cy="28" r="1" fill="#007BFF"/>
      <circle cx="12" cy="28" r="1" fill="#007BFF"/>

      {/* Gradient for shield */}
      <defs>
        <linearGradient id="shieldGradient" x1="0" y1="0" x2="40" y2="40" fill="none">
          <stop offset="0" stopColor="#007BFF" />
          <stop offset="1" stopColor="#0056b3" />
        </linearGradient>
      </defs>
    </svg>
  )
}