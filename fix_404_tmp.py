#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io

def replace_in(path, old, new):
    with io.open(path, 'r', encoding='utf-8') as f:
        data = f.read()
    count = data.count(old)
    if count == 0:
        print(f"  [MISS] {path}")
        return False
    data = data.replace(old, new)
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(data)
    print(f"  [OK {count}x] {path}")
    return True

# 404.html shares the same footer as standard pages
FOOTER_OLD = '<li><a href="mailto:services@tkvibes.in">services@tkvibes.in</a></li><li><a href="tel:+919818246938">+91 98182 46938</a></li><li><a href="https://wa.me/919818246938">WhatsApp</a></li><li><span>India, serving clients worldwide</span></li>'
FOOTER_NEW = '<li><a href="mailto:services@tkvibes.in">services@tkvibes.in</a></li><li><a href="https://wa.me/919818246938">WhatsApp</a></li><li><span>India, serving clients worldwide</span></li>'
replace_in('404.html', FOOTER_OLD, FOOTER_NEW)
print("Done")