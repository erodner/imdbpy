import json
import random
from math import exp
import math

import argparse

parser = argparse.ArgumentParser(description='Script for generation of a random movie database',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('words', help='input word list', default='/usr/share/dict/words')
args = parser.parse_args()


words= open(args.words).read().splitlines()

def sample_rating_distribution(rating):
    # distribution
    mean_rating = -1.0
    tries = 0
    while abs(mean_rating - rating)>0.1 and tries<100:
        tries += 1
        dist = [ random.expovariate(exp(abs(rating - i))) for i in range(10) ]
        sum_dist = sum(dist)
        dist = [ d/sum_dist for d in dist ]
        mean_rating = sum( [ (index+1)*d for index, d in enumerate(dist) ] )
    return dist

def sample_votes(min_votes=10000):
    votes = 0
    while votes < min_votes:
        votes = random.expovariate(1.0/50000)
    return int(votes)

def sample_title(max_words=4):
    title_words = random.sample(words, random.randint(1,max_words))
    t = " ".join(title_words)
    t = t.lower().capitalize()
    return t


def sample_movie(min_votes=10000, movies_so_far=set()):
    m = {}

    # rating
    m['rating'] = min(max(round(random.normalvariate(4.5, 1.6), 1),1.0),10.0)

    # number of votes (votes)
    m['votes'] = sample_votes(min_votes)
    # title
    while 'title' not in m or m['title'] in movies_so_far:
        m['title'] = sample_title()

    # rating distribution
    m['distribution'] = sample_rating_distribution(m['rating'])

    # year
    m['year'] = min(int(random.normalvariate(2000,5)),2015)

    return m

def sample_episodes(main_movie):
    number_seasons = max(min(int(random.gauss(3,2)),10),1)
    number_episodes_per_season = max(min(int(random.gauss(15,3)),25),1)

    episodes = []
    for i in range(number_seasons):
        for k in range(number_episodes_per_season):
            m = {}
            m['votes'] = sample_votes(2000)
            m['episode_title'] = sample_title() + ' (#{}.{})'.format(i+1,k+1)
            m['episode'] = k+1
            m['season'] = i+1
            time_passed = 0.1*(i*number_episodes_per_season+k)
            m['year'] = int(main_movie['year'] + time_passed)
            lamdb = random.uniform(0.1, 1.3)
            m['rating'] = round(math.exp(-lamdb * time_passed) * main_movie['rating'] + random.uniform(-0.3,0.3), 1)
            m['distribution'] = sample_rating_distribution(m['rating'])
            episodes.append(m)

    return episodes

def sample_sequels(main_movie):
    num_sequels = random.randint(2,8)
    sequels = []
    for k in range(num_sequels):
        m = {}
        # rating
        lamdb = random.uniform(0.1, 1.3)
        m['rating'] = round(math.exp(-lamdb * (k+1)) * main_movie['rating'] + random.uniform(-0.3,0.3), 1)
        # number of votes (votes)
        m['votes'] = sample_votes(main_movie['votes'])
        # title
        m['title'] = "{} {}".format(main_movie['title'],k+2)

        # rating distribution
        m['distribution'] = sample_rating_distribution(m['rating'])

        # year
        m['year'] = int(main_movie['year']+k+1+random.uniform(0,5))

        sequels.append(m)

    return sequels



movies = []
episodes = {}
movies_so_far = set()
for i in range(1000):
    print ("Sampling movie {}".format(i))
    m = sample_movie(movies_so_far=movies_so_far)
    movies_so_far.add(m['title'])
    movies.append(m)
    if random.uniform(0,1)>0.9:
        print ("Sampling episodes")
        episodes[m['title']] = sample_episodes(m)
    elif random.uniform(0,1)>0.9:
        print ("Sampling sequels")
        movies.extend(sample_sequels(m))

with open('randomdb.json', 'w') as f:
    json.dump({'episodes': episodes, 'movies': movies}, f, indent=4)
