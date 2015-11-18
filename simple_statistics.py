import argparse

parser = argparse.ArgumentParser(description='Script for simple movie statistics',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('input', help='input JSON file')
parser.add_argument('--movie', help='specific movie for which sequels are shown', default='Demagogue')
args = parser.parse_args()

import json

with open(args.input, 'r') as f:
    db = json.load(f)

# find a specific movie
for movie in db['movies']:
    t = movie['title']
    if t.find(args.movie)==0:
        print ("{} ({}): {}".format(movie['title'], movie['year'], movie['rating']))

# movies for 2017
for movie in db['movies']:
    if movie['year']==2017:
        print ("{} ({})".format(movie['title'], movie['year']))

# get the best movie
max_rating = -1.0
for movie in db['movies']:
    if movie['rating'] > max_rating:
        max_rating = movie['rating']
        max_movie = movie

print ("Best movie {} with rating {}".format(max_movie['title'], max_rating))

for movie in db['movies']:
    if movie['rating'] > 9.0 and movie['votes'] > 50000:
        print ("Good movie {} ({}) with rating {}".format(movie['title'], movie['year'], movie['rating']))

sum_rating_per_year = {}
num_movies_per_year = {}
for movie in db['movies']:
    y = movie['year']
    if not y in sum_rating_per_year:
        sum_rating_per_year[y] = 0
        num_movies_per_year[y] = 0
    sum_rating_per_year[y] += movie['rating']
    num_movies_per_year[y] += 1

for y in sum_rating_per_year:
    print ("mean rating in {} ({} movies): {}".format(y,
        num_movies_per_year[y], sum_rating_per_year[y]/num_movies_per_year[y]))

# maximally diverse votes
max_var_rating = -1
for movie in db['movies']:
    mean_rating = sum([ d * (index+1) for index, d in enumerate(movie['distribution']) ])
    var_rating = sum([d * (index+1-mean_rating)**2 for index, d in enumerate(movie['distribution'])])
    if var_rating > max_var_rating:
        max_var_rating = var_rating
        diverse_movie = movie

from pprint import pprint
print ("The movie with the most diverse ratings is: {}".format(diverse_movie['title']))
print ("Ratings are {}".format(diverse_movie['distribution']))
