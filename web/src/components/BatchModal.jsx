import React, { useState, useRef } from 'react';
import { X, Archive, Upload, Sparkles, CheckCircle2, Image as ImageIcon, Trash2 } from 'lucide-react';
import JSZip from 'jszip';

export default function BatchModal({
  onClose,
  allFilters,
  defaultFilter,
  onBatchStarted,
}) {
  const [files, setFiles] = useState([]);
  const [selectedFilter, setSelectedFilter] = useState(defaultFilter || 'cyber_neon');
  const [intensity, setIntensity] = useState(1.0);
  const [dateStamp, setDateStamp] = useState("'94 12 25");
  const [dateStampEnabled, setDateStampEnabled] = useState(true);
  const [frameBorder, setFrameBorder] = useState('none');
  const [isZipping, setIsZipping] = useState(false);

  const fileInputRef = useRef(null);

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files) {
      addFiles(Array.from(e.dataTransfer.files));
    }
  };

  const addFiles = (newFiles) => {
    const valid = newFiles.filter((f) => {
      const ext = f.name.toLowerCase();
      return (
        ext.endsWith('.jpg') ||
        ext.endsWith('.jpeg') ||
        ext.endsWith('.png') ||
        ext.endsWith('.webp') ||
        ext.endsWith('.zip')
      );
    });
    setFiles((prev) => [...prev, ...valid]);
  };

  const removeFile = (idx) => {
    setFiles((prev) => prev.filter((_, i) => i !== idx));
  };

  const handleStartBatch = async () => {
    if (files.length === 0) return;
    setIsZipping(true);

    try {
      let zipBlob;

      // If user uploaded a single .zip file directly
      if (files.length === 1 && files[0].name.toLowerCase().endsWith('.zip')) {
        zipBlob = files[0];
      } else {
        // Zip all loose image files using JSZip
        const zip = new JSZip();
        for (const f of files) {
          const buffer = await f.arrayBuffer();
          zip.file(f.name, buffer);
        }
        zipBlob = await zip.generateAsync({ type: 'blob' });
      }

      const formData = new FormData();
      formData.append('file', zipBlob, 'batch_upload.zip');
      formData.append('filter_name', selectedFilter);
      formData.append('intensity', intensity.toString());
      if (dateStampEnabled && dateStamp) {
        formData.append('date_stamp', dateStamp);
      }
      if (frameBorder === 'polaroid') {
        formData.append('polaroid', 'true');
      } else if (frameBorder === 'filmstrip') {
        formData.append('film_border', 'true');
      }

      const res = await fetch('/api/v1/jobs/batch', {
        method: 'POST',
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();
        onBatchStarted(data.job_id);
        onClose();
      } else {
        alert('Failed to submit batch job to worker queue.');
      }
    } catch (err) {
      console.error(err);
      alert('Error bundling batch files.');
    } finally {
      setIsZipping(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="batch-modal-box" onClick={(e) => e.stopPropagation()}>
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

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '0.4rem' }}>
          <Archive size={22} style={{ color: 'var(--neon-pink)' }} />
          <h3 style={{ fontFamily: 'Orbitron, sans-serif', fontSize: '1.2rem', color: '#ffffff' }}>
            BATCH PROCESSING STUDIO
          </h3>
        </div>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: '1.25rem' }}>
          Bulk-transform photos in parallel via our high-speed asynchronous worker queue.
        </p>

        {/* Dropzone */}
        <div
          className="batch-drop-area"
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <Upload size={36} style={{ color: 'var(--neon-pink)', margin: '0 auto 0.75rem', opacity: 0.8 }} />
          <h4 style={{ fontSize: '0.95rem', color: '#ffffff', marginBottom: '4px' }}>
            Drop loose photos or a .ZIP archive here
          </h4>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
            Supports JPEG, PNG, WEBP, or ZIP archives (Click to browse)
          </p>
          <input
            type="file"
            ref={fileInputRef}
            onChange={(e) => e.target.files && addFiles(Array.from(e.target.files))}
            multiple
            accept=".jpg,.jpeg,.png,.webp,.zip"
            style={{ display: 'none' }}
          />
        </div>

        {/* Selected Files List */}
        {files.length > 0 && (
          <div style={{ marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
              <span>{files.length} Files Ready for Processing</span>
              <button
                onClick={() => setFiles([])}
                style={{ background: 'none', border: 'none', color: '#ff4757', cursor: 'pointer', fontSize: '0.75rem' }}
              >
                Clear all
              </button>
            </div>
            <div className="batch-file-chips">
              {files.map((f, i) => (
                <div key={i} className="batch-chip">
                  <ImageIcon size={12} style={{ color: 'var(--neon-cyan)' }} />
                  <span>{f.name}</span>
                  <button
                    onClick={() => removeFile(i)}
                    style={{ background: 'none', border: 'none', color: 'var(--text-dim)', cursor: 'pointer', display: 'flex' }}
                  >
                    <X size={12} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Batch Configuration */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '1.5rem' }}>
          <div>
            <span className="control-label" style={{ marginBottom: '4px' }}>Retro Filter</span>
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

          <div>
            <span className="control-label" style={{ marginBottom: '4px' }}>Analog Frame</span>
            <select
              className="search-input"
              value={frameBorder}
              onChange={(e) => setFrameBorder(e.target.value)}
            >
              <option value="none">No Border</option>
              <option value="polaroid">Polaroid Frame</option>
              <option value="filmstrip">35mm Negative Filmstrip</option>
            </select>
          </div>
        </div>

        {/* Submit */}
        <button
          className="btn-primary"
          onClick={handleStartBatch}
          disabled={files.length === 0 || isZipping}
        >
          <Sparkles size={18} />
          <span>{isZipping ? 'Packaging & Queueing Batch...' : `Process ${files.length} Media Files`}</span>
        </button>
      </div>
    </div>
  );
}
