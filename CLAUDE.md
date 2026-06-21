# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Жоба туралы

OIQ — математикаға арналған геймификациялық оқыту платформасы (Django негізінде). Бэкенд — Django 6 + PostgreSQL,
админ панель — `django-unfold`, фронтенд — Tailwind CSS 4 + HTMX + Alpine.js + Lucide иконкалары, ал текст
редакторы ретінде CKEditor 5 (математикалық формулаларға арналған KaTeX қосылған кастомды бандл) қолданылады.
Интерфейс негізгі тілі — қазақ тілі (`kk`), бірақ `ru`/`en` локализациясы да қолдау тапқан.

## Жиі қолданылатын командалар

### Django (Python)

```bash
# виртуалды орта env/ ішінде орналасқан
source env/bin/activate

python manage.py runserver
python manage.py migrate
python manage.py makemigrations
python manage.py createsuperuser
python manage.py collectstatic
```

`config/settings.py` барлық құпия мәндерді (`.env` файлынан, `python-decouple` арқылы) оқиды: `SECRET_KEY`,
`DB_*`, `ALLOWED_HOSTS`, `EMAIL_*`, `SITE_NAME`, `ADMIN_URL`, `WEBSITE_URL`. Жаңа орынды баптағанда осы
айнымалылардың бәрі `.env`-де болуы керек.

### Фронтенд (Tailwind CSS)

`ui/static_src/` — Tailwind мен CKEditor бандлының бастапқы код каталогы (npm package.json осында).

```bash
cd ui/static_src
npm install

npm run dev      # Tailwind CSS-ті watch режимінде құрастыру (development)
npm run build    # production үшін Tailwind CSS-ті минификациялап шығару (../static/css/dist)
```

### CKEditor бандлы

CKEditor 5 + KaTeX (математика плагині) кастомды Vite конфигурациясы арқылы IIFE бандл ретінде құрастырылады:

```bash
cd ui/static_src
npm run build:ckeditor   # vite.ckeditor.config.js бойынша ../static/oiq-ckeditor/oiq-ckeditor.bundle.js шығады
```

Бастапқы код: `ui/static_src/src/js/oiq-ckeditor.js` → нәтиже: `ui/static/oiq-ckeditor/oiq-ckeditor.bundle.js`
және `ui/static/oiq-ckeditor/ui.css`. `vite.ckeditor.config.js`-те `@ckeditor/*` мен `@isaul32/*`
пакеттеріндегі SVG иконкаларды raw-string ретінде импорттайтын кастомды плагин бар (CKEditor `IconView`
SVG-ні DOMParser арқылы парстайды, сондықтан Vite-тің әдепкі asset-URL/base64 түрлендіруі жұмыс істемейді).

### Тесттер

Жобада әзірге тесттер жоқ (`apps/*/tests.py` қосылмаған). Жаңа тест қосу қажет болса, Django-ның стандартты
`python manage.py test` командасын қолданыңыз.

## Жоғары деңгейлі архитектура

### Django app-тардың құрылымы

- **`core`** — ортақ домендік модельдер, админ-конфигурация, формалар мен утилиталар орналасқан негізгі
  қосымша (`INSTALLED_APPS`-те `core.apps.CoreConfig`):
  - `core/models/` — `base.py` (`TimeStampedModel`, `ActiveModel`, `BaseModel` абстрактты модельдері),
    `account.py` (`User`, `UserSession`, `Teacher`), `education.py` (`City`, `School`, `Grade`),
    `content.py` (`Subject`, `Chapter`, `Topic`, `QuestionFormat`, `FormatVariant`, `Question`, `Option`).
    Барлық модельдер `core/models/__init__.py` арқылы re-export етіледі — жаңа модельді сол жерге қосу керек.
  - `core/admin/` — `django-unfold` негізіндегі admin класстары, тиісінше `account.py`/`education.py`/
    `content.py` бойынша бөлінген, барлығы `__init__.py` арқылы жиналады. `base.py`-да екі ортақ миксин бар:
    - `BaseModelAdmin` — `is_active`/`created_at`/`updated_at` өрістерін автоматты түрде "General information"
      fieldset-іне қосады.
    - `LinkedAdminMixin` — байланысты объектіге (`admin_link`/`parent_link`) сілтеме шығаратын хелпер.
  - `core/forms/` — кастомды формалар мен виджеттер (мыс. `RichTextTextarea` — CKEditor бандлын жүктейтін
    Django widget, `QuestionAdminForm` — `Question.text` өрісіне rich-text виджет тағайындайды).
  - `core/utils/` — `backends.py` (email немен username бойынша логин жасайтын `EmailOrUsernameBackend`),
    `decorators.py` (рөлге негізделген рұқсат декораторлары), `files.py` (upload жолдары).

- **`apps.main`** — негізгі сайт (лендинг, аутентификация, регистрация):
  - `apps/main/views/auth.py` — логин, логаут, оқушы/мұғалім регистрациясы, қала бойынша мектептер API-і.
  - `apps/main/forms/auth.py` — `LoginForm`, `LearnerRegisterForm`, `TeacherRegisterForm`.
  - `apps/main/services/` — бизнес-логика: `auth.py` (пайдаланушы құру, username генерациясы, рөл бойынша
    redirect URL), `email.py` (email хабарландырулары), `sessions.py` (`UserSession` жазбаларын сақтау —
    user-agent, IP, құрылғы түрі).

- **`apps.dashboard.learner`** және **`apps.dashboard.teacher`** — оқушы мен мұғалім панельдерінің
  Django app-тары (`apps/dashboard/<role>/views/main.py` + `urls.py`, `app_name='learner'`/`'teacher'`).
  Әзірге тек dashboard беттері бар; жаңа функционал осы құрылымды қайталай отырып қосылады
  (`views/`, `urls.py`, `apps.py` бөлек `AppConfig`).

### URL маршруттау

`config/urls.py` — `i18n_patterns` арқылы тілге қарай префикс қосады (`prefix_default_language=True`,
яғни `/kk/...`, `/ru/...`, `/en/...`). Негізгі тармақтар:
- `apps.main.urls` (`/` — лендинг, логин, регистрация)
- `apps.dashboard.learner.urls` (`/learner/`)
- `apps.dashboard.teacher.urls` (`/teacher/`)
- `admin/` — Unfold админ панелі

### Рұқсаттар мен рөлдер

`core.models.User.Role` үш рөлді анықтайды: `ADMIN`, `TEACHER`, `LEARNER`. Аутентификацияда екі backend
бар (`config/settings.py` → `AUTHENTICATION_BACKENDS`): стандартты `ModelBackend` және
`core.utils.backends.EmailOrUsernameBackend` (логин кезінде email немен username қабылдайды).

`core/utils/decorators.py`-дегі декораторлар:
- `anonymous_required` — авторизацияланған пайдаланушыны рөліне сай dashboard-қа қайта бағыттайды.
- `role_required(*roles)`, оның негізінде `learner_required`, `teacher_required`, `admin_required`.
- `partner_teacher_required` — `Teacher.type == PARTNER` болатын мұғалімдерге арналған рұқсат.

Рөл бойынша redirect логикасы орталықтандырылған: `apps.main.services.auth.get_user_redirect_url(user)`.

### Шаблондар (templates)

`ui/templates/` — барлық app-тарға ортақ шаблон каталогы (`TEMPLATES.DIRS`, `APP_DIRS=True` де қосулы):
- `base.html` — негізгі layout: Tailwind CSS, CDN арқылы htmx/Alpine.js/Lucide/dotLottie, Alpine негізінде
  toast-хабарландырулар (`django.contrib.messages` арқылы).
- `layouts/` — `auth_layout.html`, `main_layout.html`.
- `app/` — беттер бойынша топтастырылған шаблондар (`app/auth/login`, `app/auth/register`,
  `app/dashboard/learner`, `app/dashboard/teacher`).

### Админ панель (Unfold)

`config/settings.py`-дегі `UNFOLD` сөздігі сайдбар навигациясын, түс палитрасын (primary indigo)
және логин бетінің баннерін баптайды. Жаңа модель қосқанда, оны әдетте `UNFOLD['SIDEBAR']['navigation']`
тізіміне де қосу керек (тиісті `_('...')` атау мен `reverse_lazy('admin:<app>_<model>_changelist')`
сілтемесімен), әйтпесе ол сайдбарда көрінбейді.

### Аударма (i18n)

`USE_I18N = True`, `LANGUAGES = (kk, ru, en)`, `LOCALE_PATHS = [BASE_DIR / 'locales']`,
`django-modeltranslation` орнатылған — модель өрістерінің аудармаларын қажет болса
`translation.py` файлдары арқылы тіркеу керек (`modeltranslation.translator.register`).

Жаңа `{% translate '...' %}` / `gettext_lazy('...')` жолдарын `locales/kk/LC_MESSAGES/django.po` және
`locales/ru/LC_MESSAGES/django.po` файлдарына қосу үшін:

```bash
python manage.py makemessages -l kk -l ru --no-obsolete --ignore=env/* --ignore=ui/static_src/*
```

`--ignore` флагтары міндетті: олар болмаса `makemessages` `env/` (виртуалды орта, Django/Click т.б.
пакеттер) мен `ui/static_src/` (node_modules) ішін де сканерлеп, `.po`-ға мыңдаған бөгде жол қосып
кетеді.

`.po` файлдарды қолмен өзгерткеннен/толтырғаннан кейін (қазақ/орыс аудармасын жазу):

```bash
python manage.py compilemessages -l kk -l ru
```

**Ескерту:** `makemessages` жаңа жолды бұрынғы ұқсас аудармаға автоматты түрде сәйкестендіріп
(`#, fuzzy` деп белгілеп) қоя береді — бұл көбіне **қате** аударма болады. Әр `makemessages`-тен
кейін `.po` файлдағы `#, fuzzy` пен бос `msgstr ""` жолдарды тауып, дұрыс аудармамен ауыстырып,
`fuzzy` белгісін алып тастаңыз — әйтпесе `compilemessages` қате аудармамен компиляция жасап кетеді.
