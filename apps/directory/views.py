from django import forms
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from apps.directory.selectors import get_schools_by_city


# -------------- school field (HTMX) --------------
def school_field_view(request):
    city_id = request.GET.get('city')
    schools = get_schools_by_city(city_id)

    class _SchoolForm(forms.Form):
        school = forms.ModelChoiceField(queryset=schools, required=True, empty_label=_('Select school'))

    form = _SchoolForm(initial={'school': request.GET.get('school')})
    return render(request, 'directory/_school_field.html', {'field': form['school']})
