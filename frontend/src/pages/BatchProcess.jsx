import { useState } from 'react';
import { Upload, Download, FileImage, CheckCircle, Loader } from 'lucide-react';
import './BatchProcess.css';

export default function BatchProcess() {
    const [files, setFiles] = useState([]);
    const [processing, setProcessing] = useState(false);
    const [results, setResults] = useState(null);
    const [progress, setProgress] = useState(0);

    const handleFileSelect = (e) => {
        const selectedFiles = Array.from(e.target.files);
        setFiles(selectedFiles);
    };

    const startBatchProcess = async () => {
        if (files.length === 0) return;

        setProcessing(true);
        setProgress(0);

        const formData = new FormData();
        files.forEach(file => {
            formData.append('files', file);
        });

        try {
            const response = await fetch('http://localhost:8000/batch_process', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            setResults(data);
            setProgress(100);
            setProcessing(false);
        } catch (error) {
            console.error('Batch processing failed:', error);
            setProcessing(false);
        }
    };

    const downloadEnhanced = (filename) => {
        window.open(`http://localhost:8000/static/batch_enhanced/${filename}`, '_blank');
    };

    const downloadAll = () => {
        window.open('http://localhost:8000/download_batch_results', '_blank');
    };

    return (
        <div className="batch-process-page">
            <div className="page-header mb-xl">
                <div>
                    <h2 className="text-3xl font-bold">Batch Image Processing</h2>
                    <p className="text-secondary mt-sm">
                        Upload multiple blurry images and get AI-enhanced versions with OCR text extraction
                    </p>
                </div>
            </div>

            {!processing && !results && (
                <div className="upload-section">
                    <div className="card upload-card">
                        <div className="upload-zone">
                            <FileImage size={48} className="upload-icon" />
                            <h3 className="text-xl font-semibold mt-md">Select Images</h3>
                            <p className="text-secondary mt-sm mb-lg">
                                Choose multiple images from your folder
                            </p>
                            <input
                                type="file"
                                multiple
                                accept="image/*"
                                onChange={handleFileSelect}
                                style={{ display: 'none' }}
                                id="batch-file-input"
                            />
                            <label htmlFor="batch-file-input" className="btn btn-primary">
                                <Upload size={16} />
                                Browse Images
                            </label>
                        </div>

                        {files.length > 0 && (
                            <div className="file-list mt-lg">
                                <h4 className="font-semibold mb-md">Selected Files ({files.length})</h4>
                                <div className="files-grid">
                                    {files.slice(0, 10).map((file, idx) => (
                                        <div key={idx} className="file-item">
                                            <FileImage size={16} />
                                            <span className="file-name">{file.name}</span>
                                        </div>
                                    ))}
                                    {files.length > 10 && (
                                        <div className="file-item text-secondary">
                                            + {files.length - 10} more files
                                        </div>
                                    )}
                                </div>
                                <button className="btn btn-primary btn-lg mt-lg" onClick={startBatchProcess}>
                                    Start Processing
                                    <Upload size={18} />
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {processing && (
                <div className="processing-section">
                    <div className="card text-center p-xl">
                        <Loader size={48} className="spinner mx-auto" />
                        <h3 className="text-xl font-semibold mt-lg">Processing Images...</h3>
                        <p className="text-secondary mt-sm">
                            Applying AI deblurring and extracting text
                        </p>
                        <div className="progress-bar mt-lg">
                            <div className="progress-fill" style={{ width: `${progress}%` }}></div>
                        </div>
                        <p className="text-sm text-secondary mt-sm">{progress}% Complete</p>
                    </div>
                </div>
            )}

            {results && (
                <div className="results-section">
                    <div className="card mb-lg">
                        <div className="flex-between mb-lg">
                            <div>
                                <h3 className="text-2xl font-bold">Processing Complete</h3>
                                <p className="text-secondary mt-sm">
                                    {results.processed} images enhanced and analyzed
                                </p>
                            </div>
                            <div className="flex gap-md">
                                <button className="btn btn-primary" onClick={downloadAll}>
                                    <Download size={16} />
                                    Download All
                                </button>
                                <button className="btn btn-secondary" onClick={() => {
                                    setResults(null);
                                    setFiles([]);
                                }}>
                                    Process More
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-2 gap-lg">
                        {results.results?.map((result, idx) => (
                            <div key={idx} className="card result-card">
                                <div className="result-header">
                                    <CheckCircle size={20} className="text-success" />
                                    <span className="font-semibold">{result.filename}</span>
                                </div>

                                <div className="image-preview mt-md">
                                    <img
                                        src={`http://localhost:8000/static/batch_enhanced/${result.enhanced_filename}`}
                                        alt="Enhanced"
                                        className="preview-img"
                                    />
                                </div>

                                {result.ocr_text && result.ocr_text.length > 0 && (
                                    <div className="ocr-results mt-md">
                                        <h4 className="text-sm font-semibold mb-sm">Detected Text:</h4>
                                        <div className="ocr-text-box">
                                            {result.ocr_text.map((text, i) => (
                                                <div key={i} className="ocr-item">
                                                    <span className="ocr-content">{text.text}</span>
                                                    <span className="badge badge-primary">
                                                        {(text.confidence * 100).toFixed(0)}%
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                <button
                                    className="btn btn-outline btn-sm mt-md"
                                    onClick={() => downloadEnhanced(result.enhanced_filename)}
                                >
                                    <Download size={14} />
                                    Download
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
