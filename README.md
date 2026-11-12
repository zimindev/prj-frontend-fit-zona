# Fit Zona — плани тренувань і калькулятор калорій

Статичний сайт (HTML, CSS, JS), шрифт Montserrat (локально).

- `index.html` — головна
- `plan-dlya-cholovikiv.html`, `plan-dlya-zhinok.html` — річні плани: 12 місяців, 4 етапи, вправи з фото, позначки «Місяць виконано» (localStorage), друк місяця
- `kalkulyator-kaloriy.html` — калорії, БЖВ, вода, ІМТ, розподіл на прийоми їжі

## Збірка

```
python3 _build/build.py
```

Генерує HTML у `fit-zona/` з даних `_build/plans.py`, перетискає фото (`_build/photos`, Pexels) і кадри вправ (`_build/ex-img`, free-exercise-db, Unlicense) у WebP. CSS і JS у `fit-zona/assets` пишуться руками.

Локально: `python3 -m http.server 8140 -d fit-zona`

Design & Development by [Sasha Zimin](https://zimin.dev) ❤️

## Скріншоти

![Головна](screenshots/home.jpg)
![План для чоловіків](screenshots/men.jpg)
![Калькулятор калорій](screenshots/calc.jpg)

## Ліцензії ресурсів

- Шрифт Montserrat — SIL Open Font License 1.1 (`fit-zona/assets/fonts/OFL.txt`)
- Фото — [Pexels](https://www.pexels.com/license/)
- Кадри вправ — [free-exercise-db](https://github.com/yuhonas/free-exercise-db) (Unlicense)
