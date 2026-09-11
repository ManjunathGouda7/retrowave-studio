import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Sparkles, Sliders, Calendar, Image as ImageIcon, Download, 
  Upload, Search, Film, Wand2, RefreshCw, Layers, Archive, 
  ChevronDown, ChevronUp, Keyboard, HelpCircle
} from 'lucide-react';
import SplitSlider from './SplitSlider';
import JobProgressModal from './JobProgressModal';
import BatchModal from './BatchModal';
import ShortcutsModal from './ShortcutsModal';

const CATEGORIES = [
  { id: 'all', label: 'All', count: 110 },
  { id: 'cyberpunk', label: 'Cyberpunk', count: 10 },
  { id: 'horror', label: 'Horror', count: 10 },
  { id: 'dreamy', label: 'Dreamy', count: 10 },
  { id: '80s', label: '80s', count: 20 },
  { id: '90s', label: '90s', count: 20 },
  { id: 'retro', label: 'Retro', count: 20 },
  { id: 'glitch', label: 'Glitch', count: 10 },
  { id: 'artistic', label: 'Artistic', count: 10 },
];

const PRESETS = [
  { name: 'Cyber City', path: '/samples/cyberpunk_city.jpg' },
  { name: '80s Sunset Car', path: '/samples/synthwave_car.jpg' },
];

// Procedural gradient swatch generator for realistic retro thumbnail looks
export const getFilterGradient = (category, name) => {
  switch (category) {
    case 'cyberpunk':
      if (name.includes('blade')) return 'linear-gradient(135deg, #ff7b00 0%, #00f0ff 100%)';
      if (name.includes('matrix') || name.includes('rain') || name.includes('acid')) 
        return 'linear-gradient(135deg, #021a02 0%, #00ff66 100%)';
      return 'linear-gradient(135deg, #ff007f 0%, #00f0ff 100%)';
    case 'horror':
      if (name.includes('vision')) return 'linear-gradient(135deg, #052b05 0%, #00ff44 100%)';
      if (name.includes('blood') || name.includes('demon')) 
        return 'linear-gradient(135deg, #400000 0%, #ff0033 100%)';
      return 'linear-gradient(135deg, #2b0c15 0%, #8b0000 50%, #1a1a1a 100%)';
    case 'dreamy':
      return 'linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 50%, #ffc3a0 100%)';
    case '80s':
      return 'linear-gradient(135deg, #ff007f 0%, #7928ca 50%, #00f0ff 100%)';
    case '90s':
      return 'linear-gradient(135deg, #f7971e 0%, #ffd200 60%, #00c9ff 100%)';
    case 'retro':
      return 'linear-gradient(135deg, #c31432 0%, #240b36 100%)';
    case 'glitch':
      return 'linear-gradient(135deg, #00f0ff 0%, #ff007f 50%, #00ff88 100%)';
    case 'artistic':
      return 'linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%)';
    default:
      return 'linear-gradient(135deg, #ff007f 0%, #00f0ff 100%)';
  }
};

export default function ImageStudio() {
  const [allFilters, setAllFilters] = useState([]);
  const [activeCategory, setActiveCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('cyber_neon');
  const [intensity, setIntensity] = useState(1.0);

  // Finishing Touches
  const [dateStampEnabled, setDateStampEnabled] = useState(true);
  const [dateStampText, setDateStampText] = useState("'94 12 25");
  const [frameBorder, setFrameBorder] = useState('none'); // 'none' | 'polaroid' | 'filmstrip'
  const [vhsOsd, setVhsOsd] = useState(false);
  const [lightLeak, setLightLeak] = useState(false);
  const [grainAmount, setGrainAmount] = useState(0.08);

  // Pro Color Grading Drawer (Lightroom Style)
  const [showProGrading, setShowProGrading] = useState(false);
  const [proExposure, setProExposure] = useState(0);
  const [proContrast, setProContrast] = useState(1.0);
  const [proTemp, setProTemp] = useState(0);
  const [proTint, setProTint] = useState(0);
  const [proVignette, setProVignette] = useState(0);

  // Images state
  const [originalSrc, setOriginalSrc] = useState('/samples/cyberpunk_city.jpg');
  const [filteredSrc, setFilteredSrc] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isGeneratingGif, setIsGeneratingGif] = useState(false);
  const [viewMode, setViewMode] = useState('split');

  // Modals state
  const [showBatchModal, setShowBatchModal] = useState(false);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [activeBatchJobId, setActiveBatchJobId] = useState(null);

  const fileInputRef = useRef(null);

  // Fetch filter catalog
  useEffect(() => {
    fetch('/api/v1/filters')
      .then((res) => res.json())
      .then((data) => {
        if (data.filters) setAllFilters(data.filters);
      })
      .catch((err) => console.error('Failed to load filters list', err));
  }, []);

  // Filter list search & category filter
  const filteredList = allFilters.filter((f) => {
    const matchCat = activeCategory === 'all' || f.category === activeCategory;
    const matchSearch = f.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                        f.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchCat && matchSearch;
  });

  // Keyboard navigation listeners: [ for prev, ] for next, ? for shortcuts
  useEffect(() => {
    const handleKey = (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

      if (e.key === '[') {
        const idx = filteredList.findIndex((f) => f.name === selectedFilter);
        if (idx > 0) setSelectedFilter(filteredList[idx - 1].name);
      } else if (e.key === ']') {
        const idx = filteredList.findIndex((f) => f.name === selectedFilter);
        if (idx >= 0 && idx < filteredList.length - 1) {
          setSelectedFilter(filteredList[idx + 1].name);
        }
      } else if (e.key === '?') {
        setShowShortcuts((prev) => !prev);
      } else if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        handleDownload();
      }
    };

    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [filteredList, selectedFilter]);

  // Process image via API
  const applyFilter = useCallback(async () => {
    if (!originalSrc) return;
    setIsProcessing(true);

    try {
      const imgRes = await fetch(originalSrc);
      const imgBlob = await imgRes.blob();

      const formData = new FormData();
      formData.append('file', imgBlob, 'source.jpg');
      formData.append('filter_name', selectedFilter);
      formData.append('intensity', intensity.toString());

      if (dateStampEnabled && dateStampText) {
        formData.append('date_stamp', dateStampText);
      }
      if (frameBorder === 'polaroid') {
        formData.append('polaroid', 'true');
      } else if (frameBorder === 'filmstrip') {
        formData.append('film_border', 'true');
      }
      if (vhsOsd) formData.append('vhs_osd', 'true');
      if (lightLeak) formData.append('light_leak', 'true');
      if (grainAmount > 0) formData.append('grain', grainAmount.toString());

      formData.append('response_format', 'binary');

      const res = await fetch('/api/v1/process/image', {
        method: 'POST',
        body: formData,
      });

      if (res.ok) {
        const resultBlob = await res.blob();
        const url = URL.createObjectURL(resultBlob);
        setFilteredSrc(url);
      }
    } catch (err) {
      console.error('Error applying filter:', err);
    } finally {
      setIsProcessing(false);
    }
  }, [originalSrc, selectedFilter, intensity, dateStampEnabled, dateStampText, frameBorder, vhsOsd, lightLeak, grainAmount]);

  // Trigger processing on changes with debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      applyFilter();
    }, 280);
    return () => clearTimeout(timer);
  }, [applyFilter]);

  // Handle local file upload
  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setOriginalSrc(url);
    }
  };

  // Generate GIF
  const handleGenerateGif = async () => {
    if (!originalSrc) return;
    setIsGeneratingGif(true);

    try {
      const imgRes = await fetch(originalSrc);
      const imgBlob = await imgRes.blob();

      const formData = new FormData();
      formData.append('file', imgBlob, 'source.jpg');
      formData.append('filter_name', selectedFilter);
      formData.append('frames', '8');
      formData.append('duration', '110');

      const res = await fetch('/api/v1/process/image/gif', {
        method: 'POST',
        body: formData,
      });

      if (res.ok) {
        const gifBlob = await res.blob();
        const url = URL.createObjectURL(gifBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `retrowave_${selectedFilter}.gif`;
        a.click();
      }
    } catch (err) {
      console.error('GIF generation failed', err);
    } finally {
      setIsGeneratingGif(false);
    }
  };

  // Download filtered image
  const handleDownload = () => {
    if (!filteredSrc) return;
    const a = document.createElement('a');
    a.href = filteredSrc;
    a.download = `retrowave_${selectedFilter}.jpg`;
    a.click();
  };

  return (
    <div className="studio-grid">
      {/* 1. LEFT PANEL: VISUAL FILTER SWATCH CARDS */}
      <div className="panel-card">
        <div className="panel-header">
          <h3 className="panel-title">
            <Wand2 size={18} />
            <span>Filter Studio</span>
          </h3>
          <span className="brand-badge">{filteredList.length} Active</span>
        </div>

        {/* Search Input */}
        <div className="filter-search-box">
          <Search size={15} className="search-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Search 110 filters... (Use [ / ] to cycle)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Category Pills */}
        <div className="category-pills">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              className={`cat-pill ${activeCategory === cat.id ? 'active' : ''}`}
              onClick={() => setActiveCategory(cat.id)}
            >
              <span>{cat.label}</span>
              <span className="cat-count">{cat.count}</span>
            </button>
          ))}
        </div>

        {/* Visual Swatch Cards Grid */}
        <div className="filter-cards-grid">
          {filteredList.map((f) => (
            <div
              key={f.name}
              className={`swatch-card ${selectedFilter === f.name ? 'active' : ''}`}
              onClick={() => setSelectedFilter(f.name)}
              title={f.description}
            >
              <div
                className="swatch-preview-tile"
                style={{ background: getFilterGradient(f.category, f.name) }}
              >
                <Sparkles size={14} style={{ color: 'rgba(255,255,255,0.7)', filter: 'drop-shadow(0 0 3px rgba(0,0,0,0.6))' }} />
              </div>
              <div className="swatch-card-title">{f.name.replace(/_/g, ' ').toUpperCase()}</div>
              <div className="swatch-card-meta">
                <span>{f.category.toUpperCase()}</span>
                {selectedFilter === f.name && (
                  <span style={{ color: 'var(--neon-cyan)', fontWeight: 800 }}>ACTIVE</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 2. CENTER PANEL: STAGE & PRO CANVAS */}
      <div>
        {/* Sample Presets & Quick Actions Toolbar */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px', flexWrap: 'wrap', gap: '8px' }}>
          <div className="sample-presets-bar">
            <span>Presets:</span>
            {PRESETS.map((p) => (
              <button
                key={p.name}
                className="preset-chip"
                onClick={() => setOriginalSrc(p.path)}
              >
                {p.name}
              </button>
            ))}
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept="image/*"
              style={{ display: 'none' }}
            />
            <button
              className="btn-secondary"
              style={{ width: 'auto', padding: '0.4rem 0.85rem' }}
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload size={14} />
              <span>Upload Photo</span>
            </button>

            <button
              className="btn-secondary"
              style={{ width: 'auto', padding: '0.4rem 0.85rem', borderColor: 'rgba(255, 0, 127, 0.4)' }}
              onClick={() => setShowBatchModal(true)}
              title="Bulk-transform photos in parallel"
            >
              <Archive size={14} style={{ color: 'var(--neon-pink)' }} />
              <span>Batch Studio</span>
            </button>

            <button
              className="ghost-btn"
              onClick={() => setShowShortcuts(true)}
              title="Keyboard Shortcuts (?)"
              style={{ padding: '0.4rem 0.6rem' }}
            >
              <HelpCircle size={15} />
            </button>
          </div>
        </div>

        {/* Interactive Draggable Split Canvas & Workstation */}
        <SplitSlider
          originalSrc={originalSrc}
          filteredSrc={filteredSrc}
          filterName={selectedFilter}
          isProcessing={isProcessing}
          viewMode={viewMode}
          setViewMode={setViewMode}
        />
      </div>

      {/* 3. RIGHT PANEL: FINISHING TOUCHES & PRO GRADING */}
      <div className="controls-sidebar">
        <div className="panel-card">
          <div className="panel-header">
            <h3 className="panel-title">
              <Sliders size={18} />
              <span>Finishing Touches</span>
            </h3>
          </div>

          {/* Intensity Slider */}
          <div className="control-group" style={{ marginBottom: '1.25rem' }}>
            <div className="control-label">
              <span>Filter Strength</span>
              <span className="control-val">{Math.round(intensity * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={intensity}
              onChange={(e) => setIntensity(parseFloat(e.target.value))}
              className="cyber-slider"
            />
          </div>

          {/* 7-Segment LED Date Stamp */}
          <div className="control-group" style={{ marginBottom: '1rem' }}>
            <div className="switch-row">
              <span className="switch-label">
                <Calendar size={15} style={{ color: 'var(--neon-amber)' }} />
                <span>Camera Date Stamp</span>
              </span>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={dateStampEnabled}
                  onChange={(e) => setDateStampEnabled(e.target.checked)}
                />
                <span className="toggle-slider" />
              </label>
            </div>

            {dateStampEnabled && (
              <div className="date-input-wrap">
                <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>DATE:</span>
                <input
                  type="text"
                  className="date-input"
                  value={dateStampText}
                  onChange={(e) => setDateStampText(e.target.value)}
                  placeholder="'94 12 25"
                />
              </div>
            )}
          </div>

          {/* Frame Borders */}
          <div className="control-group" style={{ marginBottom: '1rem' }}>
            <span className="control-label">Analog Frame Border</span>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '6px' }}>
              <button
                className={`preset-chip ${frameBorder === 'none' ? 'active' : ''}`}
                onClick={() => setFrameBorder('none')}
                style={{ textAlign: 'center', borderColor: frameBorder === 'none' ? 'var(--neon-cyan)' : 'var(--border-glass)' }}
              >
                None
              </button>
              <button
                className={`preset-chip ${frameBorder === 'polaroid' ? 'active' : ''}`}
                onClick={() => setFrameBorder('polaroid')}
                style={{ textAlign: 'center', borderColor: frameBorder === 'polaroid' ? 'var(--neon-pink)' : 'var(--border-glass)' }}
              >
                Polaroid
              </button>
              <button
                className={`preset-chip ${frameBorder === 'filmstrip' ? 'active' : ''}`}
                onClick={() => setFrameBorder('filmstrip')}
                style={{ textAlign: 'center', borderColor: frameBorder === 'filmstrip' ? 'var(--neon-amber)' : 'var(--border-glass)' }}
              >
                35mm Film
              </button>
            </div>
          </div>

          {/* Film Grain Slider */}
          <div className="control-group" style={{ marginBottom: '1.25rem' }}>
            <div className="control-label">
              <span>Analog Film Grain</span>
              <span className="control-val">{Math.round(grainAmount * 200)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="0.3"
              step="0.02"
              value={grainAmount}
              onChange={(e) => setGrainAmount(parseFloat(e.target.value))}
              className="cyber-slider"
            />
          </div>

          {/* Light Leak Switch */}
          <div className="control-group" style={{ marginBottom: '0.75rem' }}>
            <div className="switch-row">
              <span className="switch-label">
                <Sparkles size={15} style={{ color: 'var(--neon-pink)' }} />
                <span>Vintage Light Leak</span>
              </span>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={lightLeak}
                  onChange={(e) => setLightLeak(e.target.checked)}
                />
                <span className="toggle-slider" />
              </label>
            </div>
          </div>

          {/* VHS OSD Switch */}
          <div className="control-group" style={{ marginBottom: '1.25rem' }}>
            <div className="switch-row">
              <span className="switch-label">
                <Film size={15} style={{ color: 'var(--neon-cyan)' }} />
                <span>VHS OSD Play Overlay</span>
              </span>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={vhsOsd}
                  onChange={(e) => setVhsOsd(e.target.checked)}
                />
                <span className="toggle-slider" />
              </label>
            </div>
          </div>

          {/* Collapsible Lightroom-Style Pro Grading Drawer */}
          <div className="pro-grading-panel" style={{ marginBottom: '1.25rem' }}>
            <div 
              className="pro-grading-header"
              onClick={() => setShowProGrading((prev) => !prev)}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)' }}>
                <Layers size={14} style={{ color: 'var(--neon-cyan)' }} />
                <span>Pro Color Grading</span>
              </div>
              {showProGrading ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </div>

            {showProGrading && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '6px' }}>
                <div className="pro-slider-row">
                  <div className="pro-slider-label">
                    <span>Exposure</span>
                    <span>{proExposure > 0 ? `+${proExposure}` : proExposure}</span>
                  </div>
                  <input
                    type="range"
                    min="-0.5"
                    max="0.5"
                    step="0.05"
                    value={proExposure}
                    onChange={(e) => setProExposure(parseFloat(e.target.value))}
                    className="cyber-slider"
                  />
                </div>

                <div className="pro-slider-row">
                  <div className="pro-slider-label">
                    <span>Contrast Slope</span>
                    <span>{proContrast}x</span>
                  </div>
                  <input
                    type="range"
                    min="0.5"
                    max="1.8"
                    step="0.05"
                    value={proContrast}
                    onChange={(e) => setProContrast(parseFloat(e.target.value))}
                    className="cyber-slider"
                  />
                </div>

                <div className="pro-slider-row">
                  <div className="pro-slider-label">
                    <span>Temperature</span>
                    <span>{proTemp > 0 ? `+${proTemp}` : proTemp}</span>
                  </div>
                  <input
                    type="range"
                    min="-0.5"
                    max="0.5"
                    step="0.05"
                    value={proTemp}
                    onChange={(e) => setProTemp(parseFloat(e.target.value))}
                    className="cyber-slider"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Action & Download Buttons */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <button
              className="btn-primary"
              onClick={handleDownload}
              disabled={!filteredSrc}
            >
              <Download size={18} />
              <span>Download Master JPEG (Ctrl+S)</span>
            </button>

            <button
              className="btn-secondary"
              onClick={handleGenerateGif}
              disabled={isGeneratingGif}
            >
              <RefreshCw size={16} className={isGeneratingGif ? 'spin' : ''} />
              <span>{isGeneratingGif ? 'Rendering GIF...' : 'Export Looping GIF'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Batch Processing Studio Modal */}
      {showBatchModal && (
        <BatchModal
          onClose={() => setShowBatchModal(false)}
          allFilters={allFilters}
          defaultFilter={selectedFilter}
          onBatchStarted={(jobId) => setActiveBatchJobId(jobId)}
        />
      )}

      {/* Shortcuts Cheatsheet Modal */}
      {showShortcuts && (
        <ShortcutsModal onClose={() => setShowShortcuts(false)} />
      )}

      {/* Live WebSocket Progress HUD for Batch Jobs */}
      {activeBatchJobId && (
        <JobProgressModal
          jobId={activeBatchJobId}
          onClose={() => setActiveBatchJobId(null)}
        />
      )}
    </div>
  );
}
