import configparser
import json
from pathlib import Path
import pickle
import re
import requests

def missle_hashtags():
    return ['ballisticmissile',
            'missle',
            'emergencyalert',
            'alert',
            'nuclear',
            'northkorea']
    return ['ballisticmissle',
            'falsealarm',
            'missle',
            'missilealert',
            'misslealert',
            'apocalypse',
            'nuclearwar']

def missle_query(hashtag):
    return {'query': f'#{hashtag}',
            'fromDate':'201801131800',
            'toDate':'201801140000'}

def perform_query():
    all_tweets = set()
    for hashtag in missle_hashtags():
        post_data = missle_query(hashtag)
        tweets = do_search(post_data)
        all_tweets = all_tweets.union(tweets)
    write_result_file(all_tweets, 'results/input.txt')
    return all_tweets


def write_result_file(tweets, file_path):
    with open(file_path, "w") as f:
        for tweet in list(tweets):
            s = tweet.replace('\n', ' ')
            f.write(f'{s}\n')


def do_search(post_data, all_tweets=set()):
    file_name = query_to_result_file_name(post_data)
    output_file_path = f'results/{file_name}'

    # if output exists, load it
    resp = None
    if Path(output_file_path).is_file():
        print('reading query result from cache...')
        resp = read_output_file(output_file_path)
    else:
        print('Hitting Twitter API:')
        print(post_data)
        resp = search(post_data)
    
    tweets = tweets_from_response(resp)
    set_of_tweets = set(tweets)
    set_of_all_tweets = all_tweets.union(set_of_tweets)
    print(f'new tweets: {len(set_of_tweets)} / {len(set_of_all_tweets)}')
    write_output_file(resp, output_file_path)

    # if page given, recur
    if 'next' in resp:
        next_token = resp['next']
        print(f'getting next page: {next_token}')
        post_data['next'] = next_token
        return do_search(post_data, set_of_all_tweets)
    else:
        print('Done...')
        return set_of_all_tweets

def write_output_file(data, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)

def read_output_file(file_path):
    with open(file_path, 'rb') as f:  
        data = pickle.load(f)
        return data

def get_bearer_token():
    config = configparser.ConfigParser()
    config.read('secret/tokens.txt')
    return config.get("Twitter", "BearerToken", raw=True)
    
def search(post_data):
    url = 'https://api.twitter.com/1.1/tweets/search/fullarchive/development.json'
    headers = {'Authorization': f'Bearer {get_bearer_token()}'}
    r = requests.post(url,
                      headers = headers,
                      json = post_data)
    resp = json.loads(r.text)
    return resp


def query_to_result_file_name(post_data):
    s = ''
    items = list(post_data.items())
    items.sort()
    h = hash(frozenset(items))
    return f'cachefile_{h}.py'


def tweets_from_response(resp):
    tweets = []
    if 'results' not in resp:
        return tweets
    
    results = resp['results']
    for result in results:
        if 'extended_tweet' in result:
            tweets.append(result['extended_tweet']['full_text'])
        else:
            tweets.append(result['text'])
    return tweets


if __name__ == '__main__':
    perform_query()
