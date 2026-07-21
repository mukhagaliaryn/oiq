from apps.catalog.models import City, Grade, School


def get_cities():
    return City.objects.filter(is_active=True)


def get_schools_by_city(city_id):
    if not city_id:
        return School.objects.none()
    return School.objects.filter(city_id=city_id, is_active=True).order_by('name')


def get_active_grades():
    return Grade.objects.filter(is_active=True)
