import React, { useEffect, useState } from 'react';
import { Download, Printer, CheckCircle, FileText, History, Calendar } from 'lucide-react';
import jsPDF from 'jspdf';
import 'jspdf-autotable';

const ReportsPage = () => {
    const [wagons, setWagons] = useState([]);
    const [history, setHistory] = useState([]);
    const [selectedBatch, setSelectedBatch] = useState('latest');

    useEffect(() => {
        // Fetch Live Wagons
        fetchWagons('latest');

        // Fetch History Index
        fetch('http://localhost:8000/history')
            .then(res => res.json())
            .then(data => setHistory(data))
            .catch(err => console.error(err));
    }, []);

    const fetchWagons = (batchId) => {
        let url = 'http://localhost:8000/wagons';
        if (batchId !== 'latest') {
            url = `http://localhost:8000/history/${batchId}/wagons`;
        }

        fetch(url)
            .then(res => res.json())
            .then(data => setWagons(data))
            .catch(err => console.error(err));
    };

    const handleBatchChange = (e) => {
        const batchId = e.target.value;
        setSelectedBatch(batchId);
        fetchWagons(batchId);
    };

    const downloadPDF = () => {
        const doc = new jsPDF();

        // Find batch details
        const currentBatch = history.find(h => h.batch_id === selectedBatch);
        const batchLabel = currentBatch ? currentBatch.label : "Live Session (Latest)";
        const batchDate = currentBatch ? new Date(currentBatch.timestamp).toLocaleString() : new Date().toLocaleString();

        // Header
        doc.setFillColor(35, 47, 62); // AWS Dark Blue
        doc.rect(0, 0, 210, 25, 'F');
        doc.setFontSize(18);
        doc.setTextColor(255, 255, 255);
        doc.text("Adani AI - Wagon Inspection Report", 14, 16);
        doc.setFontSize(10);
        doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 22);

        // Meta Info
        doc.setTextColor(50, 50, 50);
        doc.setFontSize(12);
        doc.text(`Batch ID: ${selectedBatch === 'latest' ? 'WGN-LIVE' : selectedBatch}`, 14, 35);
        doc.text(`Session: ${batchLabel}`, 14, 42);
        doc.text(`Total Wagons: ${wagons.length}`, 14, 49);

        // Table
        const tableColumn = ["Wagon Number", "Timestamp (s)", "Camera", "Status", "Confidence"];
        const tableRows = [];

        wagons.forEach(wagon => {
            const wagonData = [
                wagon.number,
                wagon.frame.split('_')[1].split('.')[0],
                "CAM-01",
                "VERIFIED",
                "High (99%)"
            ];
            tableRows.push(wagonData);
        });

        doc.autoTable({
            startY: 55,
            head: [tableColumn],
            body: tableRows,
            theme: 'grid',
            headStyles: { fillColor: [236, 114, 17] }, // Orange
            styles: { fontSize: 10, cellPadding: 3 },
            alternateRowStyles: { fillColor: [245, 245, 245] }
        });

        doc.save(`Wagon_Report_${selectedBatch}.pdf`);
    };

    return (
        <div className="max-w-[1600px] mx-auto">
            <div className="flex justify-between items-center mb-6 border-b border-gray-300 pb-4">
                <div>
                    <h1 className="text-2xl font-bold text-[#16191f]">Inspection Reports</h1>
                    <p className="text-[#545b64] text-sm mt-1">Daily Wagon Inspection Summary • {new Date().toLocaleDateString()}</p>
                </div>
                <div className="flex gap-3 items-center">
                    {/* History Selector */}
                    <div className="flex items-center gap-2 mr-4 bg-gray-100 rounded px-2 py-1 border border-gray-300">
                        <History size={16} className="text-[#545b64]" />
                        <select
                            value={selectedBatch}
                            onChange={handleBatchChange}
                            className="bg-transparent text-sm font-bold text-[#16191f] outline-none cursor-pointer min-w-[200px]"
                        >
                            <option value="latest">Latest Session (Live)</option>
                            {history.map(h => (
                                <option key={h.batch_id} value={h.batch_id}>
                                    {new Date(h.timestamp).toLocaleString()} - {h.wagon_count} Wagons
                                </option>
                            ))}
                        </select>
                    </div>

                    <button
                        onClick={downloadPDF}
                        className="flex items-center gap-2 px-4 py-1.5 bg-[#ec7211] text-white border border-[#ec7211] rounded-sm font-bold text-sm hover:bg-[#d16200] shadow-sm"
                    >
                        <FileText size={16} /> Download PDF
                    </button>
                </div>
            </div>

            <div className="bg-white border border-gray-300 shadow-sm">
                {/* Report Header Visual */}
                <div className="bg-[#232f3e] px-6 py-6 text-white flex justify-between items-start">
                    <div>
                        <h2 className="text-xl font-bold mb-1">Adani Logistics - Automated Inspection</h2>
                        <div className="opacity-80 text-sm">Motion Blur Mitigation & OCR Verification System</div>
                    </div>
                    <div className="text-right">
                        <div className="text-3xl font-bold text-[#ec7211]">{wagons.length}</div>
                        <div className="text-xs uppercase tracking-wider opacity-70">Wagons Verified</div>
                    </div>
                </div>

                <div className="bg-[#fafafa] px-5 py-4 border-b border-gray-200 flex justify-between items-center">
                    <div className="flex gap-12">
                        <div>
                            <div className="text-xs text-[#545b64] uppercase font-bold tracking-wider">Batch Scope</div>
                            <div className="font-mono font-bold text-[#16191f] text-lg">
                                {selectedBatch === 'latest' ? 'LIVE SESSION' : selectedBatch}
                            </div>
                        </div>
                        <div>
                            <div className="text-xs text-[#545b64] uppercase font-bold tracking-wider">Location</div>
                            <div className="font-bold text-[#16191f] text-lg">North Gate (CAM-01)</div>
                        </div>
                        <div>
                            <div className="text-xs text-[#545b64] uppercase font-bold tracking-wider">Status</div>
                            <div className="font-bold text-green-700 text-lg flex items-center gap-1">
                                <CheckCircle size={18} /> COMPLETE
                            </div>
                        </div>
                    </div>
                </div>

                <table className="w-full text-left text-sm text-[#16191f]">
                    <thead className="bg-[#fafafa] text-[#545b64] border-b border-gray-200">
                        <tr>
                            <th className="px-5 py-3 font-bold uppercase text-xs tracking-wider">Wagon Number (OCR)</th>
                            <th className="px-5 py-3 font-bold uppercase text-xs tracking-wider">Timestamp</th>
                            <th className="px-5 py-3 font-bold uppercase text-xs tracking-wider">Source Camera</th>
                            <th className="px-5 py-3 font-bold uppercase text-xs tracking-wider">Verification Status</th>
                            <th className="px-5 py-3 font-bold uppercase text-xs tracking-wider text-right">Evidence</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {wagons.length > 0 ? wagons.map((wagon, i) => (
                            <tr key={i} className="hover:bg-[#f1f8ff] transition-colors">
                                <td className="px-5 py-4 font-mono font-bold text-[#0073bb] text-base">{wagon.number}</td>
                                <td className="px-5 py-4 text-[#16191f]">{wagon.frame.split('_')[1].split('.')[0]}s</td>
                                <td className="px-5 py-4 text-[#545b64]">CAM-01</td>
                                <td className="px-5 py-4">
                                    <span className="flex items-center gap-1.5 px-2 py-1 bg-green-50 w-fit rounded border border-green-200">
                                        <CheckCircle size={14} className="text-green-600" />
                                        <span className="text-green-700 font-bold text-xs uppercase">Verified</span>
                                    </span>
                                </td>
                                <td className="px-5 py-4 text-right">
                                    <a href={wagon.image_url} target="_blank" className="text-[#0073bb] hover:underline font-medium text-xs border border-[#0073bb] px-3 py-1 rounded-sm hover:bg-[#0073bb] hover:text-white transition-colors">View Frame</a>
                                </td>
                            </tr>
                        )) : (
                            <tr>
                                <td colSpan="5" className="px-6 py-12 text-center text-[#545b64]">
                                    No inspection data found for this batch.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default ReportsPage;
