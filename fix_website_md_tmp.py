#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io

path = 'memory/business-bank/WEBSITE.md'
with io.open(path, 'r', encoding='utf-8') as f:
    data = f.read()

old = '- Contact: `+91 98182 46938` \u00b7 WhatsApp: `wa.me/919818246938`'
new = '- WhatsApp: `wa.me/919818246938`'

cnt = data.count(old)
if cnt:
    data = data.replace(old, new)
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(data)
    print(f'[OK {cnt}x] {path}')
else:
    print(f'[MISS] {path}')
    # fallback: replace just the phone number segment
    old2 = '+91 98182 46938` \u00b7 WhatsApp'
    new2 = 'WhatsApp'
    if old2 in data:
        data = data.replace('`+91 98182 46938` \u00b7 ', '')
        with io.open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(data)
        print('[OK fallback]')