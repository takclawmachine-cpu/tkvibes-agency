import Image from 'next/image'
import Link from 'next/link'

type LogoVariant = 'mark' | 'full'

interface LogoProps {
  variant?: LogoVariant
  className?: string
  href?: string
}

const sizes = {
  mark: { width: 140, height: 68, src: '/tk-vibes-mark.svg' },
  full: { width: 160, height: 122, src: '/tk-vibes-logo.svg' },
} as const

export default function Logo({ variant = 'mark', className = '', href = '/' }: LogoProps) {
  const { width, height, src } = sizes[variant]

  const image = (
    <Image
      src={src}
      alt="TK Vibes Digital Agency"
      width={width}
      height={height}
      className={`brand-logo brand-logo-${variant}`}
      priority={variant === 'mark'}
    />
  )

  if (!href) return image

  return (
    <Link href={href} className={`brand-logo-link ${className}`.trim()} aria-label="TKVibes home">
      {image}
    </Link>
  )
}
