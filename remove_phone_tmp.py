#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io, sys

def replace_in(path, old, new):
    with io.open(path, 'r', encoding='utf-8') as f:
        data = f.read()
    count = data.count(old)
    if count == 0:
        print(f"  [MISS] {path}: pattern not found")
        return False
    data = data.replace(old, new)
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(data)
    print(f"  [OK {count}x] {path}")
    return True

# Helper: build the tel href with the number (digits only, not masked)
# The actual file has the full number
tel_href = 'tel:+919818246938'
tel_display = '+91 98182 46938'
wa_url = 'https://wa.me/919818246938'

# 1. Footer: remove tel li (standard pages: index, about, services, portfolio, contact)
FOOTER_OLD = f'<li><a href="mailto:services@tkvibes.in">services@tkvibes.in</a></li><li><a href="{tel_href}">{tel_display}</a></li><li><a href="{wa_url}">WhatsApp</a></li><li><span>India, serving clients worldwide</span></li>'
FOOTER_NEW = '<li><a href="mailto:services@tkvibes.in">services@tkvibes.in</a></li><li><a href="https://wa.me/919818246938">WhatsApp</a></li><li><span>India, serving clients worldwide</span></li>'

standard = ['index.html','about.html','services.html','portfolio.html','contact.html']
for f in standard:
    replace_in(f, FOOTER_OLD, FOOTER_NEW)

# 2. packages.html: change WhatsApp link text in footer
PACKAGES_FOOTER_OLD = f'<li><a href="https://wa.me/919818246938" target="_blank" rel="noopener noreferrer">{tel_display}</a></li>'
PACKAGES_FOOTER_NEW = '<li><a href="https://wa.me/919818246938" target="_blank" rel="noopener noreferrer">WhatsApp</a></li>'
replace_in('packages.html', PACKAGES_FOOTER_OLD, PACKAGES_FOOTER_NEW)

# 3. contact.html: remove Phone detail block
PHONE_BLOCK_OLD = f'<div class="contact-detail"><div class="cd-icon"><i class="fas fa-phone"></i></div><div><h5>Phone</h5><p><a href="{tel_href}">{tel_display}</a></p><p class="contact-note">Mon to Sat, 10:00 AM to 7:00 PM</p></div></div>'
replace_in('contact.html', PHONE_BLOCK_OLD, '')

# 4. contact.html: remove Call Us button in CTA
CALLUS_OLD = f'<a href="{tel_href}" class="btn-custom btn-outline-custom"><i class="fas fa-phone"></i>Call Us</a>'
replace_in('contact.html', CALLUS_OLD, '')

# 5. contact.html: WhatsApp detail link text change from phone number to "WhatsApp"
WA_DETAIL_OLD = f'<p><a href="https://wa.me/919818246938" target="_blank" rel="noopener noreferrer">{tel_display}</a></p>'
WA_DETAIL_NEW = '<p><a href="https://wa.me/919818246938" target="_blank" rel="noopener noreferrer">WhatsApp</a></p>'
replace_in('contact.html', WA_DETAIL_OLD, WA_DETAIL_NEW)

# 6. memory/brand-and-content.md: remove Phone line
replace_in('memory/brand-and-content.md', '| Phone | +91 98182 46938 |\n', '')

# 7. memory/business-bank/WEBSITE.md: remove phone number, keep WhatsApp
WS_OLD = f'- Contact: \'+91 98182 46938\' · WhatsApp: \'wa.me/919818246938\''
WS_NEW = f"- WhatsApp: 'wa.me/919818246938'"
replace_in('memory/business-bank/WEBSITE.md', WS_OLD, WS_NEW)

print("All done!")