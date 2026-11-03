import React, { useEffect, useState } from 'react';

const CustomCursor = () => {
  const [pos, setPos] = useState({ x: -100, y: -100 });
  const [innerPos, setInnerPos] = useState({ x: -100, y: -100 });
  const [isHovered, setIsHovered] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    if (window.matchMedia('(pointer: coarse)').matches) {
      setIsMobile(true);
      return;
    }

    let mouseX = -100;
    let mouseY = -100;
    let outerX = -100;
    let outerY = -100;
    let dotX = -100;
    let dotY = -100;
    let animId;

    const onMouseMove = (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;

      const target = e.target;
      const clickable = target && (
        target.tagName === 'BUTTON' ||
        target.tagName === 'A' ||
        target.tagName === 'INPUT' ||
        target.closest('button') ||
        target.closest('a') ||
        target.classList.contains('hover-target')
      );
      setIsHovered(!!clickable);
    };

    const render = () => {
      outerX += (mouseX - outerX) * 0.18;
      outerY += (mouseY - outerY) * 0.18;
      dotX += (mouseX - dotX) * 0.45;
      dotY += (mouseY - dotY) * 0.45;

      setPos({ x: outerX, y: outerY });
      setInnerPos({ x: dotX, y: dotY });
      animId = requestAnimationFrame(render);
    };

    window.addEventListener('mousemove', onMouseMove);
    animId = requestAnimationFrame(render);

    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      cancelAnimationFrame(animId);
    };
  }, []);

  if (isMobile) return null;

  return (
    <>
      <div
        className={`custom-cursor-outer ${isHovered ? 'custom-cursor-hover' : ''}`}
        style={{ left: `${pos.x}px`, top: `${pos.y}px` }}
      />
      <div
        className="custom-cursor-inner"
        style={{ left: `${innerPos.x}px`, top: `${innerPos.y}px` }}
      />
    </>
  );
};

export default CustomCursor;

