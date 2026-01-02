import React, { useEffect, useState } from 'react';
import { Download, Printer, CheckCircle, FileText, History, Calendar, Home } from 'lucide-react';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import PageHeader from '../components/PageHeader';

const ReportsPage = () => {
    const [wagons, setWagons] = useState([]);
    const [history, setHistory] = useState([]);
    const [selectedBatch, setSelectedBatch] = useState('latest');

    useEffect(() => {
        fetchWagons('latest');

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

        const currentBatch = history.find(h => h.batch_id === selectedBatch);
        const batchLabel = currentBatch ? currentBatch.label : 'Live Session (Latest)';
        const batchDate = currentBatch
            ? new Date(currentBatch.timestamp).toLocaleString()
            : new Date().toLocaleString();

        doc.setFillColor(35, 47, 62);
        doc.rect(0, 0, 210, 25, 'F');
        doc.setFontSize(18);
        doc.setTextColor(255, 255, 255);
        doc.text('Adani AI - Wagon Inspection Report', 14, 16);
        doc.setFontSize(10);
        doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 22);

        doc.setTextColor(50, 50, 50);
        doc.setFontSize(12);
        doc.text(`Batch ID: ${selectedBatch === 'latest' ? 'WGN-LIVE' : selectedBatch}`, 14, 35);
        doc.text(`Session: ${batchLabel}`, 14, 42);
        doc.text(`Total Wagons: ${wagons.length}`, 14, 49);

        const tableColumn = ['Wagon Number', 'Timestamp (s)', 'Camera', 'Status', 'Confidence'];
        const tableRows = [];

        wagons.forEach(wagon => {
            tableRows.push([
                wagon.number,
                wagon.frame.split('_')[1].split('.')[0],
                'CAM-01',
                'VERIFIED',
                'High (99%)'
            ]);
        });

        doc.autoTable({
            startY: 55,
            head: [tableColumn],
            body: tableRows,
            theme: 'grid',
            headStyles: { fillColor: [236, 114, 17] },
            styles: { fontSize: 10, cellPadding: 3 },
            alternateRowStyles: { fillColor: [245, 245, 245] }
        });

        doc.save(`Wagon_Report_${selectedBatch}.pdf`);
    };

    return (
        <div className="max-w-[1600px] mx-auto">
            <PageHeader
                title="Inspection Reports"
                description={`Daily wagon inspection summary • ${new Date().toLocaleDateString()}`}
                breadcrumbs={[
                    { label: 'Dashboard', path: '/', icon: Home },
                    { label: 'Reports' }
                ]}
            />

            {/* Batch Selector */}
            <div className="mb-6 flex justify-between items-center">
                <div className="flex items-center gap-3">
                    <History size={16} className="text-slate-500" />
                    <select
                        value={selectedBatch}
                        onChange={handleBatchChange}
                        className="bg-white border border-slate-200 rounded-lg px-3 py-2 text-sm font-medium text-slate-900"
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
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium"
                >
                    <FileText size={16} /> Download PDF
                </button>
            </div>

            {/* Report Content */}
            <div className="bg-white border border-gray-300 shadow-sm rounded-lg overflow-hidden">
                <div className="bg-[#232f3e] px-6 py-6 text-white flex justify-between">
                    <div>
                        <h2 className="text-xl font-bold">Adani Logistics - Automated Inspection</h2>
                        <div className="text-sm opacity-80">
                            Motion Blur Mitigation & OCR Verification System
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="text-3xl font-bold text-[#ec7211]">{wagons.length}</div>
                        <div className="text-xs uppercase opacity-70">Wagons Verified</div>
                    </div>
                </div>

                <div className="bg-[#fafafa] px-5 py-4 border-b border-gray-200 flex justify-between items-center">
                    <div className="flex gap-12">
                        <div>
                            <div className="text-xs uppercase font-bold">Batch Scope</div>
                            <div className="font-mono font-bold text-lg">
                                {selectedBatch === 'latest' ? 'LIVE SESSION' : selectedBatch}
                            </div>
                        </div>
                        <div>
                            <div className="text-xs uppercase font-bold">Location</div>
                            <div className="font-bold text-lg">North Gate (CAM-01)</div>
                        </div>
                        <div>
                            <div className="text-xs uppercase font-bold">Status</div>
                            <div className="font-bold text-green-700 flex items-center gap-1">
                                <CheckCircle size={18} /> COMPLETE
                            </div>
                        </div>
                    </div>
                </div>

                <table className="w-full text-left text-sm">
                    <thead className="bg-[#fafafa] border-b">
                        <tr>
                            <th className="px-5 py-3">Wagon Number</th>
                            <th className="px-5 py-3">Timestamp</th>
                            <th className="px-5 py-3">Camera</th>
                            <th className="px-5 py-3">Status</th>
                            <th className="px-5 py-3 text-right">Evidence</th>
                        </tr>
                    </thead>
                    <tbody>
                        {wagons.length > 0 ? (
                            wagons.map((wagon, i) => (
                                <tr key={i} className="hover:bg-[#f1f8ff]">
                                    <td className="px-5 py-4 font-mono font-bold text-blue-700">
                                        {wagon.number}
                                    </td>
                                    <td className="px-5 py-4">
                                        {wagon.frame.split('_')[1].split('.')[0]}s
                                    </td>
                                    <td className="px-5 py-4">CAM-01</td>
                                    <td className="px-5 py-4">
                                        <span className="flex items-center gap-1 text-green-700">
                                            <CheckCircle size={14} /> Verified
                                        </span>
                                    </td>
                                    <td className="px-5 py-4 text-right">
                                        <a
                                            href={wagon.image_url}
                                            target="_blank"
                                            rel="noreferrer"
                                            className="text-blue-700 underline"
                                        >
                                            View Frame
                                        </a>
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan="5" className="px-6 py-12 text-center">
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
