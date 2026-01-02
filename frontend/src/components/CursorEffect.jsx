import React, { useEffect, useRef } from 'react';

/**
 * Multicolor Constellation Effect
 * 
 * - Background: Transparent (Relies on parent 'bg-white')
 * - Particles: Multicolored dots (Adani Brand + Vibrant Accents)
 * - Interaction: Magnetic Attraction (Cursor acts as a gravity well)
 * - Connections: Subtle gray lines forming a network
 */
const CursorEffect = () => {
    const canvasRef = useRef(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d', { alpha: true });
        let animeId;

        // --- CONFIG ---
        const CONFIG = {
            particleCount: 120, // Reduced for cleaner look on white
            connectionRadius: 100,
            mouseRadius: 200,
            colorPalette: [
                '236, 114, 17',  // Adani Orange
                '35, 47, 62',    // Adani Dark Blue
                '16, 185, 129',  // Emerald
                '59, 130, 246',  // Blue
                '139, 92, 246',  // Violet
                '244, 63, 94',   // Rose
            ],
            baseBaseSpeed: 0.5,
        };

        let width = 0;
        let height = 0;
        const mouse = { x: -1000, y: -1000 }; // Start off-screen

        class Particle {
            constructor() {
                this.x = Math.random() * width;
                this.y = Math.random() * height;

                // Random Velocity
                this.vx = (Math.random() - 0.5) * CONFIG.baseBaseSpeed;
                this.vy = (Math.random() - 0.5) * CONFIG.baseBaseSpeed;

                this.size = Math.random() * 2 + 1.5; // Slightly larger dots

                // Assign Random Color from Palette
                const colorStr = CONFIG.colorPalette[Math.floor(Math.random() * CONFIG.colorPalette.length)];
                this.color = `rgba(${colorStr}, 0.8)`;
                this.lineColor = `rgba(${colorStr}, 0.15)`; // For connections (optional usage)
            }

            update() {
                // 1. Mouse Interaction: ATTRACTION (Magnetic)
                // "Cursor reaction differ" -> Instead of repel, we attract gently
                const dx = mouse.x - this.x;
                const dy = mouse.y - this.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < CONFIG.mouseRadius) {
                    const forceDirectionX = dx / dist;
                    const forceDirectionY = dy / dist;
                    const force = (CONFIG.mouseRadius - dist) / CONFIG.mouseRadius;

                    // Gentle pull
                    const attractionStrength = 0.05;
                    this.vx += forceDirectionX * force * attractionStrength;
                    this.vy += forceDirectionY * force * attractionStrength;
                }

                // 2. Movement
                this.x += this.vx;
                this.y += this.vy;

                // 3. Friction/Damping (keep them stable)
                this.vx *= 0.99;
                this.vy *= 0.99;

                // 4. Boundary Wrap
                if (this.x < 0) this.x = width;
                if (this.x > width) this.x = 0;
                if (this.y < 0) this.y = height;
                if (this.y > height) this.y = 0;

                // 5. Min Speed Maintenance (don't stop completely)
                // If too slow, give random nudge
                if (Math.abs(this.vx) < 0.1 && Math.abs(this.vy) < 0.1) {
                    this.vx += (Math.random() - 0.5) * 0.2;
                    this.vy += (Math.random() - 0.5) * 0.2;
                }
            }

            draw() {
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        let particles = [];
        const init = () => {
            particles = [];
            // Responsive count
            const count = (width * height) / 15000; // Density based
            const finalCount = Math.min(Math.max(count, 50), 200); // Clamp

            for (let i = 0; i < finalCount; i++) {
                particles.push(new Particle());
            }
        }

        const animate = () => {
            ctx.clearRect(0, 0, width, height);

            // Connect Particles
            ctx.lineWidth = 0.5;

            for (let i = 0; i < particles.length; i++) {
                particles[i].update();
                particles[i].draw();

                // Check connections
                for (let j = i; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const distance = Math.sqrt(dx * dx + dy * dy);

                    if (distance < CONFIG.connectionRadius) {
                        // Opacity based on distance
                        let opacity = 1 - (distance / CONFIG.connectionRadius);
                        opacity = opacity * 0.5; // Lower max opacity

                        ctx.strokeStyle = `rgba(150, 160, 180, ${opacity})`; // Neutral Gray-ish Blue for lines
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.stroke();
                    }
                }

                // Connect to Mouse (Extra range)
                const dx = particles[i].x - mouse.x;
                const dy = particles[i].y - mouse.y;
                const distMouse = Math.sqrt(dx * dx + dy * dy);
                if (distMouse < CONFIG.connectionRadius * 1.5) {
                    let opacity = 1 - (distMouse / (CONFIG.connectionRadius * 1.5));
                    ctx.strokeStyle = `rgba(100, 116, 139, ${opacity})`; // Slightly darker for mouse connection
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(mouse.x, mouse.y);
                    ctx.stroke();
                }
            }

            animeId = requestAnimationFrame(animate);
        }

        const resize = () => {
            width = window.innerWidth;
            height = window.innerHeight;
            canvas.width = width;
            canvas.height = height;
            init(); // Re-init on resize to adjust density
        }

        const handleMouseMove = (e) => {
            const rect = canvas.getBoundingClientRect();
            mouse.x = e.clientX - rect.left;
            mouse.y = e.clientY - rect.top;
        }

        const handleMouseLeave = () => {
            mouse.x = -1000;
            mouse.y = -1000;
        }

        window.addEventListener('resize', resize);
        window.addEventListener('mousemove', handleMouseMove);
        window.addEventListener('mouseleave', handleMouseLeave);

        resize();
        animate();

        return () => {
            window.removeEventListener('resize', resize);
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseleave', handleMouseLeave);
            cancelAnimationFrame(animeId);
        };
    }, []);

    return (
        <div className="fixed inset-0 pointer-events-none z-0">
            <canvas ref={canvasRef} className="absolute inset-0 block" />
        </div>
    );
};

export default CursorEffect;
