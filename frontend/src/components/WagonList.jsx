function WagonList({ wagons }) {
    if (!wagons || wagons.length === 0) return null;

    return (
        <div className="mt-8 bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="p-6 border-b border-slate-200">
                <h3 className="text-lg font-bold text-slate-800">Detected Wagon Numbers (Unique)</h3>
                <p className="text-slate-500 text-sm">Found {wagons.length} unique 11-digit identification numbers.</p>
            </div>

            <div className="overflow-x-auto max-h-96">
                <table className="w-full text-left text-sm text-slate-600">
                    <thead className="bg-slate-50 text-slate-700 uppercase font-bold text-xs sticky top-0">
                        <tr>
                            <th className="px-6 py-4">Wagon Number</th>
                            <th className="px-6 py-4">Accuracy</th>
                            <th className="px-6 py-4">Best Frame</th>
                            <th className="px-6 py-4">Preview</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {wagons.map((wagon, idx) => (
                            <tr key={idx} className="hover:bg-slate-50 transition">
                                <td className="px-6 py-4 font-mono text-lg font-bold text-blue-600 tracking-wider">
                                    {wagon.number}
                                </td>
                                <td className="px-6 py-4">
                                    {wagon.confidence ? (
                                        <span className={`px-2 py-1 rounded text-xs font-bold ${wagon.confidence > 0.8 ? 'bg-green-100 text-green-700' :
                                                wagon.confidence > 0.5 ? 'bg-yellow-100 text-yellow-700' :
                                                    'bg-red-100 text-red-700'
                                            }`}>
                                            {(wagon.confidence * 100).toFixed(1)}%
                                        </span>
                                    ) : (
                                        <span className="text-slate-400 text-xs">N/A</span>
                                    )}
                                </td>
                                <td className="px-6 py-4 text-slate-500 font-mono">
                                    {wagon.frame}
                                </td>
                                <td className="px-6 py-4">
                                    <a
                                        href={wagon.image_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-blue-500 hover:text-blue-700 hover:underline font-medium"
                                    >
                                        View Image
                                    </a>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default WagonList;
