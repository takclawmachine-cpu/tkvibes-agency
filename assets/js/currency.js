(function () {
  'use strict'

  /* ── Currency config ──────────────────────── */
  var CURRENCY_FMT = {
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
    KRW: { loc: 'ko-KR', sym: '\u20A9', decimals: 0 },
    RUB: { loc: 'ru-RU', sym: '\u20BD', decimals: 0 },
    TRY: { loc: 'tr-TR', sym: '\u20BA', decimals: 0 },
    ZAR: { loc: 'en-ZA', sym: 'R ', decimals: 0 },
    ILS: { loc: 'he-IL', sym: '\u20AA', decimals: 0 },
  }

  /* ── Hardcoded baseline rates (1 INR = X currency) ─ */
  var BASELINE_RATES = {
    USD: 0.012, EUR: 0.011, GBP: 0.0095, CAD: 0.016, AUD: 0.018,
    JPY: 1.80, CNY: 0.086, SGD: 0.016, AED: 0.044, SAR: 0.045,
    BRL: 0.060, MXN: 0.21, CHF: 0.011, SEK: 0.12, NOK: 0.12,
    DKK: 0.082, NZD: 0.020, MYR: 0.056, THB: 0.44, IDR: 195,
    PHP: 0.70, VND: 305, PKR: 3.35, INR: 1, KRW: 16.5, RUB: 1.05,
    TRY: 0.39, ZAR: 0.22, ILS: 0.045,
  }

  var MARKUP = 1.20 // 20% increase for non-India visitors

  /* ── Locale → currency map ────────────────── */
  var LOCALE_CURRENCY = {
    'en-us': 'USD', 'en-gb': 'GBP', 'de-de': 'EUR', 'fr-fr': 'EUR',
    'ja-jp': 'JPY', 'zh-cn': 'CNY', 'en-au': 'AUD', 'en-ca': 'CAD',
    'en-sg': 'SGD', 'ar-ae': 'AED', 'ar-sa': 'SAR', 'pt-br': 'BRL',
    'es-mx': 'MXN', 'de-ch': 'CHF', 'sv-se': 'SEK', 'nb-no': 'NOK',
    'da-dk': 'DKK', 'en-nz': 'NZD', 'ms-my': 'MYR', 'th-th': 'THB',
    'id-id': 'IDR', 'en-ph': 'PHP', 'vi-vn': 'VND', 'ur-pk': 'PKR',
    'hi-in': 'INR', 'en-in': 'INR', 'mr-in': 'INR', 'ta-in': 'INR',
    'te-in': 'INR', 'bn-in': 'INR', 'gu-in': 'INR', 'kn-in': 'INR',
    'ml-in': 'INR', 'pa-in': 'INR', 'ko-kr': 'KRW', 'ru-ru': 'RUB',
    'tr-tr': 'TRY', 'en-za': 'ZAR', 'he-il': 'ILS', 'es-es': 'EUR',
    'it-it': 'EUR', 'pt-pt': 'EUR', 'nl-nl': 'EUR', 'pl-pl': 'PLN',
    'cs-cz': 'CZK', 'hu-hu': 'HUF', 'ro-ro': 'RON',
  }

  /* ── Timezone → currency map (the most reliable signal) ─ */
  var TZ_CURRENCY = {
    'asia/kolkata': 'INR', 'asia/calcutta': 'INR',
    'america/new_york': 'USD', 'america/chicago': 'USD',
    'america/denver': 'USD', 'america/los_angeles': 'USD',
    'america/anchorage': 'USD', 'pacific/honolulu': 'USD',
    'europe/london': 'GBP', 'europe/paris': 'EUR',
    'europe/berlin': 'EUR', 'europe/madrid': 'EUR',
    'europe/rome': 'EUR', 'europe/amsterdam': 'EUR',
    'europe/brussels': 'EUR', 'europe/vienna': 'EUR',
    'europe/stockholm': 'SEK', 'europe/oslo': 'NOK',
    'europe/copenhagen': 'DKK', 'europe/zurich': 'CHF',
    'europe/warsaw': 'PLN', 'europe/prague': 'CZK',
    'europe/budapest': 'HUF', 'europe/bucharest': 'RON',
    'europe/istanbul': 'TRY', 'europe/moscow': 'RUB',
    'asia/tokyo': 'JPY', 'asia/shanghai': 'CNY',
    'asia/hong_kong': 'HKD', 'asia/singapore': 'SGD',
    'asia/seoul': 'KRW', 'asia/bangkok': 'THB',
    'asia/ho_chi_minh': 'VND', 'asia/jakarta': 'IDR',
    'asia/manila': 'PHP', 'asia/kuala_lumpur': 'MYR',
    'asia/dhaka': 'BDT', 'asia/karachi': 'PKR',
    'asia/kabul': 'AFN', 'asia/colombo': 'LKR',
    'asia/kathmandu': 'NPR', 'asia/dubai': 'AED',
    'asia/riyadh': 'SAR', 'asia/tehran': 'IRR',
    'asia/baghdad': 'IQD', 'asia/tel_aviv': 'ILS',
    'asia/doha': 'QAR', 'asia/muscat': 'OMR',
    'asia/bahrain': 'BHD', 'asia/kuwait': 'KWD',
    'asia/yerevan': 'AMD', 'asia/tbilisi': 'GEL',
    'asia/baku': 'AZN', 'asia/almaty': 'KZT',
    'asia/tashkent': 'UZS', 'asia/beirut': 'LBP',
    'asia/amman': 'JOD', 'asia/damascus': 'SYP',
    'asia/nicosia': 'EUR',
    'australia/sydney': 'AUD', 'australia/melbourne': 'AUD',
    'australia/brisbane': 'AUD', 'australia/perth': 'AUD',
    'pacific/auckland': 'NZD', 'pacific/fiji': 'FJD',
    'africa/cairo': 'EGP', 'africa/casablanca': 'MAD',
    'africa/johannesburg': 'ZAR', 'africa/lagos': 'NGN',
    'africa/nairobi': 'KES', 'africa/addis_ababa': 'ETB',
    'africa/tunis': 'TND', 'africa/algiers': 'DZD',
    'america/toronto': 'CAD', 'america/vancouver': 'CAD',
    'america/montreal': 'CAD', 'america/mexico_city': 'MXN',
    'america/sao_paulo': 'BRL', 'america/argentina/buenos_aires': 'ARS',
    'america/santiago': 'CLP', 'america/bogota': 'COP',
    'america/lima': 'PEN', 'america/caracas': 'VES',
    'america/puerto_rico': 'USD',
  }

  /* ── Detect currency instantly (no network) ── */
  function detectCurrency () {
    // 1 — Timezone is the most reliable
    try {
      var tz = Intl.DateTimeFormat().resolvedOptions().timeZone
      if (tz) {
        var tzCurr = TZ_CURRENCY[tz.toLowerCase()]
        if (tzCurr) return tzCurr
      }
    } catch (e) {}

    // 2 — Intl NumberFormat locale (includes region on most systems)
    try {
      var locale = Intl.NumberFormat().resolvedOptions().locale.toLowerCase()
      if (locale) {
        var locCurr = LOCALE_CURRENCY[locale]
        if (locCurr) return locCurr
        // Try extracting just the region part (e.g. "en-US" → "en-us")
        var parts = locale.split('-')
        if (parts.length >= 2) {
          var regionWithLocale = parts[0] + '-' + parts[parts.length - 1]
          locCurr = LOCALE_CURRENCY[regionWithLocale]
          if (locCurr) return locCurr
        }
      }
    } catch (e) {}

    // 3 — navigator.language as last resort
    try {
      var lang = (navigator.language || navigator.userLanguage || '').toLowerCase()
      var langCurr = LOCALE_CURRENCY[lang]
      if (langCurr) return langCurr
      var langParts = lang.split('-')
      if (langParts.length >= 2) {
        langCurr = LOCALE_CURRENCY[langParts[0] + '-' + langParts[langParts.length - 1]]
        if (langCurr) return langCurr
      }
    } catch (e) {}

    return null // unknown — caller decides fallback
  }

  /* ── Format price helper ──────────────────── */
  function fmtPrice (n) {
    var geo = window.__tkvibes_geo
    if (geo && geo.rate && geo.fmt) {
      var converted = Math.round(n * geo.rate * MARKUP)
      return geo.fmt.sym + ' ' + converted.toLocaleString(geo.fmt.loc)
    }
    return '\u20B9 ' + n.toLocaleString('en-IN')
  }
  window.__tkvibes_fmtPrice = fmtPrice

  /* ── Set geo globally & notify ────────────── */
  function setGeo (currency, rate) {
    var fmt = CURRENCY_FMT[currency] || { loc: 'en-US', sym: currency + ' ', decimals: 0 }
    window.__tkvibes_geo = { currency: currency, rate: rate, fmt: fmt }
    window.dispatchEvent(new CustomEvent('tkvibes:geo', { detail: window.__tkvibes_geo }))
  }

  /* ── Bootstrap: instant sync detection ────── */
  var detected = detectCurrency()
  if (detected) {
    // Set geo immediately with baseline rate (zero network)
    var baseRate = BASELINE_RATES[detected] || 1
    setGeo(detected, baseRate)
    // Update prices on the page immediately
    updateDOMPrices(detected, baseRate)
  }

  /* ── Async: try to get live exchange rates ──── */
  var FX_API = 'https://open.er-api.com/v6/latest/INR'
  var GEO_APIS = [
    'https://ipapi.co/json/',
    'https://ip-api.com/json/?fields=countryCode,currency'
  ]

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
          return r.json().then(function (data) { resolve(data) })
        })
        .catch(function (e) {
          clearTimeout(timer)
          reject(e)
        })
    })
  }

  function refineWithLiveRates () {
    var geo = window.__tkvibes_geo
    if (!geo) return

    // Try geo IP first
    function tryApi (index) {
      if (index >= GEO_APIS.length) {
        // All APIs failed — try fetching live rate for current currency
        fetchLiveRate(geo.currency)
        return
      }

      fetchWithTimeout(GEO_APIS[index], 5000)
        .then(function (data) {
          var countryCode = (data.country_code || data.countryCode || '').toUpperCase()
          var currency = data.currency || geo.currency

          // If the geo API says India but our detection guessed wrong
          if (countryCode === 'IN' && currency !== 'INR') {
            setGeo('INR', 1)
            updateDOMPrices('INR', 1)
            return
          }

          // If geo API gives us a different currency than our instant guess
          if (currency && currency !== geo.currency && CURRENCY_FMT[currency]) {
            // Use the live rate for the corrected currency
            fetchLiveRate(currency)
          } else {
            // Just update the rate for our current currency
            fetchLiveRate(geo.currency)
          }
        })
        .catch(function () {
          tryApi(index + 1)
        })
    }

    tryApi(0)
  }

  function fetchLiveRate (currency) {
    if (currency === 'INR') return // already 1:1

    var xhr = new XMLHttpRequest()
    xhr.open('GET', FX_API, true)
    xhr.timeout = 5000
    xhr.onload = function () {
      if (xhr.status === 200) {
        try {
          var fxData = JSON.parse(xhr.responseText)
          var rate = fxData.rates[currency]
          if (rate) {
            // Only fire if rate differs significantly from baseline (avoid jitter)
            var baseline = BASELINE_RATES[currency] || 1
            var diff = Math.abs(rate - baseline) / baseline
            if (diff > 0.05) { // >5% difference
              setGeo(currency, rate)
              updateDOMPrices(currency, rate)
            }
          }
        } catch (e) {}
      }
    }
    xhr.send()
  }

  /* ── Update [data-inr] prices in DOM ────────── */
  function updateDOMPrices (currency, rate) {
    var prices = document.querySelectorAll('[data-inr]')
    if (!prices.length) return

    var fmt = CURRENCY_FMT[currency] || { loc: 'en-US', sym: currency + ' ', decimals: 0 }

    prices.forEach(function (el) {
      var raw = el.getAttribute('data-inr')
      if (!raw) return

      if (el.tagName === 'SELECT') {
        var options = el.querySelectorAll('option[data-inr-value]')
        options.forEach(function (opt) {
          if (!opt.hasAttribute('data-original-text')) {
            opt.setAttribute('data-original-text', opt.textContent)
          }
          var original = opt.getAttribute('data-original-text')
          opt.textContent = original.replace(/Rs\s*([\d,]+)/g, function (match, numStr) {
            var inrVal = parseFloat(numStr.replace(/,/g, ''))
            if (isNaN(inrVal)) return match
            var convertedVal = Math.round(inrVal * rate * MARKUP)
            return fmt.sym + ' ' + convertedVal.toLocaleString(fmt.loc)
          })
        })
        return
      }

      var inrVal = parseFloat(raw.replace(/,/g, ''))
      if (isNaN(inrVal)) return
      var convertedVal = Math.round(inrVal * rate * MARKUP)
      var formatted = fmt.sym + ' ' + convertedVal.toLocaleString(fmt.loc)
      var amountEl = el.querySelector('.price-amount')
      if (amountEl) {
        amountEl.textContent = formatted
      }
    })
  }

  /* ── Start async refinement after instant display ── */
  if (typeof window.requestIdleCallback === 'function') {
    window.requestIdleCallback(refineWithLiveRates, { timeout: 3000 })
  } else {
    setTimeout(refineWithLiveRates, 500)
  }

})()