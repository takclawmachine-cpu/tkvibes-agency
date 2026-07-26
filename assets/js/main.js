(function () {
  'use strict'

  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max)
  }

  /* ── Navbar ── */
  const navbar = document.querySelector('.navbar')
  const navLinks = document.querySelector('.nav-links')
  const mobileToggle = document.querySelector('.mobile-toggle')
  function pageKeyFromPath(pathname) {
    const file = pathname.split('/').pop() || ''
    if (!file || /^index\.html$/i.test(file)) return 'home'
    return file.replace(/\.html$/i, '').toLowerCase()
  }

  function pageKeyFromHref(href) {
    if (!href || /^(https?:|mailto:|tel:|#)/.test(href)) return null
    const clean = href.split('?')[0].split('#')[0]
    const file = clean.replace(/^\.\//, '').split('/').pop() || ''
    if (!file || file === '/' || /^index\.html$/i.test(file)) return 'home'
    return file.replace(/\.html$/i, '').toLowerCase()
  }

  const currentPage = pageKeyFromPath(window.location.pathname)

  document.querySelectorAll('.nav-links a').forEach((link) => {
    const href = link.getAttribute('href') || ''
    const path = pageKeyFromHref(href)
    const isActive = path === 'home'
      ? currentPage === 'home'
      : path === currentPage
    if (isActive) link.classList.add('active')
    else link.classList.remove('active')
  })

  function onScrollNav() {
    if (navbar) navbar.classList.toggle('scrolled', window.scrollY > 20)
  }

  window.addEventListener('scroll', onScrollNav, { passive: true })
  onScrollNav()

  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', () => {
      const open = navLinks.classList.toggle('open')
      mobileToggle.setAttribute('aria-expanded', String(open))
      const icon = mobileToggle.querySelector('i')
      if (icon) icon.className = open ? 'fas fa-times' : 'fas fa-bars'
    })
  }

  /* ── Footer year ── */
  document.querySelectorAll('[data-year]').forEach((el) => {
    el.textContent = String(new Date().getFullYear())
  })

  /* ── Aurora (home only) ── */
  if (document.body.classList.contains('home-route')) {
    const root = document.documentElement
    let frame = 0

    function updateAurora() {
      const maxScroll = Math.max(window.innerHeight * 1.6, 1)
      const progress = Math.min(window.scrollY / maxScroll, 1)
      root.style.setProperty('--aurora-scroll', progress.toFixed(3))
      root.style.setProperty('--aurora-tilt', `${(progress * 14 - 5).toFixed(2)}deg`)
      root.style.setProperty('--aurora-depth', (1 + progress * 0.18).toFixed(3))
      root.style.setProperty('--aurora-opacity', (0.78 - progress * 0.2).toFixed(3))
      root.style.setProperty('--aurora-grid-shift', `${Math.round(progress * 32)}px`)
    }

    function onScrollAurora() {
      cancelAnimationFrame(frame)
      frame = requestAnimationFrame(updateAurora)
    }

    updateAurora()
    window.addEventListener('scroll', onScrollAurora, { passive: true })
    window.addEventListener('resize', onScrollAurora)
  }

  /* ── Hero project stack ── */
  const stackFrame = document.querySelector('.hero-stack-frame')
  if (stackFrame) {
    const cards = Array.from(stackFrame.querySelectorAll('.hero-stack-card'))
    const dots = Array.from(document.querySelectorAll('.hero-stack-dot'))
    let activeIndex = 0
    let timer = 0

    function renderStack() {
      const total = cards.length
      cards.forEach((card, index) => {
        const delta = index - activeIndex
        const isActive = index === activeIndex
        const isPrev = delta === -1 || (activeIndex === 0 && index === total - 1)
        let translateY, translateX, scale, rotate, opacity

        if (isActive) {
          translateY = 0; translateX = 0; scale = 1; rotate = 0; opacity = 1
        } else if (isPrev) {
          translateY = -132; translateX = 42; scale = 0.89; rotate = -5.5; opacity = 0
        } else {
          const futureOffset = index > activeIndex ? index - activeIndex : total - activeIndex + index
          translateY = futureOffset * 28
          translateX = futureOffset * 10
          scale = clamp(1 - futureOffset * 0.045, 0.7, 1)
          rotate = futureOffset * -1.4
          opacity = 1
        }

        card.classList.toggle('active', isActive)
        card.style.zIndex = String(isActive ? total : total - index)
        card.style.transform = `translate3d(${translateX}px, ${translateY}px, 0) scale(${scale}) rotate(${rotate}deg)`
        card.style.opacity = String(opacity)
      })

      dots.forEach((dot, i) => dot.classList.toggle('active', i === activeIndex))
    }

    function setIndex(i) {
      activeIndex = i
      renderStack()
    }

    dots.forEach((dot, i) => dot.addEventListener('click', () => setIndex(i)))

    if (cards.length > 1) {
      timer = window.setInterval(() => setIndex((activeIndex + 1) % cards.length), 2000)
    }

    renderStack()
  }

  /* ── Portfolio filter ── */
  const filterBar = document.querySelector('.filter-bar')
  if (filterBar) {
    const cards = document.querySelectorAll('.portfolio-card')
    filterBar.addEventListener('click', (e) => {
      const btn = e.target.closest('button')
      if (!btn) return
      const filter = btn.dataset.filter || 'all'
      filterBar.querySelectorAll('button').forEach((b) => b.classList.toggle('active', b === btn))
      cards.forEach((card) => {
        const cats = (card.dataset.categories || '').split(/\s+/)
        const show = filter === 'all' || cats.includes(filter)
        card.style.display = show ? '' : 'none'
      })
    })
  }

  /* ── Website preview image fallback ── */
  document.querySelectorAll('.website-preview-image').forEach((img) => {
    img.addEventListener('error', () => {
      const frame = img.closest('.website-preview-frame')
      if (!frame) return
      img.remove()
      const title = frame.closest('.website-preview')?.querySelector('.website-preview-bar p')?.textContent || 'Project'
      const fallback = document.createElement('div')
      fallback.className = 'website-preview-fallback'
      fallback.innerHTML = `<div class="website-preview-badge">Preview unavailable</div><strong>${title}</strong><span>We are refreshing this case study preview.</span>`
      frame.insertBefore(fallback, frame.querySelector('.website-preview-glow'))
    })
  })

  /* ── Multi-select services ── */
  const multiSelect = document.querySelector('.multi-select')
  if (multiSelect) {
    const options = [
      'Website design', 'Brand identity', 'SEO services', 'Google ads',
      'Meta ads', 'Automation workflows', 'Custom package',
    ]
    const selected = new Set()
    const trigger = multiSelect.querySelector('.multi-select-trigger')
    const valueEl = multiSelect.querySelector('.multi-select-trigger span')
    let listEl = multiSelect.querySelector('.multi-select-options')

    if (!listEl) {
      listEl = document.createElement('ul')
      listEl.className = 'multi-select-options'
      listEl.setAttribute('role', 'listbox')
      listEl.hidden = true
      options.forEach((option) => {
        const li = document.createElement('li')
        li.setAttribute('role', 'option')
        li.dataset.value = option
        li.innerHTML = `<span class="checkbox"></span><span>${option}</span>`
        listEl.appendChild(li)
      })
      multiSelect.appendChild(listEl)
    }

    function syncHiddenInputs() {
      multiSelect.querySelectorAll('input[name="services"]').forEach((el) => el.remove())
      selected.forEach((s) => {
        const input = document.createElement('input')
        input.type = 'hidden'
        input.name = 'services'
        input.value = s
        multiSelect.appendChild(input)
      })
    }

    function updateDisplay() {
      const arr = [...selected]
      if (valueEl) {
        valueEl.className = arr.length ? 'value' : 'placeholder'
        valueEl.textContent = arr.length === 0 ? 'Select services' : arr.length === 1 ? arr[0] : `${arr.length} services selected`
      }
      listEl.querySelectorAll('li').forEach((li) => {
        const on = selected.has(li.dataset.value)
        li.classList.toggle('checked', on)
        li.setAttribute('aria-selected', String(on))
        const box = li.querySelector('.checkbox')
        if (box) box.innerHTML = on ? '<i class="fas fa-check"></i>' : ''
      })
      syncHiddenInputs()
    }

    multiSelect.addEventListener('click', (e) => {
      if (e.target.closest('.multi-select-clear')) {
        e.stopPropagation()
        selected.clear()
        updateDisplay()
        return
      }
      const li = e.target.closest('.multi-select-options li')
      if (li) {
        e.stopPropagation()
        const v = li.dataset.value
        if (selected.has(v)) selected.delete(v)
        else selected.add(v)
        updateDisplay()
        return
      }
      const open = multiSelect.classList.toggle('open')
      listEl.hidden = !open
      multiSelect.setAttribute('aria-expanded', String(open))
      const chevron = multiSelect.querySelector('.chevron')
      if (chevron) chevron.className = `fas fa-chevron-${open ? 'up' : 'down'} chevron`
    })

    document.addEventListener('mousedown', (e) => {
      if (!multiSelect.contains(e.target)) {
        multiSelect.classList.remove('open')
        listEl.hidden = true
      }
    })

    if (!multiSelect.querySelector('.multi-select-clear')) {
      const clearBtn = document.createElement('button')
      clearBtn.type = 'button'
      clearBtn.className = 'multi-select-clear'
      clearBtn.setAttribute('aria-label', 'Clear selected services')
      clearBtn.innerHTML = '<i class="fas fa-xmark"></i>'
      clearBtn.hidden = true
      trigger?.appendChild(clearBtn)
      multiSelect.addEventListener('click', () => {
        clearBtn.hidden = selected.size === 0
      })
    }

    updateDisplay()
  }
})()
