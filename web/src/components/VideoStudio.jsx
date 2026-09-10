import React, { useState, useRef, useEffect } from 'react';
import { Film, Play, Upload, Sparkles, Sliders, Zap, CheckSquare, Square, Download } from 'lucide-react';
import JobProgressModal from './JobProgressModal';

const TIME_EFFECTS = [
  { id: 'vhs_wobble', label: 'VHS Tracking Wobble', desc: 'Analog tape sync drift' },
  { id: 'timestamp', label: 'Blinking Timestamp', desc: '7-segment camcorder OSD' },
  { id: 'pulse', label: 'Rhythmic Pulse', desc: 'Pulsing brightness bloom' },
  { id: 'strobe', label: 'Neon Strobe Flash', desc: 'Periodic color pulse' },
  { id: 'glitch_interval', label: 'Glitch Interval', desc: 'Periodic RGB datamosh' },
  { id: 'zoom_punch', label: 'Zoom Punch', desc: 'Bass-drop camera shake' },
  { id: 'film_burn', label: 'Vintage Film Burn', desc: 'Random edge light leak flares' },
  { id: 'chromatic_cycle', label: 'Chromatic Cycle', desc: 'Rotating color fringing' },
];

export default function VideoStudio() {
  const [videoSrc, setVideoSrc] = useState('/samples/sample_clip.mp4');
  const [videoFile, setVideoFile] = useState(null);
  const [selectedFilter, setSelectedFilter] = useState('cyber_blade_runner');
  const [intensity, setIntensity] = useState(1.0);
  const [fps, setFps] = useState(15);
  const [previewOnly, setPreviewOnly] = useState(true);
  const [selectedEffects, setSelectedEffects] = useState(['vhs_wobble', 'timestamp']);
  const [videoFormat, setVideoFormat] = useState('mp4');
  const [allFilters, setAllFilters] = useState([]);

  // Active Job HUD modal
  const [activeJobId, setActiveJobId] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fileInputRef = useRef(null);

  useEffect(() => {
    fetch('/api/v1/filters')
      .then((r) => r.json())
      .then((d) => d.filters && setAllFilters(d.filters))
      .catch(() => {});
  }, []);

  const toggleEffect = (effectId) => {
    setSelectedEffects((prev) =>
      prev.includes(effectId)
        ? prev.filter((id) => id !== effectId)
        : [...prev, effectId]
    );
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setVideoFile(file);
      setVideoSrc(URL.createObjectURL(file));
    }
  };

  const handleSubmitJob = async () => {
    setIsSubmitting(true);

    try {
      let fileToUpload = videoFile;
      if (!fileToUpload) {
        // Fetch the default sample video clip blob
        const res = await fetch(videoSrc);
        fileToUpload = await res.blob();
      }

      const formData = new FormData();
      formData.append('file', fileToUpload, 'video.mp4');
      formData.append('filter_name', selectedFilter);
      formData.append('intensity', intensity.toString());
      formData.append('fps', fps.toString());
      formData.append('preview', previewOnly.toString());
      formData.append('video_format', videoFormat);

      if (selectedEffects.length > 0) {
        formData.append('time_effects', selectedEffects.join(','));
      }

      const response = await fetch('/api/v1/jobs/video', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setActiveJobId(data.job_id);
      } else {
        alert('Failed to submit video rendering job.');
      }
    } catch (err) {
      console.error(err);
      alert('Error connecting to backend video queue.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="video-grid">
      {/* LEFT: VIDEO PLAYER & PREVIEW */}
      <div className="stage-panel">
        <div className="stage-toolbar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Film size={16} style={{ color: 'var(--neon-pink)' }} />
            <span style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '0.95rem' }}>
              Dynamic Video Player & Canvas
            </span>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              className="preset-chip"
              onClick={() => {
                setVideoFile(null);
                setVideoSrc('/samples/sample_clip.mp4');
              }}
            >
              Load Sample Clip
            </button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept="video/mp4,video/mov,video/avi,video/mkv"
              style={{ display: 'none' }}
            />
            <button
              className="btn-secondary"
              style={{ width: 'auto', padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload size={13} />
              <span>Upload Video</span>
            </button>
          </div>
        </div>

        <div className="canvas-wrapper" style={{ minHeight: '480px', background: '#030508' }}>
          {videoSrc ? (
            <video
              src={videoSrc}
              controls
              loop
              style={{ width: '100%', maxHeight: '520px', display: 'block', borderRadius: '12px' }}
            />
          ) : (
            <div className="dropzone" onClick={() => fileInputRef.current?.click()}>
              <div className="dropzone-icon">
                <Film size={32} />
              </div>
              <h3 className="dropzone-title">Drop your video clip here</h3>
              <p className="dropzone-sub">Supports MP4, MOV, AVI, MKV up to 100MB</p>
            </div>
          )}
        </div>
      </div>

      {/* RIGHT: VIDEO CONTROLS & EFFECTS */}
      <div className="controls-sidebar">
        <div className="panel-card">
          <div className="panel-header">
            <h3 className="panel-title">
              <Zap size={18} />
              <span>Video Engine Controls</span>
            </h3>
          </div>

          {/* Select Filter */}
          <div className="control-group" style={{ marginBottom: '1rem' }}>
            <span className="control-label">Retro Filter Preset</span>
            <select
              className="search-input"
              style={{ paddingLeft: '0.85rem' }}
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

          {/* Intensity */}
          <div className="control-group" style={{ marginBottom: '1rem' }}>
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

          {/* FPS Selector */}
          <div className="control-group" style={{ marginBottom: '1rem' }}>
            <span className="control-label">Target Framerate (FPS)</span>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '6px' }}>
              {[12, 15, 24, 30].map((f) => (
                <button
                  key={f}
                  className={`preset-chip ${fps === f ? 'active' : ''}`}
                  onClick={() => setFps(f)}
                  style={{ textAlign: 'center', borderColor: fps === f ? 'var(--neon-cyan)' : 'var(--border-glass)' }}
                >
                  {f} FPS
                </button>
              ))}
            </div>
          </div>

          {/* 3-Second Quick Preview Toggle */}
          <div className="control-group" style={{ marginBottom: '1.15rem' }}>
            <div className="switch-row">
              <span className="switch-label">
                <Sparkles size={15} style={{ color: 'var(--neon-pink)' }} />
                <span>3-Second Fast Preview</span>
              </span>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={previewOnly}
                  onChange={(e) => setPreviewOnly(e.target.checked)}
                />
                <span className="toggle-slider" />
              </label>
            </div>
          </div>

          {/* 8 Dynamic Temporal Effects */}
          <div className="control-group" style={{ marginBottom: '1.25rem' }}>
            <span className="control-label">Dynamic Time-Based Effects</span>
            <div className="effects-grid">
              {TIME_EFFECTS.map((eff) => {
                const isActive = selectedEffects.includes(eff.id);
                return (
                  <div
                    key={eff.id}
                    className={`effect-card ${isActive ? 'active' : ''}`}
                    onClick={() => toggleEffect(eff.id)}
                  >
                    <div>
                      <div style={{ fontWeight: 600 }}>{eff.label}</div>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>{eff.desc}</div>
                    </div>
                    {isActive ? (
                      <CheckSquare size={14} style={{ color: 'var(--neon-cyan)' }} />
                    ) : (
                      <Square size={14} style={{ color: 'var(--text-dim)' }} />
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Output Format */}
          <div className="control-group" style={{ marginBottom: '1.5rem' }}>
            <span className="control-label">Export Format</span>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              <button
                className={`preset-chip ${videoFormat === 'mp4' ? 'active' : ''}`}
                onClick={() => setVideoFormat('mp4')}
                style={{ textAlign: 'center', padding: '0.4rem', borderColor: videoFormat === 'mp4' ? 'var(--neon-cyan)' : 'var(--border-glass)' }}
              >
                MP4 Video (H.264)
              </button>
              <button
                className={`preset-chip ${videoFormat === 'gif' ? 'active' : ''}`}
                onClick={() => setVideoFormat('gif')}
                style={{ textAlign: 'center', padding: '0.4rem', borderColor: videoFormat === 'gif' ? 'var(--neon-pink)' : 'var(--border-glass)' }}
              >
                Animated Looping GIF
              </button>
            </div>
          </div>

          {/* Submit Render Button */}
          <button
            className="btn-primary"
            onClick={handleSubmitJob}
            disabled={isSubmitting}
          >
            <Play size={18} />
            <span>{isSubmitting ? 'Queueing Worker Task...' : 'Render Video (WebSocket HUD)'}</span>
          </button>
        </div>
      </div>

      {/* Real-time WebSocket Progress HUD */}
      {activeJobId && (
        <JobProgressModal
          jobId={activeJobId}
          onClose={() => setActiveJobId(null)}
        />
      )}
    </div>
  );
}
