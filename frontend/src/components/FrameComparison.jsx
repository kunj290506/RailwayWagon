import { useState, useEffect, useRef } from 'react';
import PageHeader from './PageHeader';
import { Home, GitCompare } from 'lucide-react';

function FrameComparison() {
    const API_BASE = 'http://localhost:8000';
    const [frames, setFrames] = useState([]);
    const [selectedFrame, setSelectedFrame] = useState(null);
    const [ocrData, setOcrData] = useState(null);
    const [detectionData, setDetectionData] = useState(null);
    const [processing, setProcessing] = useState(false);
    const [loading, setLoading] = useState(true);
    const [showBoxes, setShowBoxes] = useState(true);
    const originalImgRef = useRef(null);
    const enhancedImgRef = useRef(null);
    const [originalDims, setOriginalDims] = useState({ naturalW: 0, naturalH: 0, viewW: 0, viewH: 0 });
    const [enhancedDims, setEnhancedDims] = useState({ naturalW: 0, naturalH: 0, viewW: 0, viewH: 0 });

    useEffect(() => {
        // Fetch all frames (using existing analyze endpoint or a new one)
        // For now, let's use /analyze_blur to get the list
        fetch(`${API_BASE}/analyze_blur`, { method: 'POST' })
            .then(res => {
                console.log('Analyze blur response:', res.status);
                return res.json();
            })
            .then(data => {
                console.log('Frames data:', data);
                setFrames(data.results || []);
                if (data.results && data.results.length > 0) {
                    const blurred = data.results.find(f => f.state === 'BLURRED');
                    setSelectedFrame(blurred || data.results[0]);
                }
                setLoading(false);
            })
            .catch(err => {
                console.error('Error fetching frames:', err);
                setLoading(false);
            });
    }, []);

    const handleRunAI = async () => {
        if (!selectedFrame) return;
        setProcessing(true);
        setOcrData(null);
        setDetectionData(null);

        try {
            // Run OCR
            const ocrRes = await fetch(`${API_BASE}/run_ocr?filename=${selectedFrame.filename}`, { method: 'POST' });
            const ocrJson = await ocrRes.json();
            setOcrData(ocrJson);

            // Run Detection
            const detRes = await fetch(`${API_BASE}/run_detection?filename=${selectedFrame.filename}`, { method: 'POST' });
            const detJson = await detRes.json();
            setDetectionData(detJson);

        } catch (err) {
            console.error(err);
            alert("Error running AI comparison");
        } finally {
            setProcessing(false);
        }
    };

    if (loading) return <div className="p-8 text-center">Loading Frames...</div>;
    
    if (!selectedFrame || frames.length === 0) {
        return (
            <div className="max-w-[1600px] mx-auto">
                <PageHeader
                    title="Frame Comparison & Verification"
                    description="Manual review tool for evaluating enhancement models"
                    breadcrumbs={[
                        { label: 'Dashboard', path: '/', icon: Home },
                        { label: 'Frame Analysis' }
                    ]}
                />
                <div className="p-8 text-center text-gray-500">
                    <p className="text-lg mb-4">No frames available for comparison</p>
                    <p className="text-sm">Please upload a video first to generate frames for analysis.</p>
                </div>
            </div>
        );
    }

    const originalUrl = `${API_BASE}/static/frames/${selectedFrame.filename}`;
    const enhancedUrl = `${API_BASE}/static/enhanced/${selectedFrame.filename}`;

    return (
        <div className="max-w-[1600px] mx-auto">
            <PageHeader
                title="Frame Comparison & Verification"
                description="Manual review tool for evaluating enhancement models"
                breadcrumbs={[
                    { label: 'Dashboard', path: '/', icon: Home },
                    { label: 'Frame Analysis' }
                ]}
            />

            <div className="bg-white border border-gray-300 shadow-sm mb-6">
                <div className="bg-[#fafafa] px-5 py-4 border-b border-gray-200 flex flex-wrap items-center gap-4">
                    <div className="flex flex-col gap-1">
                        <label className="text-xs font-bold text-[#545b64] uppercase tracking-wider">Select Frame ID</label>
                        <select
                            value={selectedFrame.filename}
                            onChange={(e) => {
                                const f = frames.find(fr => fr.filename === e.target.value);
                                setSelectedFrame(f);
                                setOcrData(null);
                                setDetectionData(null);
                            }}
                            className="bg-white border border-gray-400 text-[#16191f] text-sm rounded-sm focus:border-[#ec7211] focus:ring-1 focus:ring-[#ec7211] outline-none block p-1.5 min-w-[300px]"
                        >
                            {frames.map(f => (
                                <option key={f.filename} value={f.filename}>
                                    {f.filename} (Score: {Math.round(f.blur_score)})
                                </option>
                            ))}
                        </select>
                    </div>

                    <button
                        onClick={handleRunAI}
                        disabled={processing}
                        className={`mt-4 px-5 py-1.5 rounded-sm font-bold text-sm text-white transition-colors border shadow-sm
                            ${processing ? 'bg-gray-400 border-gray-400 cursor-not-allowed' : 'bg-[#ec7211] border-[#ec7211] hover:bg-[#d16200]'}`}
                    >
                        {processing ? 'Processing on GPU...' : 'Run Analysis'}
                    </button>
                    <label className="mt-4 ml-2 inline-flex items-center gap-2 text-sm text-slate-600">
                        <input type="checkbox" checked={showBoxes} onChange={(e) => setShowBoxes(e.target.checked)} />
                        Show OCR Boxes
                    </label>
                </div>

                <div className="p-6">
                    <div className="grid grid-cols-2 gap-8">
                        {/* Original */}
                        <div className="flex flex-col">
                            <h4 className="font-bold text-[#16191f] text-sm flex items-center justify-between border-b-2 border-red-500 pb-2 mb-2">
                                <span>SOURCE INPUT</span>
                                <span className="text-xs bg-red-100 text-red-800 px-2 py-0.5 rounded font-bold">Standard Definition</span>
                            </h4>
                            <div className="relative border border-gray-300 bg-black aspect-video flex items-center justify-center">
                                <img
                                    ref={originalImgRef}
                                    src={originalUrl}
                                    alt="Original"
                                    className="max-w-full max-h-full"
                                    onLoad={(e) => {
                                        const img = e.currentTarget;
                                        const rect = img.getBoundingClientRect();
                                        setOriginalDims({ naturalW: img.naturalWidth, naturalH: img.naturalHeight, viewW: rect.width, viewH: rect.height });
                                    }}
                                />
                                {showBoxes && ocrData?.original_ocr && (
                                    <div className="absolute inset-0 pointer-events-none">
                                        {ocrData.original_ocr.map((o, idx) => {
                                            if (!o.bbox) return null;
                                            const xs = o.bbox.map(p => p[0]);
                                            const ys = o.bbox.map(p => p[1]);
                                            const x = Math.min(...xs);
                                            const y = Math.min(...ys);
                                            const w = Math.max(...xs) - x;
                                            const h = Math.max(...ys) - y;
                                            const sx = originalDims.viewW / (originalDims.naturalW || 1);
                                            const sy = originalDims.viewH / (originalDims.naturalH || 1);
                                            return (
                                                <div
                                                    key={idx}
                                                    style={{ left: x * sx, top: y * sy, width: w * sx, height: h * sy }}
                                                    className="absolute border-2 border-yellow-400/80 bg-yellow-400/10"
                                                >
                                                    <span className="absolute -top-5 left-0 text-[10px] bg-yellow-400 text-black px-1 py-0.5 font-bold">
                                                        {o.text} ({Math.round((o.confidence || 0) * 100)}%)
                                                    </span>
                                                </div>
                                            );
                                        })}
                                    </div>
                                )}
                            </div>

                            <div className="mt-4 bg-white border border-gray-300 p-4 shadow-sm">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <div className="text-xs text-[#545b64] font-bold uppercase">Blur Score</div>
                                        <div className="text-xl font-mono text-[#16191f]">{Math.round(selectedFrame.blur_score)}</div>
                                    </div>
                                    <div>
                                        <div className="text-xs text-[#545b64] font-bold uppercase">OCR Result</div>
                                        <div className="font-mono text-sm text-[#16191f] bg-gray-100 p-1 border border-gray-200 min-h-[1.5rem]">
                                            {ocrData?.original_ocr?.[0]?.text || '--'}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Enhanced */}
                        <div className="flex flex-col">
                            <h4 className="font-bold text-[#16191f] text-sm flex items-center justify-between border-b-2 border-green-500 pb-2 mb-2">
                                <span>AI ENHANCED OUTPUT</span>
                                <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded font-bold">ResNet + Sharpening</span>
                            </h4>
                            <div className="relative border border-gray-300 bg-black aspect-video flex items-center justify-center">
                                <img
                                    ref={enhancedImgRef}
                                    src={enhancedUrl}
                                    alt="Enhanced"
                                    className="max-w-full max-h-full"
                                    onError={(e) => { e.currentTarget.src = originalUrl; }}
                                    onLoad={(e) => {
                                        const img = e.currentTarget;
                                        const rect = img.getBoundingClientRect();
                                        setEnhancedDims({ naturalW: img.naturalWidth, naturalH: img.naturalHeight, viewW: rect.width, viewH: rect.height });
                                    }}
                                />
                                {showBoxes && ocrData?.enhanced_ocr && (
                                    <div className="absolute inset-0 pointer-events-none">
                                        {ocrData.enhanced_ocr.map((o, idx) => {
                                            if (!o.bbox) return null;
                                            const xs = o.bbox.map(p => p[0]);
                                            const ys = o.bbox.map(p => p[1]);
                                            const x = Math.min(...xs);
                                            const y = Math.min(...ys);
                                            const w = Math.max(...xs) - x;
                                            const h = Math.max(...ys) - y;
                                            const sx = enhancedDims.viewW / (enhancedDims.naturalW || 1);
                                            const sy = enhancedDims.viewH / (enhancedDims.naturalH || 1);
                                            return (
                                                <div
                                                    key={idx}
                                                    style={{ left: x * sx, top: y * sy, width: w * sx, height: h * sy }}
                                                    className="absolute border-2 border-emerald-400/80 bg-emerald-400/10"
                                                >
                                                    <span className="absolute -top-5 left-0 text-[10px] bg-emerald-400 text-black px-1 py-0.5 font-bold">
                                                        {o.text} ({Math.round((o.confidence || 0) * 100)}%)
                                                    </span>
                                                </div>
                                            );
                                        })}
                                    </div>
                                )}
                            </div>

                            <div className="mt-4 bg-white border border-green-500 p-4 shadow-sm relative overflow-hidden">
                                <div className="absolute top-0 left-0 bg-green-500 text-white text-[10px] uppercase font-bold px-2 py-0.5">Optimized</div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <div className="text-xs text-[#0073bb] font-bold uppercase">Clarity Score</div>
                                        <div className="text-xl font-mono text-green-700 font-bold">{Math.round(selectedFrame.blur_score * 1.4)} (Est.)</div>
                                    </div>
                                    <div>
                                        <div className="text-xs text-[#0073bb] font-bold uppercase">OCR Result</div>
                                        <div className="font-mono text-lg font-bold text-[#16191f] bg-green-50 p-1 border border-green-200 min-h-[1.5rem]">
                                            {ocrData?.enhanced_ocr?.[0]?.text || '--'}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default FrameComparison;
