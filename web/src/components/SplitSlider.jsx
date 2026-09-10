import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Columns, SplitSquareVertical, Sparkles, MoveHorizontal } from 'lucide-react';

export default function SplitSlider({
  originalSrc,
  filteredSrc,
  filterName,
  isProcessing,
  viewMode,
  setViewMode
}) {
  const [sliderPos, setSliderPos] = useState(50); // percentage 0 - 100
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef(null);

  const handleMove = useCallback((clientX) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = clientX - rect.left;
    const pct = Math.max(0, Math.min(100, (x / rect.width) * 100));
    setSliderPos(pct);
  }, []);

  const handleMouseDown = () => setIsDragging(true);

  useEffect(() => {
    const handleMouseUp = () => setIsDragging(false);
    const handleMouseMove = (e) => {
      if (isDragging) {
        handleMove(e.clientX);
      }
    };
    const handleTouchMove = (e) => {
      if (isDragging && e.touches[0]) {
        handleMove(e.touches[0].clientX);
      }
    };

    window.addEventListener('mouseup', handleMouseUp);
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('touchend', handleMouseUp);
    window.addEventListener('touchmove', handleTouchMove);

    return () => {
      window.removeEventListener('mouseup', handleMouseUp);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('touchend', handleMouseUp);
      window.removeEventListener('touchmove', handleTouchMove);
    };
  }, [isDragging, handleMove]);

  return (
    <div className="stage-panel">
      {/* Canvas Mode Toolbar */}
      <div className="stage-toolbar">
        <div className="view-mode-group">
          <button
            className={`view-btn ${viewMode === 'split' ? 'active' : ''}`}
            onClick={() => setViewMode('split')}
            title="Interactive Split Comparison Slider"
          >
            <SplitSquareVertical size={14} />
            <span>Split Slider</span>
          </button>
          <button
            className={`view-btn ${viewMode === 'side' ? 'active' : ''}`}
            onClick={() => setViewMode('side')}
            title="Side by Side Comparison"
          >
            <Columns size={14} />
            <span>Side by Side</span>
          </button>
          <button
            className={`view-btn ${viewMode === 'filtered' ? 'active' : ''}`}
            onClick={() => setViewMode('filtered')}
            title="Single Filtered View"
          >
            <Sparkles size={14} />
            <span>Single View</span>
          </button>
        </div>

        <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span>Active Filter:</span>
          <span style={{ color: 'var(--neon-cyan)', fontWeight: 700 }}>
            {filterName ? filterName.toUpperCase().replace(/_/g, ' ') : 'NONE'}
          </span>
        </div>
      </div>

      {/* Main Display Area */}
      <div className="canvas-wrapper" ref={containerRef}>
        {/* Processing Spinner Overlay */}
        {isProcessing && (
          <div className="processing-overlay">
            <div className="cyber-spinner" />
            <span style={{ fontFamily: 'Syne, sans-serif', color: 'var(--neon-cyan)', fontSize: '0.9rem', fontWeight: 600 }}>
              Applying Retro Color Matrix...
            </span>
          </div>
        )}

        {viewMode === 'split' && (
          <div
            className="split-container"
            onMouseDown={(e) => {
              handleMouseDown();
              handleMove(e.clientX);
            }}
            onTouchStart={(e) => {
              handleMouseDown();
              if (e.touches[0]) handleMove(e.touches[0].clientX);
            }}
          >
            {/* Filtered Master (Background) */}
            <img
              src={filteredSrc || originalSrc}
              alt="Filtered Retro Preview"
              className="split-image-base"
              draggable={false}
            />

            {/* Original Image (Clipped Overlay on Left) */}
            <div
              className="split-overlay-wrapper"
              style={{ width: `${sliderPos}%` }}
            >
              <img
                src={originalSrc}
                alt="Original Media"
                className="split-image-overlay"
                style={{
                  width: containerRef.current ? `${containerRef.current.clientWidth}px` : '100%',
                  maxWidth: 'none',
                }}
                draggable={false}
              />
            </div>

            {/* Draggable Divider Line & Handle */}
            <div className="split-divider" style={{ left: `${sliderPos}%` }}>
              <div className="split-handle">
                <MoveHorizontal size={18} />
              </div>
            </div>

            {/* Badges */}
            <span className="split-badge original">Original</span>
            <span className="split-badge filtered">
              {filterName ? filterName.replace(/_/g, ' ') : 'Retro Filter'}
            </span>
          </div>
        )}

        {viewMode === 'side' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', width: '100%', height: '560px', gap: '8px', padding: '8px' }}>
            <div style={{ position: 'relative', height: '100%', overflow: 'hidden', borderRadius: '8px', background: '#05070a' }}>
              <img src={originalSrc} alt="Original" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
              <span className="split-badge original">Original</span>
            </div>
            <div style={{ position: 'relative', height: '100%', overflow: 'hidden', borderRadius: '8px', background: '#05070a' }}>
              <img src={filteredSrc || originalSrc} alt="Filtered" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
              <span className="split-badge filtered">{filterName.replace(/_/g, ' ')}</span>
            </div>
          </div>
        )}

        {viewMode === 'filtered' && (
          <div style={{ position: 'relative', width: '100%', height: '560px' }}>
            <img
              src={filteredSrc || originalSrc}
              alt="Filtered View"
              style={{ width: '100%', height: '100%', objectFit: 'contain' }}
            />
            <span className="split-badge filtered" style={{ right: '1.5rem', bottom: '1.5rem' }}>
              {filterName.replace(/_/g, ' ')}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
