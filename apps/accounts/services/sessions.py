from django.utils import timezone
from user_agents import parse
from apps.accounts.models import UserSession


# get_client_ip
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()

    return request.META.get('REMOTE_ADDR')


# get_device_type
def get_device_type(user_agent):
    if user_agent.is_mobile:
        return UserSession.DeviceTypeChoices.MOBILE

    if user_agent.is_tablet:
        return UserSession.DeviceTypeChoices.TABLET

    if user_agent.is_pc:
        return UserSession.DeviceTypeChoices.DESKTOP

    return UserSession.DeviceTypeChoices.UNKNOWN


# save_user_session
def save_user_session(request, user):
    if not request.session.session_key:
        request.session.save()

    session_key = request.session.session_key
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(user_agent_string)

    UserSession.objects.update_or_create(
        user=user,
        session_key=session_key,
        defaults={
            'device_type': get_device_type(user_agent),
            'device_name': user_agent.device.family or '',
            'browser': user_agent.browser.family or '',
            'os': user_agent.os.family or '',
            'ip_address': get_client_ip(request),
            'user_agent': user_agent_string,
            'last_activity_at': timezone.now(),
        },
    )
