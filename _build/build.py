#!/usr/bin/env python3
"""Генератор сайту Fit Zona (новий дизайн, Montserrat).

Сторінки: головна, річний план для чоловіків, річний план для жінок, калькулятор калорій.
CSS і JS лежать у ../fit-zona/assets і пишуться руками; цей скрипт збирає HTML,
перетискає фото в WebP і кадри вправ.

Запуск: python3 build.py
"""
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.join(os.path.dirname(HERE), 'fit-zona')
sys.path.insert(0, HERE)
from plans import MEN, WOMEN, RULES, EX_IMG  # noqa: E402

PHOTOS = os.path.join(HERE, 'photos')   # фото Pexels
EX_SRC = os.path.join(HERE, 'ex-img')   # кадри free-exercise-db (Unlicense)
VERSION = '1.1.0'
SITE = 'https://fit-zona.pp.ua'
LASTMOD = '2026-11-12'
OG = {}  # сторінка → (фото, заголовок на картинці)

e = html.escape
USED_PHOTOS = set()
USED_EX = set()

WOMEN_EXTRA = [('Цикл', 'У перші дні циклу орієнтуйся на самопочуття: можна знизити вагу на 20–30 % або замінити тренування прогулянкою чи йогою.')]

NAV = [
    ('index.html', 'Головна'),
    ('plan-dlya-cholovikiv.html', 'Для чоловіків'),
    ('plan-dlya-zhinok.html', 'Для жінок'),
    ('kalkulyator-kaloriy.html', 'Калькулятор калорій'),
]

LOGO = ('<svg class="logo-mark" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="9" fill="currentColor"/>'
        '<path d="M9 22V10h10M9 16h7M17 22l6-12" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>')

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='9' fill='%23FF4F1F'/%3E"
           "%3Cpath d='M9 22V10h10M9 16h7M17 22l6-12' stroke='%23fff' stroke-width='3' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")


# ---------- зображення ----------

def photo(name, alt, cls='', sizes='(max-width: 800px) 100vw, 50vw', eager=False):
    """<img> з двома WebP-розмірами (640 і 1400)."""
    USED_PHOTOS.add(name)
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    w, h = photo_size(name, 1400)
    return (f'<img class="{cls}" src="assets/img/{name}.webp" '
            f'srcset="assets/img/{name}-640.webp 640w, assets/img/{name}.webp {w}w" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{e(alt)}" {load}>')


def photo_size(name, maxw):
    from PIL import Image
    with Image.open(os.path.join(PHOTOS, name + '.jpg')) as im:
        w, h = im.size
    if w > maxw:
        h = round(h * maxw / w)
        w = maxw
    return w, h


def export_images():
    from PIL import Image
    img_dir = os.path.join(SITE_DIR, 'assets', 'img')
    ex_dir = os.path.join(SITE_DIR, 'assets', 'ex')
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(ex_dir, exist_ok=True)
    for f in os.listdir(img_dir):
        os.remove(os.path.join(img_dir, f))
    for f in os.listdir(ex_dir):
        os.remove(os.path.join(ex_dir, f))
    for name in sorted(USED_PHOTOS):
        im = Image.open(os.path.join(PHOTOS, name + '.jpg')).convert('RGB')
        for suffix, width, q in (('', 1400, 74), ('-640', 640, 70)):
            cp = im.copy()
            if cp.width > width:
                cp = cp.resize((width, round(cp.height * width / cp.width)), Image.LANCZOS)
            cp.save(os.path.join(img_dir, f'{name}{suffix}.webp'), 'WEBP', quality=q, method=6)
    for ex_id in sorted(USED_EX):
        for frame in (0, 1):
            im = Image.open(os.path.join(EX_SRC, f'{ex_id}-{frame}.jpg')).convert('RGB')
            if im.width > 480:
                im = im.resize((480, round(im.height * 480 / im.width)), Image.LANCZOS)
            im.save(os.path.join(ex_dir, f'{ex_id}-{frame}.webp'), 'WEBP', quality=62, method=6)


# ---------- каркас ----------

def page_url(fname):
    return SITE + '/' + ('' if fname == 'index.html' else fname)


def crumbs(fname, name):
    return {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Головна', 'item': SITE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': name, 'item': page_url(fname)}]}


def shell(fname, title, desc, body, scripts=(), body_attrs='', ld=None, robots='index, follow'):
    nav = ''.join(
        '<li><a href="%s"%s>%s</a></li>' % (href, ' aria-current="page"' if href == fname else '', label)
        for href, label in NAV)
    foot_nav = ''.join(f'<li><a href="{href}">{label}</a></li>' for href, label in NAV)
    head_seo = ''
    if robots.startswith('index'):
        og_img = SITE + '/assets/og/' + fname.replace('.html', '.jpg')
        head_seo = f'''<link rel="canonical" href="{page_url(fname)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Fit Zona">
<meta property="og:url" content="{page_url(fname)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:locale" content="uk_UA">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">'''
        if ld:
            head_seo += '\n<script type="application/ld+json">' + json.dumps({'@context': 'https://schema.org', '@graph': ld}, ensure_ascii=False).replace('</', '<\\/') + '</script>'
    js = ''.join(f'<script src="assets/js/{s}?v={VERSION}" defer></script>' for s in ('main.js',) + tuple(scripts))
    return f'''<!doctype html>
<html lang="uk">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#121316">
<meta name="robots" content="{robots}">
{head_seo}
<link rel="icon" href="{FAVICON}">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<link rel="preload" href="assets/fonts/montserrat-cyrillic.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/style.css?v={VERSION}">
</head>
<body{body_attrs}>
<a class="skip" href="#main">Перейти до змісту</a>
<header class="site-header">
  <div class="wrap header-in">
    <a class="logo" href="index.html" aria-label="Fit Zona — на головну">{LOGO}<span>FIT<b>ZONA</b></span></a>
    <button class="burger" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Меню"><span></span><span></span><span></span></button>
    <nav id="site-nav" class="site-nav" aria-label="Головне меню"><ul>{nav}</ul></nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <a class="logo logo-light" href="index.html">{LOGO}<span>FIT<b>ZONA</b></span></a>
      <p class="footer-text">Річні плани тренувань і калькулятор калорій. Безкоштовно, без реєстрації — прогрес зберігається у твоєму браузері.</p>
    </div>
    <nav aria-label="Посилання у футері"><ul class="footer-nav">{foot_nav}</ul></nav>
  </div>
  <div class="wrap footer-bottom">
    <span>© 2026 Fit Zona</span>
    <span>Design &amp; Development by <a href="https://zimin.dev" target="_blank" rel="noopener">Sasha Zimin</a> ❤️</span>
  </div>
</footer>
{js}
</body>
</html>
'''


def arrow():
    return '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'


# ---------- головна ----------

def page_home():
    total_ex = len({n for P in (MEN, WOMEN) for ph in P['phases'] for _, d in ph['days'] for n, _ in d if n in EX_IMG})
    steps = [
        ('01', 'Місяці 1–3', 'Фундамент', 'Техніка базових вправ, 3 тренування на тиждень, звикаємо до режиму.'),
        ('02', 'Місяці 4–6', 'Сила й форма', 'Спліт на 4 дні: кожна група мʼязів працює двічі на тиждень.'),
        ('03', 'Місяці 7–9', 'Обсяг і рельєф', 'Більше підходів, коротший відпочинок, суперсети й інтервальне кардіо.'),
        ('04', 'Місяці 10–12', 'Пік', 'Найважчі ваги року, перевірка особистих рекордів і план на наступний рік.'),
    ]
    steps_html = ''.join(f'''<li class="step"><span class="step-n">{n}</span><span class="step-when">{w}</span><h3>{t}</h3><p>{d}</p></li>''' for n, w, t, d in steps)
    rules_html = ''.join(f'<li><h3>{e(t)}</h3><p>{e(d)}</p></li>' for t, d in RULES)
    faq = [
        ('Чи підійде план новачку?', 'Так. Перші три місяці — саме для того, щоб навчитися техніки й звикнути до режиму. Якщо вже тренуєшся рік і більше, можна почати з 4-го місяця.'),
        ('Скільки триває одне тренування?', '60–75 хвилин разом з розминкою. Кардіо після тренування — ще 20–25 хвилин.'),
        ('Що потрібно із спорядження?', 'Плани розраховані на звичайний зал: штанга, гантелі, лава, блочні тренажери, турнік і бруси.'),
        ('Пропустив тиждень — що робити?', 'Повтори останній тиждень з вагою на 10 % меншою, а далі продовжуй за планом. Пропуск більше місяця — повернись на початок етапу.'),
        ('Як рахує калькулятор калорій?', 'За формулою Міффліна — Сан-Жеора (або Кетча — Макардла, якщо вказати відсоток жиру), з поправкою на активність і ціль. Це орієнтир: перевіряй вагу раз на тиждень і коригуй на 100–150 ккал.'),
        ('Де зберігається мій прогрес?', 'Позначки «Місяць виконано» і дані калькулятора зберігаються лише у твоєму браузері. Ми нічого не збираємо.'),
    ]
    faq_html = ''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in faq)
    body = f'''
<section class="hero">
  <div class="wrap hero-grid">
    <div class="hero-text">
      <p class="eyebrow">Безкоштовно · без реєстрації</p>
      <h1>Рік тренувань. <span class="accent">Один чіткий план.</span></h1>
      <p class="lead">Два річні плани — для чоловіків і для жінок — і калькулятор калорій. Кожен місяць розписаний: вправи з фото, підходи, повторення й прогресія.</p>
      <div class="btns">
        <a class="btn btn-accent" href="plan-dlya-cholovikiv.html">План для чоловіків {arrow()}</a>
        <a class="btn btn-ink" href="plan-dlya-zhinok.html">План для жінок {arrow()}</a>
      </div>
      <a class="text-link" href="kalkulyator-kaloriy.html">Або почни з калькулятора калорій {arrow()}</a>
    </div>
    <div class="hero-media">
      <figure class="hm hm-1">{photo('coach-1', 'Чоловік з гантелями в залі', sizes='(max-width: 800px) 50vw, 25vw', eager=True)}<figcaption>Для чоловіків</figcaption></figure>
      <figure class="hm hm-2">{photo('coach-3', 'Жінка зі штангою в залі', sizes='(max-width: 800px) 50vw, 25vw', eager=True)}<figcaption>Для жінок</figcaption></figure>
      <div class="hm-badge"><b>12</b><span>місяців<br>розписано</span></div>
    </div>
  </div>
</section>

<section class="stats" aria-label="Коротко про плани">
  <div class="wrap stats-grid">
    <div><b>12</b><span>місяців у кожному плані</span></div>
    <div><b>4</b><span>етапи по 3 місяці</span></div>
    <div><b>{total_ex}</b><span>вправ з фото техніки</span></div>
    <div><b>0 ₴</b><span>і жодної реєстрації</span></div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><p class="eyebrow">Обери, з чого почати</p><h2>Три інструменти на весь рік</h2></div>
    <div class="cards-3">
      <a class="tool-card" href="plan-dlya-cholovikiv.html">
        {photo('gal-4', 'Чоловік тримає штангу на плечах', sizes='(max-width: 800px) 100vw, 33vw')}
        <div class="tool-body"><span class="tag">12 місяців</span><h3>План для чоловіків</h3><p>Фундамент, сила і маса, гіпертрофія, пікова сила. 3–5 тренувань на тиждень.</p><span class="more">Відкрити план {arrow()}</span></div>
      </a>
      <a class="tool-card" href="plan-dlya-zhinok.html">
        {photo('gal-6', 'Жінка виконує станову тягу', sizes='(max-width: 800px) 100vw, 33vw')}
        <div class="tool-body"><span class="tag">12 місяців</span><h3>План для жінок</h3><p>Постава, ноги й сідниці, рельєф, сила. 3–4 тренування на тиждень.</p><span class="more">Відкрити план {arrow()}</span></div>
      </a>
      <a class="tool-card" href="kalkulyator-kaloriy.html">
        {photo('gym-dumbbells', 'Стійка з гантелями', sizes='(max-width: 800px) 100vw, 33vw')}
        <div class="tool-body"><span class="tag">2 хвилини</span><h3>Калькулятор калорій</h3><p>Норма калорій, білки, жири, вуглеводи і вода — під твою ціль.</p><span class="more">Порахувати {arrow()}</span></div>
      </a>
    </div>
  </div>
</section>

<section class="section section-dark">
  <div class="wrap">
    <div class="section-head"><p class="eyebrow">Як побудований рік</p><h2>4 етапи. Кожен — на 3 місяці.</h2><p class="section-lead">Навантаження росте поступово, а кожен третій місяць закінчується легким тижнем, щоб тіло встигало відновлюватися.</p></div>
    <ol class="steps">{steps_html}</ol>
  </div>
</section>

<section class="section">
  <div class="wrap split">
    <div class="split-media">{photo('dir-functional', 'Тренер і клієнтка в залі для функціональних тренувань', sizes='(max-width: 800px) 100vw, 45vw')}</div>
    <div>
      <p class="eyebrow">Харчування</p>
      <h2>Тренування — половина результату</h2>
      <p class="section-lead">Без правильної кількості калорій навіть найкращий план працює вполовину. Калькулятор порахує норму для схуднення, підтримки чи набору маси і розкладе її на білки, жири й вуглеводи.</p>
      <ul class="checks"><li>Формули Міффліна — Сан-Жеора і Кетча — Макардла</li><li>Білки, жири, вуглеводи в грамах</li><li>Норма води й розподіл на прийоми їжі</li></ul>
      <a class="btn btn-accent" href="kalkulyator-kaloriy.html">Порахувати калорії {arrow()}</a>
    </div>
  </div>
</section>

<section class="section section-soft">
  <div class="wrap">
    <div class="section-head"><p class="eyebrow">Правила</p><h2>Шість правил, які тримають план</h2></div>
    <ol class="rules">{rules_html}</ol>
  </div>
</section>

<section class="section">
  <div class="wrap faq-wrap">
    <div class="section-head"><p class="eyebrow">Питання</p><h2>Часті питання</h2></div>
    <div class="faq">{faq_html}</div>
  </div>
</section>
'''
    OG['index.html'] = ('cta', 'Рік тренувань.\nОдин чіткий план.')
    ld = [
        {'@type': 'WebSite', '@id': SITE + '/#site', 'url': SITE + '/', 'name': 'Fit Zona', 'inLanguage': 'uk'},
        {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]},
    ]
    return shell('index.html', 'Fit Zona — річні плани тренувань і калькулятор калорій',
                 'Безкоштовні плани тренувань у залі на 12 місяців для чоловіків і жінок та калькулятор калорій, білків, жирів і вуглеводів.',
                 body, ld=ld)


# ---------- плани ----------

def ex_row(name, sets):
    ex_id = EX_IMG.get(name)
    if ex_id:
        USED_EX.add(ex_id)
        thumb = (f'<button class="ex-thumb" type="button" data-ex="{ex_id}" data-name="{e(name)}" data-sets="{e(sets)}" aria-label="Показати техніку: {e(name)}">'
                 f'<img src="assets/ex/{ex_id}-0.webp" width="480" height="320" alt="" loading="lazy"></button>')
    else:
        thumb = '<span class="ex-thumb ex-none" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M6 9v6M18 9v6M3 11v2M21 11v2M6 12h12" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/></svg></span>'
    return f'<li>{thumb}<span class="ex-name">{e(name)}</span><span class="ex-sets">{e(sets)}</span></li>'


def plan_page(fname, plan, key, other, extra_rules):
    phases = plan['phases']
    rules = RULES + extra_rules

    # картки етапів
    phase_cards = ''
    for i, ph in enumerate(phases):
        first = i * 3 + 1
        phase_cards += f'''<a class="phase-card" href="#misyats-{first}" data-goto="{first}">
  {photo(ph['img'], ph['alt'], sizes='(max-width: 800px) 50vw, 25vw')}
  <div class="phase-body"><span class="phase-when">Етап {i + 1} · місяці {ph['months']}</span><h3>{e(ph['name'])}</h3><p>{e(ph['freq'])}</p></div>
</a>'''

    # вкладки місяців
    tabs = ''
    for i, ph in enumerate(phases):
        btns = ''.join(
            f'<button type="button" role="tab" id="tab-{m}" aria-controls="misyats-{m}" aria-selected="{"true" if m == 1 else "false"}" data-m="{m}"><span>{m}</span></button>'
            for m in range(i * 3 + 1, i * 3 + 4))
        tabs += f'<div class="mt-group"><span class="mt-label">{e(ph["name"])}</span><div class="mt-btns">{btns}</div></div>'

    # панелі місяців
    panels = ''
    for i, ph in enumerate(phases):
        days = ''
        for dname, exs in ph['days']:
            rows = ''.join(ex_row(n, s) for n, s in exs)
            days += f'<article class="day"><h4>{e(dname)}</h4><ol>{rows}</ol></article>'
        for j, (mt, mtext, mprog) in enumerate(ph['months_info']):
            m = i * 3 + j + 1
            prev_btn = f'<button class="btn btn-line" type="button" data-goto="{m - 1}">← Місяць {m - 1}</button>' if m > 1 else '<span></span>'
            next_btn = f'<button class="btn btn-ink" type="button" data-goto="{m + 1}">Місяць {m + 1} →</button>' if m < 12 else '<span></span>'
            panels += f'''<section class="month" id="misyats-{m}" role="tabpanel" aria-labelledby="tab-{m}" data-panel="{m}"{"" if m == 1 else " hidden"}>
  <div class="month-head">
    <div>
      <p class="eyebrow">Місяць {m} з 12 · етап {i + 1} «{e(ph['name'])}»</p>
      <h2>{e(mt)}</h2>
      <p class="month-text">{e(mtext)}</p>
      <p class="month-prog"><b>Прогресія.</b> {e(mprog)}</p>
    </div>
    <dl class="month-meta">
      <div><dt>Частота</dt><dd>{e(ph['freq'])}</dd></div>
      <div><dt>Кардіо</dt><dd>{e(ph['cardio'])}</dd></div>
      <div><dt>Розклад</dt><dd>{e(ph['split'])}</dd></div>
      <div><dt>Мета етапу</dt><dd>{e(ph['goal'])}</dd></div>
    </dl>
  </div>
  <div class="days">{days}</div>
  <div class="month-foot">
    <label class="done-toggle"><input type="checkbox" data-done="{m}"><span class="box" aria-hidden="true"></span>Місяць {m} виконано</label>
    <div class="month-nav">{prev_btn}{next_btn}</div>
  </div>
</section>'''

    rules_html = ''.join(f'<li><h3>{e(t)}</h3><p>{e(d)}</p></li>' for t, d in rules)
    hero_name, hero_alt = plan['hero']
    o_href, o_label = other
    n_ex = len({n for ph in phases for _, d in ph['days'] for n, _ in d if n in EX_IMG})

    body = f'''
<section class="plan-hero">
  <div class="wrap plan-hero-grid">
    <div class="hero-text">
      <p class="eyebrow">Річний план · 12 місяців</p>
      <h1>{e(plan['h1'])}</h1>
      <p class="lead">{e(plan['lead'])}</p>
      <ul class="chips"><li>4 етапи</li><li>{n_ex} вправ з фото</li><li>Прогрес зберігається</li></ul>
      <div class="progress" aria-live="polite">
        <div class="progress-top"><span>Твій прогрес</span><b data-progress-text>0 з 12 місяців</b></div>
        <div class="progress-bar"><span data-progress-bar></span></div>
      </div>
    </div>
    <figure class="plan-hero-media">{photo(hero_name, hero_alt, sizes='(max-width: 900px) 100vw, 50vw', eager=True)}</figure>
  </div>
</section>

<section class="section section-tight">
  <div class="wrap">
    <div class="section-head"><p class="eyebrow">Етапи</p><h2>Рік у чотирьох етапах</h2></div>
    <div class="phases">{phase_cards}</div>
  </div>
</section>

<section class="section section-soft plan-section" id="plan">
  <div class="wrap">
    <div class="plan-bar">
      <div class="month-tabs" role="tablist" aria-label="Місяці">{tabs}</div>
      <button class="btn btn-line print-btn" type="button" data-print>
        <svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 9V3h10v6M7 17H4v-7h16v7h-3M7 14h10v7H7z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>Друкувати місяць</button>
    </div>
    {panels}
    <p class="hint">Натисни на фото вправи, щоб побачити початок і кінець руху.</p>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><p class="eyebrow">Правила</p><h2>Що робити кожного місяця</h2></div>
    <ol class="rules">{rules_html}</ol>
    <div class="cross">
      <a class="cross-card cross-accent" href="kalkulyator-kaloriy.html"><span>Наступний крок</span><b>Порахуй норму калорій</b>{arrow()}</a>
      <a class="cross-card" href="{o_href}"><span>Інший план</span><b>{o_label}</b>{arrow()}</a>
    </div>
    <p class="note">План — загальний орієнтир для здорових дорослих. Якщо маєш травми, хронічні хвороби чи вагітність, порадься з лікарем перед початком. Фото вправ — <a href="https://github.com/yuhonas/free-exercise-db" target="_blank" rel="noopener">free-exercise-db</a> (суспільне надбання).</p>
  </div>
</section>

<dialog class="ex-dlg" aria-labelledby="ex-title">
  <div class="ex-dlg-head"><div><h3 id="ex-title"></h3><p class="ex-dlg-sets"></p></div><button class="ex-close" type="button" aria-label="Закрити">×</button></div>
  <div class="ex-frames">
    <figure><img alt="" width="480" height="320"><figcaption>Початок</figcaption></figure>
    <figure><img alt="" width="480" height="320"><figcaption>Кінець руху</figcaption></figure>
  </div>
</dialog>
'''
    OG[fname] = (hero_name, plan['h1'] + '\nна 12 місяців')
    ld = [
        {'@type': 'WebPage', 'url': page_url(fname), 'name': plan['title'], 'description': plan['desc'], 'inLanguage': 'uk',
         'isPartOf': {'@id': SITE + '/#site'}, 'primaryImageOfPage': SITE + '/assets/img/' + hero_name + '.webp',
         'about': {'@type': 'ExercisePlan', 'name': plan['title'], 'exerciseType': 'Силові тренування в залі',
                   'activityDuration': 'P12M', 'workload': '3–5 тренувань на тиждень',
                   'audience': {'@type': 'PeopleAudience', 'suggestedGender': 'male' if key == 'm' else 'female'}}},
        crumbs(fname, plan['h1']),
    ]
    return shell(fname, plan['title'] + ' — Fit Zona', plan['desc'], body, ('plan.js',), f' data-plan="{key}"', ld=ld)


# ---------- калькулятор ----------

def page_404():
    body = f'''
<section class="calc-hero section">
  <div class="wrap">
    <p class="eyebrow">Помилка 404</p>
    <h1>Такої сторінки <span class="accent">немає</span></h1>
    <p class="lead">Можливо, вона переїхала. Почни з головної або одразу відкрий план чи калькулятор.</p>
    <div class="btns">
      <a class="btn btn-accent" href="/">На головну {arrow()}</a>
      <a class="btn btn-ink" href="/kalkulyator-kaloriy.html">Калькулятор калорій {arrow()}</a>
    </div>
  </div>
</section>
'''
    html_ = shell('404.html', 'Сторінку не знайдено — Fit Zona', 'Сторінку не знайдено.', body, robots='noindex, follow')
    # 404 віддається з будь-якої адреси — шляхи до файлів робимо абсолютними
    return html_.replace('href="assets/', 'href="/assets/').replace('src="assets/', 'src="/assets/').replace('href="index.html"', 'href="/"') \
        .replace('href="plan-', 'href="/plan-').replace('href="kalkulyator', 'href="/kalkulyator')


def export_seo():
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    og_dir = os.path.join(SITE_DIR, 'assets', 'og')
    os.makedirs(og_dir, exist_ok=True)
    font = os.path.join(HERE, 'fonts', 'Montserrat-VF.ttf')  # повний шрифт (латиниця, цифри, кирилиця)
    for fname, (name, text) in OG.items():
        im = ImageOps.fit(Image.open(os.path.join(PHOTOS, name + '.jpg')).convert('RGB'), (1200, 630), Image.LANCZOS, centering=(0.5, 0.3))
        shade = Image.new('L', (1200, 630))
        sd = ImageDraw.Draw(shade)
        for x in range(1200):
            sd.line((x, 0, x, 630), fill=int(max(110, 240 - x * 0.2)))
        im = Image.composite(Image.new('RGB', im.size, (18, 19, 22)), im, shade)
        d = ImageDraw.Draw(im)
        f_big = ImageFont.truetype(font, 68); f_big.set_variation_by_axes([800])
        f_small = ImageFont.truetype(font, 30); f_small.set_variation_by_axes([800])
        d.rounded_rectangle((64, 64, 112, 112), 13, fill=(255, 79, 31))
        d.line((78, 99, 78, 77, 96, 77), fill='white', width=6, joint='curve')
        d.line((78, 88, 91, 88), fill='white', width=6)
        d.line((93, 99, 104, 77), fill='white', width=6)
        d.text((128, 72), 'FIT', font=f_small, fill='white')
        d.text((128 + d.textlength('FIT', font=f_small), 72), 'ZONA', font=f_small, fill=(255, 79, 31))
        d.multiline_text((64, 290), text, font=f_big, fill='white', spacing=12)
        d.rectangle((64, 556, 184, 564), fill=(255, 79, 31))
        im.save(os.path.join(og_dir, fname.replace('.html', '.jpg')), 'JPEG', quality=82, optimize=True, progressive=True)
    # apple-touch-icon
    ic = Image.new('RGB', (180, 180), (255, 79, 31))
    d = ImageDraw.Draw(ic)
    w = 15
    d.line((51, 124, 51, 56, 107, 56), fill='white', width=w, joint='curve')
    d.line((51, 90, 90, 90), fill='white', width=w)
    d.line((96, 124, 129, 56), fill='white', width=w)
    ic.save(os.path.join(SITE_DIR, 'assets', 'img', 'apple-touch-icon.png'))
    urls = ['index.html', 'plan-dlya-cholovikiv.html', 'plan-dlya-zhinok.html', 'kalkulyator-kaloriy.html']
    sm = ''.join(f'  <url><loc>{page_url(u)}</loc><lastmod>{LASTMOD}</lastmod></url>\n' for u in urls)
    with open(os.path.join(SITE_DIR, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + sm + '</urlset>\n')
    with open(os.path.join(SITE_DIR, 'robots.txt'), 'w', encoding='utf-8') as f:
        f.write(f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')


def page_calc():
    OG['kalkulyator-kaloriy.html'] = ('gym-dumbbells', 'Калькулятор\nкалорій і БЖВ')
    body = f'''
<section class="calc-hero">
  <div class="wrap">
    <p class="eyebrow">Калькулятор калорій</p>
    <h1>Скільки тобі <span class="accent">їсти</span>?</h1>
    <p class="lead">Норма калорій, білків, жирів і вуглеводів під твою ціль. Рахується одразу, поки вводиш дані.</p>
  </div>
</section>

<section class="section section-tight">
  <div class="wrap calc-grid">
    <form class="calc-form" novalidate aria-label="Дані для розрахунку">
      <fieldset class="seg-field">
        <legend>Стать</legend>
        <div class="seg">
          <label><input type="radio" name="sex" value="m" checked><span>Чоловік</span></label>
          <label><input type="radio" name="sex" value="f"><span>Жінка</span></label>
        </div>
      </fieldset>
      <div class="fields-3">
        <label class="field"><span>Вік</span><span class="input-unit"><input type="number" name="age" inputmode="numeric" min="16" max="90" value="30" required><i>років</i></span></label>
        <label class="field"><span>Зріст</span><span class="input-unit"><input type="number" name="height" inputmode="numeric" min="130" max="230" value="178" required><i>см</i></span></label>
        <label class="field"><span>Вага</span><span class="input-unit"><input type="number" name="weight" inputmode="decimal" min="35" max="250" step="0.1" value="80" required><i>кг</i></span></label>
      </div>
      <label class="field">
        <span>Активність</span>
        <select name="activity">
          <option value="1.2">Мінімальна — сидяча робота</option>
          <option value="1.375">Легка — 1–2 тренування на тиждень</option>
          <option value="1.55" selected>Середня — 3–4 тренування на тиждень</option>
          <option value="1.725">Висока — 5–6 тренувань на тиждень</option>
          <option value="1.9">Дуже висока — фізична праця + спорт</option>
        </select>
      </label>
      <fieldset class="seg-field">
        <legend>Ціль</legend>
        <div class="seg seg-3">
          <label><input type="radio" name="goal" value="cut"><span>Схуднути</span></label>
          <label><input type="radio" name="goal" value="keep" checked><span>Тримати вагу</span></label>
          <label><input type="radio" name="goal" value="bulk"><span>Набрати масу</span></label>
        </div>
      </fieldset>
      <fieldset class="seg-field" data-pace>
        <legend>Темп</legend>
        <div class="seg seg-3">
          <label><input type="radio" name="pace" value="soft"><span>Мʼякий</span></label>
          <label><input type="radio" name="pace" value="mid" checked><span>Помірний</span></label>
          <label><input type="radio" name="pace" value="fast"><span>Швидкий</span></label>
        </div>
      </fieldset>
      <label class="field"><span>Відсоток жиру <small>(необовʼязково)</small></span><span class="input-unit"><input type="number" name="fat" inputmode="decimal" min="3" max="60" step="0.1" placeholder="напр. 18"><i>%</i></span></label>
      <p class="form-error" role="alert" hidden></p>
    </form>

    <div class="calc-result" aria-live="polite">
      <div class="res-main">
        <span class="res-label" data-r="goal-label">Щоб тримати вагу</span>
        <div class="res-kcal"><b data-r="kcal">—</b><span>ккал на день</span></div>
        <p class="res-note" data-r="note"></p>
      </div>
      <div class="macros">
        <div class="macro m-p"><span>Білки</span><b data-r="p">—</b><i data-r="p-kcal"></i><div class="mbar"><span data-r="p-bar"></span></div></div>
        <div class="macro m-f"><span>Жири</span><b data-r="f">—</b><i data-r="f-kcal"></i><div class="mbar"><span data-r="f-bar"></span></div></div>
        <div class="macro m-c"><span>Вуглеводи</span><b data-r="c">—</b><i data-r="c-kcal"></i><div class="mbar"><span data-r="c-bar"></span></div></div>
      </div>
      <dl class="res-list">
        <div><dt>Базовий обмін <small data-r="formula">(Міффлін — Сан-Жеор)</small></dt><dd data-r="bmr">—</dd></div>
        <div><dt>Витрата з активністю</dt><dd data-r="tdee">—</dd></div>
        <div><dt>Вода</dt><dd data-r="water">—</dd></div>
        <div><dt>Індекс маси тіла</dt><dd data-r="bmi">—</dd></div>
      </dl>
      <div class="bmi-scale" aria-hidden="true"><span class="b1"></span><span class="b2"></span><span class="b3"></span><span class="b4"></span><i data-r="bmi-dot"></i></div>
      <div class="bmi-legend" aria-hidden="true"><span>&lt;18,5</span><span>18,5–25</span><span>25–30</span><span>30+</span></div>
    </div>
  </div>
</section>

<section class="section section-soft">
  <div class="wrap">
    <div class="section-head"><p class="eyebrow">На день</p><h2>Розподіл на 4 прийоми їжі</h2></div>
    <div class="meals" data-r="meals"></div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><p class="eyebrow">Як рахуємо</p><h2>Звідки ці цифри</h2></div>
    <div class="how">
      <article><h3>Базовий обмін</h3><p>Скільки енергії тіло витрачає в спокої. Формула Міффліна — Сан-Жеора: 10 × вага + 6,25 × зріст − 5 × вік, +5 для чоловіків або −161 для жінок. Якщо вказати відсоток жиру — формула Кетча — Макардла, вона точніша для тих, хто тренується.</p></article>
      <article><h3>Активність і ціль</h3><p>Базовий обмін множимо на коефіцієнт активності. Для схуднення віднімаємо 10–25 %, для набору маси додаємо 5–15 % — залежно від темпу.</p></article>
      <article><h3>Білки, жири, вуглеводи</h3><p>Білок — 1,6–2,2 г на кг ваги (на дефіциті більше, щоб зберегти мʼязи). Жири — 0,8–1 г на кг, але не менше 20 % калорій. Решта — вуглеводи.</p></article>
      <article><h3>Як коригувати</h3><p>Зважуйся щоранку і дивись середнє за тиждень. Вага стоїть 2 тижні — зміни норму на 100–150 ккал. Худнеш швидше ніж на 1 % ваги на тиждень — додай калорій.</p></article>
    </div>
    <div class="cross">
      <a class="cross-card cross-accent" href="plan-dlya-cholovikiv.html"><span>12 місяців</span><b>План для чоловіків</b>{arrow()}</a>
      <a class="cross-card" href="plan-dlya-zhinok.html"><span>12 місяців</span><b>План для жінок</b>{arrow()}</a>
    </div>
    <p class="note">Розрахунок — орієнтир для здорових дорослих, а не медична порада. Під час вагітності, годування груддю, при хворобах чи розладах харчової поведінки звернись до лікаря.</p>
  </div>
</section>
'''
    return shell('kalkulyator-kaloriy.html', 'Калькулятор калорій, білків, жирів і вуглеводів — Fit Zona',
                 'Порахуй денну норму калорій для схуднення, підтримки чи набору маси: білки, жири, вуглеводи, вода та індекс маси тіла.',
                 body, ('calc.js',), ld=[
                     {'@type': 'WebApplication', 'name': 'Калькулятор калорій Fit Zona', 'url': page_url('kalkulyator-kaloriy.html'),
                      'applicationCategory': 'HealthApplication', 'operatingSystem': 'Будь-яка (браузер)', 'inLanguage': 'uk',
                      'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'UAH'}},
                     crumbs('kalkulyator-kaloriy.html', 'Калькулятор калорій')])


def main():
    pages = {
        'index.html': page_home(),
        'plan-dlya-cholovikiv.html': plan_page('plan-dlya-cholovikiv.html', MEN, 'm', ('plan-dlya-zhinok.html', 'План для жінок'), []),
        'plan-dlya-zhinok.html': plan_page('plan-dlya-zhinok.html', WOMEN, 'f', ('plan-dlya-cholovikiv.html', 'План для чоловіків'), WOMEN_EXTRA),
        'kalkulyator-kaloriy.html': page_calc(),
        '404.html': page_404(),
    }
    for name, content in pages.items():
        content = content.replace('href="index.html"', 'href="./"').replace('href="./"', 'href="/"' if name == '404.html' else 'href="./"')
        with open(os.path.join(SITE_DIR, name), 'w', encoding='utf-8') as f:
            f.write(content)
    export_images()
    export_seo()
    print('pages:', ', '.join(pages), '| photos:', len(USED_PHOTOS), '| exercises:', len(USED_EX))


if __name__ == '__main__':
    main()
