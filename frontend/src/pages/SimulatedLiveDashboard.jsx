import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import VideoPlayer from '../components/VideoPlayer';
import TiltCard from '../components/TiltCard';
import UploadSection from '../components/UploadSection'; // Import UploadSection
import { Upload, Play, AlertCircle } from 'lucide-react';

const LiveDashboard = () => {
    const [metadata, setMetadata] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    const fetchMetadata = useCallback(() => {
        fetch('http://localhost:8000/metadata')
            .then(res => res.json())
            .then(data => {
                // Ensure data is array
                const validData = Array.isArray(data) ? data : [];
                setMetadata(validData);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to fetch metadata:", err);
                setMetadata([]);
                setLoading(false);
            });
    }, []);

    useEffect(() => {
        // Reset session on mount (Page Load / Refresh)
        const initSession = async () => {
            try {
                await fetch('http://localhost:8000/reset_session', { method: 'POST' });
                console.log("Session Reset on Mount.");
                fetchMetadata(); // Should return empty array
            } catch (e) {
                console.error("Reset failed", e);
                fetchMetadata();
            }
        };
        initSession();
    }, [fetchMetadata]);

    // Production Endpoint Configuration
    const originalVideo = "http://localhost:8000/static/data/original_video.mp4";
    const enhancedVideo = "http://localhost:8000/static/data/enhanced_video.mp4";

    if (loading) {
        return (
            <div className="h-[80vh] flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-slate-900"></div>
                    <span className="text-slate-500 font-medium animate-pulse">Connecting to Neural Engine...</span>
                </div>
            </div>
        );
    }

    if (metadata.length === 0) {
        return (
            <div className="max-w-[1600px] mx-auto pt-20 pb-20 fade-in">
                {/* Integrated Upload Section for "Empty State" */}
                <div className="max-w-3xl mx-auto">
                    <div className="text-center mb-10">
                        <h1 className="text-4xl font-extrabold text-slate-900 mb-4 tracking-tight">System Standby</h1>
                        <p className="text-slate-500 text-lg">
                            Ready to process new data. Upload CCTV footage to begin the automated inspection sequence.
                        </p>
                    </div>

                    {/* Render Upload Component Directly */}
                    <UploadSection onUploadComplete={() => {
                        setLoading(true);
                        // Small delay to allow backend to finish writing if needed, though fetch might be fast
                        setTimeout(fetchMetadata, 1000);
                    }} />
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-[1600px] mx-auto pb-20">
            {/* Header - Enterprise Typography */}
            <header className="mb-12 pt-4 flex justify-between items-end border-b border-slate-100 pb-6 fade-in">
                <div>
                    <h1 className="text-5xl font-extrabold text-slate-900 tracking-tight leading-tight">Inspection Feed</h1>
                    <p className="text-slate-500 text-lg mt-2 font-medium">Camera Feed 01 &bull; Neural Inference Active</p>
                </div>
                <div className="flex gap-4 items-center">
                    <span className="bg-red-500/10 text-red-600 border border-red-500/20 px-4 py-2 text-xs font-bold rounded-full shadow-sm flex items-center gap-2">
                        <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                        LIVE STREAM
                    </span>
                </div>
            </header>

            {loading ? (
                <div className="h-96 flex items-center justify-center bg-white rounded-3xl border border-slate-100 shadow-sm">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-slate-300"></div>
                </div>
            ) : (
                <div className="grid grid-cols-1 xl:grid-cols-4 gap-10">

                    {/* Main Feed Area */}
                    <div className="xl:col-span-3">
                        <TiltCard className="rounded-3xl shadow-[0_20px_40px_-5px_rgba(0,0,0,0.1)] bg-white border border-white/50 ring-1 ring-slate-900/5">
                            <VideoPlayer
                                originalSrc={originalVideo}
                                enhancedSrc={enhancedVideo}
                                metadata={metadata}
                            />
                        </TiltCard>

                        {/* Real-time Metrics */}
                        <div className="mt-8 grid grid-cols-3 gap-8 px-4">
                            <div>
                                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Batch ID</h4>
                                <div className="text-xl font-bold text-slate-800">#89-204-AX</div>
                            </div>
                            <div>
                                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Inference Engine</h4>
                                <div className="text-xl font-bold text-slate-800">Vanguard Neural V2</div>
                            </div>
                            <div>
                                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">System Status</h4>
                                <div className="text-xl font-bold text-emerald-600">Optimal</div>
                            </div>
                        </div>
                    </div>

                    {/* Side Panel */}
                    <div className="space-y-8">
                        <div>
                            <h3 className="text-xl font-bold text-slate-900 mb-6 px-1">Active Feeds</h3>
                            <TiltCard className="bg-white/60 backdrop-blur-xl border border-white/60 shadow-lg rounded-2xl overflow-hidden ring-1 ring-slate-900/5 hover:bg-white transition-colors">
                                <div className="p-2 space-y-1">
                                    <div className="p-4 bg-white shadow-sm border border-slate-100 rounded-xl flex items-center justify-between cursor-pointer group">
                                        <div className="flex flex-col">
                                            <span className="font-bold text-slate-900 text-sm">Gate 01 (Main)</span>
                                            <span className="text-[10px] text-slate-400 font-medium">Online - 120fps</span>
                                        </div>
                                        <span className="w-2.5 h-2.5 bg-green-500 rounded-full shadow-[0_0_8px_rgba(34,197,94,0.4)]"></span>
                                    </div>
                                    <div className="p-4 hover:bg-white hover:shadow-sm border border-transparent hover:border-slate-100 rounded-xl flex items-center justify-between cursor-pointer text-slate-500 transition-all">
                                        <div className="flex flex-col">
                                            <span className="font-bold text-sm">Yard Checkpoint</span>
                                            <span className="text-[10px] text-slate-400 font-medium">Standby</span>
                                        </div>
                                        <span className="w-2 h-2 bg-slate-300 rounded-full"></span>
                                    </div>
                                    <div className="p-4 hover:bg-white hover:shadow-sm border border-transparent hover:border-slate-100 rounded-xl flex items-center justify-between cursor-pointer text-slate-500 transition-all">
                                        <div className="flex flex-col">
                                            <span className="font-bold text-sm">Outbound Lane</span>
                                            <span className="text-[10px] text-slate-400 font-medium">Maintenance</span>
                                        </div>
                                        <span className="w-2 h-2 bg-amber-400 rounded-full"></span>
                                    </div>
                                </div>
                            </TiltCard>
                        </div>

                        <div>
                            <h3 className="text-xl font-bold text-slate-900 mb-6 px-1">System Health</h3>
                            <TiltCard className="bg-white/60 backdrop-blur-xl border border-white/60 shadow-lg rounded-2xl overflow-hidden ring-1 ring-slate-900/5 hover:bg-white transition-colors">
                                <div className="p-6 space-y-5">
                                    <div className="flex justify-between items-center border-b border-slate-100 pb-4">
                                        <span className="text-slate-500 font-medium text-sm">GPU Utilization</span>
                                        <div className="text-right">
                                            <div className="text-slate-900 font-bold text-lg">76%</div>
                                            <div className="text-[10px] text-emerald-600 font-bold uppercase">Efficient</div>
                                        </div>
                                    </div>
                                    <div className="flex justify-between items-center border-b border-slate-100 pb-4">
                                        <span className="text-slate-500 font-medium text-sm">Network Latency</span>
                                        <div className="text-right">
                                            <div className="text-slate-900 font-bold text-lg">45ms</div>
                                            <div className="text-[10px] text-slate-400 font-bold uppercase">Stable</div>
                                        </div>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-slate-500 font-medium text-sm">Session Uptime</span>
                                        <div className="text-right">
                                            <div className="text-slate-900 font-bold text-lg">12:05:41</div>
                                            <div className="text-[10px] text-emerald-600 font-bold uppercase">Recording</div>
                                        </div>
                                    </div>
                                </div>
                            </TiltCard>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default LiveDashboard;
