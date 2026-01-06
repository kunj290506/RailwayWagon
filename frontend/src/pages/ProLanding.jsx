import { Link } from 'react-router-dom';
import { ArrowRight, Cpu, Gauge, Shield } from 'lucide-react';
import '../styles/design-system.css';
import './ProLanding.css';

export default function ProLanding() {
    return (
        <div className="app">
            {/* Navigation */}
            <nav className="nav">
                <div className="container">
                    <div className="nav-content">
                        <div className="nav-brand">
                            <div className="brand-icon">
                                <Cpu size={20} strokeWidth={2} />
                            </div>
                            <span className="brand-name">WagonAI</span>
                        </div>
                        <Link to="/dashboard" className="btn btn-primary">
                            Launch Platform <ArrowRight size={16} />
                        </Link>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="hero section">
                <div className="container">
                    <div className="hero-content">
                        <div className="badge badge-primary mb-6">
                            <span>PRODUCTION AI SYSTEM</span>
                        </div>

                        <h1 className="hero-title">
                            Advanced Railway Wagon
                            <br />
                            Detection System
                        </h1>

                        <p className="hero-description text-secondary">
                            State-of-the-art computer vision system powered by NAFNet neural architecture.
                            Achieving 33.7 dB PSNR with real-time processing capabilities for industrial railway inspection.
                        </p>

                        <div className="hero-actions">
                            <Link to="/dashboard" className="btn btn-primary btn-lg">
                                Access Dashboard
                            </Link>
                            <button className="btn btn-secondary btn-lg">
                                Technical Documentation
                            </button>
                        </div>

                        {/* Performance Metrics */}
                        <div className="metrics-grid">
                            <div className="metric">
                                <div className="metric-value">33.7 dB</div>
                                <div className="metric-label">PSNR Quality</div>
                            </div>
                            <div className="metric">
                                <div className="metric-value">0.967</div>
                                <div className="metric-label">SSIM Score</div>
                            </div>
                            <div className="metric">
                                <div className="metric-value">8-15x</div>
                                <div className="metric-label">Processing Speed</div>
                            </div>
                            <div className="metric">
                                <div className="metric-value">FP16</div>
                                <div className="metric-label">Precision Mode</div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Technical Features */}
            <section className="features section">
                <div className="container">
                    <div className="grid grid-3">
                        <div className="feature-card card card-hoverable">
                            <div className="feature-icon">
                                <Cpu size={24} />
                            </div>
                            <h3>NAFNet Architecture</h3>
                            <p className="text-secondary">
                                Pre-trained neural network achieving industry-leading deblurring performance
                                with nonlinear activation-free design.
                            </p>
                            <div className="badge badge-success mt-4">
                                <span>Pre-trained Model</span>
                            </div>
                        </div>

                        <div className="feature-card card card-hoverable">
                            <div className="feature-icon">
                                <Gauge size={24} />
                            </div>
                            <h3>Optimized Pipeline</h3>
                            <p className="text-secondary">
                                FP16 inference, automatic resolution scaling, and parallel processing
                                for maximum throughput.
                            </p>
                            <div className="badge badge-primary mt-4">
                                <span>8-15x Faster</span>
                            </div>
                        </div>

                        <div className="feature-card card card-hoverable">
                            <div className="feature-icon">
                                <Shield size={24} />
                            </div>
                            <h3>Production Ready</h3>
                            <p className="text-secondary">
                                Robust OCR with PaddleOCR, comprehensive error handling, and full
                                batch processing capabilities.
                            </p>
                            <div className="badge badge-success mt-4">
                                <span>Enterprise Grade</span>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Technical Specs */}
            <section className="specs section">
                <div className="container">
                    <div className="specs-card card">
                        <h2 className="mb-6">Technical Specifications</h2>
                        <div className="specs-grid">
                            <div className="spec-item">
                                <div className="spec-label">Model Architecture</div>
                                <div className="spec-value">NAFNet (width-64)</div>
                            </div>
                            <div className="spec-item">
                                <div className="spec-label">Image Processing</div>
                                <div className="spec-value">Up to 720p</div>
                            </div>
                            <div className="spec-item">
                                <div className="spec-label">OCR Engine</div>
                                <div className="spec-value">PaddleOCR + EasyOCR</div>
                            </div>
                            <div className="spec-item">
                                <div className="spec-label">Compute Mode</div>
                                <div className="spec-value">CUDA + FP16</div>
                            </div>
                            <div className="spec-item">
                                <div className="spec-label">Batch Processing</div>
                                <div className="spec-value">Unlimited</div>
                            </div>
                            <div className="spec-item">
                                <div className="spec-label">API Framework</div>
                                <div className="spec-value">FastAPI</div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="footer">
                <div className="container">
                    <div className="footer-content">
                        <div className="footer-brand">
                            <Cpu size={20} />
                            <span>WagonAI</span>
                        </div>
                        <p className="text-tertiary">
                            Advanced AI-powered railway inspection system
                        </p>
                    </div>
                </div>
            </footer>
        </div>
    );
}
