import { useState, useEffect, useRef } from 'react';
import { Upload, FileVideo, CheckCircle, ArrowRight, Clock } from 'lucide-react';
import '../styles/design-system.css';
import './UploadPage.css';

export default function UploadPage() {
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [processing, setProcessing] = useState(false);
    const [progress, setProgress] = useState(0);
    const [status, setStatus] = useState('');
    const [results, setResults] = useState(null);
    const [ocrMode, setOcrMode] = useState('wagon');

    // Time tracking
    const [elapsedTime, setElapsedTime] = useState(0);
    const [estimatedRemaining, setEstimatedRemaining] = useState(null);
    const [startTime, setStartTime] = useState(null);
    const timerRef = useRef(null);

    // Format time in mm:ss
    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    // Timer effect
    useEffect(() => {
        if (uploading || processing) {
            if (!startTime) {
                setStartTime(Date.now());
            }
            timerRef.current = setInterval(() => {
                const elapsed = Math.floor((Date.now() - (startTime || Date.now())) / 1000);
                setElapsedTime(elapsed);

                // Estimate remaining time based on progress
                if (progress > 0 && progress < 100) {
                    const totalEstimated = (elapsed / progress) * 100;
                    const remaining = Math.max(0, totalEstimated - elapsed);
                    setEstimatedRemaining(Math.floor(remaining));
                }
            }, 1000);
        } else {
            if (timerRef.current) {
                clearInterval(timerRef.current);
            }
            setStartTime(null);
            setElapsedTime(0);
            setEstimatedRemaining(null);
        }

        return () => {
            if (timerRef.current) clearInterval(timerRef.current);
        };
    }, [uploading, processing, startTime, progress]); // 'wagon' or 'normal'

    const handleDrop = (e) => {
        e.preventDefault();
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile && droppedFile.type.startsWith('video/')) {
            setFile(droppedFile);
        }
    };

    const handleFileSelect = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
        }
    };

    const startProcessing = async () => {
        if (!file) return;

        setUploading(true);
        setStatus('Uploading video...');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const uploadRes = await fetch('http://localhost:8000/upload_video', {
                method: 'POST',
                body: formData
            });
            const uploadData = await uploadRes.json();

            setUploading(false);
            setProcessing(true);
            setProgress(25);
            setStatus('NAFNet deblurring in progress...');

            await fetch('http://localhost:8000/enhance_frames', { method: 'POST' });

            setProgress(75);
            setStatus('Running PaddleOCR detection...');

            const scanRes = await fetch('http://localhost:8000/scan_wagons', { method: 'POST' });
            const scanData = await scanRes.json();

            setProgress(100);
            setStatus('Processing complete');
            setResults(scanData);
            setProcessing(false);

        } catch (error) {
            console.error('Processing failed:', error);
            setStatus('Error: ' + error.message);
            setUploading(false);
            setProcessing(false);
        }
    };

    return (
        <div className="upload-container">
            {!file && !processing && !results && (
                <div className="upload-section">
                    {/* Mode Selection Buttons */}
                    <div className="mode-selection mb-8">
                        <h3 className="text-lg font-semibold mb-4">Select Detection Mode</h3>
                        <div className="flex gap-4 justify-center">
                            <button
                                className={`mode-button ${ocrMode === 'wagon' ? 'active' : ''}`}
                                onClick={() => setOcrMode('wagon')}
                            >
                                <div className="mode-icon">
                                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <rect x="2" y="6" width="20" height="12" rx="2" />
                                        <circle cx="6" cy="18" r="2" />
                                        <circle cx="18" cy="18" r="2" />
                                        <line x1="6" y1="10" x2="18" y2="10" />
                                    </svg>
                                </div>
                                <div className="mode-title">Wagon Mode</div>
                                <div className="mode-description">11-Digit Wagon Numbers Only</div>
                                <div className="mode-example">e.g. ABC12345678</div>
                            </button>
                            <button
                                className={`mode-button ${ocrMode === 'normal' ? 'active' : ''}`}
                                onClick={() => setOcrMode('normal')}
                            >
                                <div className="mode-icon">
                                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                                        <polyline points="14,2 14,8 20,8" />
                                        <line x1="16" y1="13" x2="8" y2="13" />
                                        <line x1="16" y1="17" x2="8" y2="17" />
                                    </svg>
                                </div>
                                <div className="mode-title">General Mode</div>
                                <div className="mode-description">All Detectable Text</div>
                                <div className="mode-example">e.g. WAGON, ABC, 123</div>
                            </button>
                        </div>
                        <div className="mode-info mt-4">
                            <span className="badge badge-primary">
                                {ocrMode === 'wagon' ? 'Strict 11-digit validation' : 'Flexible text extraction'}
                            </span>
                        </div>
                    </div>

                    <div
                        className="upload-dropzone"
                        onDrop={handleDrop}
                        onDragOver={(e) => e.preventDefault()}
                    >
                        <div className="upload-icon-wrapper">
                            <Upload size={48} strokeWidth={1.5} />
                        </div>
                        <h2 className="upload-title">Upload Railway Video</h2>
                        <p className="text-secondary">Drop video file or click to browse</p>

                        <input
                            type="file"
                            accept="video/*"
                            onChange={handleFileSelect}
                            style={{ display: 'none' }}
                            id="file-input"
                        />
                        <label htmlFor="file-input" className="btn btn-primary btn-lg mt-6">
                            Select Video File
                        </label>

                        <div className="upload-features mt-6">
                            <div className="badge badge-success">NAFNet 33.7 dB</div>
                            <div className="badge badge-primary">PaddleOCR</div>
                            <div className="badge badge-success">FP16 Accelerated</div>
                        </div>
                    </div>
                </div>
            )}

            {file && !processing && !results && (
                <div className="file-preview-section">
                    <div className="card">
                        <div className="file-preview-header">
                            <FileVideo size={32} />
                            <div className="file-details">
                                <div className="file-name">{file.name}</div>
                                <div className="file-meta text-secondary">
                                    {(file.size / 1024 / 1024).toFixed(2)} MB
                                </div>
                            </div>
                        </div>

                        <div className="preview-actions mt-6">
                            <button className="btn btn-primary btn-lg" onClick={startProcessing}>
                                Start Processing <ArrowRight size={16} />
                            </button>
                            <button className="btn btn-secondary" onClick={() => setFile(null)}>
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {(uploading || processing) && (
                <div className="processing-section">
                    <div className="card processing-card">
                        <div className="processing-spinner"></div>
                        <h3 className="processing-status mt-6">{status}</h3>

                        {/* Time Display */}
                        <div className="time-display mt-4">
                            <div className="time-item">
                                <Clock size={16} />
                                <span className="time-label">Elapsed</span>
                                <span className="time-value">{formatTime(elapsedTime)}</span>
                            </div>
                            {estimatedRemaining !== null && (
                                <div className="time-item">
                                    <Clock size={16} />
                                    <span className="time-label">Remaining</span>
                                    <span className="time-value">{formatTime(estimatedRemaining)}</span>
                                </div>
                            )}
                        </div>

                        <div className="progress-wrapper mt-4">
                            <div className="progress-bar">
                                <div className="progress-fill" style={{ width: `${progress}%` }}></div>
                            </div>
                            <div className="progress-label text-secondary mt-2">{progress}% Complete</div>
                        </div>

                        {/* Timestamp */}
                        <div className="timestamp mt-4">
                            Started at {startTime ? new Date(startTime).toLocaleTimeString() : '--:--:--'}
                        </div>
                    </div>
                </div>
            )}

            {results && (
                <div className="results-section">
                    <div className="card">
                        <div className="results-header">
                            <div className="results-icon">
                                <CheckCircle size={24} />
                            </div>
                            <h2>Processing Complete</h2>
                        </div>

                        <div className="metrics-grid mt-8">
                            <div className="metric">
                                <div className="metric-value">{results.scanned_frames}</div>
                                <div className="metric-label">Frames Processed</div>
                            </div>
                            <div className="metric">
                                <div className="metric-value">{results.wagons?.length || 0}</div>
                                <div className="metric-label">Wagons Detected</div>
                            </div>
                            <div className="metric">
                                <div className="metric-value">33.7 dB</div>
                                <div className="metric-label">PSNR Quality</div>
                            </div>
                        </div>

                        {results.wagons && results.wagons.length > 0 && (
                            <div className="wagons-section mt-8">
                                <h3 className="mb-4">Detected Wagon Numbers</h3>
                                <div className="grid grid-3">
                                    {results.wagons.map((wagon, idx) => (
                                        <div key={idx} className="wagon-card card">
                                            <div className="wagon-number">{wagon.number}</div>
                                            <div className="wagon-confidence text-secondary">
                                                {(wagon.confidence * 100).toFixed(1)}% confidence
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        <div className="results-actions mt-8">
                            <button className="btn btn-primary" onClick={() => window.location.href = '/dashboard/comparison'}>
                                View Comparison <ArrowRight size={16} />
                            </button>
                            <button className="btn btn-secondary" onClick={() => {
                                setFile(null);
                                setResults(null);
                                setProgress(0);
                            }}>
                                Process Another
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
