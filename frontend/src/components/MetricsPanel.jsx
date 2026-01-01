function MetricsPanel({ metrics }) {
    if (!metrics) return null;

    return (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px', margin: '24px 0' }}>
            <div className="card" style={{ textAlign: 'center' }}>
                <h4 style={{ color: 'var(--text-muted)' }}>Total Frames</h4>
                <p style={{ fontSize: '36px', marginTop: '10px' }}>{metrics.total}</p>
            </div>
            <div className="card" style={{ textAlign: 'center' }}>
                <h4 style={{ color: 'var(--text-muted)' }}>Blurred Frames</h4>
                <p style={{ fontSize: '36px', marginTop: '10px', color: 'var(--error)' }}>{metrics.blurred_count}</p>
            </div>
            <div className="card" style={{ textAlign: 'center' }}>
                <h4 style={{ color: 'var(--text-muted)' }}>Blur Percentage</h4>
                <p style={{ fontSize: '36px', marginTop: '10px', color: metrics.blurred_percentage > 20 ? 'orange' : 'var(--success)' }}>
                    {metrics.blurred_percentage}%
                </p>
            </div>
        </div>
    );
}

export default MetricsPanel;
