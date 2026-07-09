# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠ Ең маңызды ереже

**Кез келген құрылымдық немесе код өзгерісінен БҰРЫН `prompts/RULES.md` файлын оқы және оны қатаң сақта.**
Ол — жобаның архитектура конституциясы (қабаттар, тәуелділік бағыты, `services`/`selectors` шекарасы,
FK ережелері, URL/UI ережелері). Егер тапсырма сол ережелерге қайшы келсе — орындама, қайшылықты хабарла.

---

## Жоба туралы

OIQ — мектеп оқушылары мен оқытушыларына арналған қазақ тіліндегі геймификациялық оқыту платформасы.

Екі өнім бағыты бар:
1. **Оқытушы бағыты** (`teaching`) — Kahoot стилі: сұрақ құрастыру (authoring) және тірі ойын сессиялары.
   Қатысушылар (оқушылар) сессияға аутентификациясыз, кодпен қосылады.
2. **Оқушы бағыты** (`learning`) — Duolingo / Brilliant.org стилі: аутентификацияланған оқушы өз бетімен
   пәндік бағытты кезең-кезеңімен өтеді (прогресс, ұпай, ЖИ-көмекші).

Болашақта үшінші бағыт қосылады: **SIS** (`school`) — мектептің администрациялық/құжаттамалық жүйесі
(қатысу, кесте, КТЖ/ҚМЖ, мекеме workspace-і). Ол `school.oiq.kz/<org>/` жолымен, субдоменсіз жасалады.

**Стек:** Django 6 + PostgreSQL, admin — `django-unfold`, фронтенд — Tailwind CSS 4 + HTMX + Alpine.js +
Lucide иконкалары, rich-text — CKEditor 5 (KaTeX қосылған кастомды бандл). Деплой — Ubuntu + Gunicorn + Nginx.
Интерфейс негізгі тілі — қазақша (`kk`), `ru`/`en` локализациясы бар.

---

## Архитектура: модульді монолит

Бір Django проекті, бір `settings.py`, бір `User`, бір деплой — бірақ ішінде **таза шекаралы домен модульдері**.
Шекара кодтың ішінде (Python модулі + `services`/`selectors` қабаты), желіде емес.

### Төрт қабат (тәуелділік тек төмен қарай)

```
ӨНІМ:      apps.teaching · apps.learning · apps.main   (болашақта apps.school)
              ↓ тұтынады (тек services/selectors арқылы)
ACCOUNTS:  apps.accounts
              ↓ тұтынады (тек services/selectors арқылы)
НЕГІЗГІ:   apps.catalog · apps.directory   (бір-бірінен тәуелсіз)
              ↓ қолданады (мұра, утилита, layout)
ІРГЕТАС:   core (абстракт модель, утилита) · ui (дизайн-жүйе)
```

> `accounts` бөлек қабатта: `Teacher` (accounts) қала/мектепті (`directory`) және пәнді (`catalog`) FK
> арқылы сілтейді, сондықтан тіркелу/профиль формасында сол таңдау тізімдерін көрсету үшін `accounts`-қа
> `catalog`/`directory`-дің **ашық интерфейсін** (services/selectors, models емес) тұтынуға рұқсат
> етілген. `catalog` мен `directory` өздері бір-бірінен және `accounts`-тан толық тәуелсіз.

| App | Қабат | Иеленеді (модельдер) | Беттері |
|-----|-------|----------------------|---------|
| `core` | іргетас | **concrete модель ЖОҚ** — тек `BaseModel`/`TimeStampedModel`/`ActiveModel` абстракттары, утилита, ортақ виджет | — |
| `ui` | іргетас | — | Tailwind, `base.html`, `layouts/`, ортақ `components/` |
| `accounts` | негізгі | `User`, `UserSession`, `Teacher` | `/auth/*`, `/account/*` |
| `catalog` | негізгі | `Subject`, `Chapter`, `Topic`, `QuestionFormat`, `FormatVariant`, `Question`, `Option` | HTMX: format-variants |
| `directory` | негізгі | `City`, `School`, `Grade` | HTMX: school-field |
| `teaching` | өнім | (болашақ) Kahoot сессия модельдері | `/subjects/*`, мұғалім dashboard |
| `learning` | өнім | (болашақ) прогресс/XP модельдері | `/learn/*` |
| `main` | өнім | — | `/` (лендинг) |

### Негізгі ережелер (толығы — `prompts/RULES.md`)

- **Ашық интерфейс:** домен сыртқа тек `selectors.py` (оқу, side effect жоқ) және `services.py` (жазу/әрекет)
  арқылы сөйлеседі. Басқа app-тан `Model.objects.filter(...)` жазуға болмайды.
- **Жабық іші:** `models.py`, `forms/`, шаблондар, `_` префиксті функциялар — басқа app көрмейді.
- **Кросс-app FK — әрқашан жол-сілтеме** (`'catalog.Subject'`, `'accounts.Teacher'`, `'directory.Grade'`)
  және User-ге `settings.AUTH_USER_MODEL`. Модель импорты циклдік тәуелділік тудырады.
- **Өнім app-тар бір-бірін ешқашан импорттамайды.** Негізгі домендер де бір-бірінің Python кодын импорттамайды.
- **Бет қай app-та?** — оны істейтін *рөл* емес, ол өзгертетін *дерек/домен* шешеді.
  Мысалы «мұғалім профилін өңдейді» беті → `accounts` (User дерегі), `teaching` емес.
- **URL — бөлек өлшем:** бір app бірнеше префикске қызмет етеді (`accounts` → `/auth/*` және `/account/*`).
- Шекараны `import-linter` қорғайды: `lint-imports` (конфиг — `.importlinter`).

---

## App-тың канондық құрылымы

```
apps/<app>/
  apps.py                 # AppConfig (name='apps.<app>'), ready() — сигналдар осында
  models/                 # ← ӘРҚАШАН ПАКЕТ (бос болса да), __init__.py-де re-export
  selectors/               # АШЫҚ: оқу, __init__.py-де re-export
  services/                # АШЫҚ: жазу/әрекет, __init__.py-де re-export
  forms/  views/  urls/   # urls — бірнеше префикс болса пакет
  admin/  signals.py
  templates/<app>/        # ДОМЕНДІК шаблондар (namespace-пен)
  migrations/
```

Толығы — `prompts/RULES.md` §5. Жаңа app-ты `INSTALLED_APPS`-қа тіркеуді ұмытпа — әйтпесе `ready()`,
сигналдар, миграциялар жүктелмейді.

---

## URL маршруттау

`config/urls.py` — `i18n_patterns` арқылы тілге қарай префикс (`prefix_default_language=True`: `/kk/...`, `/ru/...`, `/en/...`).

```python
path('admin/',     admin.site.urls),
path('core/',      include('core.urls')),                    # ckeditor upload
path('',           include('apps.main.urls')),               # лендинг
path('auth/',      include('apps.accounts.urls.auth')),      # login, logout, register
path('account/',   include('apps.accounts.urls.account')),   # profile, edit, settings, security
path('subjects/',  include('apps.teaching.urls')),           # authoring + мұғалім dashboard
path('learn/',     include('apps.learning.urls')),           # оқушы dashboard
path('catalog/',   include('apps.catalog.urls')),            # HTMX: format-variants
path('directory/', include('apps.directory.urls')),          # HTMX: school-field
```

---

## Рұқсаттар мен рөлдер

`apps.accounts.models.User.Role`: `ADMIN`, `TEACHER`, `LEARNER`.
`AUTH_USER_MODEL = 'accounts.User'`.

Аутентификация backend-тері (`AUTHENTICATION_BACKENDS`): стандартты `ModelBackend` және
`apps.accounts.backends.EmailOrUsernameBackend` (логин email немен username бойынша).

`apps/accounts/decorators.py`:
- `anonymous_required` — авторизацияланған қолданушыны рөліне сай dashboard-қа бағыттайды.
- `role_required(*roles)` және оның негізінде `learner_required`, `teacher_required`, `admin_required`.
- `partner_teacher_required` — `Teacher.Type.PARTNER` («жүйелік/серіктес оқытушы») мұғалімдерге.

Рөл бойынша redirect: `apps.accounts.services.get_user_redirect_url(user)`.

> Рөлдік қол жеткізу **декоратормен** шешіледі, app бөлумен емес. «Dashboard» — URL префиксі емес,
> layout + навигация ұғымы.

---

## Шаблондар (templates)

Екі бөлек нәрсе (`prompts/RULES.md` §6):

- **Дизайн-жүйе → `ui/templates/`:** `base.html` (Tailwind, htmx/Alpine/Lucide, toast),
  `layouts/` (`auth_layout`, `main_layout`, `teacher_layout`),
  **ортақ** `components/` (`_messages`, `_confirm_modal`, `select`, `checkbox`, `radio`).
- **Домендік шаблон → сол app-та:** `apps/<app>/templates/<app>/...`

Ережелер:
- `ui` домендік шаблонды білмейді. Домен ортақ `ui`-ды қолданады:
  `{% extends "layouts/teacher_layout.html" %}`, `{% include "components/select.html" %}`.
- `TEMPLATES['DIRS'] = [BASE_DIR / 'ui/templates']` **және** `APP_DIRS=True` — екеуі де қосулы.
- Домендік шаблонды әрқашан namespace-пен шақыр: `render(request, 'teaching/subject/detail.html', ...)`.
- Tailwind сканері домендік шаблондарды да оқуы керек — `tailwind.config.js`-тегі `content`-те
  `'../../apps/**/templates/**/*.html'` болуы шарт.

**UI ескертпелері:**
- Базалық HTML `select` ыңғайсыз — дайын кастомды компонент бар:
  `{% include "components/select.html" with field=form.field_name %}` (Alpine.js dropdown).
- CRUD әрекеттері reload-сыз (HTMX/Alpine), нәтижесінде animate toast шығады (`components/_messages.html`,
  OOB swap). Қажет болса `HX-Retarget`/`HX-Reswap`/`HX-Trigger` тақырыптары.
- Түстер мен мәндер айнымалы түрінде `styles.css`-те. Платформа адаптивті (мобиль/планшет/десктоп).

---

## Код конвенциялары

- Барлық нақты модель `core.models` абстракттарынан мұра алады (`BaseModel` = `TimeStampedModel` + `ActiveModel`).
- **Soft-delete:** жою деген `is_active = False`; сұраныстар `.filter(is_active=True)`.
  Шынымен `delete()` жасама (арнайы айтылмаса).
- Өрісті нүктелі жаңартқанда `save(update_fields=[...])`.
- Бизнес логика — `services`/`selectors`-та. View тек HTTP-ті өңдейді (сұраныс → service шақыру → шаблон).
- Rich-text өрістер (`Question.text`, `Chapter.description`) — `core.forms.RichTextTextarea` (oiq-ckeditor).

---

## Жиі қолданылатын командалар

### Django

```bash
source env/bin/activate          # виртуалды орта env/ ішінде

python manage.py runserver
python manage.py migrate
python manage.py makemigrations
python manage.py createsuperuser
python manage.py collectstatic

lint-imports                     # import-linter: архитектура шекарасын тексеру
```

`config/settings.py` барлық құпия мәндерді `.env`-тен (`python-decouple`) оқиды:
`SECRET_KEY`, `DB_*`, `ALLOWED_HOSTS`, `EMAIL_*`, `SITE_NAME`, `ADMIN_URL`, `WEBSITE_URL`,
`ANTHROPIC_API_KEY`, `QUESTION_IMPORT_MODEL`.

### Фронтенд (Tailwind CSS)

`ui/static_src/` — Tailwind мен CKEditor бандлының бастапқы код каталогы (`package.json` осында).

```bash
cd ui/static_src
npm install
npm run dev      # watch режимі (development)
npm run build    # production, минификациямен → ../static/css/dist
```

### CKEditor бандлы

CKEditor 5 + KaTeX (математика плагині) кастомды Vite конфигурациясы арқылы IIFE бандл ретінде құрастырылады:

```bash
cd ui/static_src
npm run build:ckeditor   # vite.ckeditor.config.js → ../static/js/oiq-ckeditor/
```

Бастапқы код: `ui/static_src/src/js/oiq-ckeditor.js` → нәтиже: `oiq-ckeditor.bundle.js` + `ui.css`.
`vite.ckeditor.config.js`-те `@ckeditor/*` мен `@isaul32/*` пакеттеріндегі SVG иконкаларды raw-string
ретінде импорттайтын кастомды плагин бар (CKEditor `IconView` SVG-ні DOMParser арқылы парстайды, сондықтан
Vite-тің әдепкі asset-URL/base64 түрлендіруі жұмыс істемейді).

### Тесттер

Жобада әзірге тесттер жоқ. Қосу қажет болса — Django-ның стандартты `python manage.py test`.

---

## Админ панель (Unfold)

`config/settings.py`-дегі `UNFOLD` сөздігі сайдбар навигациясын, түс палитрасын (primary indigo) және
логин бетінің баннерін баптайды.

Жаңа модель қосқанда оны `UNFOLD['SIDEBAR']['navigation']` тізіміне де қосу керек —
`_('...')` атауы мен `reverse_lazy('admin:<app_label>_<model>_changelist')` сілтемесімен, әйтпесе сайдбарда көрінбейді.

> App белгісі (`app_label`) — жаңа құрылымда `accounts`, `catalog`, `directory`
> (мыс. `admin:catalog_question_changelist`), бұрынғы `core` емес.

`core/admin/base.py`-да екі ортақ миксин бар:
- `BaseModelAdmin` — `is_active`/`created_at`/`updated_at` өрістерін "General information" fieldset-іне қосады.
- `LinkedAdminMixin` — байланысты объектіге сілтеме шығаратын хелпер (`admin_link`/`parent_link`).

---

## AI арқылы сұрақ импорты

`apps/teaching/services/question_import.py` — мұғалім жүктеген `.docx` файлдан сұрақтарды шығару:
`soffice` арқылы docx→pdf → Claude API (`ANTHROPIC_API_KEY`, JSON schema, `QUESTION_IMPORT_MODEL`) →
суреттерді `python-docx` арқылы ретімен шығарып сақтау → `{{img:N}}` плейсхолдерлерін ауыстыру.

AI/docx логикасы `teaching`-те, ал сұрақты **сақтау** `apps.catalog.services.create_question(...)` арқылы
(домен шекарасы: дерек — catalog-та).

Талаптар: жүйеде `soffice` (LibreOffice) орнатылған болуы керек.

---

## Аударма (i18n)

`USE_I18N = True`, `LANGUAGES = (kk, ru, en)`, `LOCALE_PATHS = [BASE_DIR / 'locales']`,
`django-modeltranslation` орнатылған (модель өрістерінің аудармасын `translation.py`-да
`modeltranslation.translator.register` арқылы тіркеу).

Кодта бастапқы тіл — **ағылшынша**: `gettext_lazy('...')`. Шаблондарда: `{% translate '...' %}`.

Жаңа жолдарды `.po`-ға қосу:

```bash
python manage.py makemessages -l kk -l ru --no-obsolete --ignore=env/* --ignore=ui/static_src/*
```

`--ignore` флагтары **міндетті**: олар болмаса `makemessages` `env/` (виртуалды орта) мен
`ui/static_src/` (node_modules) ішін де сканерлеп, `.po`-ға мыңдаған бөгде жол қосып кетеді.

`.po` файлдарды толтырғаннан кейін:

```bash
python manage.py compilemessages -l kk -l ru
```

**Ескерту:** `makemessages` жаңа жолды бұрынғы ұқсас аудармаға автоматты сәйкестендіріп (`#, fuzzy` деп
белгілеп) қоя береді — бұл көбіне **қате** аударма. Әр `makemessages`-тен кейін `.po`-дағы `#, fuzzy` пен
бос `msgstr ""` жолдарды тауып, дұрыс аудармамен ауыстырып, `fuzzy` белгісін алып таста — әйтпесе
`compilemessages` қате аудармамен компиляция жасайды.

---

## Деректер қоры туралы ескерту

Базада нақты дерек бар. Модель құрылымын өзгерту/миграция жасағанда:
- Алдымен `pg_dump` арқылы backup ал, `media/` бумасын да көшір.
- Ешқашан backup-сыз миграция жасама.
