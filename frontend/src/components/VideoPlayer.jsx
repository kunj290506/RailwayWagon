import React, { useRef, useState, useEffect } from 'react';
import { Play, Pause, Camera, Eye, AlertTriangle } from 'lucide-react';

const VideoPlayer = ({ originalSrc, enhancedSrc, metadata, wagonData }) => {
    const videoRef = useRef(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [viewMode, setViewMode] = useState('original'); // 'original' or 'enhanced'
    const [currentMeta, setCurrentMeta] = useState(null);
    const [wagonCount, setWagonCount] = useState(0);

    // Simulated FPS (we saved at 30fps)
    const FPS = 30;

    // Toggle Play/Pause
    const togglePlay = () => {
        if (videoRef.current) {
            if (isPlaying) videoRef.current.pause();
            else videoRef.current.play();
            setIsPlaying(!isPlaying);
        }
    };

    // Sync Metadata
    useEffect(() => {
        const interval = setInterval(() => {
            if (videoRef.current && isPlaying) {
                const time = videoRef.current.currentTime;
                setCurrentTime(time);

                // Find metadata for current frame
                const frameIdx = Math.floor(time * FPS);
                if (metadata && metadata[frameIdx]) {
                    setCurrentMeta(metadata[frameIdx]);
                }

                // Calculate wagon count based on time (simulated accumulation)
                // In real app, we check if current frame's wagon number is new.
                // Quick hack: Count unique wagons seen up to this frame index in metadata
                if (metadata) {
                    const seen = new Set();
                    for (let i = 0; i <= frameIdx; i++) {
                        if (metadata[i]?.wagon_number) seen.add(metadata[i].wagon_number);
                    }
                    setWagonCount(seen.size);
                }
            }
        }, 100); // Poll every 100ms
        return () => clearInterval(interval);
    }, [isPlaying, metadata]);

    // Handle Source Toggle (maintain timestamp)
    const currentSrc = viewMode === 'original' ? originalSrc : enhancedSrc;

    return (
        <div className="relative w-full bg-slate-50 shadow-lg border border-slate-200 rounded-xl overflow-hidden">

            {/* Metrics Overlay - Industrial Style */}
            <div className="absolute top-4 left-4 z-20 flex flex-col gap-2 pointer-events-none">
                {/* Live Indicator */}
                <div className="flex items-center gap-2 bg-red-600 text-white px-3 py-1 text-xs font-bold uppercase tracking-wider w-fit rounded-full shadow-lg">
                    <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div> Live Feed
                </div>

                {/* Stats Panel (Glassmorphism) */}
                <div className="bg-white/90 backdrop-blur-md p-4 text-slate-800 border-l-4 border-blue-600 w-64 rounded-r-xl shadow-xl mt-2">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <div className="text-[10px] text-slate-500 uppercase tracking-wide font-bold">Blur Score</div>
                            <div className={`text-3xl font-mono font-bold ${currentMeta?.is_blurred ? 'text-red-500' : 'text-emerald-600'}`}>
                                {currentMeta ? Math.round(currentMeta.blur_score) : '--'}
                            </div>
                        </div>
                        <div>
                            <div className="text-[10px] text-slate-500 uppercase tracking-wide font-bold">Wagon Count</div>
                            <div className="text-3xl font-mono font-bold text-blue-600">{wagonCount}</div>
                        </div>
                    </div>

                    <div className="mt-3 border-t border-slate-200 pt-2">
                        <div className="text-[10px] text-slate-500 uppercase tracking-wide mb-1 font-bold">OCR Result</div>
                        {currentMeta?.wagon_number ? (
                            <div className="font-mono text-xl text-slate-900 font-bold bg-yellow-100 border border-yellow-300 px-3 py-1 inline-block rounded">
                                {currentMeta.wagon_number}
                            </div>
                        ) : (
                            <div className="text-xs text-slate-400 italic">Scanning ROI...</div>
                        )}
                    </div>
                </div>
            </div>

            {/* Damage Overlay Box */}
            {currentMeta?.is_blurred && (
                <div className="absolute top-4 right-4 z-20 bg-yellow-400 text-black px-4 py-2 font-bold flex items-center gap-2 border border-yellow-500 rounded-lg shadow-xl animate-pulse">
                    <AlertTriangle size={20} /> MOTION BLUR DETECTED
                </div>
            )}

            {/* Video Element */}
            <video
                ref={videoRef}
                src={currentSrc}
                className="w-full h-auto object-cover bg-slate-900/5"
                onTimeUpdate={() => setCurrentTime(videoRef.current?.currentTime)}
                loop
                playsInline
            />

            {/* Controls Bar */}
            <div className="bg-white p-3 flex items-center justify-between border-t border-slate-200">
                <div className="flex items-center gap-4">
                    <button onClick={togglePlay} className="text-slate-600 hover:text-blue-600 transition p-2 hover:bg-slate-100 rounded-full">
                        {isPlaying ? <Pause size={20} fill="currentColor" /> : <Play size={20} fill="currentColor" />}
                    </button>
                    <div className="text-slate-500 font-mono text-xs font-medium">
                        {currentTime.toFixed(2)}s <span className="text-slate-300 mx-2">|</span> 30 FPS
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <span className="text-xs text-slate-400 uppercase font-bold">Source View:</span>
                    <div className="flex bg-slate-100 p-1 rounded-lg border border-slate-200">
                        <button
                            onClick={() => setViewMode('original')}
                            className={`px-3 py-1 text-xs font-bold rounded-md transition-all shadow-sm ${viewMode === 'original' ? 'bg-white text-blue-600 ring-1 ring-slate-200' : 'text-slate-400 hover:text-slate-600'}`}
                        >
                            ORIGINAL
                        </button>
                        <button
                            onClick={() => setViewMode('enhanced')}
                            className={`px-3 py-1 text-xs font-bold rounded-md transition-all shadow-sm ${viewMode === 'enhanced' ? 'bg-blue-600 text-white shadow-blue-500/30' : 'text-slate-400 hover:text-slate-600'}`}
                        >
                            ENHANCED
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default VideoPlayer;