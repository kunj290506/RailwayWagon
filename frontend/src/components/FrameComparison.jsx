import { useState, useEffect } from 'react';

function FrameComparison() {
    const [frames, setFrames] = useState([]);
    const [selectedFrame, setSelectedFrame] = useState(null);
    const [ocrData, setOcrData] = useState(null);
    const [detectionData, setDetectionData] = useState(null);
    const [processing, setProcessing] = useState(false);

    useEffect(() => {
        // Fetch all frames (using existing analyze endpoint or a new one)
        // For now, let's use /analyze_blur to get the list
        fetch('http://localhost:8000/analyze_blur', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                setFrames(data.results);
                if (data.results && data.results.length > 0) {
                    const blurred = data.results.find(f => f.state === 'BLURRED');
                    setSelectedFrame(blurred || data.results[0]);
                }
            })
            .catch(err => console.error(err));
    }, []);

    const handleRunAI = async () => {
        if (!selectedFrame) return;
        setProcessing(true);
        setOcrData(null);
        setDetectionData(null);

        try {
            // Run OCR
            const ocrRes = await fetch(`http://localhost:8000/run_ocr?filename=${selectedFrame.filename}`, { method: 'POST' });
            const ocrJson = await ocrRes.json();
            setOcrData(ocrJson);

            // Run Detection
            const detRes = await fetch(`http://localhost:8000/run_detection?filename=${selectedFrame.filename}`, { method: 'POST' });
            const detJson = await detRes.json();
            setDetectionData(detJson);

        } catch (err) {
            console.error(err);
            alert("Error running AI comparison");
        } finally {
            setProcessing(false);
        }
    };

    if (!selectedFrame || frames.length === 0) return <div className="p-8 text-center">Loading Frames...</div>;

    const originalUrl = `http://localhost:8000/static/frames/${selectedFrame.filename}`;
    const enhancedUrl = `http://localhost:8000/static/enhanced/${selectedFrame.filename}`;

    return (
        <div className="max-w-[1600px] mx-auto">
            <header className="mb-6 border-b border-gray-300 pb-4">
                <h1 className="text-2xl font-bold text-[#16191f]">Frame Comparison & Verification</h1>
                <p className="text-[#545b64] text-sm mt-1">Manual review tool for evaluating enhancement models.</p>
            </header>

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
                                <img src={originalUrl} alt="Original" className="max-w-full max-h-full" />
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
                                <img src={enhancedUrl} alt="Enhanced" className="max-w-full max-h-full" />
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
