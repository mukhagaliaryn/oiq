from django import forms
from django.urls import reverse_lazy

INPUT_CLASS = (
    'w-full rounded-full border border-default bg-neutral-primary px-6 py-3 '
    'outline-none transition focus:ring-2 focus:ring-brand'
)


class RichTextTextarea(forms.Textarea):
    class Media:
        css = {
            'all': (
                'js/oiq-ckeditor/ui.css',
            )
        }
        js = (
            'js/oiq-ckeditor/oiq-ckeditor.bundle.js',
        )

    def __init__(self, attrs=None, height=None, width=None):
        default_attrs = {
            'data-oiq-editor': 'true',
            'data-oiq-editor-upload-url': reverse_lazy('core:ckeditor-upload'),
            'rows': 8,
        }

        if height:
            default_attrs['data-oiq-editor-height'] = height

        if width:
            default_attrs['data-oiq-editor-width'] = width

        if attrs:
            default_attrs.update(attrs)

        super().__init__(attrs=default_attrs)
