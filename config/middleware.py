class HostURLConfMiddleware:
    """
    Хостқа қарап urlconf-ты ауыстырады: school.<BASE_DOMAIN> — мектеп жүйесі,
    қалғаны — негізгі сайт. LocaleMiddleware-ден (CookieLocaleMiddleware) БҰРЫН тұруы керек,
    себебі олар да request.urlconf-ты оқиды.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]
        request.urlconf = 'config.urls_school' if host.startswith('school.') else 'config.urls_main'
        return self.get_response(request)
