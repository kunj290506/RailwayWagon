import { Link } from 'react-router-dom';
import { ArrowRight, Upload, BarChart, Zap } from 'lucide-react';
import '../styles/design-system.css';
import './SaaSLanding.css';

export default function SaaSLanding() {
    return (
        <div className="landing">
            {/* Header */}
            <header className="header">
                <div className="container">
                    <nav className="nav">
                        <div className="logo">WagonAI</div>
                        <Link to="/dashboard" className="btn btn-primary">
                            Get Started
                            <ArrowRight size={16} />
                        </Link>
                    </nav>
                </div>
            </header>

            {/* Hero */}
            <section className="hero">
                <div className="container text-center">
                    <div className="hero-content fade-in">
                        <h1 className="hero-title">
                            AI-Powered Railway
                            <br />
                            Wagon Detection
                        </h1>
                        <p className="hero-subtitle">
                            Transform blurry footage into actionable insights with NAFNet deblurring
                            and advanced OCR. Production-ready AI for railway inspection.
                        </p>
                        <div className="hero-actions">
                            <Link to="/dashboard" className="btn btn-primary btn-lg">
                                Launch Dashboard
                            </Link>
                            <button className="btn btn-secondary btn-lg">
                                View Demo
                            </button>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features */}
            <section className="features">
                <div className="container">
                    <div className="features-grid">
                        <div className="feature">
                            <div className="feature-icon">
                                <Zap size={24} />
                            </div>
                            <h3>Lightning Fast</h3>
                            <p className="text-secondary">
                                8-15x faster processing with optimized pipelines
                            </p>
                        </div>

                        <div className="feature">
                            <div className="feature-icon">
                                <Upload size={24} />
                            </div>
                            <h3>Easy Upload</h3>
                            <p className="text-secondary">
                                Simple drag-and-drop interface for videos and images
                            </p>
                        </div>

                        <div className="feature">
                            <div className="feature-icon">
                                <BarChart size={24} />
                            </div>
                            <h3>Detailed Analytics</h3>
                            <p className="text-secondary">
                                Comprehensive wagon detection with confidence scores
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="footer">
                <div className="container text-center">
                    <p className="text-secondary">
                        © 2026 WagonAI. Railway inspection made intelligent.
                    </p>
                </div>
            </footer>
        </div>
    );
}
