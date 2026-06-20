from django.conf import settings
from django.middleware.locale import LocaleMiddleware
from django.utils import translation


class CookieLocaleMiddleware(LocaleMiddleware):
    """
    Accept-Language заголовын елемейді.
    Тіл тек URL префикс немесе cookie арқылы анықталады,
    екеуі де жоқ болса LANGUAGE_CODE-қа (kk) түседі.
    """

    def process_request(self, request):
        language = None

        # 1. URL префиксінен тіл анықтайды (i18n_patterns)
        language_from_path = translation.get_language_from_path(request.path_info)
        if language_from_path:
            language = language_from_path

        # 2. Cookie-ден тіл алады
        if not language:
            cookie_lang = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
            if cookie_lang:
                supported = dict(settings.LANGUAGES)
                if cookie_lang in supported:
                    language = cookie_lang

        # 3. Fallback — LANGUAGE_CODE (kk)
        if not language:
            language = settings.LANGUAGE_CODE

        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
