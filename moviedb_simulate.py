import json
import random
from math import exp
import math

word_file = "/usr/share/dict/words"
words= open(word_file).read().splitlines()

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
        votes = random.expovariate(1.0/10000)
    return int(votes)

def sample_movie(min_votes=10000):
    m = {}

    # rating
    m['rating'] = min(max(round(random.normalvariate(4.5, 1.2), 1),1.0),10.0)

    # number of votes (votes)
    m['votes'] = sample_votes(min_votes)
    # title
    title_words = random.sample(words, random.randint(1,4))
    m['title'] = " ".join(title_words)

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
            title_words = random.sample(words, random.randint(1,3))
            m['episode_title'] = " ".join(title_words) + ' (#{}.{})'.format(i+1,k+1)
            m['episode'] = k+1
            m['season'] = i+1
            time_passed = 0.1*(i*number_episodes_per_season+k)
            m['year'] = int(main_movie['year'] + time_passed)
            lamdb = random.uniform(0.1, 1.3)
            m['rating'] = round(math.exp(-lamdb * time_passed) * main_movie['rating'] + random.uniform(-0.3,0.3), 1)
            m['distribution'] = sample_rating_distribution(m['rating'])
            episodes.append(m)

    return episodes

movies = []
episodes = {}
for i in range(1000):
    print "Sampling movie {}".format(i)
    m = sample_movie()
    movies.append(m)
    if random.uniform(0,1)>0.9:
        episodes[m['title']] = sample_episodes(m)

with open('randomdb.json', 'w') as f:
    json.dump({'episodes': episodes, 'movies': movies}, f, indent=4)
