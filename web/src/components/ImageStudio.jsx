import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Sparkles, Sliders, Calendar, Image as ImageIcon, Download, 
  Upload, Search, Film, Wand2, RefreshCw, Layers
} from 'lucide-react';
import SplitSlider from './SplitSlider';

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

  // Images state
  const [originalSrc, setOriginalSrc] = useState('/samples/cyberpunk_city.jpg');
  const [filteredSrc, setFilteredSrc] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isGeneratingGif, setIsGeneratingGif] = useState(false);
  const [viewMode, setViewMode] = useState('split');

  const fileInputRef = useRef(null);

  // Fetch filter catalog
  useEffect(() => {
    fetch('/api/v1/filters')
      .then((res) => res.json())
      .then((data) => {
        if (data.filters) {
          setAllFilters(data.filters);
        }
      })
      .catch((err) => console.error('Failed to load filters list', err));
  }, []);

  // Process image using API
  const applyFilter = useCallback(async () => {
    if (!originalSrc) return;
    setIsProcessing(true);

    try {
      // Get image blob from originalSrc
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
      if (vhsOsd) {
        formData.append('vhs_osd', 'true');
      }
      if (lightLeak) {
        formData.append('light_leak', 'true');
      }
      if (grainAmount > 0) {
        formData.append('grain', grainAmount.toString());
      }
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

  // Filter list search & category filter
  const filteredList = allFilters.filter((f) => {
    const matchCat = activeCategory === 'all' || f.category === activeCategory;
    const matchSearch = f.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                        f.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchCat && matchSearch;
  });

  return (
    <div className="studio-grid">
      {/* 1. LEFT PANEL: FILTER EXPLORER */}
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
            placeholder="Search 110 filters..."
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

        {/* Scrollable Filters List */}
        <div className="filters-scroll">
          {filteredList.map((f) => (
            <div
              key={f.name}
              className={`filter-item-card ${selectedFilter === f.name ? 'active' : ''}`}
              onClick={() => setSelectedFilter(f.name)}
            >
              <div className="filter-info">
                <h4>{f.name.replace(/_/g, ' ')}</h4>
                <p>{f.description}</p>
              </div>
              <span className="filter-tag">{f.category}</span>
            </div>
          ))}
        </div>
      </div>

      {/* 2. CENTER PANEL: STAGE & SPLIT SLIDER */}
      <div>
        {/* Sample Presets & Quick Upload Row */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
          <div className="sample-presets-bar">
            <span>Sample Presets:</span>
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
              <span>Upload Custom Photo</span>
            </button>
          </div>
        </div>

        {/* Interactive Draggable Split Canvas */}
        <SplitSlider
          originalSrc={originalSrc}
          filteredSrc={filteredSrc}
          filterName={selectedFilter}
          isProcessing={isProcessing}
          viewMode={viewMode}
          setViewMode={setViewMode}
        />
      </div>

      {/* 3. RIGHT PANEL: FINISHING TOUCHES & EXPORTS */}
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
              <span>Filter Intensity</span>
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
          <div className="control-group" style={{ marginBottom: '1.5rem' }}>
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

          {/* Download & GIF Buttons */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <button
              className="btn-primary"
              onClick={handleDownload}
              disabled={!filteredSrc}
            >
              <Download size={18} />
              <span>Download Master JPEG</span>
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
    </div>
  );
}
