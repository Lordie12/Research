# -*- coding: utf-8 -*-
"""
Created on Sun Nov  2 10:39:18 2014

@author: Lanfear
"""

from GetGenes import GetGenes
from BeautifulSoup import BeautifulSoup as BS
import urllib as UL
import urlparse as UP
import urllib2 as UL2
from collections import OrderedDict as OD
import re

moviedict = OD()
sort_order = ['desc', 'asc']
year = ('1980', '1990')
imdb_url = ('http://www.imdb.com/search/title?at=0&release_date=1990,2000&'
            'sort=user_rating,desc&start=1&title_type=feature&country=us')
movie_url = 'http://www.imdb.com'
binfo_url = 'business?ref_=tt_dt_bus'
file_url = ('/Users/Lanfear/Desktop/Research/CLuuData/'
            'TimeWindowResults/moviewindow' + str(year[0]) + '-' +
            str(year[1]) + '.csv')


def modify_url(url=imdb_url, page=1, order='desc', release=(1990, 2000)):
    url_parts = list(UP.urlparse(url))
    query = dict(UP.parse_qsl(url_parts[4]))
    params = {'sort': 'user_rating,' + order,
              'release_date': str(release[0]) + ',' + str(release[1]),
              'start': str(page)}
    query.update(params)
    url_parts[4] = UL.urlencode(query)

    return UP.urlunparse(url_parts)


def get_title_from_soup(soup):
    '''
    Get Movie title from html
    '''
    title = str(soup.find('span', {'class': 'itemprop'}))
    title = title[title.find('"name"') + 7:]
    title = title[:title.find('</sp')]
    return title


def get_rating_from_soup(soup):
    '''
    Method to obtain the movie rating from html
    '''
    rating = soup.find('div',
                       attrs={'class': 'titlePageSprite star-box-giga-star'})
    return float(str(rating.contents[0]).strip(' '))


def get_genre_from_soup(soup):
    '''
    Method to obtain the movie rating from html
    '''
    return [str(genre.contents[0]) for genre in
            soup.findAll('span', {'itemprop': 'genre'})]


def get_budget_from_soup(soup):
    '''
    Method to obtain the movie rating from html
    '''
    cond = soup.findAll('h4', attrs={'class': 'inline'},
                        text=re.compile(r'Budget:'))

    if (len(cond)) == 0:
        #No budget information found, exit
        raise Exception('Budget not found')

    budget = str(cond[0].next).strip(' ')
    if budget.startswith('$') is False:
        #Budget not in USD
        raise Exception('Budget not in $$$')
    return int(budget.replace(',', '')[1:])


def get_gross_from_soup(url):
    '''
    Method to obtain the movie gross from html
    '''
    html = UL2.urlopen(url.rstrip(' ') + binfo_url).read()
    soup = BS(html)
    ginfo = soup.findAll('h5', text=re.compile('Gross'))

    if len(ginfo) == 0:
        raise Exception('Gross info not found')

    gross = str(ginfo[0].next)
    if gross.find('USA') == -1:
        raise Exception('American gross not found')

    return int(gross[2:gross.find('(USA)')].replace(',', ''))


def get_movie_info(movie):
    '''
    Method to obtain the list of movies in the IMDB page
    '''

    G = GetGenes()
    soup = BS(UL2.urlopen(movie_url + movie).read())
    title = get_title_from_soup(soup)
    budget = 0
    gross = 0

    try:
        genes = G.Get_Genes(title)
    except:
        raise Exception('Gene not found')

    try:
        budget = get_budget_from_soup(soup)
    except Exception:
        raise Exception('No budget, skip current movie')

    try:
        gross = get_gross_from_soup(movie_url + movie)
    except Exception:
        raise Exception('No gross info found, skip current movie')

    moviedict[title] = {}
    moviedict[title]['Genes'] = genes
    moviedict[title]['Budget'] = budget
    moviedict[title]['ROI'] = round((0.55 * gross - budget) / float(budget), 6)
    moviedict[title]['Rating'] = get_rating_from_soup(soup)
    moviedict[title]['Genre'] = get_genre_from_soup(soup)


def write_to_file():
    '''
    Method to write dictionary to a csv file
    '''

    f = open(file_url, 'w')
    for movie in moviedict.keys():
        f.write(movie + ',' + str(moviedict[movie]['Rating']) + ',')
        for genre in moviedict[movie]['Genre']:
            f.write(genre + ' ')
        f.write(',' + str(moviedict[movie]['Budget']) + ',')
        f.write(str(moviedict[movie]['ROI']) + ',')
        for gene in moviedict[movie]['Genes']:
            f.write(gene + ',')
        f.write('\n')
    f.close()


def movie_list(order):
    '''
    Method to obtain the list of movies in the IMDB page
    '''

    mc = 1
    page = 1
    while (True):
        url = modify_url(imdb_url, page, order, year)
        print url
        soup = BS(UL2.urlopen(url).read())
        table = soup.find('table', attrs={'class': 'results'})

        for td in table.findAll('tr')[1:]:
            print mc
            row = str(td.findAll('td', attrs={'class': 'image'})[0])
            title = row[row.find('/title'):row.find('title=')].replace('"', '')
            try:
                get_movie_info(title)
                mc += 1
                if (mc > 100):
                    return
            except:
                pass
        page += 50
        print 'Page is ' + str(page)


def main():
    for order in sort_order:
        movie_list(order)

    write_to_file()


if __name__ == '__main__':
    main()
