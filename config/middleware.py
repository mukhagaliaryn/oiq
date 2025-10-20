from django.utils import translation


class ForceKazakhLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        cookie_name = 'language'

        if cookie_name not in request.COOKIES:
            translation.activate('kk')
            request.LANGUAGE_CODE = 'kk'
        else:
            lang = request.COOKIES.get(cookie_name)
            translation.activate(lang)
            request.LANGUAGE_CODE = lang

        response = self.get_response(request)

        if cookie_name not in request.COOKIES:
            response.set_cookie(
                key=cookie_name,
                value='kk',
                max_age=60 * 60 * 24 * 30,
                path='/',
                samesite='Lax',
                secure=False,
                httponly=False,
            )

        return response
