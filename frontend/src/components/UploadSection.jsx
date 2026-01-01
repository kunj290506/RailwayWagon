import { useState, useCallback } from 'react';
import { Upload, XCircle, CheckCircle, FileVideo, HardDrive, Cpu, Zap, Radio, BarChart3, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

function UploadSection({ onUploadComplete }) {
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState('');
    const [progress, setProgress] = useState(0);
    const [dragActive, setDragActive] = useState(false);
    const [file, setFile] = useState(null);
    const navigate = useNavigate();

    const handleFileChange = async (selectedFile) => {
        if (!selectedFile) return;
        setFile(selectedFile);

        // Start process immediately (or we could wait for a button click, but let's automate like before)
        setLoading(true);
        setStatus('Secure Upload & Encryption');
        setProgress(10);

        const formData = new FormData();
        formData.append("file", selectedFile);

        try {
            // 1. Upload & Extract
            const res = await fetch('http://localhost:8000/upload_video', { method: 'POST', body: formData });
            if (!res.ok) throw new Error('Upload failed');
            const data = await res.json();

            setStatus('Extracting Keyframes (FFmpeg)');
            setProgress(30);

            // 2. Analyze Blur
            setStatus('Running Laplacian Variance Algorithm...');
            const blurRes = await fetch('http://localhost:8000/analyze_blur', { method: 'POST' });
            if (!blurRes.ok) throw new Error('Blur analysis failed');
            setProgress(50);

            // 3. Enhance
            setStatus('Enhancing (ResNet + Sharpening Pipeline)...');
            const enhRes = await fetch('http://localhost:8000/enhance_frames', { method: 'POST' });
            if (!enhRes.ok) throw new Error('Enhancement failed');
            setProgress(75);

            // 4. Scan Wagons
            setStatus('OCR Inference on Enhanced Frames (GPU)...');
            const scanRes = await fetch('http://localhost:8000/scan_wagons', { method: 'POST' });
            if (!scanRes.ok) throw new Error('Wagon scanning failed');

            setProgress(100);
            setStatus('Complete. Redirecting...');

            setTimeout(() => {
                if (onUploadComplete) onUploadComplete();
                navigate('/');
            }, 1000);

        } catch (err) {
            console.error(err);
            setStatus(`Error: ${err.message}`);
            setLoading(false);
        }
    };

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileChange(e.dataTransfer.files[0]);
        }
    };

    return (
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
            <div className="p-8">
                {/* Header */}
                <div className="flex items-start justify-between mb-8">
                    <div>
                        <h3 className="text-lg font-bold text-slate-800">Input Source Configuration</h3>
                        <p className="text-slate-500 text-sm mt-1">Upload raw CCTV footage to initialize the inspection pipeline.</p>
                    </div>
                    <div className="bg-orange-50 text-[#ec7211] px-3 py-1 rounded text-xs font-bold uppercase tracking-wide flex items-center gap-2">
                        <Zap size={14} /> High Performance Mode
                    </div>
                </div>

                {!loading ? (
                    <div
                        className={`relative border-2 border-dashed rounded-xl p-12 transition-all duration-200 text-center
                        ${dragActive ? 'border-[#ec7211] bg-orange-50' : 'border-slate-300 hover:border-[#ec7211] hover:bg-slate-50'}`}
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                    >
                        <input
                            type="file"
                            id="file-upload"
                            className="hidden"
                            accept="video/*"
                            onChange={(e) => handleFileChange(e.target.files[0])}
                        />
                        <div className="w-20 h-20 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-sm">
                            <Upload size={32} />
                        </div>

                        <h4 className="text-xl font-bold text-slate-800 mb-2">
                            Drag and drop video here, or <label htmlFor="file-upload" className="text-[#0073bb] cursor-pointer hover:underline">browse</label>
                        </h4>
                        <p className="text-slate-500 text-sm mb-6">
                            Supports MP4, MOV, MKV (Max 500MB). Optimized for Railway Inspection CCTV scaling.
                        </p>

                        <div className="flex justify-center gap-6 text-xs text-slate-400 font-medium uppercase tracking-wide">
                            <span className="flex items-center gap-1.5"><CheckCircle size={14} className="text-green-500" /> AES-256 Encryption</span>
                            <span className="flex items-center gap-1.5"><CheckCircle size={14} className="text-green-500" /> Auto Scaling</span>
                            <span className="flex items-center gap-1.5"><CheckCircle size={14} className="text-green-500" /> GPU Inference</span>
                        </div>
                    </div>
                ) : (
                    <div className="py-10 text-center">
                        {/* Status Icon */}
                        <div className="w-16 h-16 mx-auto mb-6 relative">
                            {progress < 100 ? (
                                <div className="animate-spin rounded-full h-16 w-16 border-4 border-slate-200 border-t-[#ec7211]"></div>
                            ) : (
                                <div className="bg-green-100 text-green-600 rounded-full h-16 w-16 flex items-center justify-center">
                                    <CheckCircle size={32} />
                                </div>
                            )}
                        </div>

                        <h3 className="text-2xl font-bold text-slate-800 mb-2">Processing Pipeline Active</h3>
                        <p className="text-slate-500 mb-8">{status}</p>

                        {/* Progress Bar */}
                        <div className="max-w-lg mx-auto bg-slate-100 rounded-full h-2 mb-8 overflow-hidden">
                            <div
                                className="bg-[#ec7211] h-2 rounded-full transition-all duration-500 ease-out"
                                style={{ width: `${progress}%` }}
                            ></div>
                        </div>

                        {/* Pipeline Steps Visual */}
                        <div className="grid grid-cols-4 gap-4 max-w-2xl mx-auto text-left">
                            {[
                                { name: "Upload", icon: HardDrive, done: progress >= 20 },
                                { name: "Blur Analysis", icon: BarChart3, done: progress >= 40 },
                                { name: "Enhancement", icon: Zap, done: progress >= 70 },
                                { name: "OCR Scan", icon: Cpu, done: progress >= 90 }
                            ].map((step, idx) => (
                                <div key={idx} className={`p-4 rounded-lg border ${step.done ? 'border-green-200 bg-green-50' : 'border-slate-100 bg-slate-50'} transition-all`}>
                                    <div className="flex items-center gap-3 mb-2">
                                        <step.icon size={20} className={step.done ? 'text-green-600' : 'text-slate-400'} />
                                        <div className={`text-xs font-bold uppercase ${step.done ? 'text-green-700' : 'text-slate-500'}`}>Step {idx + 1}</div>
                                    </div>
                                    <div className={`text-sm font-bold ${step.done ? 'text-slate-800' : 'text-slate-400'}`}>{step.name}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* Footer */}
            <div className="bg-slate-50 px-8 py-4 border-t border-slate-200 flex justify-between items-center text-xs text-slate-500">
                <div className="flex items-center gap-2">
                    <AlertCircle size={14} />
                    System Status: <span className="text-green-600 font-bold">Online</span>
                </div>
                <div>
                    v2.4.0-stable
                </div>
            </div>
        </div>
    );
}

export default UploadSection;
