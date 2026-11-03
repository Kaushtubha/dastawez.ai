import React, { useEffect, useRef } from 'react';

const MatrixBackground = ({ opacity = 0.22, color = 'purple' }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let animationFrameId;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789§±¥$€£#@!%&*()<>{}[]';
    const fontSize = 14;
    let columns = Math.floor(canvas.width / fontSize);
    let drops = Array(columns).fill(1).map(() => Math.floor(Math.random() * -50));

    let lastDraw = 0;
    const fpsInterval = 1000 / 30; // 30 FPS

    const draw = (timestamp) => {
      animationFrameId = requestAnimationFrame(draw);
      const elapsed = timestamp - lastDraw;
      if (elapsed < fpsInterval) return;
      lastDraw = timestamp - (elapsed % fpsInterval);

      // Semi-transparent fade layer
      ctx.fillStyle = 'rgba(15, 12, 41, 0.08)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.font = `${fontSize}px 'JetBrains Mono', monospace`;

      for (let i = 0; i < drops.length; i++) {
        const char = characters.charAt(Math.floor(Math.random() * characters.length));
        const x = i * fontSize;
        const y = drops[i] * fontSize;

        // Custom gradient for characters
        if (color === 'pink') {
          ctx.fillStyle = drops[i] % 2 === 0 ? '#f093fb' : '#f5576c';
        } else if (color === 'cyan') {
          ctx.fillStyle = drops[i] % 2 === 0 ? '#38bdf8' : '#00f2fe';
        } else {
          ctx.fillStyle = drops[i] % 2 === 0 ? '#a78bfa' : '#c084fc';
        }

        ctx.fillText(char, x, y);

        if (y > canvas.height && Math.random() > 0.975) {
          drops[i] = 0;
        }
        drops[i]++;
      }
    };

    animationFrameId = requestAnimationFrame(draw);

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animationFrameId);
    };
  }, [color]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 1,
        opacity: opacity
      }}
    />
  );
};

export default MatrixBackground;

