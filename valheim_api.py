from re import findall, finditer, search, sub
from requests import get


api_url = 'https://valheim.fandom.com/api.php'
wiki_url = 'https://valheim.fandom.com/'
query_params = {'format': 'json'}
html_tag_pattern = r'<.+?>'


def _request_json(query_params, url=wiki_url):
    """Join the keypair value of query_params with '&'
    Then retrieve contents using requests.get in JSON form"""
    query_string = '?' + \
        '&'.join([f'{key}={value}' for key, value in query_params.items()])
    url = api_url + query_string
    # print(url)
    return get(url).json()


def search_pages(query, search_limit=5):
    query_params.update({'action': 'query',
                         'list': 'search',
                         'srsearch': query,
                         'srlimit': search_limit,
                         'srprop': 'sectiontitle'})
    result = _request_json(query_params)
    result = result.get('query').get('search')

    if result:
        return [result.get('title') for result in result]
    else:
        return f'No results found for {query}'


def _clean_field_value(value, list_indicator='<li>'):
    """Remove HTML tags from field value. If it contains list elements return values in a list.
    Return error string if value is empty."""
    if value == '':
        return '*Unable to retrieve contents*'
    if search(html_tag_pattern, value):
        if list_indicator in value:
            list_item_pattern = r'<li>(.+?)</li>'
            value = '\n'.join(findall(list_item_pattern, value))
        value = sub(html_tag_pattern, '', value)

    return value


def _get_page_thumbnail(html, page_details):
    # Get the thumbnail URL
    thumbnail_pattern = r'<a href="(.+?)" class="image image-thumbnail"'
    page_details['thumbnail'] = findall(thumbnail_pattern, html)[0]

    # Get the thumbnail caption if available
    caption_pattern = r'pi-caption">(.+?)</figcaption>'
    if search(caption_pattern, html):
        page_details['description'] = findall(caption_pattern, html)[0]

    return page_details


def _get_page_infobox(html, page_details):
    """Retrieve field names and values from infoboxes and return them in a dictionary"""
    # Check if field names exists in infobox and store them in a list
    # If they don't exist return page_details
    field_name_pattern = r'pi-data-label .+?>(.+?)</'
    field_names = findall(field_name_pattern, html)

    # Get a list of field values
    field_value_pattern = r'<(div|td).+?pi-data-value .+?>(?P<value>.+?)</(div|td)'
    field_values = [value.group('value')
                    for value in finditer(field_value_pattern, html)]

    # Combine names and values into a dictionary
    for (name, value) in zip(field_names, field_values):
        page_details['fields'].update({name: _clean_field_value(value)})

    return page_details


def _get_page_text(html, page_details):
    field_pattern = r'mw-headline.+?(?=<span class="mw-headline"|$)'
    field_name_pattern = r'>(.+?)</span>'
    field_value_pattern = r'<(pr?e?|li)>(?P<value>.+?)</(pr?e?|li)>'

    # Group field names and values in case there are many values to one field
    for field in findall(field_pattern, html):
        name = findall(field_name_pattern, field)[0]
        value = '\n'.join([value.group('value')
                          for value in finditer(field_value_pattern, field)])
        page_details['fields'].update({name: _clean_field_value(value)})

    return page_details


def get_page(title):
    # Convert title to title case to conform to titles of wiki pages
    query_params.update({'action': 'parse',
                         'page': title,
                         'redirects': 'true'})
    result = _request_json(query_params)

    # If there's an error try title case with page name
    # Return error message as string if failure still occurs
    if 'error' in result:
        query_params['page'] = query_params['page'].title()
        result = _request_json(query_params)
        if 'error' in result:
            return result.get('error').get('info')

    # Get the HTML of the page and remove newlines for easier regex pattern matching
    page_title = result.get('parse').get('title')
    html = result.get('parse').get('text').get('*').replace('\n', '')

    page_details = {
        'title': page_title,
        'thumbnail': '',
        'description': '',
        'fields': {},
    }

    # Get the image thumbnail if it exists exists (the space is intentional)
    thumbnail_identifier = ' image-thumbnail'
    if thumbnail_identifier in html:
        page_details = _get_page_thumbnail(html, page_details)

    # Get infobox details if it exists
    infobox_label_identifier = 'pi-data-label'
    if infobox_label_identifier in html:
        page_details = _get_page_infobox(html, page_details)

    # Else, get the detailed page contents
    else:
        # Remove infobox in case there is only an image thumbnail
        infobox_tag_pattern = r'<aside.+?</aside>'
        html = sub(infobox_tag_pattern, '', html)

        # Get the first paragraph as the description and remove it from the html
        description_pattern = r'(?<=parser-output">)<p>.+?</p>'
        description_match = search(description_pattern, html)
        if description_match:
            page_details['description'] = sub(
                html_tag_pattern, '', description_match.group())
            html = html[description_match.end():]

        # If headlines exists retrieve them as field names
        headline_identifier = 'mw-headline'
        if headline_identifier in html:
            page_details = _get_page_text(html, page_details)

        # Else discard fields from page_details and add paragraphs to description
        else:
            page_details.pop('fields')
            p_pattern = r'<p>(.+)</p>'
            for value in findall(p_pattern, html):
                page_details['description'] += '\n' + _clean_field_value(value)

    return page_details


if __name__ == "__main__":
    print(get_page('valheim'))
    print(get_page('bronze'))
    print(get_page('haldor'))
    print(get_page('bronze armor'))
    print(get_page('the elder'))
    print(get_page('the elder power'))
