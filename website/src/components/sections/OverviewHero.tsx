'use client';

import {useCallback, useEffect, useRef, useState} from 'react';
import {assets} from '@/data/assets';
import PixelWash from '../interactive/PixelWash';

export default function OverviewHero() {
  const root = useRef<HTMLElement>(null);
  const [revealed, setRevealed] = useState(false);
  const onReveal = useCallback(() => setRevealed(true), []);

  useEffect(() => {
    const element = root.current;
    if (!element) return;
    let frame = 0;
    const scroll = () => {
      if (frame) return;
      frame = requestAnimationFrame(() => {
        element.style.setProperty('--overview-scroll', `${Math.min(window.scrollY, element.clientHeight) * -0.08}px`);
        frame = 0;
      });
    };
    const move = (event: PointerEvent) => {
      if (event.pointerType !== 'mouse') return;
      const rect = element.getBoundingClientRect();
      element.style.setProperty('--overview-x', `${(event.clientX / rect.width - 0.5) * 12}px`);
      element.style.setProperty('--overview-y', `${((event.clientY - rect.top) / rect.height - 0.5) * 9}px`);
    };
    const leave = () => {
      element.style.setProperty('--overview-x', '0px');
      element.style.setProperty('--overview-y', '0px');
    };
    window.addEventListener('scroll', scroll, {passive: true});
    element.addEventListener('pointermove', move, {passive: true});
    element.addEventListener('pointerleave', leave);
    scroll();
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener('scroll', scroll);
      element.removeEventListener('pointermove', move);
      element.removeEventListener('pointerleave', leave);
    };
  }, []);

  return <section ref={root} id="overview" className="overview-hero" aria-label="酸性合金键盘概览" data-phase={revealed ? 'ambient' : 'opening'}>
    <PixelWash onReveal={onReveal}/>
    <figure className="overview-product">
      <div className="overview-product-media"><div className="overview-product-float">
        <img className="overview-keyboard" src={assets.overviewImage.src} alt={assets.overviewImage.alt} width={assets.overviewImage.width} height={assets.overviewImage.height} fetchPriority="high" draggable={false}/>
      </div></div>
      <figcaption><h1>Key board</h1></figcaption>
    </figure>
  </section>;
}
