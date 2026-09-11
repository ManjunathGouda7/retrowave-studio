import React, { useState, useRef, useEffect, useCallback } from 'react';
import { 
  Columns, SplitSquareVertical, Sparkles, MoveHorizontal, 
  ZoomIn, ZoomOut, RotateCw, FlipHorizontal, Tv, Maximize, 
  Minimize, Eye, RotateCcw
} from 'lucide-react';

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
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [flipH, setFlipH] = useState(false);
  const [isCrtMode, setIsCrtMode] = useState(false);
  const [isPeeking, setIsPeeking] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const containerRef = useRef(null);
  const stageWrapperRef = useRef(null);

  // Split slider drag handling
  const handleMove = useCallback((clientX) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = clientX - rect.left;
    const pct = Math.max(0, Math.min(100, (x / rect.width) * 100));
    setSliderPos(pct);
  }, []);

  const handleMouseDown = () => setIsDragging(true);

  // Mouse & Touch listeners for dragging
  useEffect(() => {
    const handleMouseUp = () => setIsDragging(false);
    const handleMouseMove = (e) => {
      if (isDragging) handleMove(e.clientX);
    };
    const handleTouchMove = (e) => {
      if (isDragging && e.touches[0]) handleMove(e.touches[0].clientX);
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

  // Keyboard shortcut listeners (Spacebar peek, F fullscreen, C for CRT, Z for zoom reset)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

      if (e.code === 'Space') {
        e.preventDefault();
        setIsPeeking(true);
      } else if (e.key === 'c' || e.key === 'C') {
        setIsCrtMode((prev) => !prev);
      } else if (e.key === 'f' || e.key === 'F') {
        toggleFullscreen();
      } else if (e.key === 'z' || e.key === 'Z') {
        resetTransform();
      }
    };

    const handleKeyUp = (e) => {
      if (e.code === 'Space') {
        setIsPeeking(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, []);

  const resetTransform = () => {
    setZoom(1);
    setRotation(0);
    setFlipH(false);
  };

  const toggleFullscreen = () => {
    if (!stageWrapperRef.current) return;
    if (!document.fullscreenElement) {
      stageWrapperRef.current.requestFullscreen().catch(() => {});
      setIsFullscreen(true);
    } else {
      document.exitFullscreen().catch(() => {});
      setIsFullscreen(false);
    }
  };

  const transformStyle = {
    transform: `scale(${zoom}) rotate(${rotation}deg) scaleX(${flipH ? -1 : 1})`,
    transition: isDragging ? 'none' : 'transform 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
    transformOrigin: 'center center',
  };

  // Determine effective display source based on peek mode
  const effectiveFiltered = isPeeking ? originalSrc : (filteredSrc || originalSrc);

  return (
    <div className="stage-panel" ref={stageWrapperRef}>
      {/* Top Toolbar */}
      <div className="stage-toolbar">
        <div className="view-mode-group">
          <button
            className={`view-btn ${viewMode === 'split' ? 'active' : ''}`}
            onClick={() => setViewMode('split')}
            title="Interactive Split Comparison Slider"
          >
            <SplitSquareVertical size={14} />
            <span>Split</span>
          </button>
          <button
            className={`view-btn ${viewMode === 'side' ? 'active' : ''}`}
            onClick={() => setViewMode('side')}
            title="Side by Side Comparison"
          >
            <Columns size={14} />
            <span>Side-by-Side</span>
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

        {/* Spacebar Hold to Peek Button */}
        <button
          className={`hold-peek-btn ${isPeeking ? 'peeking' : ''}`}
          onMouseDown={() => setIsPeeking(true)}
          onMouseUp={() => setIsPeeking(false)}
          onTouchStart={() => setIsPeeking(true)}
          onTouchEnd={() => setIsPeeking(false)}
          title="Hold Spacebar or mouse to peek original"
        >
          <Eye size={13} />
          <span>{isPeeking ? 'Showing Original' : 'Hold to Peek (SPACE)'}</span>
        </button>

        {/* Active Filter Label */}
        <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span>Filter:</span>
          <span style={{ color: 'var(--neon-cyan)', fontWeight: 700 }}>
            {filterName ? filterName.toUpperCase().replace(/_/g, ' ') : 'NONE'}
          </span>
        </div>
      </div>

      {/* Main Display Canvas with CRT Option */}
      <div className={isCrtMode ? 'crt-monitor-casing' : ''}>
        <div className={`canvas-wrapper ${isCrtMode ? 'crt-screen-glass' : ''}`} ref={containerRef}>
          {/* Processing Overlay */}
          {isProcessing && (
            <div className="processing-overlay">
              <div className="cyber-spinner" />
              <span style={{ fontFamily: 'Syne, sans-serif', color: 'var(--neon-cyan)', fontSize: '0.9rem', fontWeight: 600 }}>
                Applying Retro Color Matrix...
              </span>
            </div>
          )}

          {/* SPLIT VIEW MODE */}
          {viewMode === 'split' && (
            <div
              className="split-container"
              style={transformStyle}
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
                src={effectiveFiltered}
                alt="Filtered Retro Preview"
                className="split-image-base"
                draggable={false}
              />

              {/* Original Image (Clipped Overlay on Left) */}
              <div
                className="split-overlay-wrapper"
                style={{ width: `${isPeeking ? 100 : sliderPos}%` }}
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
              {!isPeeking && (
                <div className="split-divider" style={{ left: `${sliderPos}%` }}>
                  <div className="split-handle">
                    <MoveHorizontal size={18} />
                  </div>
                </div>
              )}

              {/* Badges */}
              <span className="split-badge original">Original</span>
              <span className="split-badge filtered">
                {isPeeking ? 'Original (Peek)' : (filterName ? filterName.replace(/_/g, ' ') : 'Retro')}
              </span>
            </div>
          )}

          {/* SIDE-BY-SIDE MODE */}
          {viewMode === 'side' && (
            <div 
              style={{ 
                display: 'grid', 
                gridTemplateColumns: '1fr 1fr', 
                width: '100%', 
                height: '560px', 
                gap: '8px', 
                padding: '8px',
                ...transformStyle
              }}
            >
              <div style={{ position: 'relative', height: '100%', overflow: 'hidden', borderRadius: '8px', background: '#05070a' }}>
                <img src={originalSrc} alt="Original" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
                <span className="split-badge original">Original</span>
              </div>
              <div style={{ position: 'relative', height: '100%', overflow: 'hidden', borderRadius: '8px', background: '#05070a' }}>
                <img src={effectiveFiltered} alt="Filtered" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
                <span className="split-badge filtered">{filterName.replace(/_/g, ' ')}</span>
              </div>
            </div>
          )}

          {/* SINGLE VIEW MODE */}
          {viewMode === 'filtered' && (
            <div style={{ position: 'relative', width: '100%', height: '560px', ...transformStyle }}>
              <img
                src={effectiveFiltered}
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

      {/* Floating Bottom Control Dock */}
      <div className="canvas-dock">
        {/* Zoom Controls */}
        <div className="canvas-tool-group">
          <button
            className="canvas-tool-btn"
            onClick={() => setZoom((z) => Math.max(0.5, +(z - 0.25).toFixed(2)))}
            title="Zoom Out"
          >
            <ZoomOut size={16} />
          </button>
          <span style={{ fontSize: '0.78rem', fontFamily: 'VT323, monospace', color: 'var(--neon-cyan)', width: '42px', textAlign: 'center' }}>
            {Math.round(zoom * 100)}%
          </span>
          <button
            className="canvas-tool-btn"
            onClick={() => setZoom((z) => Math.min(3.0, +(z + 0.25).toFixed(2)))}
            title="Zoom In"
          >
            <ZoomIn size={16} />
          </button>
          <button
            className="canvas-tool-btn"
            onClick={resetTransform}
            title="Reset Zoom & Transform (Z)"
          >
            <RotateCcw size={14} />
          </button>
        </div>

        {/* Orientation Tools */}
        <div className="canvas-tool-group">
          <button
            className="canvas-tool-btn"
            onClick={() => setRotation((r) => (r + 90) % 360)}
            title="Rotate 90°"
          >
            <RotateCw size={15} />
          </button>
          <button
            className={`canvas-tool-btn ${flipH ? 'active' : ''}`}
            onClick={() => setFlipH((f) => !f)}
            title="Mirror / Flip Horizontal"
          >
            <FlipHorizontal size={15} />
          </button>
        </div>

        {/* CRT Mode & Fullscreen */}
        <div className="canvas-tool-group">
          <button
            className={`canvas-tool-btn ${isCrtMode ? 'active' : ''}`}
            onClick={() => setIsCrtMode((c) => !c)}
            title="Toggle CRT TV Screen Simulation (C)"
            style={{ width: 'auto', padding: '0 0.5rem', gap: '4px', fontSize: '0.75rem' }}
          >
            <Tv size={14} />
            <span>CRT Mode</span>
          </button>

          <button
            className="canvas-tool-btn"
            onClick={toggleFullscreen}
            title="Fullscreen Canvas (F)"
          >
            {isFullscreen ? <Minimize size={15} /> : <Maximize size={15} />}
          </button>
        </div>
      </div>
    </div>
  );
}
