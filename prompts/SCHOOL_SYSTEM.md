# SCHOOL_SYSTEM.md — Мектеп жүйесі, рөлдер, субдомен, аккаунт (тапсырмалар)

> Оқы: `prompts/RULES.md`. Бұл — модульді монолит рефакторингінен **кейінгі** фаза (2-фаза).
> Әр тапсырманы ретімен орында, статусты жаңарт, `python manage.py check` іске қоспай келесіге өтпе.

## Статустар
`[ ]` жасалу керек · `[!]` жасалуда · `[x]` дайын · `[~]` жартылай · `[-]` алынды

## Алдын ала талаптар
- `prompts/REFACTORING.md` аяқталған: `accounts`, `catalog`, `directory`, `teaching`, `learning` app-тары бар,
  `AUTH_USER_MODEL = 'accounts.User'`, домен шекаралары таза.
- `apps/school/` әлі жоқ — ол TASK-02-де құрылады.
- Тапсырмалардың орындалу реті: **TASK-01 → TASK-02 → TASK-03 → TASK-04**
  (сенің пункттеріңмен байланысы әр тапсырмада көрсетілген).

---

## Ортақ принциптер (бұларды бұзба)

**1. «Рөл» — үш ортогональ (тәуелсіз) ұғым, оларды шатастырма:**

| Ұғым | Қайда | Мәні | Саны |
|------|-------|------|------|
| **Аккаунт түрі** | `accounts.User.role` | платформаға кім болып тіркелді (admin/teacher/learner), қай dashboard | глобал, біреу |
| **Мұғалім қабілеті** | `accounts.Teacher.type` | `regular` (external) / `partner` (catalog-қа контент сала алады) | біреу |
| **Ұйымдағы рөл** | `school.Membership.roles` | директор/меңгеруші/пән мұғалімі/сынып жетекшісі... | мектепке қатысты, **бірнешеу** |

Бір адам бір мезгілде үшеуін де ұстай алады, олар бір-біріне кедергі жасамайды. Мысалы:
`User.role=teacher` + `Teacher.type=partner` + `Membership(org=42, roles=[deputy_academic, teacher])`.

**2. Сыртқы (external) қолданушылар.** `teaching`/`learning` қолданушылары `oiq.kz`-те өздері тіркеледі
де, **ешбір мектепке тиесілі емес**. `User` — глобал, ешбір ұйымға байланбаған. Мектеппен байланыс —
бөлек нәрсе (`Membership`), оны мектеп әкімшісі қолмен жасайды.

**3. Тіркелу нүктесі — біреу (`oiq.kz`).** Мектеп жүйесінің өз тіркелуі жоқ. Логин де ортақ (бір identity).

**4. Субдомен — тек маршрут қабаты.** Монолит: бір Django процесі, бір DB, бір сессия.
Cookie `.oiq.kz` деңгейінде ортақ болғандықтан SSO мәселесі мүлдем жоқ (токен/gateway керек емес).

**5. Аккаунт беттері — әр өнімде бөлек, бірақ identity логикасы `accounts`-та.**
Әр платформаның аккаунт/профиль беті өз UI-ы мен өз дерегімен (teaching басқа, learning басқа, school басқа).
Ал ортақ `User`-ді өзгертетін логика (пароль, email, аватар, аккаунт жою) — `accounts.services`-те, бір көзден.
Беттер сол сервистерді шақырады.

---

## TASK-01: Субдомен маршруты (`school.oiq.kz`) + dev орта
**Статус:** [ ]  ·  **Пункт:** 3  ·  **Тәуелділік:** жоқ (бірінші осыны жаса)

Мектеп жүйесі `school.oiq.kz`-те, қалғаны `oiq.kz`-те. Бір процесс, хостқа қарап `urlconf` ауысады.

### Dev — ең қарапайым шешім: `lvh.me`
`lvh.me` және оның барлық субдомені DNS-те **автоматты** `127.0.0.1`-ге шешіледі. `/etc/hosts`-ты
өзгертудің қажеті жоқ, Nginx керек емес — жай `runserver`.

- Басты хост: `http://oiq.lvh.me:8000`
- Мектеп хосты: `http://school.oiq.lvh.me:8000`

*(Егер жұмыс желісі DNS-over-HTTPS салдарынан `lvh.me`-ні бөгесе — балама ретінде `/etc/hosts`-қа
`127.0.0.1 oiq.local school.oiq.local` жаз да, `BASE_DOMAIN=oiq.local` қой.)*

### Орындалу
- [ ] `settings.py`-та домендерді `BASE_DOMAIN`-нен шығар:
  ```python
  BASE_DOMAIN = config('BASE_DOMAIN', default='oiq.lvh.me')   # prod: .env-те oiq.kz
  SCHOOL_HOST = f'school.{BASE_DOMAIN}'

  ALLOWED_HOSTS = [BASE_DOMAIN, SCHOOL_HOST]
  SESSION_COOKIE_DOMAIN = f'.{BASE_DOMAIN}'
  CSRF_COOKIE_DOMAIN = f'.{BASE_DOMAIN}'

  _scheme = 'http' if DEBUG else 'https'
  _port = ':8000' if DEBUG else ''
  CSRF_TRUSTED_ORIGINS = [f'{_scheme}://{BASE_DOMAIN}{_port}', f'{_scheme}://{SCHOOL_HOST}{_port}']
  ```
- [ ] `.env` мен `.env.example`-ге `BASE_DOMAIN` қос.
- [ ] `config/urls_main.py` (oiq.kz) және `config/urls_school.py` (school.oiq.kz) жаса. `ROOT_URLCONF = 'config.urls_main'` (әдепкі/fallback):
  ```python
  # config/urls_main.py — i18n_patterns ішінде
  path('',           include('apps.main.urls')),
  path('auth/',      include('apps.accounts.urls.auth')),     # ортақ логин/тіркелу
  path('subjects/',  include('apps.teaching.urls')),
  path('learn/',     include('apps.learning.urls')),
  # + accounts, catalog, directory HTMX эндпоинттері

  # config/urls_school.py — i18n_patterns ішінде
  path('',            include('apps.school.urls.landing')),   # мектеп таңдау/онбординг
  path('<slug:org>/', include('apps.school.urls.workspace')), # tenant workspace
  ```
- [ ] `config/middleware.py`-ге хост→urlconf middleware қос:
  ```python
  class HostURLConfMiddleware:
      def __init__(self, get_response):
          self.get_response = get_response
      def __call__(self, request):
          host = request.get_host().split(':')[0]
          request.urlconf = 'config.urls_school' if host.startswith('school.') else 'config.urls_main'
          return self.get_response(request)
  ```
- [ ] `MIDDLEWARE`-де `HostURLConfMiddleware`-ді **LocaleMiddleware-ден (және жобадағы `CookieLocaleMiddleware`-ден) БҰРЫН** қой — олар да `request.urlconf`-ты оқиды.
- [ ] Хосттар арасында сілтеме керек болғанда абсолют URL хелперін жаз (`build_absolute_url(host, name, **kwargs)`) немесе `django-hosts` пакетін ал (`{% host_url %}`). `reverse()` тек ағымдағы urlconf ішінде жұмыс істейтінін ұмытпа.

### Тексеру
- [ ] `runserver 0.0.0.0:8000`. `oiq.lvh.me:8000`-де кіріп, `school.oiq.lvh.me:8000`-ге өткенде **қайта кірмей** тұрсын (ортақ cookie).
- [ ] Продакшн: Nginx-те екі `server_name` (`oiq.kz`, `school.oiq.kz`) бір Gunicorn upstream-ге; `*.oiq.kz` wildcard TLS немесе екі сертификат.

---

## TASK-02: Organization / Membership модельдері (`school` app)
**Статус:** [ ]  ·  **Пункт:** 2  ·  **Тәуелділік:** TASK-01

Модельдер **`school` жүйесіне тиесілі** — жеке `organizations` app **керек емес**. Оларды `school`-да сақта.

### Орындалу
- [ ] `apps/school/` құр (RULES.md §5 канондық құрылым, `models/` — пакет). `INSTALLED_APPS`-қа қос.
- [ ] `.importlinter`-ге `apps.school`-ды қос: `products-independent` пен `layers` контрактына
      (RULES.md §10-дағы түсініктемелі жолды аш).
- [ ] `apps/school/models/organization.py`:
  ```python
  from django.conf import settings
  from django.contrib.postgres.fields import ArrayField
  from django.db import models
  from django.utils.translation import gettext_lazy as _
  from core.models import BaseModel

  class Organization(BaseModel):                      # мектеп-тенант
      school = models.ForeignKey('directory.School', null=True, blank=True,
                                 on_delete=models.SET_NULL, related_name='organizations')
      name = models.CharField(_('name'), max_length=255)
      slug = models.SlugField(_('slug'), unique=True)  # URL-дегі 'school42'

  class OrgRole(models.TextChoices):
      DIRECTOR = 'director', _('Director')
      DEPUTY_ACADEMIC = 'deputy_academic', _('Deputy director (academic)')
      DEPUTY_UPBRINGING = 'deputy_upbringing', _('Deputy director (upbringing)')
      HOMEROOM = 'homeroom', _('Homeroom teacher')
      TEACHER = 'teacher', _('Subject teacher')
      STUDENT = 'student', _('Student')
      PARENT = 'parent', _('Parent')

  class Membership(BaseModel):                         # User ↔ Organization байланысы
      user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='memberships')
      organization = models.ForeignKey(Organization, on_delete=models.CASCADE,
                                       related_name='memberships')
      roles = ArrayField(models.CharField(max_length=32, choices=OrgRole.choices), default=list)

      class Meta:
          constraints = [models.UniqueConstraint(fields=['user', 'organization'], name='uniq_member')]

      def has_role(self, *roles):
          return any(r in self.roles for r in roles)
  ```
  > `roles` — ArrayField (Postgres, қарапайым). Рөлге тән дерек (мыс. сынып жетекшісінің қай сыныбы) —
  > рөл тізімінде емес, кейін бөлек операциялық модельде (attendance/timetable) `Membership`-ке FK арқылы.
- [ ] `models/__init__.py`: `from .organization import Organization, OrgRole, Membership`.
- [ ] `selectors/`: `get_organization_by_slug(slug)`, `get_membership(user, organization)`,
      `get_org_members(organization, role=None)`, `get_user_organizations(user)`.
- [ ] `services/`: `create_organization(...)`, `add_member(organization, user, roles)`,
      `update_member_roles(membership, roles)`, `remove_member(membership)` (soft-delete).
- [ ] Tenant middleware: `<slug:org>` → `request.organization` + мүшелікті тексеру:
  ```python
  # apps/school/middleware.py — HostURLConfMiddleware-ден КЕЙІН
  # kwargs-тан 'org' slug-ты алып, Organization-ды request-ке қой; мүше еместі 404/redirect ет.
  ```
- [ ] `org_role_required(*roles)` декоратор (`school`-та): `request.organization` + `Membership.has_role`.

### Тексеру
- [ ] Организация құрып, `school.oiq.kz/<slug>/`-ке мүше кіре алады, мүше емес — жоқ.
- [ ] `lint-imports` жасыл (school тек accounts/directory-ге жол-сілтемесі арқылы тәуелді).

---

## TASK-03: Сыртқы мүшені қосу ағыны
**Статус:** [ ]  ·  **Пункт:** 1  ·  **Тәуелділік:** TASK-02

Мектеп әкімшісі жүйеден қолданушыны іздейді. **Табылса** — мүше етіп қосады. **Табылмаса** — сол жерден
тіркеп (жаңа external аккаунт жасап) қосады. **Invitation моделі керек емес.**

### Орындалу
- [ ] Бет: `school.oiq.kz/<org>/members/` — мүшелер тізімі + «Мүше қосу». Қорғау: `org_role_required(DIRECTOR, DEPUTY_ACADEMIC)`.
- [ ] Іздеу (HTMX): email/телефон/аты бойынша `accounts.selectors`-тан қолданушыны тап
      (жаңа selector қажет болса `accounts`-та жаса: `find_users(query)`), нәтижені тізіп көрсет.
- [ ] **Табылды →** `school.services.add_member(organization, user, roles)`. Қолданушы келесі кірген сәтте мектеп бөлімін көреді.
- [ ] **Табылмады →** сол формада «жаңа мұғалім тіркеп қосу»: аты/email/рөл толтырылады →
      `school.services.register_and_add_member(...)` мынаны істейді:
  1. `accounts.services`-тегі жасау функциясымен external `User` жасайды
     (мыс. `create_external_user(email=..., first_name=..., role=User.Role.TEACHER)` —
     керек болса `accounts.services`-те осындай функция жаса; пароль генерацияланады немесе «парольді орнату» email-і жіберіледі).
  2. `school.services.add_member(organization, user, roles)` шақырады.
  > Барлық User жасау логикасы **`accounts.services`-те** (identity бір көзден); `school` тек шақырады.
- [ ] Мүшенің рөлін өзгерту/өшіру (HTMX): `update_member_roles`, `remove_member`.

### Тексеру
- [ ] Бар қолданушыны тауып қосу → мүше көрінеді.
- [ ] Жоқ қолданушыны тіркеп қосу → жаңа User + Membership жасалады, ол кіре алады.

---

## TASK-04: Өнімге тән аккаунт/профиль беттері
**Статус:** [ ]  ·  **Пункт:** 4  ·  **Тәуелділік:** TASK-01

Ортақ `/account/*`-ты **барлық хостта көрсету идеясынан бас тарт.** Әр өнімнің аккаунт/профиль беті —
өз app-ында, өз UI-ы мен өз дерегімен. Ал `User`-ді өзгертетін identity логикасы — `accounts`-та, бір көзден.

### Архитектура
- **`accounts` иеленеді:** `User`/`Teacher` модельдері; auth ағыны (login/logout/register) — тек `oiq.kz`-те, ортақ;
  identity **сервистері** (басқа app шақыратын): `change_password`, `update_email`, `set_avatar`,
  `update_basic_info`, `deactivate_account`. `accounts` **өнімге тән аккаунт бетін иеленбейді.**
- **Әр өнім өз аккаунт аймағын иеленеді** (өз views/templates/layout, өз дерегі), `accounts.services`-ті шақырады:
  - `teaching` → `oiq.kz/subjects/account/...` — мұғалім профилі (Teacher: пән, мектеп, био, partner белгісі) + баптау.
  - `learning` → `oiq.kz/learn/account/...` — оқушы профилі (прогресс, мақсат, преференция) + баптау.
  - `school` → `school.oiq.kz/<org>/account/...` — мүше профилі (ұйымдағы рөлдер, лауазым) + баптау.

### Орындалу
- [ ] `accounts.services`-ке identity операцияларын шығар (валидацияны сервис жасайды, `ValidationError` көтереді):
      `change_password(user, current, new)`, `update_email(user, email)`, `set_avatar(user, file)`,
      `update_basic_info(user, **fields)`, `deactivate_account(user)`. `selectors`: `get_teacher(user)` т.б.
- [ ] Қазіргі `/account/*` беттерін (рефакторингте `accounts`-қа көшкен teacher account беттері) →
      **`teaching`-ке** көшір (мұғалім аккаунт аймағы), шаблондарды `teaching/templates/teaching/account/`-қа қой,
      логиканы `accounts.services` шақыруларына ауыстыр.
- [ ] `learning`-те learner аккаунт аймағын жаса (өз беті/шаблоны), `accounts.services` шақырады.
- [ ] `school`-та `<org>/account/` мүше профилін жаса (ұйымдағы рөлдер көрінеді), `accounts.services` шақырады.
- [ ] Әр өнім өз layout-ын қолданады (teaching → teacher layout, school → school layout). Ортақ форма
      элементтері `ui/components/`-тан. Пароль/email формасы әр өнімде жеңіл (тек өріс жинайды), валидация — сервисте.
- [ ] Login/logout/register `accounts`-та, тек `oiq.kz`-те қалады. `school.oiq.kz`-ке аноним келсе →
      `oiq.kz/auth/login/?next=<толық URL>`-ге бағыттайсың (ортақ cookie болғандықтан кіргеннен кейін оралады).

### Тексеру
- [ ] Мұғалім `subjects/account/`, оқушы `learn/account/`, мектеп мүшесі `school.oiq.kz/<org>/account/`-та
      өз профилін бөлек UI-мен көреді.
- [ ] Пароль өзгерту үш жерде де жұмыс істейді (логика бір — `accounts.services.change_password`).
- [ ] Ешбір өнім басқа өнімнің аккаунт бетін импорттамайды (RULES.md §2).

---

## Аяқтау критерийі
- Субдомен: `school.oiq.kz` бөлек маршрутта, dev-те `lvh.me` арқылы, ортақ cookie жұмыс істейді.
- `Organization`/`Membership` — `school` app-та; ұйымдағы рөл `Membership.roles`-та (бірнешеу).
- Сыртқы мүшені іздеп қосу да, тіркеп қосу да жұмыс істейді (Invitation жоқ).
- Аккаунт беттері әр өнімде бөлек; identity логикасы `accounts.services`-те бір көзден.
- Үш «рөл» ұғымы бөлек: `User.role` · `Teacher.type` · `Membership.roles`.
- `lint-imports` жасыл.



Жалпы school жүйесі қалай жұмыс жасайтынын айтып кетейін.

Мектеп жүйесінде бірнеше рөлдердегі қолданушылар болады (Жүйелік администратор, директор, меңгеруші, мұғалім, ...). Жүйедегі қолданушы бір уақытта бірнеше рөлді атқара алады.

1. Workspace. Мектеп бұл - ұйым болып есептеледі. Әр ұйымның өз мүшелері бар. Сол ұйымның мүшелеріне арналған жұмыс жасау алаңы (workspace) болады. Әр мүшенің өзіне тиісті рөл(дер)і бар. Сол рөл(дер)ге  байланысты workspace-те қолданушыға байланысты мүмкіндіктер мен функциялар қолжетімді болады. Алдағы уақытта рөлдерге байланысты жеке ерекшеліктері болмаса, барлық рөлдегі қолданушыларға workspace ортақ болады;

2. Рөлдер. Жалпы мектепте қандай және қанша лауазымды тұлғалардың барына байланысты жүйені басқаратын сонша рөлдер болады және сол рөлдерге тағайымдалған мүшелер болады. Соладың тізімін басымдылық бойынша жазып шығайын:

- Жүйелік администратор. Тиісті мектеп ортасында (workspace) бүкіл мүмкіндіктер мен функцияларды басқара алады. Яғни create, read, update, delete. Сонымен қатар мектеп мүшелерінің аккаунттарын басқару, рөлдерін тағайымдау және т.б. Белгілі бір мүшеге тиісті рөл(дер)ін берген кезде, автоматты түрде сол рөлдерге байланысты мүмкіндіктері мен фунциялары қолжетімді болады;

- Директор. Мектеп директоры. Бұл рөлге жүйелік администратордың мүмкіндіктері кіреді;

- Хатшы. 