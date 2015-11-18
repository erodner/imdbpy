import argparse

parser = argparse.ArgumentParser(description='Script for simple movie statistics',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('input', help='input JSON file')
args = parser.parse_args()

import json

with open(args.input, 'r') as f:
    db = json.load(f)

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
