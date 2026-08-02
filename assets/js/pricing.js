(function () {
  'use strict'

  /* ── Config ──────────────────────────────────── */
  const MARKUP = 1.20 // 20% increase for non-India visitors
  const GEO_APIS = [
    'https://ipapi.co/json/',
    'https://ip-api.com/json/?fields=countryCode,currency'
  ]
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
  var currentGeo = null

  /* ── Browser locale → currency guess ───────── */
  function guessCurrencyFromLocale () {
    try {
      var lang = (navigator.language || navigator.userLanguage || '').toLowerCase()
      var localeMap = {
        'en-us': 'USD', 'en-gb': 'GBP', 'de-de': 'EUR', 'fr-fr': 'EUR',
        'ja-jp': 'JPY', 'zh-cn': 'CNY', 'en-au': 'AUD', 'en-ca': 'CAD',
        'en-sg': 'SGD', 'ar-ae': 'AED', 'ar-sa': 'SAR', 'pt-br': 'BRL',
        'es-mx': 'MXN', 'de-ch': 'CHF', 'sv-se': 'SEK', 'nb-no': 'NOK',
        'da-dk': 'DKK', 'en-nz': 'NZD', 'ms-my': 'MYR', 'th-th': 'THB',
        'id-id': 'IDR', 'en-ph': 'PHP', 'vi-vn': 'VND', 'ur-pk': 'PKR',
        'hi-in': 'INR', 'en-in': 'INR', 'mr-in': 'INR', 'ta-in': 'INR',
        'te-in': 'INR', 'bn-in': 'INR', 'gu-in': 'INR', 'kn-in': 'INR',
        'ml-in': 'INR', 'pa-in': 'INR'
      }
      return localeMap[lang] || null
    } catch (e) {
      return null
    }
  }

  function formatCurrency(amount, currencyCode) {
    const fmt = CURRENCY_FMT[currencyCode]
    if (fmt) {
      const formatted = Math.round(amount).toLocaleString(fmt.loc)
      return fmt.sym + ' ' + formatted
    }
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
      if (el.tagName === 'SELECT') {
        var options = el.querySelectorAll('option[data-inr-value]')
        options.forEach(function (opt) {
          if (!opt.hasAttribute('data-original-text')) {
            opt.setAttribute('data-original-text', opt.textContent)
          }
          var original = opt.getAttribute('data-original-text')
          opt.textContent = convertInrText(original, rate, currencyCode)
        })
        return
      }
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

  /* ── Try geo APIs with timeout + fallback ───── */
  function fetchWithTimeout (url, ms) {
    return new Promise(function (resolve, reject) {
      var controller
      if (typeof AbortController !== 'undefined') {
        controller = new AbortController()
      }
      var timer = setTimeout(function () {
        if (controller) controller.abort()
        reject(new Error('timeout'))
      }, ms)
      fetch(url, controller ? { signal: controller.signal } : {})
        .then(function (r) {
          clearTimeout(timer)
          // ip-api.com returns status text, ipapi.co doesn't
          return r.json().then(function (data) { resolve(data) })
        })
        .catch(function (e) {
          clearTimeout(timer)
          reject(e)
        })
    })
  }

  function detectGeo () {
    var localeGuess = guessCurrencyFromLocale()

    // Try each geo API in order until one succeeds
    function tryApi (index) {
      if (index >= GEO_APIS.length) {
        // All APIs failed — use locale guess as last resort
        if (localeGuess && localeGuess !== 'INR') {
          fetch(FX_API)
            .then(function (r) { return r.json() })
            .then(function (fxData) {
              var rate = fxData.rates[localeGuess]
              if (rate) {
                updatePrices(localeGuess, rate)
                setGeo(localeGuess, rate)
              }
            })
            .catch(function () {})
        }
        return
      }

      fetchWithTimeout(GEO_APIS[index], 5000)
        .then(function (data) {
          var countryCode = (data.country_code || data.countryCode || '').toUpperCase()
          if (countryCode === 'IN') return // India — stay on INR

          var currency = data.currency || localeGuess || 'USD'
          if (!currency || currency === 'INR') return

          fetch(FX_API)
            .then(function (r) { return r.json() })
            .then(function (fxData) {
              var rate = fxData.rates[currency]
              if (rate) {
                updatePrices(currency, rate)
                setGeo(currency, rate)
              }
            })
            .catch(function () {})
        })
        .catch(function () {
          // Try next API, but also fall back to locale guess
          if (localeGuess && localeGuess !== 'INR') {
            fetch(FX_API)
              .then(function (r) { return r.json() })
              .then(function (fxData) {
                var rate = fxData.rates[localeGuess]
                if (rate) {
                  updatePrices(localeGuess, rate)
                  setGeo(localeGuess, rate)
                }
              })
              .catch(function () {})
          }
          tryApi(index + 1)
        })
    }

    tryApi(0)
  }

  /* ── Start detection ─────────────────────────── */
  detectGeo()
})()