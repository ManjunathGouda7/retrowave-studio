import React, { useState, useEffect } from 'react';
import { Sparkles, Camera, Film, ListOrdered, BookOpen, Code2 } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab }) {
  const [serverOnline, setServerOnline] = useState(false);
  const [latency, setLatency] = useState(null);

  const checkHealth = async () => {
    const start = performance.now();
    try {
      const res = await fetch('/health');
      if (res.ok) {
        setServerOnline(true);
        setLatency(Math.round(performance.now() - start));
      } else {
        setServerOnline(false);
      }
    } catch {
      setServerOnline(false);
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 8000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="studio-nav">
      <div className="brand-section">
        <div className="brand-logo-icon">
          <Sparkles size={22} />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="brand-title">RETROWAVE STUDIO</span>
            <span className="brand-badge">ENTERPRISE</span>
          </div>
          <p style={{ fontSize: '0.72rem', color: 'var(--text-dim)', letterSpacing: '0.5px' }}>
            110 RETRO FILTERS • 8 CATEGORIES • DYNAMIC VIDEO ENGINE
          </p>
        </div>
      </div>

      <div className="nav-tabs">
        <button
          className={`nav-tab-btn ${activeTab === 'image' ? 'active' : ''}`}
          onClick={() => setActiveTab('image')}
        >
          <Camera size={16} />
          <span>Image Studio</span>
        </button>
        <button
          className={`nav-tab-btn ${activeTab === 'video' ? 'active' : ''}`}
          onClick={() => setActiveTab('video')}
        >
          <Film size={16} />
          <span>Video Studio</span>
        </button>
        <button
          className={`nav-tab-btn ${activeTab === 'queue' ? 'active' : ''}`}
          onClick={() => setActiveTab('queue')}
        >
          <ListOrdered size={16} />
          <span>Job Queue</span>
        </button>
      </div>

      <div className="nav-actions">
        <div className="server-status-pill" title="FastAPI Microservice Health Status">
          <span className={`status-dot ${serverOnline ? '' : 'offline'}`} />
          <span>{serverOnline ? `API Online (${latency}ms)` : 'Connecting API...'}</span>
        </div>

        <a
          href="/docs"
          target="_blank"
          rel="noreferrer"
          className="ghost-btn"
          title="Interactive OpenAPI / Swagger Documentation"
        >
          <BookOpen size={14} />
          <span>API Docs</span>
        </a>

        <a
          href="https://github.com/ManjunathGouda7/retrowave-studio"
          target="_blank"
          rel="noreferrer"
          className="ghost-btn"
          title="View GitHub Repository"
        >
          <Code2 size={14} />
          <span>GitHub</span>
        </a>
      </div>
    </header>
  );
}
