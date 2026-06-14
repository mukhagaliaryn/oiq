from html import escape
from html.parser import HTMLParser

SKIP_TAGS = {'img', 'table', 'ul', 'ol'}
BLOCK_TAGS = {'p', 'div', 'li', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}


class QuestionTextPreviewParser(HTMLParser):
    """Question.text HTML-інен сурет/кесте/тізімдерді алып тастап, тек мәтін мен
    math-tex формулаларын қалдыратын және берілген ұзындыққа дейін қысқартатын парсер."""

    def __init__(self, max_length):
        super().__init__()
        self.max_length = max_length
        self.parts = []
        self.length = 0
        self.skip_depth = 0
        self.math_depth = 0
        self.truncated = False

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.skip_depth += 1
            return

        if self.skip_depth or self.truncated:
            return

        if tag == 'span' and 'math-tex' in dict(attrs).get('class', '').split():
            self.math_depth += 1
            self.parts.append('<span class="math-tex">')
        elif tag in BLOCK_TAGS and self.parts:
            self.parts.append(' ')

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS:
            if self.skip_depth:
                self.skip_depth -= 1
            return

        if self.skip_depth:
            return

        if tag == 'span' and self.math_depth:
            self.math_depth -= 1
            self.parts.append('</span>')

    def handle_data(self, data):
        if self.skip_depth or self.truncated:
            return

        if self.math_depth:
            self.parts.append(escape(data))
            return

        remaining = self.max_length - self.length
        if remaining <= 0:
            self.truncated = True
            return

        if len(data) > remaining:
            data = data[:remaining]
            self.truncated = True

        self.length += len(data)
        self.parts.append(escape(data))

    def get_html(self):
        html = ''.join(self.parts).strip()

        if self.truncated:
            html += '…'

        return html


def question_text_preview(html, max_length=50):
    parser = QuestionTextPreviewParser(max_length)
    parser.feed(html or '')

    return parser.get_html()
