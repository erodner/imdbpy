""" The following script downloads IMDB ratings and
    saves a part of these results as a JSON file.
    The author of the script does not take any warranty for
    the damage this script might cause.

    Author: Erik Rodner (2015)
"""
copyright = """

    Use this software and it's created data
    at your own risk. Only a small part of the IMDB data should be
    used and only for individual and personal use.

    IMDB: http://www.imdb.com/help/show_leaf?usedatasoftware
    Information courtesy of IMDb (http://www.imdb.com).

"""

import json
import re
import urllib2
import gzip
from StringIO import StringIO
import argparse

mirrors = {'berlin': 'ftp://ftp.fu-berlin.de/pub/misc/movies/database/ratings.list.gz',
           'sweden': 'ftp://ftp.sunet.se/pub/tv+movies/imdb/ratings.list.gz',
           'finland': 'ftp://ftp.funet.fi/pub/mirrors/ftp.imdb.com/pub/ratings.list.gz'}

parser = argparse.ArgumentParser(description='Script for IMDB ratings parsing',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--minvotes', help='minimum number of votes needed', default=10000, type=int)
parser.add_argument('--mirror', help='specify mirror site to use', choices=mirrors.keys(), default='berlin')
args = parser.parse_args()

# minimum number of votes needed to be added in the database
min_votes = args.minvotes
# regular expression for a single line in the ratings file
# there are a few movies where this expression doesn't work, but
# these movies shouldn't be part of our small dataset anyway
line_pattern = '^\s*([\.\d\*]+)\s+(\d+)\s+([\d\.]+)\s+"?(.+?)"?\s+\((\d\d\d\d).*?\)\s*(.*?)$'
# regular expression for a single episode
episode_pattern = '^\s*\{(.+?)\}\s*$'
# regular expression to extract episode season and number
episode_numbers_pattern = '\(#(\d+)\.(\d+)\)\s*$'
# URL to the ratings file we are downloading
# http://www.imdb.com/interfaces
ratings_link = mirrors[args.mirror]

#
#
# Downloading the ratings file and open gzip stream
print ("Opening connection...")
response = urllib2.urlopen(ratings_link)
print ("Downloading file...")
buf = StringIO( response.read() )

print ("Processing file...")
f = gzip.GzipFile(fileobj=buf)

# counting the lines processed
line_count = 0

# this is the total number of lines in the ratings.list file currently
total_count = 663327

# initializing the database
movies = []
episodes = {}
movies_set = set()
copying_policy_section = False

rating_error = 0.0
rating_error_num = 0
for line in f:
    # display a small progress bar
    line_count += 1
    if line_count % 10000 == 1 or line_count == total_count:
        print ("{:4.2f}% read from the database".format(line_count*100.0/total_count))

    # regular expression matching for movies or episodes
    m = re.match(line_pattern, line)
    if m:
        distribution, number_of_votes, rating, title, year, episode = m.groups(0)
        number_of_votes = int(number_of_votes)
        rating = float(rating)
        year = int(year)

        # The distribution of votes is given as a string
        # with the following characters for each rating

        # "." no votes cast        "3" 30-39% of the votes  "7" 70-79% of the votes
        # "0"  1-9%  of the votes  "4" 40-49% of the votes  "8" 80-89% of the votes
        # "1" 10-19% of the votes  "5" 50-59% of the votes  "9" 90-99% of the votes
        # "2" 20-29% of the votes  "6" 60-69% of the votes  "*" 100%   of the votes

        vote_sum = 0.0
        mean_rating = 0.0
        single_votes = []
        for index, l in enumerate(list(distribution)):
            if l == '.':
                p = 0
            elif l == '*':
                p = 1.0
            else:
                p = (int(l)*10 + 5)/100.0
            vote_sum += p
            mean_rating += p*(index+1)
            single_votes.append(p)

        mean_rating /= vote_sum
        single_votes = [ v/vote_sum for v in single_votes ]

        rating_error += abs(mean_rating - rating)
        rating_error_num += 1

        stats = {'votes': number_of_votes, 'rating': rating, 'year': year,
                'title': title, 'distribution': single_votes}

        m_episode = re.match(episode_pattern, episode)
        if m_episode and title in movies_set:
            # this is an episode, add it no matter the number of votes
            episode_title = m_episode.groups(0)[0]
            if not title in episodes:
                episodes[title] = []

            # get the season or episode if possible
            m_episode_numbers = re.search(episode_numbers_pattern, episode_title)
            if m_episode_numbers:
                stats['season'] = int(m_episode_numbers.groups(0)[0])
                stats['episode'] = int(m_episode_numbers.groups(0)[1])

            stats['episode_title'] = episode_title
            episodes[title].append ( stats )

        elif number_of_votes > min_votes:
            # add the movie
            movies.append(stats)
            movies_set.add(title)

    else:
        #print ("The following line can not be parsed: {}".format(line)

        # find the COPYING POLICY section
        if line.find('COPYING POLICY') >= 0:
            copying_policy_section = True

        # add the COPYING POLICY section
        if copying_policy_section:
            copyright += line

# print some statistics
rating_error /= rating_error_num
print ("Error for the rating estimation according to the distribution: {}".format(rating_error))
print ("Number of movies in the database: {}".format(len(movies)))
print ("Number of series in the database: {}".format(len(episodes)))

# output the resulting dataset subset in a json file together
# with the copyright
with open('imdb.json', 'w') as f:
    json.dump({'movies': movies, 'episodes': episodes, 'copyright': copyright},
            f, encoding='latin1', indent=4)
