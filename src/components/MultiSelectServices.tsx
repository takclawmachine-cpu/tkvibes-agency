'use client'

import { useEffect, useRef, useState } from 'react'

const SERVICE_OPTIONS = [
  'Website design',
  'Brand identity',
  'SEO services',
  'Google ads',
  'Meta ads',
  'Automation workflows',
  'Custom package',
]

export default function MultiSelectServices() {
  const [open, setOpen] = useState(false)
  const [selected, setSelected] = useState<string[]>([])
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function onClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', onClick)
    return () => document.removeEventListener('mousedown', onClick)
  }, [])

  function toggle(option: string) {
    setSelected((prev) =>
      prev.includes(option) ? prev.filter((o) => o !== option) : [...prev, option]
    )
  }

  function clearAll(e: React.MouseEvent) {
    e.stopPropagation()
    setSelected([])
  }

  const displayText =
    selected.length === 0
      ? 'Select services'
      : selected.length === 1
        ? selected[0]
        : `${selected.length} services selected`

  return (
    <div
      className={`multi-select ${open ? 'open' : ''}`}
      ref={ref}
      tabIndex={0}
      role="combobox"
      aria-expanded={open}
      aria-haspopup="listbox"
      aria-multiselectable="true"
      onClick={() => setOpen((v) => !v)}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          setOpen((v) => !v)
        } else if (e.key === 'Escape') {
          setOpen(false)
        }
      }}
    >
      <div className="multi-select-trigger">
        <span className={selected.length === 0 ? 'placeholder' : 'value'}>
          {displayText}
        </span>
        {selected.length > 0 && (
          <button
            type="button"
            className="multi-select-clear"
            aria-label="Clear selected services"
            onClick={clearAll}
          >
            <i className="fas fa-xmark" />
          </button>
        )}
        <i className={`fas fa-chevron-${open ? 'up' : 'down'} chevron`} />
      </div>

      {open && (
        <ul className="multi-select-options" role="listbox">
          {SERVICE_OPTIONS.map((option) => {
            const checked = selected.includes(option)
            return (
              <li
                key={option}
                role="option"
                aria-selected={checked}
                className={checked ? 'checked' : ''}
                onClick={(e) => {
                  e.stopPropagation()
                  toggle(option)
                }}
              >
                <span className="checkbox">
                  {checked && <i className="fas fa-check" />}
                </span>
                <span>{option}</span>
              </li>
            )
          })}
        </ul>
      )}

      {/* Hidden inputs submitted with the form */}
      {selected.map((s) => (
        <input key={s} type="hidden" name="services" value={s} />
      ))}
    </div>
  )
}
