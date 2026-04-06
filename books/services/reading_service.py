import io
from lxml import etree
from django.utils.safestring import mark_safe

FB_NS = 'http://www.gribuser.ru/xml/fictionbook/2.0'
XLINK_NS = 'http://www.w3.org/1999/xlink'


def get_book_content(book):
    try:
        with book.file.open('rb') as f:
            raw = f.read()
        tree = etree.parse(io.BytesIO(raw))
        root = tree.getroot()
        bodies = root.findall(f'{{{FB_NS}}}body')
        main_body = next(
            (b for b in bodies if b.get('name', '').lower() not in ('notes', 'comments', 'footnotes')),
            bodies[0] if bodies else None,
        )
        if main_body is None:
            return mark_safe('<p>Содержимое не найдено.</p>')
        return mark_safe(_to_html(main_body))
    except Exception as e:
        return mark_safe(f'<p class="text-red-400/70">Ошибка загрузки содержимого.</p>')


def _to_html(el):
    tag = el.tag.split('}')[-1] if '}' in el.tag else el.tag
    dispatch = {
        'body': ('div', 'class="book-body space-y-6"'),
        'section': ('div', 'class="book-section py-4"'),
        'title': ('h2', 'class="text-3xl font-bold my-10 leading-tight text-white/90 text-center"'),
        'subtitle': ('h3', 'class="text-xl font-semibold my-6 text-white/60 text-center"'),
        'epigraph': ('blockquote', 'class="border-l-4 border-blue-500/50 pl-6 italic my-8 text-white/60 max-w-lg ml-auto"'),
        'p': ('p', 'class="text-white/80 leading-[1.9] text-justify tracking-wide"'),
        'emphasis': ('em', 'class="text-white/90 italic"'),
        'strong': ('strong', 'class="font-bold text-white"'),
        'poem': ('div', 'class="my-8 text-center italic text-white/70"'),
        'stanza': ('div', 'class="mb-6"'),
        'v': ('p', 'class="mb-2"'),
        'a': ('a', 'class="text-blue-400 hover:text-blue-300 hover:underline transition-colors"'),
    }

    if tag == 'empty-line':
        return '<div class="h-8"></div>'
    if tag == 'image':
        return ''

    if tag not in dispatch:
        return _children(el)

    html_tag, attrs = dispatch[tag]
    extra = ''
    if tag == 'a':
        href = el.get(f'{{{XLINK_NS}}}href', el.get('href', '#'))
        extra = f' href="{href}"'

    inner = _children(el)
    if not inner.strip() and tag not in ['empty-line']:
        return ''
        
    return f'<{html_tag} {attrs}{extra}>{inner}</{html_tag}>'


def _children(el):
    parts = []
    if el.text:
        parts.append(_esc(el.text))
    for child in el:
        parts.append(_to_html(child))
        if child.tail:
            parts.append(_esc(child.tail))
    return ''.join(parts)


def _esc(text):
    return (text or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
