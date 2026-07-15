'use client';

import { useRef, useState, useEffect, memo } from 'react';

interface WebsitePreviewProps {
  /** HTML file path, e.g. /websites/lets-smile-dental.html — auto-mapped to screenshot */
  src?: string;
  title: string;
}

const MAX_HEIGHT_DEFAULT = 300;

const WebsitePreview = memo(function WebsitePreview({
  src,
  title,
}: WebsitePreviewProps) {
  const outerRef = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [maxHeight, setMaxHeight] = useState(MAX_HEIGHT_DEFAULT);

  // Map HTML path → screenshot PNG
  const screenshotSrc = src
    ? src
        .replace(/\.html$/, '.png')
        .replace('/websites/', '/websites/screenshots/')
    : null;

  // ---------- IntersectionObserver: lazy-load ----------
  useEffect(() => {
    const el = outerRef.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          obs.disconnect();
        }
      },
      { rootMargin: '200px' },
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  // ---------- Responsive max-height ----------
  useEffect(() => {
    if (!outerRef.current) return;
    const update = () => {
      const w = outerRef.current!.offsetWidth;
      setMaxHeight(Math.max(300, Math.min(500, w * 0.95)));
    };
    update();
    const ro = new ResizeObserver(update);
    ro.observe(outerRef.current);
    return () => ro.disconnect();
  }, []);

  // ---------- No-src placeholder ----------
  if (!screenshotSrc) {
    return (
      <div
        className="website-preview"
        style={{
          width: '100%',
          height: 180,
          background: '#1e1e2e',
          borderRadius: '12px 12px 0 0',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 8,
          color: 'rgba(255,255,255,0.2)',
          fontSize: '0.8rem',
        }}
      >
        <div style={{ fontSize: '2rem', opacity: 0.4 }}>🎨</div>
        <span>Brand Identity Preview</span>
      </div>
    );
  }

  return (
    <div
      ref={outerRef}
      className="website-preview"
      style={{
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        background: '#1e1e2e',
        borderRadius: '12px 12px 0 0',
        overflow: 'hidden',
        maxHeight: maxHeight,
      }}
    >
      {/* ===== Scrollable image area ===== */}
      <div
        className="preview-scroll"
        style={{
          flex: 1,
          overflowY: 'auto',
          overflowX: 'hidden',
          scrollbarWidth: 'thin',
          scrollbarColor: '#4f46e5 #1e1e2e',
        }}
      >
        <style>{`
          .preview-scroll::-webkit-scrollbar { width: 5px; }
          .preview-scroll::-webkit-scrollbar-track { background: #1e1e2e; }
          .preview-scroll::-webkit-scrollbar-thumb { background: #4f46e5; border-radius: 3px; }
        `}</style>
        {/* Skeleton */}
        {!loaded && (
          <div
            style={{
              height: 300,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 12,
              color: 'rgba(255,255,255,0.25)',
              fontSize: '0.8rem',
            }}
          >
            <div
              style={{
                width: 28,
                height: 28,
                borderRadius: '50%',
                border: '3px solid rgba(255,255,255,0.08)',
                borderTopColor: '#818cf8',
                animation: 'wpspin 0.8s linear infinite',
              }}
            />
            <span>Loading preview…</span>
          </div>
        )}

        {/* Screenshot image */}
        {isVisible && (
          <img
            src={screenshotSrc}
            alt={title}
            onLoad={() => setLoaded(true)}
            style={{
              width: '100%',
              height: 'auto',
              display: 'block',
              opacity: loaded ? 1 : 0,
              transition: 'opacity 0.4s',
            }}
          />
        )}
      </div>

      {/* ===== Viewer bar (always visible at bottom) ===== */}
      <div
        style={{
          flexShrink: 0,
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          padding: '7px 12px',
          background: '#2a2a3e',
          borderTop: '1px solid rgba(255,255,255,0.06)',
        }}
      >
        <span
          style={{
            width: 10,
            height: 10,
            borderRadius: '50%',
            background: '#ff5f57',
            flexShrink: 0,
          }}
        />
        <span
          style={{
            width: 10,
            height: 10,
            borderRadius: '50%',
            background: '#febc2e',
            flexShrink: 0,
          }}
        />
        <span
          style={{
            width: 10,
            height: 10,
            borderRadius: '50%',
            background: '#28c840',
            flexShrink: 0,
          }}
        />
        <span
          style={{
            marginLeft: 8,
            fontSize: '0.65rem',
            color: 'rgba(255,255,255,0.4)',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {title}
        </span>
        {loaded && (
          <span
            style={{
              marginLeft: 'auto',
              fontSize: '0.6rem',
              color: 'rgba(255,255,255,0.25)',
              display: 'flex',
              alignItems: 'center',
              gap: 4,
            }}
          >
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M7 13l5 5 5-5M7 6l5 5 5-5" />
            </svg>
            Scroll to explore
          </span>
        )}
      </div>
    </div>
  );
});

export default WebsitePreview;