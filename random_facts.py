from ast import literal_eval
from random import choice
from requests import get

api_list = ['https://thefact.space/random',
            'https://uselessfacts.jsph.pl/random.json?language=en']


# Return a tuple of the fact text and source url
def get_random_fact():
    response = get(choice(api_list))
    content_dict = literal_eval(response.text)
    if 'source_url' in content_dict:
        return content_dict['text'], content_dict['source_url'].replace('\\', '')
    else:
        return content_dict['text'], content_dict['source']


if __name__ == "__main__":
    print(get_random_fact())
