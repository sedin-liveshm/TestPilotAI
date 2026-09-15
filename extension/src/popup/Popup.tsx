import { useState } from 'react';
import { Circle, Info, Layers, CheckCircle2 } from 'lucide-react';
import { RecorderStatus } from '../types/recorder';

export function Popup() {
  const [status, setStatus] = useState<RecorderStatus>('idle');
  const [infoNotice, setInfoNotice] = useState<string | null>(null);

  const handleRecordClick = () => {
    // Day 6 Scope: Do NOT pretend to record or capture events.
    // Display clear, accurate informational message indicating readiness.
    setInfoNotice('Recorder setup is ready. Recording will be enabled in the next step.');
  };

  const handleReset = () => {
    setStatus('idle');
    setInfoNotice(null);
  };

  return (
    <div className="popup-container">
      {/* Header */}
      <header className="popup-header">
        <div className="brand-section">
          <div className="brand-icon">TP</div>
          <h1 className="brand-title">TestPilot AI</h1>
        </div>
        <span className="version-badge">v0.1.0</span>
      </header>

      {/* Main Content Area */}
      <main className="popup-content">
        <div className="action-card">
          <div className="popup-hero">
            <h2 className="popup-headline">Record browser actions</h2>
            <p className="popup-description">
              Capture web interactions to generate canonical Test IR specifications for automated testing.
            </p>
          </div>

          {!infoNotice ? (
            <button
              id="record-btn"
              className="btn-primary"
              onClick={handleRecordClick}
              type="button"
            >
              <Circle className="w-4 h-4 fill-current text-white" />
              <span>Record</span>
            </button>
          ) : (
            <>
              <div className="info-box">
                <Info className="w-5 h-5 info-icon" />
                <div>
                  <div className="info-text-title">Recorder setup ready</div>
                  <div className="info-text-desc">{infoNotice}</div>
                </div>
              </div>

              <button
                id="reset-btn"
                className="btn-secondary"
                onClick={handleReset}
                type="button"
              >
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Dismiss</span>
              </button>
            </>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="popup-footer">
        <div className="status-indicator">
          <span className={`status-dot ${status === 'idle' ? 'idle' : ''}`} />
          <span>Status: {status === 'idle' ? 'Idle' : status}</span>
        </div>
        <div className="flex items-center gap-1">
          <Layers className="w-3 h-3 text-muted-foreground" />
          <span>Manifest V3</span>
        </div>
      </footer>
    </div>
  );
}
