import io
from lxml import etree

def parse_metadata(file_obj):
    metadata = {
        'title': 'Unknown Title',
        'author': 'Unknown Author',
        'cover': None
    }
    try:
        if isinstance(file_obj, bytes):
            tree = etree.parse(io.BytesIO(file_obj))
        else:
            tree = etree.parse(file_obj)
            file_obj.seek(0)
            
        namespaces = {'fb': 'http://www.gribuser.ru/xml/fictionbook/2.0'}
        
        title_nodes = tree.xpath('//fb:description/fb:title-info/fb:book-title', namespaces=namespaces)
        if title_nodes and title_nodes[0].text:
            metadata['title'] = title_nodes[0].text.strip()
            
        author_first_nodes = tree.xpath('//fb:description/fb:title-info/fb:author/fb:first-name', namespaces=namespaces)
        author_last_nodes = tree.xpath('//fb:description/fb:title-info/fb:author/fb:last-name', namespaces=namespaces)
        
        author_parts = []
        if author_first_nodes and author_first_nodes[0].text:
            author_parts.append(author_first_nodes[0].text.strip())
        if author_last_nodes and author_last_nodes[0].text:
            author_parts.append(author_last_nodes[0].text.strip())
            
        if author_parts:
            metadata['author'] = " ".join(author_parts)
            
        # Placeholder for cover image parsing (would extract from binary section)
            
    except Exception as e:
        pass
        
    return metadata
