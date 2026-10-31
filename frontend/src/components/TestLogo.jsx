import React from 'react';
import PrivexisLogo from './PrivexisLogo';

export default function TestLogo() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', backgroundColor: '#0c0e14' }}>
      <div style={{ width: '40px', height: '40px', border: '1px solid red', margin: '20px' }}>
        <PrivexisLogo />
      </div>
      <div style={{ marginLeft: '20px', color: 'white' }}>Test Logo Render</div>
    </div>
  );
}