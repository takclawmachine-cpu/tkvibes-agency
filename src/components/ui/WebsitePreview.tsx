'use client'

import Image from 'next/image'
import { useState } from 'react'

interface WebsitePreviewProps {
  imageSrc?: string
  title: string
}

export default function WebsitePreview({
  imageSrc,
  title,
}: WebsitePreviewProps) {
  const [hasError, setHasError] = useState(false)

  return (
    <div className="website-preview">
      <div className="website-preview-bar">
        <span />
        <span />
        <span />
        <p>{title}</p>
      </div>
      <div className="website-preview-frame">
        {imageSrc && !hasError ? (
          <Image
            src={imageSrc}
            alt={title}
            fill
            sizes="(max-width: 768px) 100vw, 33vw"
            className="website-preview-image"
            onError={() => setHasError(true)}
          />
        ) : (
          <div className="website-preview-fallback">
            <div className="website-preview-badge">Preview unavailable</div>
            <strong>{title}</strong>
            <span>We are refreshing this case study preview.</span>
          </div>
        )}
        <div className="website-preview-glow" />
      </div>
    </div>
  )
}
