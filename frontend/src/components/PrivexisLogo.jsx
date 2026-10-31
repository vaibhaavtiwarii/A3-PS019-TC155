import React from 'react';

export default function PrivexisLogo({ size = 32, className = '' }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-label="Privexis"
    >
      <defs>
        <linearGradient id="pGrad" x1="0" y1="0" x2="1" y2="1" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#fbbf24" />
          <stop offset="100%" stop-color="#b45309" />
        </linearGradient>
        <linearGradient id="pOutline" x1="0" y1="0" x2="1" y2="1" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#f59e0b" />
          <stop offset="100%" stop-color="#c27103" />
        </linearGradient>
      </defs>
      <rect x="2" y="2" width="28" height="28" rx="8" fill="url(#pGrad)" />
      <rect x="2" y="2" width="28" height="28" rx="8" fill="none" stroke="url(#pOutline)" strokeWidth="0.5" />
      <path
        d="M9 9.5 H19.5 C21.3 9.5 22.7 10.9 22.7 12.7 C22.7 14.5 21.3 15.9 19.5 15.9 H13.5 V22.5 H9 V9.5 Z"
        fill="#07080a"
      />
      <path
        d="M13.5 12.7 H19 C19.9 12.7 20.6 12 20.6 11.1 C20.6 10.2 19.9 9.5 19 9.5 H13.5 V12.7 Z"
        fill="url(#pGrad)"
      />
      <path
        d="M13.5 18.5 H19 C19.9 18.5 20.6 18 20.6 17.1 C20.6 16.2 19.9 17.5 19 17.5 H13.5 V18.5 Z"
        fill="#fbbf24"
      />
    </svg>
  );
}