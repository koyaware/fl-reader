import io
import base64
from lxml import etree
from django.core.files.base import ContentFile

NAMESPACES = {'fb': 'http://www.gribuser.ru/xml/fictionbook/2.0'}
XLINK_HREF = '{http://www.w3.org/1999/xlink}href'


def parse_metadata(file_obj):
    metadata = {'title': 'Unknown Title', 'author': 'Unknown Author', 'cover': None}
    try:
        if isinstance(file_obj, bytes):
            tree = etree.parse(io.BytesIO(file_obj))
        else:
            tree = etree.parse(file_obj)
            file_obj.seek(0)

        title_nodes = tree.xpath('//fb:description/fb:title-info/fb:book-title', namespaces=NAMESPACES)
        if title_nodes and title_nodes[0].text:
            metadata['title'] = title_nodes[0].text.strip()

        first_nodes = tree.xpath('//fb:description/fb:title-info/fb:author/fb:first-name', namespaces=NAMESPACES)
        last_nodes = tree.xpath('//fb:description/fb:title-info/fb:author/fb:last-name', namespaces=NAMESPACES)
        parts = []
        if first_nodes and first_nodes[0].text:
            parts.append(first_nodes[0].text.strip())
        if last_nodes and last_nodes[0].text:
            parts.append(last_nodes[0].text.strip())
        if parts:
            metadata['author'] = ' '.join(parts)

        cover_nodes = tree.xpath(
            '//fb:description/fb:title-info/fb:coverpage/fb:image', namespaces=NAMESPACES
        )
        if cover_nodes:
            href = cover_nodes[0].get(XLINK_HREF, '')
            if href.startswith('#'):
                binary_id = href[1:]
                binary_nodes = tree.xpath(f'//fb:binary[@id="{binary_id}"]', namespaces=NAMESPACES)
                if binary_nodes and binary_nodes[0].text:
                    raw = base64.b64decode(binary_nodes[0].text.strip())
                    content_type = binary_nodes[0].get('content-type', 'image/jpeg')
                    ext = 'jpg' if 'jpeg' in content_type else content_type.split('/')[-1]
                    metadata['cover'] = ContentFile(raw, name=f'cover.{ext}')

    except Exception:
        pass

    return metadata
