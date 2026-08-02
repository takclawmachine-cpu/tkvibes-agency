(function () {
  'use strict'

  const MARKUP = 1.20 // 20% increase for non-India visitors (mirrors pricing.js)

  /* ── Browser locale → USD fallback for non-India users ── */
  function guessNotIndia () {
    try {
      var lang = (navigator.language || navigator.userLanguage || '').toLowerCase()
      if (/^en-?(us|gb|au|ca|nz|sg|ph)/.test(lang)) return true
      if (/^(de|fr|es|pt|it|nl|sv|no|da|fi|pl|cs|hu|ro|ar|ja|zh|ko|th|vi|id|ms|tr)/.test(lang)) return true
    } catch (e) {}
    return false
  }

  /* ── Geo-aware price formatting ───────────── */
  function fmtPrice (n) {
    var geo = window.__tkvibes_geo
    if (geo && geo.rate && geo.fmt) {
      var converted = Math.round(n * geo.rate * MARKUP)
      return geo.fmt.sym + ' ' + converted.toLocaleString(geo.fmt.loc)
    }
    // Fallback: check browser locale for non-India users
    if (guessNotIndia()) {
      // Rough USD conversion (~84 INR = 1 USD, +20% markup = ~100 INR = 1 USD)
      var approxUsd = Math.round(n / 100)
      return '$ ' + approxUsd.toLocaleString('en-US')
    }
    // Last resort: INR
    return '\u20B9 ' + n.toLocaleString('en-IN')
  }

  /* ── Services catalog ──────────────────────── */
  const SERVICES = [
    { name: 'Logo Design', price: 1999 },
    { name: 'Brand Identity Package', price: 4999 },
    { name: '5-Page Static Website', price: 3999 },
    { name: 'Multi-Page Business Website', price: 9999 },
    { name: 'E-Commerce Store', price: 14999 },
    { name: 'Custom Admin Dashboard', price: 19999 },
    { name: 'AI Automation Workflow', price: 14999 },
    { name: 'Custom API Integration', price: 7999 },
    { name: 'Custom CRM Setup', price: 24999 },
    { name: 'Technical SEO Audit', price: 2999 },
    { name: 'Monthly Ad Management', price: 3999 },
    { name: 'Google Business Optimization', price: 2499 },
    { name: 'Content Writing', price: 499 },
    { name: 'Brochure / Deck Design', price: 1999 },
    { name: 'Ongoing Support (Monthly)', price: 2999 },
  ]

  /* ── DOM refs ──────────────────────────────── */
  var overlay = document.getElementById('planModalOverlay')
  var modal = document.getElementById('planModal')
  var closeBtn = document.getElementById('planModalClose')
  var openBtn = document.getElementById('openPlanBuilder')
  var serviceList = document.getElementById('planServiceList')
  var summaryItems = document.getElementById('planSummaryItems')
  var summaryTotal = document.getElementById('planSummaryTotal')
  var submitBtn = document.getElementById('planSubmitBtn')

  var nameInput = document.getElementById('planClientName')
  var businessInput = document.getElementById('planClientBusiness')
  var emailInput = document.getElementById('planClientEmail')
  var phoneInput = document.getElementById('planClientPhone')
  var notesInput = document.getElementById('planClientNotes')

  var successOverlay = document.getElementById('planSuccessOverlay')
  var successClose = document.getElementById('planSuccessClose')

  var selected = {} // { index: true/false }

  /* ── Render service list in modal ──────────── */
  function renderServices () {
    serviceList.innerHTML = ''
    SERVICES.forEach(function (svc, i) {
      var btn = document.createElement('button')
      btn.type = 'button'
      btn.className = 'plan-service-item' + (selected[i] ? ' selected' : '')
      btn.setAttribute('data-index', i)

      var formatted = fmtPrice(svc.price)

      btn.innerHTML =
        '<span class="psi-check"><i class="fas fa-check"></i></span>' +
        '<span class="psi-name">' + svc.name + '</span>' +
        '<span class="psi-price">' + formatted + '</span>'

      btn.addEventListener('click', function () {
        toggleService(i)
      })

      serviceList.appendChild(btn)
    })
  }

  /* ── Toggle a service ──────────────────────── */
  function toggleService (index) {
    if (selected[index]) {
      delete selected[index]
    } else {
      selected[index] = true
    }
    renderServices()
    updateSummary()
  }

  /* ── Update summary panel ──────────────────── */
  function updateSummary () {
    var names = Object.keys(selected)
    if (names.length === 0) {
      summaryItems.innerHTML = '<p class="plan-summary-empty">No services selected yet.</p>'
      summaryTotal.textContent = fmtPrice(0)
      submitBtn.disabled = true
      return
    }

    var total = 0
    var html = ''
    names.forEach(function (key) {
      var svc = SERVICES[parseInt(key)]
      total += svc.price
      html += '<div class="plan-summary-item">' +
        '<span class="psi-item-name">' + svc.name + '</span>' +
        '<span class="psi-item-price">' + fmtPrice(svc.price) + '</span>' +
        '</div>'
    })
    summaryItems.innerHTML = html
    summaryTotal.textContent = fmtPrice(total)
    submitBtn.disabled = false
  }

  /* ── Form validation ───────────────────────── */
  function validateForm () {
    var valid = true
    ;[nameInput, emailInput, phoneInput].forEach(function (el) {
      if (!el.value.trim()) {
        el.style.borderColor = '#ef4444'
        valid = false
      } else {
        el.style.borderColor = ''
      }
    })
    // email format
    if (emailInput.value.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value.trim())) {
      emailInput.style.borderColor = '#ef4444'
      valid = false
    }
    return valid
  }

  /* ── Format price for WhatsApp text ────────── */
  function fmtINR (n) {
    var s = fmtPrice(n)
    // Remove HTML entities, use plain text
    return s.replace(/\u20B9/g, 'Rs').replace(/\u00A3/g, 'GBP ').replace(/\u20AC/g, 'EUR ').replace(/\u0024/g, '$')
  }

  /* ── Build WhatsApp message ────────────────── */
  function buildWhatsAppMessage (data) {
    var lines = [
      '📋 *New Custom Plan Request — TKVibes*',
      '',
      '👤 *Name:* ' + data.name,
      '🏢 *Business:* ' + (data.business || '—'),
      '📧 *Email:* ' + data.email,
      '📞 *Phone:* ' + data.phone,
      '',
      '📦 *Selected Services:*'
    ]

    data.services.forEach(function (svc) {
      lines.push('  ✅ ' + svc.name + ' — ' + fmtINR(svc.price))
    })

    lines.push('')
    lines.push('💰 *Total:* ' + fmtINR(data.total))

    if (data.notes) {
      lines.push('')
      lines.push('📝 *Notes:* ' + data.notes)
    }

    return lines.join('\n')
  }

  /* ── Send plan request ─────────────────────── */
  function submitPlan () {
    if (!validateForm()) return

    var selectedNames = Object.keys(selected)
    if (selectedNames.length === 0) return

    var data = {
      name: nameInput.value.trim(),
      business: businessInput.value.trim(),
      email: emailInput.value.trim(),
      phone: phoneInput.value.trim(),
      notes: notesInput.value.trim(),
      services: selectedNames.map(function (k) { return SERVICES[parseInt(k)] }),
      total: selectedNames.reduce(function (sum, k) { return sum + SERVICES[parseInt(k)].price }, 0)
    }

    // 1 — Open WhatsApp with pre-filled message
    var waText = buildWhatsAppMessage(data)
    var waUrl = 'https://wa.me/919818246938?text=' + encodeURIComponent(waText)
    window.open(waUrl, '_blank')

    // 2 — Send via email (PHP backend)
    var xhr = new XMLHttpRequest()
    xhr.open('POST', 'send-plan-request.php', true)
    xhr.setRequestHeader('Content-Type', 'application/json')
    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4) {
        // Show success regardless — email is a best-effort delivery
        showSuccess()
      }
    }
    xhr.onerror = function () {
      // Network error — still show success, WhatsApp was already opened
      showSuccess()
    }
    xhr.send(JSON.stringify(data))

    // 3 — Fallback: mailto link as additional redundancy
    var mailBody = buildWhatsAppMessage(data).replace(/\*/g, '')
    var mailto = 'mailto:services@tkvibes.in?subject=' +
      encodeURIComponent('Custom Plan Request from ' + data.name) +
      '&body=' + encodeURIComponent(mailBody)
    // Open mailto silently — user may have a mail client
    var mailAnchor = document.createElement('a')
    mailAnchor.href = mailto
    mailAnchor.style.display = 'none'
    document.body.appendChild(mailAnchor)
    mailAnchor.click()
    document.body.removeChild(mailAnchor)

    // Reset form
    closeModal()
    selected = {}
  }

  /* ── Success overlay ───────────────────────── */
  function showSuccess () {
    successOverlay.classList.add('open')
    document.body.style.overflow = 'hidden'
  }

  /* ── Modal open/close ──────────────────────── */
  function openModal () {
    overlay.classList.add('open')
    document.body.style.overflow = 'hidden'
    renderServices()
    updateSummary()
    // Reset form fields
    nameInput.value = ''
    businessInput.value = ''
    emailInput.value = ''
    phoneInput.value = ''
    notesInput.value = ''
    ;[nameInput, emailInput, phoneInput].forEach(function (el) { el.style.borderColor = '' })
  }

  function closeModal () {
    overlay.classList.remove('open')
    document.body.style.overflow = ''
  }

  /* ── Event wiring ──────────────────────────── */
  if (openBtn) {
    openBtn.addEventListener('click', openModal)
  }

  if (closeBtn) {
    closeBtn.addEventListener('click', closeModal)
  }

  if (submitBtn) {
    submitBtn.addEventListener('click', submitPlan)
  }

  if (successClose) {
    successClose.addEventListener('click', function () {
      successOverlay.classList.remove('open')
      document.body.style.overflow = ''
    })
  }

  // Close on overlay click
  if (overlay) {
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) closeModal()
    })
  }

  if (successOverlay) {
    successOverlay.addEventListener('click', function (e) {
      if (e.target === successOverlay) {
        successOverlay.classList.remove('open')
        document.body.style.overflow = ''
      }
    })
  }

  // Real-time validation clearing
  ;[nameInput, emailInput, phoneInput].forEach(function (el) {
    if (el) {
      el.addEventListener('input', function () {
        if (el.value.trim()) el.style.borderColor = ''
      })
    }
  })

  if (emailInput) {
    emailInput.addEventListener('input', function () {
      if (emailInput.value.trim() && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value.trim())) {
        emailInput.style.borderColor = ''
      }
    })
  }

  // Re-render prices when geo data arrives (pricing.js fires this)
  window.addEventListener('tkvibes:geo', function () {
    if (overlay && overlay.classList.contains('open')) {
      renderServices()
      updateSummary()
    }
  })

})()