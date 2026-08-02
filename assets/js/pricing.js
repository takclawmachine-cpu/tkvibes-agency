(function () {
  'use strict'

  /* ── Config ──────────────────────────────────── */
  const MARKUP = 1.20 // 20% increase for non-India visitors
  const GEO_API = 'https://ipapi.co/json/'
  const FX_API = 'https://open.er-api.com/v6/latest/INR'

  /* ── Currency display map ────────────────────── */
  const CURRENCY_FMT = {
    USD: { loc: 'en-US', sym: '$', decimals: 0 },
    EUR: { loc: 'de-DE', sym: '\u20AC', decimals: 0 },
    GBP: { loc: 'en-GB', sym: '\u00A3', decimals: 0 },
    CAD: { loc: 'en-CA', sym: 'CA$', decimals: 0 },
    AUD: { loc: 'en-AU', sym: 'AU$', decimals: 0 },
    JPY: { loc: 'ja-JP', sym: '\u00A5', decimals: 0 },
    CNY: { loc: 'zh-CN', sym: '\u00A5', decimals: 0 },
    SGD: { loc: 'en-SG', sym: 'S$', decimals: 0 },
    AED: { loc: 'ar-AE', sym: '\u062F.\u0625', decimals: 0 },
    SAR: { loc: 'ar-SA', sym: '\uFDFC', decimals: 0 },
    BRL: { loc: 'pt-BR', sym: 'R$', decimals: 0 },
    MXN: { loc: 'es-MX', sym: 'MX$', decimals: 0 },
    CHF: { loc: 'de-CH', sym: 'CHF ', decimals: 0 },
    SEK: { loc: 'sv-SE', sym: 'kr ', decimals: 0 },
    NOK: { loc: 'nb-NO', sym: 'kr ', decimals: 0 },
    DKK: { loc: 'da-DK', sym: 'kr ', decimals: 0 },
    NZD: { loc: 'en-NZ', sym: 'NZ$', decimals: 0 },
    MYR: { loc: 'ms-MY', sym: 'RM', decimals: 0 },
    THB: { loc: 'th-TH', sym: '\u0E3F', decimals: 0 },
    IDR: { loc: 'id-ID', sym: 'Rp', decimals: 0 },
    PHP: { loc: 'en-PH', sym: '\u20B1', decimals: 0 },
    VND: { loc: 'vi-VN', sym: '\u20AB', decimals: 0 },
    PKR: { loc: 'ur-PK', sym: '\u20A8', decimals: 0 },
    INR: { loc: 'en-IN', sym: '\u20B9', decimals: 0 },
  }

  const prices = document.querySelectorAll('[data-inr]')
  if (!prices.length) return

  let converted = false

  /* ── Expose geo data globally for plan-builder ── */
  var currentGeo = null

  function formatCurrency(amount, currencyCode) {
    const fmt = CURRENCY_FMT[currencyCode]
    if (fmt) {
      const formatted = Math.round(amount).toLocaleString(fmt.loc)
      return fmt.sym + ' ' + formatted
    }
    // Fallback: use currency code
    return currencyCode + ' ' + Math.round(amount).toLocaleString('en-US')
  }

  /* ── Tab switching ─────────────────────────── */
  var tabBtns = document.querySelectorAll('.pricing-tab')
  var tabPanels = {
    individual: document.getElementById('tab-individual'),
    enterprise: document.getElementById('tab-enterprise')
  }

  tabBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var tab = btn.getAttribute('data-tab')
      if (!tab || !tabPanels[tab]) return

      tabBtns.forEach(function (b) { b.classList.remove('active') })
      btn.classList.add('active')

      Object.keys(tabPanels).forEach(function (key) {
        tabPanels[key].classList.toggle('active', key === tab)
      })
    })
  })

  /* ── Enterprise+ "Book Free Consultation" opens modal ── */
  var consultBtns = document.querySelectorAll('.btn-consult-custom')
  var entOverlay = document.getElementById('enterpriseModalOverlay')
  var entModal = document.getElementById('enterpriseModal')
  var entClose = document.getElementById('enterpriseModalClose')

  if (consultBtns.length && entOverlay) {
    consultBtns.forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        // Only intercept if it's not a plain link (keep href fallback)
        if (entOverlay) {
          e.preventDefault()
          entOverlay.classList.add('open')
          document.body.style.overflow = 'hidden'
        }
      })
    })
  }

  if (entClose && entOverlay) {
    entClose.addEventListener('click', function () {
      entOverlay.classList.remove('open')
      document.body.style.overflow = ''
    })
  }

  if (entOverlay) {
    entOverlay.addEventListener('click', function (e) {
      if (e.target === entOverlay) {
        entOverlay.classList.remove('open')
        document.body.style.overflow = ''
      }
    })
  }
  function convertInrText(text, rate, currencyCode) {
    // Replace all "Rs [number]" patterns with converted currency
    return text.replace(/Rs\s*([\d,]+)/g, function (match, numStr) {
      var inrVal = parseFloat(numStr.replace(/,/g, ''))
      if (isNaN(inrVal)) return match
      var convertedVal = inrVal * rate * MARKUP
      return formatCurrency(convertedVal, currencyCode)
    })
  }

  function updatePrices(currencyCode, rate) {
    prices.forEach(function (el) {
      var raw = el.getAttribute('data-inr')
      // ── Select elements (e.g. budget dropdown) ──
      if (el.tagName === 'SELECT') {
        var options = el.querySelectorAll('option[data-inr-value]')
        options.forEach(function (opt) {
          // Store original text on first run
          if (!opt.hasAttribute('data-original-text')) {
            opt.setAttribute('data-original-text', opt.textContent)
          }
          var original = opt.getAttribute('data-original-text')
          opt.textContent = convertInrText(original, rate, currencyCode)
        })
        return
      }
      // ── Regular price spans ──
      if (!raw) return
      var inrVal = parseFloat(raw.replace(/,/g, ''))
      if (isNaN(inrVal)) return

      var convertedVal = inrVal * rate * MARKUP
      var formatted = formatCurrency(convertedVal, currencyCode)

      var amountEl = el.querySelector('.price-amount')
      if (amountEl) {
        amountEl.textContent = formatted
      }
    })
    converted = true
  }

  /* ── Expose geo globally for other modules ──── */
  function setGeo (currency, rate) {
    currentGeo = { currency: currency, rate: rate, fmt: CURRENCY_FMT[currency] || null }
    window.__tkvibes_geo = currentGeo
    window.dispatchEvent(new CustomEvent('tkvibes:geo', { detail: currentGeo }))
  }

  /* ── Step 1: detect location ─────────────────── */
  fetch(GEO_API)
    .then(function (r) { return r.json() })
    .then(function (data) {
      // India — no conversion needed
      if (data.country_code === 'IN') return

      var currency = data.currency || 'USD'

      // Step 2: fetch exchange rate
      fetch(FX_API)
        .then(function (r) { return r.json() })
        .then(function (fxData) {
          var rate = fxData.rates[currency]
          if (!rate) return // fallback: leave INR
          updatePrices(currency, rate)
          setGeo(currency, rate)
        })
        .catch(function () {
          // Exchange rate API failed — stay on INR
        })
    })
    .catch(function () {
      // Geolocation failed — stay on INR
    })
})()