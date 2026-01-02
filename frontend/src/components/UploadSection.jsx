import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

function UploadSection({ onUploadComplete }) {
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState('');
    const [progress, setProgress] = useState(0);
    const [eta, setEta] = useState(null);
    const navigate = useNavigate();

    const handleFileChange = async (selectedFile) => {
        if (!selectedFile) return;
        setLoading(true);
        setStatus('Uploading...');
        setProgress(10);

        const formData = new FormData();
        formData.append("file", selectedFile);

        try {
            const res = await fetch('http://localhost:8000/upload_video', { method: 'POST', body: formData });
            if (!res.ok) throw new Error('Upload failed');

            setStatus('Processing (Blur Analysis + Enhancement)...');
            setProgress(30);

            await fetch('http://localhost:8000/analyze_blur', { method: 'POST' });
            setProgress(50);

            await fetch('http://localhost:8000/enhance_frames', { method: 'POST' });
            setProgress(80);

            setStatus('Scanning Wagons...');
            await fetch('http://localhost:8000/scan_wagons', { method: 'POST' });
            setProgress(100);

            if (onUploadComplete) onUploadComplete();
            navigate('/');

        } catch (err) {
            console.error(err);
            setStatus('Error: ' + err.message);
            setLoading(false);
        }
    };

    return (
        <div className="p-8 border-2 border-dashed border-gray-300 rounded-xl text-center">
            <h3 className="text-xl font-bold mb-4">Upload Video</h3>
            {!loading ? (
                <input
                    type="file"
                    accept="video/*"
                    onChange={(e) => e.target.files && handleFileChange(e.target.files[0])}
                    className="block w-full text-sm text-slate-500
                        file:mr-4 file:py-2 file:px-4
                        file:rounded-full file:border-0
                        file:text-sm file:font-semibold
                        file:bg-blue-50 file:text-blue-700
                        hover:file:bg-blue-100"
                />
            ) : (
                <div>
                    <div className="font-bold text-blue-600 mb-2">{status}</div>
                    <div className="w-full bg-gray-200 h-2 rounded-full mb-2">
                        <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${progress}%` }}></div>
                    </div>
                    {eta && <div className="text-sm text-gray-500">Time Remaining: {eta}</div>}
                </div>
            )}
        </div>
    );
}

export default UploadSection;
