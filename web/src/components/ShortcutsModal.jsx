import React from 'react';
import { X, Keyboard, Sparkles } from 'lucide-react';

const SHORTCUTS = [
  { key: 'SPACE', desc: 'Hold to instantly peek at original photo' },
  { key: '[ / ]', desc: 'Cycle to previous or next retro filter' },
  { key: 'F', desc: 'Toggle Fullscreen distraction-free canvas' },
  { key: 'C', desc: 'Toggle Authentic CRT TV simulation' },
  { key: 'Z', desc: 'Reset zoom & pan to 100% center' },
  { key: 'CTRL + S', desc: 'Quick download master JPEG' },
  { key: '?', desc: 'Toggle keyboard shortcuts cheatsheet' },
  { key: 'ESC', desc: 'Close open modals & dialogs' },
];

export default function ShortcutsModal({ onClose }) {
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="batch-modal-box" style={{ maxWidth: '520px' }} onClick={(e) => e.stopPropagation()}>
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '1.25rem',
            right: '1.25rem',
            background: 'transparent',
            border: 'none',
            color: 'var(--text-dim)',
            cursor: 'pointer',
          }}
        >
          <X size={20} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '0.5rem' }}>
          <Keyboard size={22} style={{ color: 'var(--neon-cyan)' }} />
          <h3 style={{ fontFamily: 'Orbitron, sans-serif', fontSize: '1.15rem', color: '#ffffff' }}>
            STUDIO SHORTCUTS
          </h3>
        </div>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
          Speed up your creative workflow with rapid keyboard triggers.
        </p>

        <div className="shortcuts-grid">
          {SHORTCUTS.map((s, idx) => (
            <div key={idx} className="shortcut-row">
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{s.desc}</span>
              <span className="shortcut-key">{s.key}</span>
            </div>
          ))}
        </div>

        <button className="btn-secondary" onClick={onClose} style={{ marginTop: '0.5rem' }}>
          Got It
        </button>
      </div>
    </div>
  );
}
