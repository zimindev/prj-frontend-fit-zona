/* Fit Zona — калькулятор калорій. */
(function () {
  var form = document.querySelector('.calc-form');
  if (!form) return;
  var KEY = 'fz2-calc';
  var err = form.querySelector('.form-error');
  var R = {};
  document.querySelectorAll('[data-r]').forEach(function (el) { R[el.getAttribute('data-r')] = el; });

  var fmt = function (n) { return Math.round(n).toLocaleString('uk-UA'); };
  var dec = function (n, d) { return n.toLocaleString('uk-UA', { minimumFractionDigits: d, maximumFractionDigits: d }); };

  // зміна калорій відносно витрати: [мʼякий, помірний, швидкий]
  var GOALS = {
    cut: { label: 'Щоб схуднути', k: [-0.10, -0.18, -0.25], protein: 2.0 },
    keep: { label: 'Щоб тримати вагу', k: [0, 0, 0], protein: 1.6 },
    bulk: { label: 'Щоб набрати масу', k: [0.05, 0.10, 0.15], protein: 1.8 }
  };
  var PACE = { soft: 0, mid: 1, fast: 2 };
  var MEALS = [
    ['Сніданок', 0.25, 'Каша або омлет, фрукти, кава чи чай.'],
    ['Обід', 0.35, 'Мʼясо чи риба, крупа, овочі.'],
    ['Перекус', 0.15, 'Сир, йогурт, горіхи або протеїн.'],
    ['Вечеря', 0.25, 'Білок і овочі, трохи крупи після тренування.']
  ];

  function val(name) { return form.elements[name]; }
  function radio(name) { var r = form.querySelector('input[name="' + name + '"]:checked'); return r ? r.value : ''; }
  function num(name) {
    var v = String(val(name).value).replace(',', '.').trim();
    return v === '' ? NaN : parseFloat(v);
  }

  function restore() {
    var s;
    try { s = JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) { s = null; }
    if (!s || typeof s !== 'object') return;
    ['age', 'height', 'weight', 'fat'].forEach(function (k) { if (s[k] != null) val(k).value = s[k]; });
    if (s.activity) val('activity').value = s.activity;
    ['sex', 'goal', 'pace'].forEach(function (k) {
      var r = s[k] && form.querySelector('input[name="' + k + '"][value="' + s[k] + '"]');
      if (r) r.checked = true;
    });
  }
  function store() {
    var s = { sex: radio('sex'), goal: radio('goal'), pace: radio('pace'), activity: val('activity').value };
    ['age', 'height', 'weight', 'fat'].forEach(function (k) { s[k] = val(k).value; });
    try { localStorage.setItem(KEY, JSON.stringify(s)); } catch (e) { /* приватний режим */ }
  }

  function check(name, min, max, label, optional) {
    var v = num(name);
    var wrap = val(name).closest('.input-unit');
    var bad = optional ? (!isNaN(v) && (v < min || v > max)) : (isNaN(v) || v < min || v > max);
    wrap.classList.toggle('invalid', bad);
    val(name).setAttribute('aria-invalid', String(bad));
    return bad ? label + ': від ' + min + ' до ' + max : '';
  }

  function calc() {
    var problems = [
      check('age', 16, 90, 'Вік'),
      check('height', 130, 230, 'Зріст'),
      check('weight', 35, 250, 'Вага'),
      check('fat', 3, 60, 'Відсоток жиру', true)
    ].filter(Boolean);
    var goal = radio('goal') || 'keep';
    form.querySelector('[data-pace]').hidden = goal === 'keep';
    if (problems.length) {
      err.textContent = 'Перевір: ' + problems.join('; ') + '.';
      err.hidden = false;
      return;
    }
    err.hidden = true;

    var sex = radio('sex'), age = num('age'), h = num('height'), w = num('weight'), fat = num('fat');
    var act = parseFloat(val('activity').value) || 1.55;
    var useKatch = !isNaN(fat);
    var bmr = useKatch ? 370 + 21.6 * w * (1 - fat / 100)
                       : 10 * w + 6.25 * h - 5 * age + (sex === 'f' ? -161 : 5);
    var tdee = bmr * act;
    var g = GOALS[goal];
    var target = tdee * (1 + g.k[PACE[radio('pace')] || 1]);
    var floor = sex === 'f' ? 1200 : 1500;
    var note = '';
    if (target < floor) { target = floor; note = 'Менше ' + floor + ' ккал на день без лікаря не радимо — показуємо мінімум.'; }
    else if (goal === 'cut') note = 'Це приблизно −' + dec((tdee - target) * 7 / 7700, 1) + ' кг на тиждень.';
    else if (goal === 'bulk') note = 'Очікуй +' + dec((target - tdee) * 7 / 7700 * 0.6 + 0.1, 1) + ' кг на тиждень, частина — вода і глікоген.';
    else note = 'Вага коливається ±1 кг — дивись на середнє за тиждень.';

    // при зайвій вазі білок рахуємо від «нормальної» ваги (ІМТ 25)
    var bmi = w / Math.pow(h / 100, 2);
    var refW = bmi > 30 ? 25 * Math.pow(h / 100, 2) : w;
    var p = g.protein * refW;
    var f = Math.max(0.9 * refW, target * 0.22 / 9);
    var c = Math.max(0, (target - p * 4 - f * 9) / 4);
    var kcalP = p * 4, kcalF = f * 9, kcalC = c * 4, sum = kcalP + kcalF + kcalC || 1;

    R['goal-label'].textContent = g.label;
    R.kcal.textContent = fmt(Math.round(target / 10) * 10);
    R.note.textContent = note;
    R.p.textContent = fmt(p) + ' г';
    R.f.textContent = fmt(f) + ' г';
    R.c.textContent = fmt(c) + ' г';
    R['p-kcal'].textContent = Math.round(kcalP / sum * 100) + ' % калорій';
    R['f-kcal'].textContent = Math.round(kcalF / sum * 100) + ' % калорій';
    R['c-kcal'].textContent = Math.round(kcalC / sum * 100) + ' % калорій';
    R['p-bar'].style.width = (kcalP / sum * 100) + '%';
    R['f-bar'].style.width = (kcalF / sum * 100) + '%';
    R['c-bar'].style.width = (kcalC / sum * 100) + '%';
    R.formula.textContent = useKatch ? '(Кетч — Макардл)' : '(Міффлін — Сан-Жеор)';
    R.bmr.textContent = fmt(bmr) + ' ккал';
    R.tdee.textContent = fmt(tdee) + ' ккал';
    var water = w * (sex === 'f' ? 0.031 : 0.035) + (act >= 1.55 ? 0.5 : 0);
    R.water.textContent = dec(water, 1) + ' л';
    var cat = bmi < 18.5 ? 'недостатня вага' : bmi < 25 ? 'норма' : bmi < 30 ? 'надмірна вага' : 'ожиріння';
    R.bmi.textContent = dec(bmi, 1) + ' — ' + cat;
    // шкала 0–40
    R['bmi-dot'].style.left = (Math.min(40, Math.max(0, bmi)) / 40 * 100) + '%';

    R.meals.innerHTML = '';
    MEALS.forEach(function (m) {
      var el = document.createElement('article');
      el.className = 'meal';
      el.innerHTML = '<span></span><b></b><small></small><p></p>';
      el.children[0].textContent = m[0];
      el.children[1].textContent = fmt(Math.round(target * m[1] / 10) * 10) + ' ккал';
      el.children[2].textContent = 'Б ' + fmt(p * m[1]) + ' · Ж ' + fmt(f * m[1]) + ' · В ' + fmt(c * m[1]) + ' г';
      el.children[3].textContent = m[2];
      R.meals.appendChild(el);
    });
    store();
  }

  restore();
  form.addEventListener('input', calc);
  form.addEventListener('change', calc);
  form.addEventListener('submit', function (e) { e.preventDefault(); calc(); });
  calc();
})();
