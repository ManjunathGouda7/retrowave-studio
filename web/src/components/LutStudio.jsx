import React, { useState, useEffect, useRef } from 'react';
import { Palette, Sliders, Download, Sparkles, RefreshCw, Upload, Film, Eye } from 'lucide-react';
import confetti from 'canvas-confetti';

const LUT_PRESETS = [
  { name: 'Warm CineStill 800T', temp: 0.55, tint: 0.15, contrast: 1.35, sat: 1.25 },
  { name: 'Moody Blade Runner', temp: -0.4, tint: 0.35, contrast: 1.5, sat: 1.1 },
  { name: 'Cyberpunk Neon', temp: -0.6, tint: 0.6, contrast: 1.6, sat: 1.5 },
  { name: 'Vintage Kodachrome', temp: 0.35, tint: -0.1, contrast: 1.2, sat: 1.3 },
  { name: 'Bleach Bypass', temp: -0.2, tint: -0.15, contrast: 1.8, sat: 0.4 },
];

export default function LutStudio() {
  const [recipeName, setRecipeName] = useState('RETROWAVE_CUBIC');
  const [temperature, setTemperature] = useState(0.3);
  const [tint, setTint] = useState(0.1);
  const [contrast, setContrast] = useState(1.25);
  const [saturation, setSaturation] = useState(1.2);
  const [lutSize, setLutSize] = useState(33);

  // Selected filter for direct filter LUT export
  const [allFilters, setAllFilters] = useState([]);
  const [selectedFilter, setSelectedFilter] = useState('cyber_neon');

  // Preview canvas
  const [sampleSrc, setSampleSrc] = useState('/samples/cyberpunk_city.jpg');
  const [isExporting, setIsExporting] = useState(false);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetch('/api/v1/filters')
      .then((r) => r.json())
      .then((d) => d.filters && setAllFilters(d.filters))
      .catch(() => {});
  }, []);

  // Update canvas simulation
  useEffect(() => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = sampleSrc;
    img.onload = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      canvas.width = img.naturalWidth || 600;
      canvas.height = img.naturalHeight || 600;

      // Draw base
      ctx.drawImage(img, 0, 0);

      // Fast Client-side simulation of color matrix
      const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const data = imgData.data;

      const tempVal = temperature;
      const tintVal = tint;
      const contVal = contrast;
      const satVal = saturation;

      for (let i = 0; i < data.length; i += 4) {
        let r = data[i] / 255.0;
        let g = data[i + 1] / 255.0;
        let b = data[i + 2] / 255.0;

        // Temperature
        if (tempVal > 0) {
          r += tempVal * 0.15 * (1.0 - r);
          b -= tempVal * 0.12 * b;
        } else if (tempVal < 0) {
          const t = Math.abs(tempVal);
          b += t * 0.15 * (1.0 - b);
          r -= t * 0.12 * r;
        }

        // Tint
        if (tintVal > 0) {
          r += tintVal * 0.08 * (1.0 - r);
          b += tintVal * 0.08 * (1.0 - b);
          g -= tintVal * 0.08 * g;
        } else if (tintVal < 0) {
          const tn = Math.abs(tintVal);
          g += tn * 0.12 * (1.0 - g);
          r -= tn * 0.06 * r;
          b -= tn * 0.06 * b;
        }

        // Contrast
        r = 0.5 + (r - 0.5) * contVal;
        g = 0.5 + (g - 0.5) * contVal;
        b = 0.5 + (b - 0.5) * contVal;

        // Saturation
        const lum = 0.299 * r + 0.587 * g + 0.114 * b;
        r = lum + (r - lum) * satVal;
        g = lum + (g - lum) * satVal;
        b = lum + (b - lum) * satVal;

        data[i] = Math.max(0, Math.min(255, r * 255));
        data[i + 1] = Math.max(0, Math.min(255, g * 255));
        data[i + 2] = Math.max(0, Math.min(255, b * 255));
      }

      ctx.putImageData(imgData, 0, 0);
    };
  }, [sampleSrc, temperature, tint, contrast, saturation]);

  const applyPreset = (p) => {
    setRecipeName(p.name.toUpperCase().replace(/\s+/g, '_'));
    setTemperature(p.temp);
    setTint(p.tint);
    setContrast(p.contrast);
    setSaturation(p.sat);
  };

  const handleDownloadCustomLut = async () => {
    setIsExporting(true);
    try {
      const res = await fetch('/api/v1/lut/custom', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: recipeName,
          temperature,
          tint,
          contrast,
          saturation,
          size: lutSize,
        }),
      });

      if (res.ok) {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${recipeName.toLowerCase()}.cube`;
        a.click();

        confetti({
          particleCount: 50,
          spread: 60,
          colors: ['#00f0ff', '#ff007f', '#ffb700'],
        });
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsExporting(false);
    }
  };

  const handleDownloadFilterLut = () => {
    window.location.href = `/api/v1/lut/filter/${selectedFilter}?size=${lutSize}`;
  };

  return (
    <div className="studio-grid">
      {/* LEFT: RECIPE CONTROLS */}
      <div className="panel-card">
        <div className="panel-header">
          <h3 className="panel-title">
            <Palette size={18} />
            <span>3D LUT Grading Matrix</span>
          </h3>
          <span className="brand-badge">.CUBE 33x33</span>
        </div>

        {/* Recipe Presets */}
        <div style={{ marginBottom: '1.25rem' }}>
          <span className="control-label" style={{ marginBottom: '6px' }}>
            Color Science Presets
          </span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
            {LUT_PRESETS.map((p) => (
              <button
                key={p.name}
                className="preset-chip"
                style={{ textAlign: 'left', padding: '0.45rem 0.75rem', width: '100%' }}
                onClick={() => applyPreset(p)}
              >
                {p.name}
              </button>
            ))}
          </div>
        </div>

        {/* Recipe Name */}
        <div className="control-group" style={{ marginBottom: '1rem' }}>
          <span className="control-label">LUT Title (Shown in NLE)</span>
          <input
            type="text"
            className="search-input"
            value={recipeName}
            onChange={(e) => setRecipeName(e.target.value)}
          />
        </div>

        {/* Temperature */}
        <div className="control-group" style={{ marginBottom: '1rem' }}>
          <div className="control-label">
            <span>Color Temperature</span>
            <span className="control-val">{temperature > 0 ? `+${temperature}` : temperature}</span>
          </div>
          <input
            type="range"
            min="-1.0"
            max="1.0"
            step="0.05"
            value={temperature}
            onChange={(e) => setTemperature(parseFloat(e.target.value))}
            className="cyber-slider"
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', color: 'var(--text-dim)' }}>
            <span>Cool Cyan</span>
            <span>Warm Gold</span>
          </div>
        </div>

        {/* Tint */}
        <div className="control-group" style={{ marginBottom: '1rem' }}>
          <div className="control-label">
            <span>Tint (Green / Magenta)</span>
            <span className="control-val">{tint > 0 ? `+${tint}` : tint}</span>
          </div>
          <input
            type="range"
            min="-1.0"
            max="1.0"
            step="0.05"
            value={tint}
            onChange={(e) => setTint(parseFloat(e.target.value))}
            className="cyber-slider"
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', color: 'var(--text-dim)' }}>
            <span>Green Cast</span>
            <span>Magenta</span>
          </div>
        </div>

        {/* Contrast */}
        <div className="control-group" style={{ marginBottom: '1rem' }}>
          <div className="control-label">
            <span>S-Curve Contrast Slope</span>
            <span className="control-val">{contrast}x</span>
          </div>
          <input
            type="range"
            min="0.5"
            max="2.0"
            step="0.05"
            value={contrast}
            onChange={(e) => setContrast(parseFloat(e.target.value))}
            className="cyber-slider"
          />
        </div>

        {/* Saturation */}
        <div className="control-group" style={{ marginBottom: '1.25rem' }}>
          <div className="control-label">
            <span>Color Saturation</span>
            <span className="control-val">{Math.round(saturation * 100)}%</span>
          </div>
          <input
            type="range"
            min="0.0"
            max="2.0"
            step="0.05"
            value={saturation}
            onChange={(e) => setSaturation(parseFloat(e.target.value))}
            className="cyber-slider"
          />
        </div>

        {/* Export Custom LUT Button */}
        <button
          className="btn-primary"
          onClick={handleDownloadCustomLut}
          disabled={isExporting}
        >
          <Download size={18} />
          <span>{isExporting ? 'Generating Lattice...' : 'Export .cube 3D LUT'}</span>
        </button>
      </div>

      {/* CENTER: LIVE CANVAS SIMULATION */}
      <div className="stage-panel">
        <div className="stage-toolbar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Eye size={16} style={{ color: 'var(--neon-cyan)' }} />
            <span style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '0.95rem' }}>
              Real-Time 3D LUT Color Simulation
            </span>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <button className="preset-chip" onClick={() => setSampleSrc('/samples/cyberpunk_city.jpg')}>
              Cyber City
            </button>
            <button className="preset-chip" onClick={() => setSampleSrc('/samples/synthwave_car.jpg')}>
              Sunset Car
            </button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={(e) => e.target.files?.[0] && setSampleSrc(URL.createObjectURL(e.target.files[0]))}
              accept="image/*"
              style={{ display: 'none' }}
            />
            <button
              className="btn-secondary"
              style={{ width: 'auto', padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload size={13} />
              <span>Upload Photo</span>
            </button>
          </div>
        </div>

        <div className="canvas-wrapper" style={{ minHeight: '520px' }}>
          <canvas
            ref={canvasRef}
            style={{ maxWidth: '100%', maxHeight: '520px', objectFit: 'contain', display: 'block' }}
          />
          <span className="split-badge filtered" style={{ right: '1.5rem', bottom: '1.5rem' }}>
            {recipeName}
          </span>
        </div>
      </div>

      {/* RIGHT: FILTER TO LUT EXPORTER & SPECS */}
      <div className="controls-sidebar">
        <div className="panel-card">
          <div className="panel-header">
            <h3 className="panel-title">
              <Film size={18} />
              <span>110 Filter to 3D LUT</span>
            </h3>
          </div>

          <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: '1rem', lineHeight: '1.5' }}>
            Export any of Retrowave Studio's authentic 110 filters directly into an industry-grade 3D LUT for DaVinci Resolve, Adobe Premiere, and Final Cut Pro.
          </p>

          <div className="control-group" style={{ marginBottom: '1rem' }}>
            <span className="control-label">Select Retro Filter</span>
            <select
              className="search-input"
              value={selectedFilter}
              onChange={(e) => setSelectedFilter(e.target.value)}
            >
              {allFilters.map((f) => (
                <option key={f.name} value={f.name}>
                  {f.name.replace(/_/g, ' ').toUpperCase()} ({f.category})
                </option>
              ))}
            </select>
          </div>

          <div className="control-group" style={{ marginBottom: '1.5rem' }}>
            <span className="control-label">Lattice Grid Size</span>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '6px' }}>
              {[17, 33, 65].map((s) => (
                <button
                  key={s}
                  className={`preset-chip ${lutSize === s ? 'active' : ''}`}
                  onClick={() => setLutSize(s)}
                  style={{ textAlign: 'center', borderColor: lutSize === s ? 'var(--neon-cyan)' : 'var(--border-glass)' }}
                >
                  {s}³
                </button>
              ))}
            </div>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '4px' }}>
              33³ is recommended for Adobe Premiere & DaVinci Resolve.
            </span>
          </div>

          <button className="btn-secondary" onClick={handleDownloadFilterLut}>
            <Download size={16} />
            <span>Download Filter .cube LUT</span>
          </button>
        </div>

        {/* NLE Compatibility Badge Card */}
        <div className="panel-card" style={{ padding: '1rem' }}>
          <span style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--neon-cyan)', display: 'block', marginBottom: '8px' }}>
            COMPATIBLE APPLICATIONS:
          </span>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
            <span className="filter-tag">DaVinci Resolve</span>
            <span className="filter-tag">Adobe Premiere Pro</span>
            <span className="filter-tag">Final Cut Pro</span>
            <span className="filter-tag">Adobe After Effects</span>
            <span className="filter-tag">Photoshop</span>
            <span className="filter-tag">OBS Studio</span>
          </div>
        </div>
      </div>
    </div>
  );
}
