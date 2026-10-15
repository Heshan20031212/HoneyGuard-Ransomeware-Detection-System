/**
 * HoneyGuard - Interactive Cyber Constellation Plexus Background Animation
 * High-performance HTML5 Canvas particle & node connectivity mesh
 */

class CyberMesh {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.maxParticles = options.maxParticles || 65;
        this.maxDistance = options.maxDistance || 130;
        this.nodeColor = options.nodeColor || '#06b6d4';
        this.lineColor = options.lineColor || 'rgba(6, 182, 212, 0.15)';
        this.accentNodeColor = options.accentNodeColor || '#10b981';
        this.mouse = { x: null, y: null, radius: 150 };

        this.init();
    }

    init() {
        this.resize();
        window.addEventListener('resize', () => this.resize());
        
        window.addEventListener('mousemove', (e) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
        });

        window.addEventListener('mouseout', () => {
            this.mouse.x = null;
            this.mouse.y = null;
        });

        this.createParticles();
        this.animate();
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    createParticles() {
        this.particles = [];
        const count = Math.min(this.maxParticles, Math.floor((this.canvas.width * this.canvas.height) / 18000));
        for (let i = 0; i < count; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 0.7,
                vy: (Math.random() - 0.5) * 0.7,
                radius: Math.random() * 2 + 1,
                isAccent: Math.random() > 0.7,
                pulse: Math.random() * Math.PI,
                pulseSpeed: 0.02 + Math.random() * 0.03
            });
        }
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Update and draw particles
        for (let i = 0; i < this.particles.length; i++) {
            const p = this.particles[i];

            p.x += p.vx;
            p.y += p.vy;
            p.pulse += p.pulseSpeed;

            // Bounce off edges
            if (p.x < 0 || p.x > this.canvas.width) p.vx *= -1;
            if (p.y < 0 || p.y > this.canvas.height) p.vy *= -1;

            // Mouse interaction
            if (this.mouse.x !== null && this.mouse.y !== null) {
                const dx = this.mouse.x - p.x;
                const dy = this.mouse.y - p.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < this.mouse.radius) {
                    const force = (this.mouse.radius - dist) / this.mouse.radius;
                    p.x -= (dx / dist) * force * 1.5;
                    p.y -= (dy / dist) * force * 1.5;
                }
            }

            // Draw glowing node
            const currentRadius = p.radius + Math.sin(p.pulse) * 0.8;
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, Math.max(0.5, currentRadius), 0, Math.PI * 2);
            this.ctx.fillStyle = p.isAccent ? this.accentNodeColor : this.nodeColor;
            this.ctx.shadowBlur = 8;
            this.ctx.shadowColor = p.isAccent ? this.accentNodeColor : this.nodeColor;
            this.ctx.fill();
            this.ctx.shadowBlur = 0;

            // Connect nearby nodes
            for (let j = i + 1; j < this.particles.length; j++) {
                const p2 = this.particles[j];
                const dx = p.x - p2.x;
                const dy = p.y - p2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < this.maxDistance) {
                    const alpha = (1 - dist / this.maxDistance) * 0.28;
                    this.ctx.beginPath();
                    this.ctx.moveTo(p.x, p.y);
                    this.ctx.lineTo(p2.x, p2.y);
                    this.ctx.strokeStyle = `rgba(6, 182, 212, ${alpha})`;
                    this.ctx.lineWidth = 1;
                    this.ctx.stroke();
                }
            }
        }

        requestAnimationFrame(() => this.animate());
    }
}

// Auto-initialize canvas if present
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('cyberCanvas')) {
        new CyberMesh('cyberCanvas');
    }
});
