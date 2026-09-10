import React, { useState } from 'react';
import Navbar from './components/Navbar';
import ImageStudio from './components/ImageStudio';
import LutStudio from './components/LutStudio';
import VideoStudio from './components/VideoStudio';
import QueueMonitor from './components/QueueMonitor';

export default function App() {
  const [activeTab, setActiveTab] = useState('image'); // 'image' | 'lut' | 'video' | 'queue'

  return (
    <div className="studio-app">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="studio-content">
        {activeTab === 'image' && <ImageStudio />}
        {activeTab === 'lut' && <LutStudio />}
        {activeTab === 'video' && <VideoStudio />}
        {activeTab === 'queue' && <QueueMonitor />}
      </main>

      <footer
        style={{
          borderTop: '1px solid var(--border-glass)',
          padding: '1.5rem 2rem',
          textAlign: 'center',
          fontSize: '0.8rem',
          color: 'var(--text-dim)',
          background: 'rgba(7, 9, 14, 0.9)',
        }}
      >
        <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
          <div>
            <span style={{ fontFamily: 'Orbitron, sans-serif', color: 'var(--neon-pink)', fontWeight: 700 }}>
              RETROWAVE STUDIO
            </span>
            <span style={{ margin: '0 8px' }}>•</span>
            <span>Enterprise Visual Processing Suite</span>
          </div>

          <div style={{ display: 'flex', gap: '15px' }}>
            <span>110 Filters</span>
            <span>•</span>
            <span>FastAPI Microservice</span>
            <span>•</span>
            <span>Real-Time WebSockets</span>
            <span>•</span>
            <span>Redis Broker</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
