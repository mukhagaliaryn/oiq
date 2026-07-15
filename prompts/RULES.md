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
    main/        # ӨНІМ — лендинг + ортақ auth (login/register/logout)
    teaching/    # ӨНІМ
    learning/    # ӨНІМ
    school/      # ӨНІМ — мектеп жүйесі (SIS), бөлек субдомен (school.oiq.kz)
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
| `accounts` | негізгі | User, UserSession, Teacher | **бет ЖОҚ** — тек identity `services`/`selectors`/`decorators` (§1.1) |
| `catalog` | негізгі | Subject, Chapter, Topic, QuestionFormat, FormatVariant, Question, Option | HTMX: format-variants |
| `directory` | негізгі | City, School, Grade | HTMX: school-field |
| `main` | өнім | — | `/` (лендинг) + ортақ `/auth/*` (login/register/logout, §1.1) |
| `teaching` | өнім | (болашақ) Kahoot сессия модельдері | `/teaching/*` (authoring, dashboard, `/teaching/account/*`) |
| `learning` | өнім | (болашақ) прогресс/XP модельдері | `/learning/*` (dashboard, `/learning/account/`) |
| `school` | өнім | `Organization`, `Membership` (мектеп-тенант, мүшелік) | `school.oiq.kz` (бөлек субдомен, §7.1): `/`, `/<org>/*` |

### 1.1. Identity vs auth vs account — үш бөлек орын

`accounts` **ешбір бетті иеленбейді** — ол таза identity домені: `User`/`Teacher` модельдері + `services`
(`change_password`, `update_email`, `set_avatar`, `update_basic_info`, `deactivate_account`,
`create_learner_user`, `create_teacher_user`, `create_external_user`, `get_user_redirect_url` т.б.) +
`selectors` + `decorators` (`teacher_required`, `learner_required`, `partner_teacher_required`...).
Басқа app-тар осы **сервистерді шақырады**, `accounts`-тың өз бет/шаблоны жоқ.

- **Тіркелу (register) — тек `main`-де, бір рет, `oiq.kz`-те.** Тіркелу нүктесі біреу (SCHOOL_SYSTEM.md
  принципі): `main` `accounts.services`-ті шақырып, `User` жасайды. School мүшелері өздігінен тіркелмейді —
  оларды сол ұйымның `school.OrgRole.SYS_ADMIN`-і қосады (§1.2, TASK-03).
- **Login — хостқа қарай екі бөлек нүкте, бірақ бір `accounts` identity-мен.** `main:login` (`oiq.kz`) —
  `teacher`/`learner`/`admin` `account_type`-ке; `school:login` (`school.oiq.kz`) — тек `SCHOOL_USER`-ге
  (басқа `account_type` кірсе — `AuthenticationForm.confirm_login_allowed` қатесі, кіргізбейді). Екеуі де
  бір `User` кестесін, бір parolь/сессияны қолданады — тек **қай форма қай account_type-ты қабылдайды**
  соны шектейді. Logout те дәл солай хостқа тән (`main:logout`, `school:logout`).
- **Аккаунт/профиль беті — әр өнімде бөлек.** `teaching` → `/teaching/account/*` (мұғалім профилі: Teacher
  дерегі), `learning` → `/learning/account/` (оқушы профилі), `school` → `<org>/account/` (мүше профилі,
  ұйымдағы рөлдер). Әрқайсысы өз UI-ымен, бірақ жазу/валидация логикасы **тек `accounts.services`-те**
  (бір көзден) — форма жеңіл, сервис валидациялап, `ValidationError` көтереді.

**Неге бөлек:** «Бет қай app-та?» ережесі (§7) бойынша auth (User дерегін жасау/тексеру) — `accounts`-тың
жауапкершілігі, бірақ оның **презентациясы** ортақ кіру нүктесі болғандықтан `main`-де; ал профиль/аккаунт
беті — өнімге тән (мұғалім/оқушы/мектеп мүшесі әртүрлі дерек көреді), сондықтан әр өнімде.

### 1.2. «Рөл» — үш ортогональ (тәуелсіз) ұғым

Бұларды шатастырма — үшеуі бір-біріне кедергі жасамайды, бір адам үшеуін де бір мезгілде ұстай алады:

| Ұғым | Қайда | Мәні | Саны |
|------|-------|------|------|
| **Аккаунт түрі** | `accounts.User.account_type` | платформаға кім болып тіркелді (`admin`/`teacher`/`learner`/`school_user`) — қай хостқа/dashboard-қа бағытталады | глобал, біреу |
| **Мұғалім қабілеті** | `accounts.Teacher.type` | `regular` (сыртқы) / `partner` (catalog-қа контент сала алады) | біреу |
| **Ұйымдағы рөл** | `school.Membership.roles` | директор/жүйелік администратор/сынып жетекшісі/пән мұғалімі/оқушы/ата-ана... | мектепке қатысты, **бірнешеу** |

`User.account_type = SCHOOL_USER` болса, ол қолданушы `teacher_required`/`learner_required`
декораторларымен автоматты бөгеледі (§1.1-дегі `teaching`/`learning`-ге кіре алмайды) — қосымша тексеру
керек емес, себебі декоратор дәл `account_type`-ты тексереді. `get_user_redirect_url` (`accounts.services`)
`SCHOOL_USER`-ды `school.oiq.kz`-ке (cross-host, `core.utils.urls.build_absolute_url` арқылы) бағыттайды.

`school.services.register_and_add_member(...)` жаңа қолданушыны әрқашан `account_type='school_user'`
етіп жасайды (`accounts.services.create_external_user`), `Teacher` профилін жасамайды — себебі мектеп
мүшесі мен `teaching` өнімінің сыртқы мұғалімі **бөлек ұғым**.

---

## 2. Тәуелділік ережелері

| Кім | Нені импорттай алады | Нені импорттай АЛМАЙДЫ |
|-----|----------------------|------------------------|
| `core`, `ui` | Django, сыртқы кітапханалар | **ешбір `apps.*`** |
| `catalog`, `directory` | `core` | бір-бірін, `accounts`-ты, кез келген өнім app-ты |
| `accounts` | `catalog`/`directory`-дің **ашық интерфейсі** (`services`/`selectors`) + `core` | `catalog`/`directory`-дің **жабық ішін** (`models`, `forms`); кез келген өнім app-ты |
| өнім app (main/teaching/learning/school) | `accounts` пен негізгі домендердің **ашық интерфейсі** (`services`/`selectors`/`decorators`) + `core` | басқа өнім app-ты; кез келген доменнің **жабық ішін** (`models`, `forms`, `_` функциялар) |

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
- **Жалпы принцип:** локалды компонент/partial (тек бір app қолданады) — әрқашан сол
  `apps/<app>/templates/<app>/**` ішінде, ешқашан `ui`-де емес. Global (бірнеше app/дизайн тіл
  қолданатын) компонент/layout қана `ui`-ге шығады. `ui` өзі ішінде де бір біркелкі жиын емес —
  дизайн тіл бөлек болса (мыс. `school` vs `teaching`/`learning`/`main`), `ui/templates/components/`
  сол дизайн тілдер бойынша namespace-пен бөлінеді (толығы — §6.1).
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

### 6.1. `school` — екінші дизайн-тіл (shadcn-стиль)

`school` (`school.oiq.kz`) `teaching`/`learning`/`main`-нің дөңгеленген (rounded-2xl), Phosphor-негізді
дизайн тілін **қайталамайды** — ол dashboard/workspace admin, сондықтан **shadcn UI**-ге ұқсас (тар
radius, нәзік border, дерекке бай) стильде жасалады. Ортақ болатыны — **тек түс жүйесі**
(`ui/static_src/src/styles.css`-тегі `@theme`: `--color-brand`, `--color-neutral-*`,
`--color-success/danger/warning-*` т.б.) және иконка жиынтығы (Phosphor — жаңа тәуелділік қосылмайды).
Button, input, select, nav, card секілді блоктар — екеуінде де бөлек стильде.

Орналасу — жоғарыдағы жалпы принциптің нақты мысалы (**global → `ui`, локал → app өзінде**), бірақ
shadcn-стиль блоктар teaching/learning-тің ортақ `components/`-іне араласпайды — бөлек namespace-те:

- `ui/templates/layouts/school_layout.html` — бар (sidebar + workspace layout).
- `ui/templates/components/school/` — school-ға тән button/input/select/nav/card т.б. partial-дар
  (мыс. `components/school/button.html`). Тек school шаблондары қолданады
  (`{% include "components/school/button.html" %}`), teaching/learning оларды импорттамайды.
- Ортақ `components/` (`_messages`, `_confirm_modal`, `select`, `checkbox`, `radio`) — тек
  teaching/learning/main дизайн тіліне тиесілі, `school` оларды қолданбайды (форма/nav элементінің
  өз shadcn-стиль баламасы болады).
- `apps/school/templates/school/...` — бұрынғысынша домендік (бет-контент) шаблондар, §6 ережесі
  бойынша.

School беттерінің дизайны жеке-жеке `TASK` ретінде бекітіледі.

---

## 7. URL — бөлек өлшем

App пен URL — екі бөлек нәрсе. **Бір app бірнеше URL префиксіне қызмет ете алады, әрі префикс app атымен бірдей болуы шарт емес.**

- Мыс: `main` app-ы әрі `/` (лендинг), әрі `/auth/*` (login, register, logout) беттерін береді (§1.1).
- **Бет қай app-та?** — оны істейтін **рөл** емес, ол өзгертетін **дерек/домен** шешеді.
  «Мұғалім профилін өңдейді» беті → `teaching` (мұғалім аккаунт аймағы, §1.1), «жаңа User жасайды/
  аутентификациялайды» беті → презентация ортақ болғандықтан `main`-де (логика — `accounts.services`).
- «Dashboard» деген — URL префиксі емес, **layout + навигация** ұғымы.
  Рөлдік қол жеткізу декоратор/permission-мен шешіледі, app бөлумен емес.
- Бірнеше префикс керек болса, app ішінде `urls/` пакеті болады.
  **Ескерту (белгілі gotcha):** пакет ішіндегі әр submodule-де **бөлек** `app_name` қоюға БОЛМАЙДЫ —
  Django-да екінші submodule-дің URL аттары `reverse()`-те табылмай қалады (`namespace_dict` тек
  біріншісін сақтайды, тек W005 warning шығады, қате емес — сондықтан байқалмай қалуы оңай). Дұрысы:
  `app_name` тек пакеттің `__init__.py`-інде бір рет, ішінде submodule-дерді `include()` ет:
  ```python
  # apps/school/urls/__init__.py
  from django.urls import include, path
  from . import landing, workspace

  app_name = 'school'          # ← тек осында, бір рет
  urlpatterns = [
      path('', include(landing)),        # landing.py-де app_name ЖОҚ
      path('<slug:org>/', include(workspace)),  # workspace.py-де де ЖОҚ
  ]
  ```

### 7.1. Субдомен маршруты (`school.oiq.kz`)

Бір Django процесі, бір DB, бір сессия — тек хостқа қарап `urlconf` ауысады (монолит, gateway/token
керек емес):

- `config/urls_main.py` — `oiq.kz` (`main`, `teaching`, `learning`, `catalog`, `directory` HTMX-і).
- `config/urls_school.py` — `school.oiq.kz` (тек `apps.school.urls`).
- `settings.ROOT_URLCONF = 'config.urls_main'` — әдепкі/fallback.
- `config/middleware.py::HostURLConfMiddleware` — хост `school.`-мен басталса `request.urlconf =
  'config.urls_school'` қояды. **`LocaleMiddleware`-ден (`CookieLocaleMiddleware`) БҰРЫН** тұруы керек.
- `settings.BASE_DOMAIN`/`SCHOOL_HOST` — `.env`-тен (`BASE_DOMAIN`, dev әдепкісі `oiq.lvh.me` — DNS-тен
  автоматты `127.0.0.1`-ге шешіледі, `/etc/hosts` керек емес). `SESSION_COOKIE_DOMAIN`/`CSRF_COOKIE_DOMAIN`
  `.{BASE_DOMAIN}` — сондықтан сессия екі хостта да ортақ (қайта кіру керек емес).
- `reverse()` тек **ағымдағы** `request.urlconf` ішінде жұмыс істейді. Хостаралық сілтеме (мыс. `main`-нен
  `school`-ге, немесе керісінше — аноним `school.oiq.kz`-ке келгенде `oiq.kz/auth/login/`-ге бағыттау)
  керек болса — `core.utils.urls.build_absolute_url(host, viewname, urlconf=..., ...)` хелперін қолдан.
- `apps/school/middleware.py::OrganizationMiddleware` — `HostURLConfMiddleware`-ден және
  `AuthenticationMiddleware`-ден **КЕЙІН**. `<slug:org>` view kwarg-ын `process_view`-де ұстап,
  `Organization`/`Membership`-ті `request`-ке қояды (мүше емес → 404, аноним → cross-host login redirect).

---

## 8. Атау конвенциялары

- «education» сөзін домен атауы ретінде **қолданба** — ол екіұшты.
  Анықтамалық дерек (City/School/Grade) → `directory`. Мұғалім бағыты → `teaching`. Оқушы бағыты → `learning`.
- `directory.School` (анықтамалық: city + name, мұғалімнің мектебі) мен `school.Organization` (SIS
  тенанты — slug, workspace, мүшелік) **бөлек** модельдер, шатастырма. `Organization.school` FK арқылы
  анықтамалыққа сілтейді (§1 жоғарыдағы FK ережесі).
- «Жүйелік/серіктес оқытушы» ұғымы кодта `Teacher.Type.PARTNER`-ге сәйкес — бұл `school.OrgRole.SYS_ADMIN`
  (мектептің IT-әкімшісі, ұйымдағы рөл) ұғымымен шатастырылмайды (§1.2).

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
    apps.school

[importlinter:contract:layers]
name = тәуелділік тек төмен қарай
type = layers
layers =
    apps.main | apps.teaching | apps.learning | apps.school
    apps.accounts
    apps.catalog | apps.directory
    core
```

> `accounts` бөлек қабатта (§1 ескертпесі): ол `catalog`/`directory`-дің ашық интерфейсін тұтынады,
> ал солар `accounts`-ты да, бір-бірін де импорттамайды.

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
- ❌ **Жаңа/өзгерген `gettext_lazy(...)` немесе `{% translate %}` жолын `.po`-ға аудармай қалдырма.**
  Сол тапсырма/commit ішінде дереу орында (§9): `makemessages -l kk -l ru --no-obsolete
  --ignore=env/* --ignore=ui/static_src/*` → шыққан `#, fuzzy` мен бос `msgstr ""`-ды **нақты**
  kk/ru аудармасымен ауыстыр (ескі fuzzy-сәйкестік көбіне қате аударма болады, тексерместен қалдырма) →
  `compilemessages -l kk -l ru`. Кейінге қалдырылған аударма — техникалық борыш емес, **бітпеген жұмыс**.
- ❌ Ережеге қайшы тапсырманы «айналып өтіп» орындама — қайшылықты хабарла.
