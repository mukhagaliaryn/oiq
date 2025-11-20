from django.utils.html import format_html
from django.urls import reverse


# LinkedAdminMixin
# ----------------------------------------------------------------------------------------------------------------------
class LinkedAdminMixin:
    admin_site_name = 'admin'

    def admin_link(self, obj, model_name: str, label=None, field='pk', new_tab=False):
        if not obj or not getattr(obj, field, None):
            return '-'
        try:
            url = reverse(
                f'{self.admin_site_name}:{obj._meta.app_label}_{model_name}_change',
                args=[getattr(obj, field)]
            )
            target = ' target="_blank"' if new_tab else ''
            text = label or str(obj)
            return format_html(f'<a href="{url}"{target}>{text}</a>')
        except Exception:
            return '-'

    def parent_link(self, obj, parent_field_name: str, label_field='__str__', new_tab=False):
        parent = getattr(obj, parent_field_name, None)
        if not parent:
            return '-'
        try:
            url = reverse(
                f'{self.admin_site_name}:{parent._meta.app_label}_{parent._meta.model_name}_change',
                args=[parent.pk]
            )
            label = getattr(parent, label_field) if label_field != '__str__' else str(parent)
            target = ' target="_blank"' if new_tab else ''
            return format_html(f'<a href="{url}"{target}>{label}</a>')
        except Exception:
            return '-'
