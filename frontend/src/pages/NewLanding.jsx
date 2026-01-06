import { Link } from 'react-router-dom';
import { Play, Zap, Shield, TrendingUp, ArrowRight, Sparkles } from 'lucide-react';
import '../styles/design-system.css';
import './NewLanding.css';

export default function NewLanding() {
    return (
        <div className="landing-page">
            {/* Light Background */}
            <div className="light-bg"></div>

            {/* Hero Section */}
            <section className="hero">
                <div className="container">
                    <div className="hero-content fade-in">
                        <div className="hero-badge">
                            <Sparkles size={16} />
                            <span>AI-Powered Wagon Detection</span>
                        </div>

                        <h1 className="hero-title">
                            Railway Vision
                            <br />
                            <span className="gradient-text">Redefined</span>
                        </h1>

                        <p className="hero-subtitle">
                            Transform blurry railway footage into crystal-clear insights with our
                            state-of-the-art NAFNet deblurring (33.7 dB PSNR) and advanced OCR technology.
                        </p>

                        <div className="hero-actions">
                            <Link to="/dashboard" className="btn btn-primary btn-lg">
                                Launch Dashboard
                                <ArrowRight size={20} />
                            </Link>
                            <button className="btn btn-outline btn-lg">
                                <Play size={20} />
                                Watch Demo
                            </button>
                        </div>

                        <div className="hero-stats">
                            <div className="stat">
                                <div className="stat-value gradient-text">33.7 dB</div>
                                <div className="stat-label">PSNR Quality</div>
                            </div>
                            <div className="stat">
                                <div className="stat-value gradient-text">0.967</div>
                                <div className="stat-label">SSIM Score</div>
                            </div>
                            <div className="stat">
                                <div className="stat-value gradient-text">8-15x</div>
                                <div className="stat-label">Faster Processing</div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="features">
                <div className="container">
                    <h2 className="section-title text-center mb-xl">
                        Powerful Features
                    </h2>

                    <div className="features-grid">
                        <div className="feature-card card-glass">
                            <div className="feature-icon gradient-primary">
                                <Zap size={32} />
                            </div>
                            <h3>Lightning Fast</h3>
                            <p className="text-secondary">
                                8-15x faster processing with FP16 inference and optimized pipelines
                            </p>
                        </div>

                        <div className="feature-card card-glass">
                            <div className="feature-icon gradient-success">
                                <Shield size={32} />
                            </div>
                            <h3>Production Ready</h3>
                            <p className="text-secondary">
                                Pre-trained NAFNet model achieving industry-leading 33.7 dB PSNR
                            </p>
                        </div>

                        <div className="feature-card card-glass">
                            <div className="feature-icon gradient-secondary">
                                <TrendingUp size={32} />
                            </div>
                            <h3>Advanced OCR</h3>
                            <p className="text-secondary">
                                PaddleOCR with advanced preprocessing for accurate wagon number detection
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="cta">
                <div className="container">
                    <div className="cta-card card-glass">
                        <h2>Ready to Transform Your Railway Inspection?</h2>
                        <p className="text-secondary mt-md mb-lg">
                            Get started in seconds with our powerful AI-driven platform
                        </p>
                        <Link to="/dashboard" className="btn btn-primary btn-lg">
                            Get Started Now
                            <ArrowRight size={20} />
                        </Link>
                    </div>
                </div>
            </section>
        </div>
    );
}
