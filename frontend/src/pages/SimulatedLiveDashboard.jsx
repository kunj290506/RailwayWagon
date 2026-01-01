import React, { useState, useEffect } from 'react';
import VideoPlayer from '../components/VideoPlayer';

const SimulatedLiveDashboard = () => {
    const [metadata, setMetadata] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('http://localhost:8000/metadata')
            .then(res => res.json())
            .then(data => {
                setMetadata(data);
                setLoading(false);
            })
            .catch(err => setLoading(false));
    }, []);

    // We assume backend serves these at fixed URLs for the "latest" upload
    // or we could make this dynamic. For MVP, we use the ones we just generated.
    const originalVideo = "http://localhost:8000/static/data/original_video.mp4";
    const enhancedVideo = "http://localhost:8000/static/data/enhanced_video.mp4";

    return (
        <div className="max-w-[1600px] mx-auto">
            <header className="mb-6 flex justify-between items-end border-b border-gray-300 pb-4">
                <div>
                    <h1 className="text-2xl font-bold text-[#16191f]">Live Wagon Inspection Feed</h1>
                    <p className="text-[#545b64] text-sm mt-1">Real-time inference stream • Camera 01 (North Gate)</p>
                </div>
                <div className="flex gap-2">
                    <span className="bg-[#ec7211] text-white px-3 py-1 text-sm font-bold rounded-sm shadow-sm">LIVE STREAMING</span>
                </div>
            </header>

            {loading ? (
                <div className="h-96 flex items-center justify-center bg-white rounded border border-gray-300 shadow-sm">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#ec7211]"></div>
                </div>
            ) : (
                <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
                    {/* Main Feed Area */}
                    <div className="xl:col-span-3">
                        <VideoPlayer
                            originalSrc={originalVideo}
                            enhancedSrc={enhancedVideo}
                            metadata={metadata}
                        />
                    </div>

                    {/* Side Panel for Camera List / Quick Stats */}
                    <div className="space-y-6">
                        <div className="bg-white border border-gray-300 shadow-sm">
                            <div className="bg-[#fafafa] px-4 py-3 border-b border-gray-200">
                                <h3 className="font-bold text-[#16191f] text-sm">Camera Feeds</h3>
                            </div>
                            <div className="p-2 space-y-1">
                                <div className="p-3 bg-[#f1f8ff] border border-[#0073bb] rounded-sm flex items-center justify-between cursor-pointer">
                                    <span className="font-bold text-[#0073bb] text-sm">CAM-01 (Main)</span>
                                    <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                                </div>
                                <div className="p-3 hover:bg-[#fafafa] border border-transparent rounded-sm flex items-center justify-between cursor-pointer text-[#545b64]">
                                    <span className="font-medium text-sm">CAM-02 (Yard)</span>
                                    <span className="w-2 h-2 bg-gray-300 rounded-full"></span>
                                </div>
                                <div className="p-3 hover:bg-[#fafafa] border border-transparent rounded-sm flex items-center justify-between cursor-pointer text-[#545b64]">
                                    <span className="font-medium text-sm">CAM-03 (Exit)</span>
                                    <span className="w-2 h-2 bg-gray-300 rounded-full"></span>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white border border-gray-300 shadow-sm">
                            <div className="bg-[#fafafa] px-4 py-3 border-b border-gray-200">
                                <h3 className="font-bold text-[#16191f] text-sm">System Health</h3>
                            </div>
                            <div className="p-4 space-y-4 text-sm">
                                <div className="flex justify-between border-b border-gray-100 pb-2">
                                    <span className="text-[#545b64]">GPU Status</span>
                                    <span className="text-green-600 font-bold flex items-center gap-1">
                                        <div className="w-2 h-2 bg-green-500 rounded-full"></div> Active (CUDA)
                                    </span>
                                </div>
                                <div className="flex justify-between border-b border-gray-100 pb-2">
                                    <span className="text-[#545b64]">Inference Latency</span>
                                    <span className="text-[#16191f] font-mono">12ms</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-[#545b64]">Uptime</span>
                                    <span className="text-[#16191f] font-mono">04:22:11</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SimulatedLiveDashboard;
