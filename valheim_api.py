from re import findall, sub
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
    print(url)
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


def get_page_details(title):
    query_params.update({'action': 'parse',
                         'page': title,
                         'redirects': 'true'})
    result = _request_json(_get_query_string(query_params))

    if 'error' in result:
        return result['error']['info']
    else:
        page_title = result['parse']['title'].replace(' ', '_')
    html = urlopen(wiki_url + page_title).read().decode('utf-8')
    sub_patterns = [
        r'^[\w\W]+<!-- End Google Tag Manager \(noscript\) -->', r'<!--[\w\W]+$']
    for pattern in sub_patterns:
        html = sub(pattern, '', html)

    details = {
        'title': '',
        'thumbnail': '',
        'description': '',
        'fields': {},
    }

    details['title'] = page_title

    thumbnail_pattern = r'(?<=<a href=").+(?=" class="image image-thumbnail")'
    thumbnail = findall(thumbnail_pattern, html)
    if thumbnail:
        details['thumbnail'] = thumbnail[0]

        caption_pattern = r'(?<=pi-caption">).+(?=</figcaption>)'
        caption = findall(caption_pattern, html)
        details['description'] = caption[0]

        field_name_sub_pattern = r'(?<=pi-data-label ).+?(?=">)'
        html = sub(field_name_sub_pattern, '', html)
        field_name_pattern = r'(?<=pi-data-label ">).+(?=<\/)'
        field_names = findall(field_name_pattern, html)

        field_value_sub_pattern = r'(?<=pi-data-value ).+?(?=">)'
        html = sub(field_value_sub_pattern, '', html)
        field_value_pattern = r'(?<=pi-data-value ">).+(?=<\/\w+>)'
        field_values = findall(field_value_pattern, html)

        print(field_names)
        print(field_values)

    return details


if __name__ == "__main__":
    # print(search_page('bronze'))
    # print(search_page('the elder'))
    # print(search_page('asdfasdf'))
    # print(get_page_details('elder'))
    print(get_page_details('bronze'))
