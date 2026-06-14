from django import forms


class RichTextTextarea(forms.Textarea):
    class Media:
        css = {
            'all': (
                'oiq-ckeditor/ui.css',
            )
        }
        js = (
            'oiq-ckeditor/oiq-ckeditor.bundle.js',
        )

    def __init__(self, attrs=None):
        default_attrs = {
            'data-oiq-editor': 'true',
            'rows': 8,
        }

        if attrs:
            default_attrs.update(attrs)

        super().__init__(attrs=default_attrs)
