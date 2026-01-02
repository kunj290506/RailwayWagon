import React, { useEffect, useState } from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    ArcElement
} from 'chart.js';
import { Line, Doughnut } from 'react-chartjs-2';
import PageHeader from '../components/PageHeader';
import { BarChart, TrendingUp, AlertTriangle, Home } from 'lucide-react';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    ArcElement
);

const AnalyticsPage = () => {
    const [metadata, setMetadata] = useState([]);

    useEffect(() => {
        fetch('http://localhost:8000/metadata')
            .then(res => res.json())
            .then(data => setMetadata(data));
    }, []);

    const blurScores = metadata.map(m => m.blur_score);
    const labels = metadata.map(m => m.frame_index);
    const blurredCount = metadata.filter(m => m.is_blurred).length;
    const sharpCount = metadata.length - blurredCount;

    const lineData = {
        labels: labels.filter((_, i) => i % 10 === 0), // Sample for chart
        datasets: [
            {
                label: 'Blur Score (Laplacian Variance)',
                data: blurScores.filter((_, i) => i % 10 === 0),
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.5)',
                tension: 0.4
            },
            {
                label: 'Threshold (100)',
                data: Array(labels.filter((_, i) => i % 10 === 0).length).fill(100),
                borderColor: 'rgb(239, 68, 68)',
                borderDash: [5, 5],
                pointRadius: 0
            }
        ],
    };

    const pieData = {
        labels: ['Sharp Frames', 'Blurred Frames'],
        datasets: [
            {
                data: [sharpCount, blurredCount],
                backgroundColor: ['#10B981', '#EF4444'],
                hoverOffset: 4
            }
        ]
    };

    return (
        <div className="max-w-[1600px] mx-auto">
            <PageHeader
                title="Motion Analytics"
                description="Telemetry and blur variance metrics across inspection sessions"
                breadcrumbs={[
                    { label: 'Dashboard', path: '/', icon: Home },
                    { label: 'Analytics' }
                ]}
            />

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 bg-blue-50 rounded-lg">
                            <BarChart className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-slate-600">Total Frames</p>
                            <p className="text-2xl font-bold text-slate-900">{metadata.length}</p>
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 bg-red-50 rounded-lg">
                            <AlertTriangle className="w-5 h-5 text-red-600" />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-slate-600">Blurred Frames</p>
                            <p className="text-2xl font-bold text-slate-900">{blurredCount}</p>
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 bg-emerald-50 rounded-lg">
                            <TrendingUp className="w-5 h-5 text-emerald-600" />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-slate-600">Sharp Frames</p>
                            <p className="text-2xl font-bold text-slate-900">{sharpCount}</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className="bg-white p-4 border border-gray-300 shadow-sm">
                    <h3 className="text-sm font-bold text-[#16191f] mb-4 border-b border-gray-100 pb-2">Blur Score Variance (Time Series)</h3>
                    <div className="h-64">
                        <Line options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, usePointStyle: true } } },
                            scales: {
                                x: { grid: { display: false } },
                                y: { grid: { color: '#f3f4f6' }, border: { dash: [4, 4] } }
                            }
                        }} data={lineData} />
                    </div>
                </div>

                <div className="bg-white p-4 border border-gray-300 shadow-sm">
                    <h3 className="text-sm font-bold text-[#16191f] mb-4 border-b border-gray-100 pb-2">Quality Distribution</h3>
                    <div className="h-64 flex justify-center">
                        <div className="w-64">
                            <Doughnut options={{ plugins: { legend: { position: 'right', labels: { boxWidth: 10, usePointStyle: true } } } }} data={pieData} />
                        </div>
                    </div>
                </div>
            </div>

            <div className="bg-white border border-gray-300 shadow-sm">
                <div className="bg-[#fafafa] px-5 py-3 border-b border-gray-200">
                    <h3 className="font-bold text-[#16191f] text-sm">Raw Telemetry Data</h3>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left text-[#16191f]">
                        <thead className="bg-[#fafafa] text-[#545b64] uppercase font-bold text-xs border-b border-gray-200">
                            <tr>
                                <th className="px-5 py-2">Frame Sequence ID</th>
                                <th className="px-5 py-2">Timestamp (Offset)</th>
                                <th className="px-5 py-2">Laplacian Variance</th>
                                <th className="px-5 py-2">QC Status</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {metadata.slice(0, 10).map((row, idx) => (
                                <tr key={idx} className="hover:bg-[#f1f8ff]">
                                    <td className="px-5 py-2 font-mono text-[#545b64]">{row.frame_index}</td>
                                    <td className="px-5 py-2 font-mono">{row.timestamp.toFixed(4)}s</td>
                                    <td className="px-5 py-2 font-bold">{Math.round(row.blur_score)}</td>
                                    <td className="px-5 py-2">
                                        {row.is_blurred ? (
                                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800 border border-red-200">
                                                REJECTED (BLUR)
                                            </span>
                                        ) : (
                                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800 border border-green-200">
                                                PASS
                                            </span>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    <div className="bg-[#fafafa] px-5 py-2 border-t border-gray-200 text-xs text-[#545b64] flex justify-between">
                        <span>Showing 1-10 of {metadata.length} records</span>
                        <span className="text-[#0073bb] cursor-pointer hover:underline">View All</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AnalyticsPage;
