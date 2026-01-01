import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, FileVideo, CheckCircle, Loader2, AlertCircle } from 'lucide-react';

function UploadSection() {
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState('');
    const [error, setError] = useState('');
    const [dragActive, setDragActive] = useState(false);
    const navigate = useNavigate();

    const handleFile = async (file) => {
        if (!file) return;
        if (!file.type.startsWith('video/')) {
            setError('Please upload a valid video file (MP4, MKV, etc.)');
            return;
        }

        setLoading(true);
        setError('');
        setStatus('Initializing secure upload...');

        const formData = new FormData();
        formData.append("file", file);

        try {
            // 1. Upload & Extract
            setStatus('Uploading video and extracting frames...');
            const res = await fetch('http://localhost:8000/upload_video', {
                method: 'POST',
                body: formData,
            });
            if (!res.ok) throw new Error('Upload failed. Please check server connection.');
            const data = await res.json();

            // 2. Analyze Blur
            setStatus(`Analyzing ${data.frames_extracted} frames for motion blur...`);
            const blurRes = await fetch('http://localhost:8000/analyze_blur', { method: 'POST' });
            if (!blurRes.ok) throw new Error('Blur analysis failed');

            // 3. Enhance
            setStatus('Enhancing blurred frames with AI...');
            const enhRes = await fetch('http://localhost:8000/enhance_frames', { method: 'POST' });
            if (!enhRes.ok) throw new Error('Enhancement failed');
            const enhData = await enhRes.json();

            // 4. Scan Wagons
            setStatus('Detecting wagon numbers (GPU Accelerated)...');
            const scanRes = await fetch('http://localhost:8000/scan_wagons', { method: 'POST' });
            if (!scanRes.ok) throw new Error('Wagon scanning failed');

            setStatus('Finalizing dashboard...');
            // Small delay to let user see success
            setTimeout(() => {
                navigate('/'); // Redirect to live dashboard
            }, 1000);

        } catch (err) {
            console.error(err);
            setError(err.message);
            setStatus('');
        } finally {
            setLoading(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    };

    const handleChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    };

    return (
        <div className="max-w-3xl mx-auto">
            <div className="bg-white border border-gray-300 rounded shadow-sm overflow-hidden">
                <div className="p-6 border-b border-gray-200 bg-gray-50">
                    <h3 className="text-lg font-bold text-[#16191f]">Input Source Configuration</h3>
                    <p className="text-sm text-[#545b64]">Upload raw CCTV footage to initialize the simulation stream.</p>
                </div>

                <div className="p-8">
                    <div
                        className={`relative border-2 border-dashed rounded-lg p-12 text-center transition-all duration-200 ease-in-out
                            ${dragActive ? 'border-[#ec7211] bg-[#fffbf7]' : 'border-gray-300 hover:border-[#ec7211] hover:bg-gray-50'}
                            ${loading ? 'opacity-50 pointer-events-none' : ''}
                        `}
                        onDragEnter={(e) => { e.preventDefault(); setDragActive(true); }}
                        onDragLeave={(e) => { e.preventDefault(); setDragActive(false); }}
                        onDragOver={(e) => { e.preventDefault(); }}
                        onDrop={handleDrop}
                    >
                        <input
                            type="file"
                            id="video-upload"
                            className="hidden"
                            accept="video/*"
                            onChange={handleChange}
                            disabled={loading}
                        />

                        {loading ? (
                            <div className="flex flex-col items-center justify-center py-4">
                                <Loader2 className="w-12 h-12 text-[#ec7211] animate-spin mb-4" />
                                <h4 className="text-[#16191f] font-bold text-lg mb-2">Processing Video Pipeline</h4>
                                <p className="text-[#545b64] font-mono text-sm">{status}</p>
                            </div>
                        ) : (
                            <label htmlFor="video-upload" className="flex flex-col items-center cursor-pointer">
                                <div className="w-16 h-16 bg-[#ec7211]/10 rounded-full flex items-center justify-center mb-4">
                                    <UploadCloud className="w-8 h-8 text-[#ec7211]" />
                                </div>
                                <h4 className="text-[#16191f] font-bold text-lg mb-2">
                                    Drag and drop video here, or <span className="text-[#0073bb] hover:underline">browse</span>
                                </h4>
                                <p className="text-sm text-[#545b64] max-w-sm">
                                    Supports MP4, MOV, MKV (Max 500MB). Optimized for Railway Inspection CCTV scaling.
                                </p>
                            </label>
                        )}
                    </div>

                    {error && (
                        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded flex items-start gap-3">
                            <AlertCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
                            <div>
                                <h5 className="font-bold text-red-900 text-sm">Upload Failed</h5>
                                <p className="text-sm text-red-700">{error}</p>
                            </div>
                        </div>
                    )}

                    <div className="mt-8 flex gap-4 text-sm text-[#545b64] justify-center">
                        <div className="flex items-center gap-2">
                            <CheckCircle size={16} className="text-green-500" />
                            <span>AES-256 Encryption</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <CheckCircle size={16} className="text-green-500" />
                            <span>Auto-Scaling</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <CheckCircle size={16} className="text-green-500" />
                            <span>GPU Inference</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default UploadSection;
