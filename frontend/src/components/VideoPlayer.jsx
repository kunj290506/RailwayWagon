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
        <div className="relative w-full bg-black shadow-sm border border-gray-400">

            {/* Metrics Overlay - Industrial Style */}
            <div className="absolute top-4 left-4 z-20 flex flex-col gap-2 pointer-events-none">
                {/* Live Indicator */}
                <div className="flex items-center gap-2 bg-red-600 text-white px-2 py-0.5 text-xs font-bold uppercase tracking-wider w-fit">
                    <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div> Live Feed
                </div>

                {/* Stats Panel */}
                <div className="bg-black/80 backdrop-blur-sm p-3 text-white border-l-4 border-[#ec7211] w-56">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <div className="text-[10px] text-gray-400 uppercase tracking-wide">Blur Score</div>
                            <div className={`text-2xl font-mono font-bold ${currentMeta?.is_blurred ? 'text-red-500' : 'text-green-500'}`}>
                                {currentMeta ? Math.round(currentMeta.blur_score) : '--'}
                            </div>
                        </div>
                        <div>
                            <div className="text-[10px] text-gray-400 uppercase tracking-wide">Wagon Count</div>
                            <div className="text-2xl font-mono font-bold text-blue-400">{wagonCount}</div>
                        </div>
                    </div>

                    <div className="mt-3 border-t border-gray-700 pt-2">
                        <div className="text-[10px] text-gray-400 uppercase tracking-wide mb-1">OCR Result</div>
                        {currentMeta?.wagon_number ? (
                            <div className="font-mono text-lg text-yellow-500 font-bold bg-yellow-900/30 px-2 py-0.5 inline-block">
                                {currentMeta.wagon_number}
                            </div>
                        ) : (
                            <div className="text-xs text-gray-500 italic">Scanning ROI...</div>
                        )}
                    </div>
                </div>
            </div>

            {/* Damage Overlay Box */}
            {currentMeta?.is_blurred && (
                <div className="absolute top-4 right-4 z-20 bg-yellow-400 text-black px-4 py-2 font-bold flex items-center gap-2 border-2 border-yellow-600 shadow-lg">
                    <AlertTriangle size={20} /> MOTION BLUR
                </div>
            )}

            {/* Video Element */}
            <video
                ref={videoRef}
                src={currentSrc}
                className="w-full h-auto object-cover bg-[#0f1115]"
                onTimeUpdate={() => setCurrentTime(videoRef.current?.currentTime)}
                loop
                playsInline
            />

            {/* Controls Bar */}
            <div className="bg-[#16191f] p-3 flex items-center justify-between border-t border-gray-600">
                <div className="flex items-center gap-4">
                    <button onClick={togglePlay} className="text-gray-300 hover:text-white transition">
                        {isPlaying ? <Pause size={20} /> : <Play size={20} />}
                    </button>
                    <div className="text-gray-400 font-mono text-xs">
                        {currentTime.toFixed(2)}s <span className="text-gray-600">|</span> 30 FPS
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-400 uppercase font-bold mr-2">Video Source:</span>
                    <div className="flex bg-black p-0.5 rounded-sm border border-gray-600">
                        <button
                            onClick={() => setViewMode('original')}
                            className={`px-3 py-1 text-xs font-bold rounded-sm transition ${viewMode === 'original' ? 'bg-[#ec7211] text-white' : 'text-gray-400 hover:text-white'}`}
                        >
                            ORIGINAL
                        </button>
                        <button
                            onClick={() => setViewMode('enhanced')}
                            className={`px-3 py-1 text-xs font-bold rounded-sm transition ${viewMode === 'enhanced' ? 'bg-[#0073bb] text-white' : 'text-gray-400 hover:text-white'}`}
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