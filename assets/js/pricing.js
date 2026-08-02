(function () {
  'use strict'

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

})()