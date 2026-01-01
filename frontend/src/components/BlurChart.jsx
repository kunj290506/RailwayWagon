import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
);

function BlurChart({ frames }) {
    if (!frames || frames.length === 0) return null;

    // Let's show top 20 frames or a sample to avoid overcrowding
    const displayFrames = frames.slice(0, 50);

    const options = {
        responsive: true,
        plugins: {
            legend: { position: 'top' },
            title: { display: true, text: 'Blur Scores (Lower is derived from low variance, usually means Blurred)' },
        },
    };

    const data = {
        labels: displayFrames.map(f => f.filename),
        datasets: [
            {
                label: 'Blur Score',
                data: displayFrames.map(f => f.blur_score),
                backgroundColor: displayFrames.map(f => f.state === 'BLURRED' ? 'rgba(255, 99, 132, 0.5)' : 'rgba(53, 162, 235, 0.5)'),
            },
        ],
    };

    return (
        <div className="card" style={{ height: '400px' }}>
            <Bar options={options} data={data} />
        </div>
    );
}

export default BlurChart;
