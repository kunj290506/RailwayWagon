import React, { useEffect, useState } from 'react';
import { Clock, Download, ChevronRight, HardDrive, Calendar, Database, Home } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import PageHeader from '../components/PageHeader';

const HistoryPage = () => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetch('http://localhost:8000/history')
            .then(res => res.json())
            .then(data => {
                setHistory(data);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    return (
        <div className="max-w-[1600px] mx-auto animate-fade-in">
            <PageHeader
                title="Archives & History"
                description="Permanent record of all inspection batches and enhancement sessions"
                breadcrumbs={[
                    { label: 'Dashboard', path: '/', icon: Home },
                    { label: 'History' }
                ]}
            />

            {loading ? (
                <div className="flex items-center justify-center py-20">
                    <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-[#ec7211]"></div>
                </div>
            ) : history.length === 0 ? (
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-12 text-center">
                    <div className="bg-slate-50 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
                        <HardDrive size={40} className="text-slate-400" />
                    </div>
                    <h3 className="text-xl font-bold text-slate-800 mb-2">No Archives Found</h3>
                    <p className="text-slate-500 max-w-md mx-auto">
                        Your history will appear here once you process your first video.
                    </p>
                </div>
            ) : (
                <div className="grid grid-cols-1 gap-4">
                    {history.map((batch) => (
                        <div
                            key={batch.batch_id}
                            className="group bg-white rounded-lg border border-slate-200 p-6 flex items-center justify-between hover:border-[#ec7211] hover:shadow-md transition-all cursor-pointer"
                            onClick={() => {
                                // Navigate to reports with this batch selected? 
                                // Or better, just show a "View Report" button that goes to reports
                                navigate(`/reports?batch=${batch.batch_id}`);
                            }}
                        >
                            <div className="flex items-center gap-6">
                                <div className="bg-orange-50 text-[#ec7211] p-4 rounded-lg">
                                    <Clock size={24} />
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold text-slate-800 flex items-center gap-3">
                                        Batch #{batch.batch_id}
                                        <span className="bg-slate-100 text-slate-600 text-xs px-2 py-0.5 rounded-full uppercase font-bold tracking-wide">
                                            Archived
                                        </span>
                                    </h3>
                                    <div className="flex items-center gap-6 mt-2 text-sm text-slate-500">
                                        <span className="flex items-center gap-1.5">
                                            <Calendar size={14} />
                                            {new Date(batch.timestamp).toLocaleString()}
                                        </span>
                                        <span className="flex items-center gap-1.5">
                                            <HardDrive size={14} />
                                            {batch.wagon_count} Wagons Processed
                                        </span>
                                        <span className="flex items-center gap-1.5">
                                            <Database size={14} />
                                            {batch.total_frames} Frames Analyzed
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <div className="flex items-center gap-4">
                                <button className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1 text-sm font-bold text-[#ec7211] hover:underline">
                                    View Full Report <ChevronRight size={16} />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default HistoryPage;
