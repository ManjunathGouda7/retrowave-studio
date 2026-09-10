import React, { useState, useEffect } from 'react';
import { ListOrdered, RefreshCw, Download, StopCircle, Eye, Film, Image as ImageIcon, Clock } from 'lucide-react';
import JobProgressModal from './JobProgressModal';

export default function QueueMonitor() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedJobId, setSelectedJobId] = useState(null);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/jobs');
      if (res.ok) {
        const data = await res.json();
        setJobs(data.jobs || []);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 3500);
    return () => clearInterval(interval);
  }, []);

  const handleCancel = async (jobId) => {
    try {
      await fetch(`/api/v1/jobs/${jobId}`, { method: 'DELETE' });
      fetchJobs();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
      <div className="panel-card">
        <div className="panel-header">
          <h3 className="panel-title">
            <ListOrdered size={20} />
            <span>Distributed Asynchronous Job Queue</span>
          </h3>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
              Auto-refreshing every 3.5s
            </span>
            <button
              className="btn-secondary"
              style={{ width: 'auto', padding: '0.35rem 0.75rem' }}
              onClick={fetchJobs}
            >
              <RefreshCw size={14} className={loading ? 'spin' : ''} />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {jobs.length === 0 ? (
          <div style={{ padding: '3.5rem 1rem', textAlign: 'center', color: 'var(--text-dim)' }}>
            <Clock size={40} style={{ marginBottom: '1rem', opacity: 0.4 }} />
            <p style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>No Active or Recent Jobs</p>
            <p style={{ fontSize: '0.85rem' }}>Submit a video render or asynchronous image task to track it here in real-time.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {jobs.map((job) => {
              const isCompleted = job.status === 'completed';
              const isProcessing = job.status === 'processing';
              const isFailed = job.status === 'failed';
              const isCancelled = job.status === 'cancelled';

              return (
                <div
                  key={job.job_id}
                  style={{
                    background: 'var(--bg-tertiary)',
                    border: '1px solid var(--border-glass)',
                    borderRadius: '8px',
                    padding: '1rem 1.25rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: '1rem',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div
                      style={{
                        width: '36px',
                        height: '36px',
                        borderRadius: '8px',
                        background: job.job_type === 'video' ? 'rgba(255, 0, 127, 0.15)' : 'rgba(0, 240, 255, 0.15)',
                        color: job.job_type === 'video' ? 'var(--neon-pink)' : 'var(--neon-cyan)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      {job.job_type === 'video' ? <Film size={18} /> : <ImageIcon size={18} />}
                    </div>

                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '2px' }}>
                        <span style={{ fontWeight: 600, fontSize: '0.9rem', color: '#ffffff' }}>
                          {job.metadata?.filter_name ? job.metadata.filter_name.replace(/_/g, ' ').toUpperCase() : 'TRANSFORMATION'}
                        </span>
                        <span
                          style={{
                            fontSize: '0.68rem',
                            padding: '1px 6px',
                            borderRadius: '10px',
                            fontWeight: 700,
                            textTransform: 'uppercase',
                            background: isCompleted
                              ? 'rgba(0, 255, 136, 0.15)'
                              : isProcessing
                              ? 'rgba(0, 240, 255, 0.15)'
                              : isFailed
                              ? 'rgba(255, 71, 87, 0.15)'
                              : 'rgba(255, 255, 255, 0.1)',
                            color: isCompleted
                              ? 'var(--neon-green)'
                              : isProcessing
                              ? 'var(--neon-cyan)'
                              : isFailed
                              ? '#ff4757'
                              : 'var(--text-muted)',
                            border: `1px solid ${
                              isCompleted ? 'var(--neon-green)' : isProcessing ? 'var(--neon-cyan)' : 'var(--border-glass)'
                            }`,
                          }}
                        >
                          {job.status}
                        </span>
                      </div>

                      <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                        {job.current_step || 'In queue'} • Created: {new Date(job.created_at).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>

                  {/* Progress & Actions */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <div style={{ width: '120px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', marginBottom: '4px' }}>
                        <span style={{ color: 'var(--text-dim)' }}>Progress</span>
                        <span style={{ fontWeight: 700, color: 'var(--neon-cyan)' }}>{job.progress}%</span>
                      </div>
                      <div style={{ height: '4px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '2px', overflow: 'hidden' }}>
                        <div
                          style={{
                            height: '100%',
                            width: `${job.progress}%`,
                            background: isCompleted ? 'var(--neon-green)' : 'var(--grad-primary)',
                            transition: 'width 0.3s ease',
                          }}
                        />
                      </div>
                    </div>

                    <div style={{ display: 'flex', gap: '6px' }}>
                      <button
                        className="ghost-btn"
                        onClick={() => setSelectedJobId(job.job_id)}
                        title="Open Live HUD Monitor"
                      >
                        <Eye size={14} />
                      </button>

                      {isCompleted && (
                        <a
                          href={`/api/v1/jobs/${job.job_id}/download`}
                          download
                          className="ghost-btn"
                          title="Download Artifact"
                        >
                          <Download size={14} />
                        </a>
                      )}

                      {(isProcessing || job.status === 'queued') && (
                        <button
                          className="ghost-btn"
                          onClick={() => handleCancel(job.job_id)}
                          style={{ color: '#ff4757', borderColor: 'rgba(255, 71, 87, 0.3)' }}
                          title="Cancel Job"
                        >
                          <StopCircle size={14} />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {selectedJobId && (
        <JobProgressModal
          jobId={selectedJobId}
          onClose={() => setSelectedJobId(null)}
        />
      )}
    </div>
  );
}
