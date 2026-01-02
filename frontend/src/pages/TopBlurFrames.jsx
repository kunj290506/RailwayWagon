import React, { useEffect, useState } from 'react';
import { AlertTriangle, Eye, Home } from 'lucide-react';
import { Link } from 'react-router-dom';
import PageHeader from '../components/PageHeader';

const TopBlurFrames = () => {
    const [frames, setFrames] = useState([]);

    useEffect(() => {
        fetch('http://localhost:8000/analytics/top_blur?limit=10')
            .then(res => res.json())
            .then(data => setFrames(data))
            .catch(err => console.error(err));
    }, []);

    return (
        <div className="max-w-[1600px] mx-auto">
            <PageHeader
                title="Variance Anomalies"
                description="Frames requiring manual review due to high breakdown/blur scores"
                breadcrumbs={[
                    { label: 'Dashboard', path: '/', icon: Home },
                    { label: 'Top Blur Frames' }
                ]}
            />

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {frames.map((frame, idx) => (
                    <div key={idx} className="bg-white border border-gray-300 shadow-sm hover:border-[#ec7211] hover:ring-1 hover:ring-[#ec7211] transition-all cursor-pointer">
                        <div className="relative aspect-video bg-[#0f1115]">
                            <img
                                src={`http://localhost:8000/static/frames/${frame.filename}`}
                                alt={frame.filename}
                                className="w-full h-full object-cover opacity-80"
                            />
                            <div className="absolute top-2 right-2 bg-red-600 text-white text-[10px] uppercase font-bold px-2 py-0.5 shadow-sm">
                                Score: {Math.round(frame.blur_score)}
                            </div>
                            <div className="absolute bottom-0 w-full bg-gradient-to-t from-black/80 to-transparent p-2">
                                <span className="text-white font-mono text-xs">{frame.filename}</span>
                            </div>
                        </div>
                        <div className="p-3">
                            <div className="flex justify-between items-center mb-2">
                                <div className="text-xs font-bold text-[#545b64] uppercase tracking-wider">Rank #{idx + 1}</div>
                                <Link to={`/comparison?frame=${frame.filename}`} className="text-[#0073bb] text-xs font-bold hover:underline flex items-center gap-1">
                                    <Eye size={12} /> Inspect
                                </Link>
                            </div>
                            <div className="w-full bg-gray-200 h-1.5 mb-2">
                                <div className="bg-[#ec7211] h-1.5" style={{ width: `${Math.min(100, frame.blur_score / 10)}%` }}></div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default TopBlurFrames;
