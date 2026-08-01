(function () {
  'use strict'

  /* ── DOM refs ──────────────────────────────── */
  var overlay = document.getElementById('enterpriseModalOverlay')
  var submitBtn = document.getElementById('enterpriseSubmitBtn')
  var nameInput = document.getElementById('entName')
  var orgInput = document.getElementById('entOrg')
  var emailInput = document.getElementById('entEmail')
  var phoneInput = document.getElementById('entPhone')
  var sizeInput = document.getElementById('entSize')
  var budgetInput = document.getElementById('entBudget')
  var notesInput = document.getElementById('entNotes')

  if (!submitBtn) return

  /* ── Form validation ───────────────────────── */
  function validate () {
    var valid = true
    ;[nameInput, orgInput, emailInput, phoneInput].forEach(function (el) {
      if (!el || !el.value.trim()) {
        if (el) el.style.borderColor = '#ef4444'
        valid = false
      } else {
        if (el) el.style.borderColor = ''
      }
    })
    if (notesInput && !notesInput.value.trim()) {
      notesInput.style.borderColor = '#ef4444'
      valid = false
    } else if (notesInput) {
      notesInput.style.borderColor = ''
    }
    if (emailInput && emailInput.value.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value.trim())) {
      emailInput.style.borderColor = '#ef4444'
      valid = false
    }
    return valid
  }

  /* ── Real-time validation clearing ─────────── */
  ;[nameInput, orgInput, emailInput, phoneInput, notesInput].forEach(function (el) {
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

  /* ── Build message ─────────────────────────── */
  function buildMessage (data) {
    var lines = [
      '🏢 *Enterprise+ Consultation Request — TKVibes*',
      '',
      '👤 *Name:* ' + data.name,
      '🏛️ *Organization:* ' + data.org,
      '📧 *Email:* ' + data.email,
      '📞 *Phone:* ' + data.phone,
      '📊 *Size:* ' + (data.size || 'Not specified'),
      '💰 *Budget:* ' + (data.budget || 'Not specified'),
      '',
      '📝 *Project Details:*',
      data.notes
    ]
    return lines.join('\n')
  }

  /* ── Submit ────────────────────────────────── */
  function submit () {
    if (!validate()) return

    var data = {
      name: nameInput.value.trim(),
      org: orgInput.value.trim(),
      email: emailInput.value.trim(),
      phone: phoneInput.value.trim(),
      size: sizeInput.value,
      budget: budgetInput.value,
      notes: notesInput.value.trim()
    }

    // WhatsApp
    var waText = buildMessage(data)
    var waUrl = 'https://wa.me/919818246938?text=' + encodeURIComponent(waText)
    window.open(waUrl, '_blank')

    // Email via PHP
    var xhr = new XMLHttpRequest()
    xhr.open('POST', 'send-enterprise-inquiry.php', true)
    xhr.setRequestHeader('Content-Type', 'application/json')
    xhr.onload = function () { closeModal() }
    xhr.onerror = function () { closeModal() }
    xhr.send(JSON.stringify(data))

    // Mailto fallback
    var mailBody = buildMessage(data).replace(/\*/g, '')
    var mailto = 'mailto:services@tkvibes.in?subject=' +
      encodeURIComponent('Enterprise+ Inquiry from ' + data.name + ' - ' + data.org) +
      '&body=' + encodeURIComponent(mailBody)
    var a = document.createElement('a')
    a.href = mailto
    a.style.display = 'none'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)

    closeModal()
  }

  function closeModal () {
    overlay.classList.remove('open')
    document.body.style.overflow = ''
    // Reset
    ;[nameInput, orgInput, emailInput, phoneInput, notesInput].forEach(function (el) {
      if (el) { el.value = ''; el.style.borderColor = '' }
    })
    if (sizeInput) sizeInput.value = ''
    if (budgetInput) budgetInput.value = ''
  }

  submitBtn.addEventListener('click', submit)
})()