import React, { useRef, useState } from 'react';

const TiltCard = ({ children, className = "" }) => {
    const cardRef = useRef(null);
    const [transform, setTransform] = useState('');
    const [shine, setShine] = useState('');

    const handleMouseMove = (e) => {
        if (!cardRef.current) return;

        const { left, top, width, height } = cardRef.current.getBoundingClientRect();
        const x = e.clientX - left;
        const y = e.clientY - top;

        const centerX = width / 2;
        const centerY = height / 2;

        const rotateX = ((y - centerY) / centerY) * -3; // Max rotation deg
        const rotateY = ((x - centerX) / centerX) * 3;

        setTransform(`perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`);

        // Calculate Shine Gradient
        const shineOpacity = 0.15;
        const shineX = (x / width) * 100;
        const shineY = (y / height) * 100;

        // Apple Card-like holographic shine
        setShine(`
            radial-gradient(
                circle at ${shineX}% ${shineY}%, 
                rgba(255, 255, 255, 0.8) 0%, 
                rgba(255, 255, 255, 0) 60%
            )
        `);
    };

    const handleMouseLeave = () => {
        setTransform('perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)');
        setShine('');
    };

    return (
        <div
            ref={cardRef}
            className={`relative transition-all duration-200 ease-out will-change-transform ${className}`}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
            style={{
                transformStyle: 'preserve-3d',
                transform
            }}
        >
            {/* Glossy Content */}
            <div className="relative z-10 h-full">
                {children}
            </div>

            {/* Apple Card Gradient Mesh (Subtle Background) */}
            <div className={`absolute inset-0 z-0 rounded-2xl opacity-50 transition-opacity duration-300 pointer-events-none ${shine ? 'opacity-100' : 'opacity-0'}`}
                style={{
                    background: 'linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0) 100%)',
                    boxShadow: 'inset 0 0 0 1px rgba(255,255,255,0.2)'
                }}
            />

            {/* Dynamic Glare Overlay */}
            <div
                className="absolute inset-0 z-20 rounded-2xl pointer-events-none mix-blend-overlay"
                style={{ background: shine }}
            />
        </div>
    );
};

export default TiltCard;
