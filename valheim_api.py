from requests import get


base_url = 'https://valheim.fandom.com/api.php'


def search(query, search_limit=5):
    query_param = {'action': 'query',
                   'list': 'search',
                   'srsearch': query,
                   'srlimit': search_limit,
                   'srprop': 'sectiontitle',
                   'format': 'json'}
    query_string = '?'
    for key, value in query_param.items():
        query_string += f'&{key}={value}'

    url = base_url + query_string
    print(url)
    response = get(url)
    results = response.json()['query']['search']

    if results:
        return [result['title'] for result in results]
    else:
        return f'No results found for {query}'


def parse():
    # https://valheim.fandom.com/api.php?action=parse&page=bronze&format=json
    pass


if __name__ == "__main__":
    print(search('bronze'))
    print(search('the elder'))
    print(search('asdfasdf'))
