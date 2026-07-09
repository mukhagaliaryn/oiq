# RULES.md — OIQ архитектура ережелері (конституция)

> **Бұл файл кез келген құрылымдық немесе код өзгерісінен БҰРЫН оқылады.**
> Мұндағы ережелер — ұсыныс емес, заң. Егер тапсырма осы ережелерге қайшы келсе,
> тапсырманы орындама — қайшылықты хабарла.

Жобаның архитектурасы — **модульді монолит** (modular monolith): бір Django проекті, бір `settings.py`,
бір `User`, бір деплой — бірақ ішінде **таза шекаралы домен модульдері**.
Шекара **кодтың ішінде** жүреді (Python модулі + `services`/`selectors` қабаты), **желіде емес**.

---

## 1. Жоба құрылымы және қабаттар

```
oiq-main/
  config/        # settings, urls, wsgi/asgi
  core/          # ІРГЕТАС: абстракт модель, утилита, ортақ виджет (concrete модель ЖОҚ)
  ui/            # ІРГЕТАС: Tailwind, base.html, layouts/, ортақ components/
  apps/
    accounts/    # НЕГІЗГІ домен
    catalog/     # НЕГІЗГІ домен
    directory/   # НЕГІЗГІ домен
    main/        # ӨНІМ
    teaching/    # ӨНІМ
    learning/    # ӨНІМ
    school/      # ӨНІМ (болашақ SIS — әзірге жасалмайды)
  locales/
```

Төрт қабат. Тәуелділік **тек төмен қарай** жүреді.

```
┌─ ӨНІМ app-тары ──────────────────────────────────────────┐
│  apps.main · apps.teaching · apps.learning · apps.school  │  ← өз дерегі + өз беттері
└───────────────────────────────────────────────────────────┘
              │ тұтынады (тек services/selectors арқылы)
              ▼
┌─ accounts ────────────────────────────────────────────────┐
│  apps.accounts                                             │  ← User/Teacher, catalog+directory-ды тұтынады
└───────────────────────────────────────────────────────────┘
              │ тұтынады (тек services/selectors арқылы)
              ▼
┌─ НЕГІЗГІ (іргеталық) домендер ───────────────────────────┐
│  apps.catalog · apps.directory                             │  ← ортақ дерек, бір-бірінен тәуелсіз
└───────────────────────────────────────────────────────────┘
              │ қолданады (мұра, утилита, layout)
              ▼
┌─ ІРГЕТАС ────────────────────────────────────────────────┐
│  core · ui                                                │  ← нақты домен ЖОҚ
└───────────────────────────────────────────────────────────┘
```

> **Неге `accounts` бөлек қабатта:** `Teacher` (accounts) қала/мектепті (`directory`) және пәнді (`catalog`)
> FK арқылы сілтейді (тіркелу/профиль формасында сол таңдау тізімдерін көрсету керек). Сол себепті
> `accounts`-қа **catalog мен directory-дің ашық интерфейсін (services/selectors) тұтынуға рұқсат етілген**
> (§2), ал `catalog` мен `directory` бір-бірінен және `accounts`-тан толық тәуелсіз қалады. Кері бағытта
> (`catalog.Question.author → accounts.Teacher`) байланыс **тек FK жол-сілтемесімен** жасалады (§4) —
> Python импорты жоқ, сондықтан циклдік тәуелділік пайда болмайды.

**Қай app неге жауапты:**

| App | Қабат | Иеленеді (модельдер) | Беттері |
|-----|-------|----------------------|---------|
| `core` | іргетас | абстракт база (`BaseModel` т.б.), утилита, ортақ виджет. **Concrete модель ЖОҚ** | — |
| `ui` | іргетас | Tailwind, `base.html`, `layouts/`, ортақ `components/` | — |
| `accounts` | негізгі | User, UserSession, Teacher | `/auth/*`, `/account/*` |
| `catalog` | негізгі | Subject, Chapter, Topic, QuestionFormat, FormatVariant, Question, Option | HTMX: format-variants |
| `directory` | негізгі | City, School, Grade | HTMX: school-field |
| `main` | өнім | — | `/` (лендинг) |
| `teaching` | өнім | (болашақ) Kahoot сессия модельдері | `/subjects/*`, мұғалім dashboard |
| `learning` | өнім | (болашақ) прогресс/XP модельдері | `/learn/*` |
| `school` | өнім (болашақ) | Attendance, Timetable, КТЖ/ҚМЖ | `/school/*` |

---

## 2. Тәуелділік ережелері

| Кім | Нені импорттай алады | Нені импорттай АЛМАЙДЫ |
|-----|----------------------|------------------------|
| `core`, `ui` | Django, сыртқы кітапханалар | **ешбір `apps.*`** |
| `catalog`, `directory` | `core` | бір-бірін, `accounts`-ты, кез келген өнім app-ты |
| `accounts` | `catalog`/`directory`-дің **ашық интерфейсі** (`services`/`selectors`) + `core` | `catalog`/`directory`-дің **жабық ішін** (`models`, `forms`); кез келген өнім app-ты |
| өнім app (main/teaching/learning/school) | негізгі домендердің **ашық интерфейсі** (`services`/`selectors`) + `core` | басқа өнім app-ты; кез келген доменнің **жабық ішін** (`models`, `forms`, `_` функциялар) |

**Алтын ереже:** өнім app-тар бір-бірін ешқашан импорттамайды. `catalog` мен `directory` бір-бірінің
Python кодын импорттамайды — олар тек FK жол-сілтемесі арқылы байланысады (§4). `accounts` — ерекшелік:
ол `catalog`/`directory`-дің **ашық интерфейсін** (models емес!) тұтынуға құқылы (себебі жоғарыдағы §1
ескертпесі), бірақ солардың жабық ішіне (models/forms) қатынай алмайды — тек `services`/`selectors`.

---

## 3. Ашық интерфейс: services vs selectors

Әр домен сыртқа тек екі есік арқылы сөйлеседі:

- **`selectors/`** — **оқу** (query). Дерек қайтарады, side effect жоқ.
  Мыс: `get_questions_for_topic(topic_id)`, `get_schools_by_city(city_id)`.
- **`services/`** — **жазу/әрекет** (side effect бар: сақтау, өшіру, email, транзакция).
  Мыс: `create_teacher_user(...)`, `create_question(...)`.

Ережелер:
- Басқа app доменге жүгінгенде **тек** `services`/`selectors` шақырады. Тікелей `Model.objects.filter(...)` жазуға болмайды.
- Модельдер, формалар, шаблондар, `_` префиксті функциялар — **жабық**, оларды басқа app көрмейді.
- Бизнес логика (мыс. «белсенді оқушы деген кім») сол доменнің selector/service-інде тұрады, шақырушыда емес.
- View тек HTTP-ті өңдейді: сұранысты алу → service/selector шақыру → шаблон/фрагмент қайтару.
- Ішкі бағыт бір жақты: `services` → `selectors` → `models`. Айналмалы байланыс жасама.

```python
# ✅ ДҰРЫС
from apps.catalog.selectors import get_questions_for_topic
questions = get_questions_for_topic(topic.id, level='easy')

# ❌ ДҰРЫС ЕМЕС — басқа доменнің жабық ішіне қол салу
from apps.catalog.models import Question
questions = Question.objects.filter(topic_id=topic.id, is_active=True, level='easy')
```

---

## 4. FK ережелері (МАҢЫЗДЫ — circular import тұзағы)

Домендер модельдері бір-біріне сілтейді: `Teacher.subject → catalog.Subject` (accounts→catalog) және
`Question.author → accounts.Teacher` (catalog→accounts). Бұл **циклдік тәуелділік**.

1. **Кросс-app FK әрқашан жол-сілтеме (string) арқылы, ешқашан модель импортымен емес:**
   ```python
   # ❌ Python импорты → circular import
   from apps.catalog.models import Subject
   subject = models.ForeignKey(Subject, ...)

   # ✅ жол-сілтеме → импорт жоқ
   subject = models.ForeignKey('catalog.Subject', on_delete=models.SET_NULL, null=True, blank=True)
   ```

2. **User-ге сілтеме әрқашан `settings.AUTH_USER_MODEL` арқылы** (app ішінде де):
   ```python
   from django.conf import settings
   user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher')
   ```

3. Осылай негізгі домендер бір-бірінің Python кодын импорттамайды → `import-linter`-де **тәуелсіз** бола алады.

4. FK орнату — байланыс жасауға рұқсат. Бірақ басқа доменнің **сұраныс логикасын** өз ішіңде қайта жазба —
   оны сол доменнің selector-ынан шақыр (§3).

---

## 5. App-тың канондық құрылымы

```
apps/<app>/
  __init__.py
  apps.py                 # AppConfig (name='apps.<app>'), ready() — сигналдар осында
  models/                 # ← ӘРҚАШАН ПАКЕТ (бос болса да)
    __init__.py           #   re-export (МІНДЕТТІ, §5.1)
    <domain>.py
  selectors/              # АШЫҚ: оқу
    __init__.py           #   re-export = доменнің ашық беті
    <domain>.py
  services/               # АШЫҚ: жазу/әрекет
    __init__.py           #   re-export = доменнің ашық беті
    <domain>.py
  admin/                  # немесе admin.py
    __init__.py
  forms/                  # немесе forms.py — ЖАБЫҚ (UI-ға тән)
  views/                  # HTTP қабаты (feature бойынша)
  urls/                   # немесе urls.py — бірнеше префикс болса пакет (§7)
  signals.py              # apps.py::ready() ішінде қосылады
  templates/<app>/        # ДОМЕНДІК шаблондар (namespace-пен, §6)
  migrations/
```

### 5.1. `models/` — әрқашан пакет

**Ереже: әр app-та `models.py` емес, `models/` пакеті болады — модель әлі жоқ болса да.**
Себебі: домен уақыт өте өседі, ал `models.py`-ды кейін пакетке айналдыру миграцияға тиеді және
модельдерді қайта көшіруді талап етеді. Ал `services`, `views`, `urls` — кез келген уақытта еркін
қайта ұйымдастырылады, сондықтан олар үшін бұл талап жоқ.

**`models/__init__.py`-де re-export МІНДЕТТІ.** Django app жүктегенде `<app>.models` модулін импорттайды.
Ішкі файлдағы модель сонда импортталмаса — **тіркелмейді, миграцияға түспейді**.

```python
# apps/accounts/models/__init__.py
from .user import User, UserSession
from .teacher import Teacher

__all__ = ['User', 'UserSession', 'Teacher']
```

- Импорт реті маңызды: тәуелдісін кейін қой (`user` → `teacher`).
- Модель әлі жоқ болса: `models/__init__.py` бос қалады (файл бар, мазмұны жоқ).
- `app_label`-ды қолмен жазудың қажеті жоқ — модуль `apps.<app>` пакетінің ішінде болғандықтан Django өзі анықтайды.

### 5.2. Импорт жолы — әрқашан пакет деңгейінде

```python
from apps.accounts.models import User          # ✅ тұрақты
from apps.accounts.models.user import User      # ❌ ішкі құрылымға байланасың
```

Сонда ішкі файлды кейін бөлсең де ешкім сынбайды.

### 5.3. `services/` мен `selectors/` `__init__.py`-і — доменнің ашық беті

Мұндағы re-export — ыңғайлылық емес, **архитектуралық мәлімдеме**: не жарияланса, сол ашық.
Жарияланбаған функция — ішкі.

```python
# apps/accounts/services/__init__.py
from .auth import create_learner_user, create_teacher_user, activate_user, get_user_redirect_url
from .sessions import save_user_session

__all__ = [
    'create_learner_user', 'create_teacher_user', 'activate_user',
    'get_user_redirect_url', 'save_user_session',
]
```

Басқа app `from apps.accounts.services import create_teacher_user` деп жазады, `...services.auth`-қа кірмейді.

### 5.4. Басқа қабаттар

- `admin/__init__.py` — тіркеу submodule-де, `__init__` тек импорттайды: `from . import user, teacher  # noqa: F401`
- `views/`, `forms/`, `urls/` — re-export қажет емес, нақты модуль импортталады.
- `signals.py` — жалғыз файл жеткілікті. `apps.py::ready()` ішінде: `from . import signals  # noqa: F401`
- App **`INSTALLED_APPS`-қа тіркеледі** (`apps.<app>.apps.<App>Config`). Тіркелмесе — `ready()`, сигналдар, миграциялар жүктелмейді.
- Шаблондар әрқашан `templates/<app>/...` деп namespace-пен.

---

## 6. UI ережелері (дизайн-жүйе vs домендік шаблон)

Екі бөлек нәрсе:

- **Дизайн-жүйе / құрал-жабдық** → `ui`-де қалады: Tailwind көзі мен build (`ui/static_src`),
  компиляцияланған CSS, `base.html`, `layouts/` (`auth_layout`, `main_layout`, `teacher_layout`),
  **ортақ** `components/` (`_messages`, `_confirm_modal`, `select`, `checkbox`, `radio`).
- **Домендік шаблон** → сол app-та: `apps/<app>/templates/<app>/...`

Ережелер:
- `ui` домендік шаблонды **білмейді** (ui → домен ❌).
- Домен ортақ `ui`-ды қолданады (домен → ui ✅): `{% extends "layouts/teacher_layout.html" %}`, `{% include "components/select.html" %}`.
- Компонент ортақ болса (форма элементі, modal, toast) → `ui/components/`. Нақты доменнің partial-і (`_subject_info.html`) → сол app-та.
- `TEMPLATES['DIRS'] = [BASE_DIR / 'ui/templates']` **және** `APP_DIRS=True` — екеуі де қосулы қалады.
- Домендік шаблонды namespace-пен шақыр: `render(request, 'teaching/subject/detail.html', ...)`.
- Tailwind сканері домендік шаблондарды да оқуы керек. `ui/static_src/tailwind.config.js`:
  ```js
  content: [
    '../templates/**/*.html',
    '../../apps/**/templates/**/*.html',   // ← домендік шаблондар
  ]
  ```
  Өзгерткен соң: `cd ui/static_src && npm run build`.

---

## 7. URL — бөлек өлшем

App пен URL — екі бөлек нәрсе. **Бір app бірнеше URL префиксіне қызмет ете алады, әрі префикс app атымен бірдей болуы шарт емес.**

- Мыс: `accounts` app-ы әрі `/auth/*` (login, register), әрі `/account/*` (profile, edit, security) беттерін береді.
- **Бет қай app-та?** — оны істейтін **рөл** емес, ол өзгертетін **дерек/домен** шешеді.
  «Мұғалім профилін өңдейді» беті → `accounts` (User дерегі), `teaching` емес.
- «Dashboard» деген — URL префиксі емес, **layout + навигация** ұғымы.
  Рөлдік қол жеткізу декоратор/permission-мен шешіледі, app бөлумен емес.
- Бірнеше префикс керек болса, app ішінде `urls/` пакеті болады (`urls/auth.py`, `urls/account.py`),
  ал `config/urls.py` соларды бөлек `include` етеді.

---

## 8. Атау конвенциялары

- «education» сөзін домен атауы ретінде **қолданба** — ол екіұшты.
  Анықтамалық дерек (City/School/Grade) → `directory`. Мұғалім бағыты → `teaching`. Оқушы бағыты → `learning`.
- Қазіргі `directory.School` (анықтамалық: city + name, мұғалімнің мектебі) мен болашақ SIS тенанты **бөлек**.
  Тенант-мекеме болашақта `accounts.Organization` деп аталады. Шатастырма.
- «Жүйелік/серіктес оқытушы» ұғымы кодта `Teacher.Type.PARTNER`-ге сәйкес.

---

## 9. Код конвенциялары (жобаның қазіргі стилі — сақта)

- Барлық нақты модель `core.models.BaseModel` (немесе `TimeStampedModel`/`ActiveModel`) абстракттарынан мұра алады.
- **Soft-delete:** жою деген `is_active = False`; сұраныстар `.filter(is_active=True)`. Шынымен `delete()` жасама (арнайы айтылмаса).
- Өрісті нүктелі жаңартқанда `save(update_fields=[...])` қолдан.
- **i18n:** қолданушыға көрінетін мәтін — `gettext_lazy` (кодта, бастапқы тіл `en`) немесе `{% translate %}` (шаблонда).
  Жаңа/көшкен жолдардан кейін `makemessages` → `.po`-дағы `#, fuzzy` мен бос `msgstr`-ды түзет → `compilemessages`.
- **HTMX:** reload-сыз CRUD. OOB toast (`components/_messages.html`), қажет болса `HX-Retarget`/`HX-Reswap`/`HX-Trigger`.
- Логин email немесе username бойынша (`EmailOrUsernameBackend`).
- Rich-text (сұрақ мәтіні, сипаттама) — жобадағы дайын `oiq-ckeditor-5` бандлы (`RichTextTextarea` виджеті).

---

## 10. import-linter контракты

Шекараны машина қорғайды. Жоба түбіндегі `.importlinter`:

```ini
[importlinter]
root_packages =
    core
    apps

[importlinter:contract:core-is-foundation]
name = core ешбір app-ты импорттамайды
type = forbidden
source_modules =
    core
forbidden_modules =
    apps

[importlinter:contract:foundation-independent]
name = catalog және directory бір-бірінен тәуелсіз (FK тек жол-сілтеме)
type = independence
modules =
    apps.catalog
    apps.directory

[importlinter:contract:products-independent]
name = өнім app-тар бір-бірін импорттамайды
type = independence
modules =
    apps.main
    apps.teaching
    apps.learning
    # apps.school  ← SIS жасалғанда қос

[importlinter:contract:layers]
name = тәуелділік тек төмен қарай
type = layers
layers =
    apps.main | apps.teaching | apps.learning
    apps.accounts
    apps.catalog | apps.directory
    core
```

> `accounts` бөлек қабатта (§1 ескертпесі): ол `catalog`/`directory`-дің ашық интерфейсін тұтынады,
> ал солар `accounts`-ты да, бір-бірін де импорттамайды.

> `apps.school` әлі жоқ. Ол жасалғанда `products-independent` пен `layers` контрактына қос.
> Жоқ модульді контрактқа жазсаң `lint-imports` қате береді.

Тексеру: `lint-imports`. Контракт бұзылса — қате; оны кодты түзетіп шеш, контрактты әлсіретіп «жасырма».

> `import-linter` тек **импорт бағытын** тексереді. «Тек services/selectors арқылы» деген тәртіп (§3) —
> code review деңгейінде ұсталады.

---

## 11. ЖАСАМА (қатаң тыйым)

- ❌ Concrete модельді `core`-ға қоспа. Модель әрқашан өз доменінде.
- ❌ `models.py` жалғыз файл жасама — әрқашан `models/` пакеті (§5.1).
- ❌ `models/__init__.py`-де re-export жасауды ұмытпа — әйтпесе модель тіркелмейді.
- ❌ Бір доменнің моделін екінші доменде тікелей импорттама (FK — жол-сілтеме, §4).
- ❌ Өнім app-ты басқа өнім app-тан импорттама.
- ❌ Домендік шаблонды `ui`-ге қоспа; `ui`-ден домендік шаблонды `include` жасама.
- ❌ Бизнес логиканы view немесе шаблонға жазба — `services`/`selectors`-ке қой.
- ❌ Дерек бар DB-де миграцияны backup-сыз жасама.
- ❌ Ережеге қайшы тапсырманы «айналып өтіп» орындама — қайшылықты хабарла.
