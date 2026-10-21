'use client';

import {useEffect, useRef} from 'react';

// Integer noise keeps the moving blocks coherent instead of flickering each frame.
function noise(x: number, y: number, seed = 0) {
  let n = Math.imul(x + seed * 71, 374761393) + Math.imul(y, 668265263);
  n = Math.imul(n ^ (n >>> 13), 1274126177);
  return ((n ^ (n >>> 16)) >>> 0) / 4294967295;
}

export default function PixelWash({onReveal}: {onReveal: () => void}) {
  const ambient = useRef<HTMLCanvasElement>(null);
  const intro = useRef<HTMLCanvasElement>(null);
  const overlay = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const canvas = ambient.current;
    const opening = intro.current;
    const cover = overlay.current;
    const section = canvas?.closest('section');
    if (!canvas || !opening || !cover || !section) return;
    const ctx = canvas.getContext('2d', {alpha: true});
    const openingCtx = opening.getContext('2d', {alpha: true});
    if (!ctx || !openingCtx) { cover.hidden = true; onReveal(); return; }

    const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
    let width = 1, height = 1, cell = 12;
    let frame = 0, last = 0, elapsed = 0, drift = 0;
    let visible = true, complete = false, disposed = false;
    const duration = 1380;

    function resize() {
      width = section!.clientWidth;
      height = section!.clientHeight;
      cell = Math.max(10, Math.round(width / 112));
      // These are deliberately low-resolution pixels, not a device-pixel-ratio surface.
      for (const target of [canvas!, opening!]) {
        target.width = width;
        target.height = height;
      }
      drawAmbient(drift);
      if (!complete) drawOpening(elapsed);
    }

    function drawAmbient(time: number) {
      ctx!.clearRect(0, 0, width, height);
      const rows = Math.ceil(height / cell);
      const columns = Math.ceil(width / cell);
      for (let row = 0; row < rows; row++) {
        const speed = 1.4 + noise(row, 9) * 2.7;
        const offset = time * speed;
        for (let col = 0; col <= columns + 5; col++) {
          const world = col + Math.floor(offset);
          const x = (col - offset % 1) * cell;
          const n = noise(Math.floor(world / 2), row, 3);
          const density = 0.05 + Math.pow(Math.max(0, x / width), 2) * 0.75;
          if (n > density) continue;
          const block = noise(world, row, 7);
          const green = block > 0.965 && x > width * 0.3;
          const purple = block > 0.58 ? '#7139b1' : '#462071';
          ctx!.globalAlpha = green ? 0.86 : 0.26 + n * 0.7;
          ctx!.fillStyle = green ? '#79ff37' : purple;
          ctx!.fillRect(Math.floor(x), row * cell, cell * (green ? 2 : 1) + 1, green ? Math.max(3, Math.floor(cell * 0.48)) : cell + 1);
        }
      }
      ctx!.globalAlpha = 1;
    }

    function drawOpening(ms: number) {
      openingCtx!.clearRect(0, 0, width, height);
      const progress = Math.max(0, Math.min(1, (ms - 160) / 1150));
      const sweep = progress * progress * (3 - 2 * progress);
      const front = width * (1 - sweep);
      const rows = Math.ceil(height / cell);
      const offset = Math.floor(ms * width / 480 / cell);
      for (let row = 0; row < rows; row++) {
        const edge = progress === 1 ? -cell : progress === 0 ? width + cell : front + (noise(row, 4) - 0.5) * cell * 10;
        for (let col = 0; col * cell < Math.min(width, edge); col++) {
          const n = noise(Math.floor((col + offset) / 2), row);
          const green = col * cell > width * 0.24 && n > 0.955;
          openingCtx!.fillStyle = green ? '#76ff36' : n > 0.65 ? '#070609' : n > 0.3 ? '#3c1b61' : '#2c124d';
          openingCtx!.fillRect(col * cell, row * cell, cell + 1, cell + 1);
          if (green) {
            openingCtx!.fillStyle = '#120b1d';
            openingCtx!.fillRect(col * cell, row * cell + Math.floor(cell / 2), cell + 1, Math.ceil(cell / 2));
          }
        }
      }
      cover!.dataset.painted = 'true';
    }

    function reveal() {
      if (complete) return;
      complete = true;
      cover!.hidden = true;
      onReveal();
    }

    function tick(now: number) {
      frame = 0;
      if (disposed || document.hidden || (!visible && complete)) { last = 0; return; }
      const delta = last ? Math.min(now - last, 70) : 0;
      last = now;
      elapsed += delta;
      drift += delta / 1000;
      if (!complete) {
        drawOpening(elapsed);
        if (elapsed >= duration) reveal();
      }
      drawAmbient(drift);
      if (!preference.matches) frame = requestAnimationFrame(tick);
    }

    function resume() {
      if (!frame && !preference.matches && !document.hidden && (visible || !complete)) frame = requestAnimationFrame(tick);
    }
    function preferenceChanged() {
      if (preference.matches) {
        cancelAnimationFrame(frame); frame = 0; reveal(); drawAmbient(drift);
      } else resume();
    }
    const observer = new ResizeObserver(resize);
    const visibility = new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; resume(); });
    observer.observe(section);
    visibility.observe(section);
    document.addEventListener('visibilitychange', resume);
    preference.addEventListener('change', preferenceChanged);
    resize();
    if (preference.matches) { reveal(); drawAmbient(0); } else resume();
    return () => {
      disposed = true;
      cancelAnimationFrame(frame);
      observer.disconnect(); visibility.disconnect();
      document.removeEventListener('visibilitychange', resume);
      preference.removeEventListener('change', preferenceChanged);
    };
  }, [onReveal]);

  return <>
    <canvas ref={ambient} className="overview-pixels" data-renderer="pixel-2d" aria-hidden="true"/>
    <div ref={overlay} className="overview-opening" aria-hidden="true"><canvas ref={intro} data-renderer="pixel-2d"/></div>
  </>;
}
