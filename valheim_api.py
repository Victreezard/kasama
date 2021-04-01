from re import findall, search, sub
from requests import get
from urllib.request import urlopen


base_url = 'https://valheim.fandom.com/api.php'
wiki_url = 'https://valheim.fandom.com/wiki/'
query_params = {'format': 'json'}


def _get_query_string(query_params):
    # Return a query string. Iterate that key pair values of query_params and join them with &
    return '?' + '&'.join([f'{key}={value}' for key, value in query_params.items()])


def _request_json(query_string):
    url = base_url + query_string
    # print(url)
    return get(url).json()


def search_page(query, search_limit=5):
    query_params.update({'action': 'query',
                         'list': 'search',
                         'srsearch': query,
                         'srlimit': search_limit,
                         'srprop': 'sectiontitle'})
    result = _request_json(_get_query_string(query_params))
    result = result['query']['search']

    if result:
        return [result['title'] for result in result]
    else:
        return f'No results found for {query}'


def _get_infobox(html, details):
    """Retrieve field names and values from infoboxes.
    Remove hyperlinks from values and form list if they values are in html lists.
    Finally, combine and return field names and values as a dict."""
    thumbnail_pattern = r'(?<=<a href=").+(?=" class="image image-thumbnail")'
    details['thumbnail'] = findall(thumbnail_pattern, html)[0]

    caption_pattern = r'(?<=pi-caption">).+(?=</figcaption>)'
    caption = findall(caption_pattern, html)
    if caption:
        details['description'] = caption[0]

    field_name_sub_pattern = r'(?<=pi-data-label ).+?(?=">)'
    html = sub(field_name_sub_pattern, '', html)
    field_name_pattern = r'(?<=pi-data-label ">).+(?=<\/)'
    field_names = findall(field_name_pattern, html)

    field_value_sub_pattern = r'(?<=pi-data-value ).+?(?=">)'
    html = sub(field_value_sub_pattern, '', html)
    field_value_pattern = r'(?<=pi-data-value ">).+(?=<\/\w+>)'
    field_values = findall(field_value_pattern, html)

    html_tag_pattern = r'<.+?>'
    delimeter = '++'
    list_indicator = '</li><li>'
    for (name, value) in zip(field_names, field_values):
        if search(html_tag_pattern, value) is not None:
            if list_indicator in value:
                value = value.replace(list_indicator, delimeter)
                value = sub(html_tag_pattern, '', value)
                value = value.split(delimeter)
            else:
                value = sub(html_tag_pattern, '', value)
        details['fields'].update({name: value})

    return details


def get_page_details(title):
    # Convert title to title case to conform to titles of wiki pages
    query_params.update({'action': 'parse',
                         'page': title,
                         'redirects': 'true'})
    result = _request_json(_get_query_string(query_params))

    # If there's an error try title case with page name
    # Return error message as string if failure still occurs
    if 'error' in result:
        query_params['page'] = query_params['page'].title()
        result = _request_json(_get_query_string(query_params))
        if 'error' in result:
            return result['error']['info']

    # Retrieve HTML of the page and remove a good chunk of it and retain only useful info
    # Replace spaces with underscore to conform to wiki page URL format
    page_title = result['parse']['title']
    page_url = wiki_url + page_title.replace(' ', '_')
    html = urlopen(page_url).read().decode('utf-8')
    sub_patterns = [
        r'^[\w\W]+<!-- End Google Tag Manager \(noscript\) -->', r'<!--[\w\W]+$']
    for pattern in sub_patterns:
        html = sub(pattern, '', html)

    details = {
        'title': page_title,
        'url': page_url,
        'thumbnail': '',
        'description': '',
        'fields': {},
    }

    # If image thumbnail exists get details from page's infobox (the space is intentional)
    thumbnail_attribute = ' image-thumbnail'
    if thumbnail_attribute in html:
        details = _get_infobox(html, details)

    return details


if __name__ == "__main__":
    print(get_page_details('valheim'))
