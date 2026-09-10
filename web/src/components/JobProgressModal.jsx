import React, { useState, useEffect, useRef } from 'react';
import { X, CheckCircle, AlertTriangle, Download, Film, Play, StopCircle } from 'lucide-react';
import confetti from 'canvas-confetti';

export default function JobProgressModal({ jobId, onClose }) {
  const [job, setJob] = useState({
    status: 'queued',
    progress: 0,
    current_step: 'Connecting to real-time render socket...',
  });
  const [logs, setLogs] = useState([]);
  const [isCompleted, setIsCompleted] = useState(false);
  const [isFailed, setIsFailed] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    if (!jobId) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/jobs/${jobId}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setLogs((prev) => [...prev, `[SYSTEM] Connected to WebSocket channel /ws/jobs/${jobId}`]);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setJob(data);
        if (data.current_step) {
          setLogs((prev) => {
            const last = prev[prev.length - 1];
            if (last !== data.current_step) {
              return [...prev.slice(-30), `[RENDER] ${data.current_step}`];
            }
            return prev;
          });
        }

        if (data.status === 'completed') {
          setIsCompleted(true);
          confetti({
            particleCount: 80,
            spread: 70,
            origin: { y: 0.6 },
            colors: ['#ff007f', '#00f0ff', '#9d00ff', '#ffb700']
          });
        } else if (data.status === 'failed' || data.status === 'cancelled') {
          setIsFailed(true);
        }
      } catch (err) {
        console.error('Error parsing WS message', err);
      }
    };

    ws.onerror = (e) => {
      setLogs((prev) => [...prev, '[WARN] WebSocket error, polling fallback active.']);
    };

    // Also poll every 1s as a backup
    const pollInterval = setInterval(async () => {
      try {
        const res = await fetch(`/api/v1/jobs/${jobId}`);
        if (res.ok) {
          const pollData = await res.json();
          setJob(pollData);
          if (pollData.status === 'completed') {
            setIsCompleted(true);
            clearInterval(pollInterval);
          } else if (pollData.status === 'failed' || pollData.status === 'cancelled') {
            setIsFailed(true);
            clearInterval(pollInterval);
          }
        }
      } catch {}
    }, 1200);

    return () => {
      clearInterval(pollInterval);
      if (wsRef.current) wsRef.current.close();
    };
  }, [jobId]);

  const handleCancel = async () => {
    try {
      await fetch(`/api/v1/jobs/${jobId}`, { method: 'DELETE' });
      setLogs((prev) => [...prev, '[ABORT] Render job cancelled by user.']);
    } catch (e) {
      console.error(e);
    }
  };

  const circumference = 2 * Math.PI * 54;
  const strokeDashoffset = circumference - (job.progress / 100) * circumference;

  return (
    <div className="modal-backdrop">
      <div className="hud-modal">
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '1rem',
            right: '1rem',
            background: 'transparent',
            border: 'none',
            color: 'var(--text-dim)',
            cursor: 'pointer',
          }}
        >
          <X size={20} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginBottom: '1.25rem' }}>
          <Film size={20} style={{ color: 'var(--neon-pink)' }} />
          <h3 style={{ fontFamily: 'Orbitron, sans-serif', fontSize: '1.15rem', color: '#ffffff', letterSpacing: '1px' }}>
            {isCompleted ? 'RENDER COMPLETE' : 'RENDER PROGRESS HUD'}
          </h3>
        </div>

        {/* Circular Progress Gauge */}
        <div className="hud-progress-circle">
          <svg width="140" height="140">
            <circle
              cx="70"
              cy="70"
              r="54"
              fill="transparent"
              stroke="rgba(255, 255, 255, 0.08)"
              strokeWidth="8"
            />
            <circle
              cx="70"
              cy="70"
              r="54"
              fill="transparent"
              stroke={isCompleted ? 'var(--neon-green)' : 'url(#hudGrad)'}
              strokeWidth="8"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              style={{ transition: 'stroke-dashoffset 0.3s ease' }}
            />
            <defs>
              <linearGradient id="hudGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#ff007f" />
                <stop offset="100%" stopColor="#00f0ff" />
              </linearGradient>
            </defs>
          </svg>
          <div className="hud-pct-text">
            {job.progress}%
          </div>
        </div>

        {/* Step Status Text */}
        <div className="hud-step-text">
          {job.current_step || 'Processing...'}
        </div>

        {/* Live Terminal Output */}
        <div className="hud-terminal-log">
          {logs.map((log, idx) => (
            <div key={idx} style={{ marginBottom: '2px' }}>
              &gt; {log}
            </div>
          ))}
        </div>

        {/* Result Video Player if Completed */}
        {isCompleted && (
          <div style={{ marginBottom: '1.5rem', borderRadius: '8px', overflow: 'hidden', border: '1px solid var(--border-glass)' }}>
            <video
              src={`/api/v1/jobs/${jobId}/download`}
              controls
              autoPlay
              loop
              style={{ width: '100%', maxHeight: '240px', display: 'block' }}
            />
          </div>
        )}

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '10px' }}>
          {isCompleted ? (
            <a
              href={`/api/v1/jobs/${jobId}/download`}
              download
              className="btn-primary"
              style={{ textDecoration: 'none' }}
            >
              <Download size={18} />
              <span>Download Master Video</span>
            </a>
          ) : !isFailed ? (
            <button
              onClick={handleCancel}
              className="btn-secondary"
              style={{ color: '#ff4757', borderColor: 'rgba(255, 71, 87, 0.4)' }}
            >
              <StopCircle size={16} />
              <span>Cancel Render Task</span>
            </button>
          ) : (
            <button onClick={onClose} className="btn-secondary">
              Close
            </button>
          )}

          {isCompleted && (
            <button onClick={onClose} className="btn-secondary" style={{ width: 'auto', padding: '0.85rem 1.25rem' }}>
              Done
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
