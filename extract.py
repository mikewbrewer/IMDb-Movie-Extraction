import mysql.connector
import requests
import re

from bs4 import BeautifulSoup
from password import PASSWORD




# sets and returns the correct url to be used based on the genre and movie numbers
def getUrl(_movie_count, _genre):
    if (_genre == 'documentary'):
        return ('https://www.imdb.com/search/title/?genres=documentary&start=' + str(_movie_count) + '&explore=genres&ref_=adv_nxt')
    else:
        return ('https://www.imdb.com/search/title/?title_type=feature&genres=' + _genre + '&start=' + str(_movie_count) + '&explore=genres&ref_=adv_nxt')


# find and calculate the number of pages to iterate through based on the number of films in the list
def setMovieCountTotal(_g):
    url_temp = getUrl(1, _g)
    page = requests.get(url_temp)
    soup = BeautifulSoup(page.content, 'html.parser')
    temp = soup.find(class_='desc')

    temp = temp.span.get_text().split()[2]
    temp = temp.replace(',', '')
    print ('total movies: ' + temp)
    return int(temp)


# strip the desired information from the movie container and insert it into the
# movies table
def stripInfo(_movie, _genre, _cursor, _db):
    title = _movie.find(class_ = 'lister-item-header')
    if not(title == None):
        title = title.a.get_text()

    classification = _movie.find(class_='certificate')
    if not(classification == None):
        classification = classification.get_text()

    runtime = _movie.find(class_='runtime')
    if not(runtime == None):
        runtime = runtime.get_text().split()[0]

    year = _movie.find(class_='lister-item-year text-muted unbold')
    if not(year == None):
        year = year.get_text()[-5:-1]

        # make sure the text gather is in the YYYY format, otherwise set to None
        if not(re.search('[0-9][0-9][0-9][0-9]', year)):
            year = None

    rating = _movie.find(class_='inline-block ratings-imdb-rating')
    if not(rating == None):
        rating = rating.get_text().strip()

    metascore = _movie.find(class_='inline-block ratings-metascore')
    if not(metascore == None):
        metascore = metascore.get_text().split()[0]

    # there are few exceptions to the formatting pulled from the HTML, this just makes sure that the script doesn't crash
    # and keeps on chugging
    try:
        _cursor.execute("""
            INSERT INTO movies (title, classification, genre, runtime, release_year, rating, metascore)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (title, classification, _genre, runtime, year, rating, metascore)
        )
    except:
        print ('title:\t' + (title if title is not None else 'None'))
        print ('class:\t' + (classification if classification is not None else 'None'))
        print ('genre:\t' + (_genre if _genre is not None else 'None'))
        print ('rtime:\t' + (runtime if runtime is not None else 'None'))
        print ('year:\t' + (year if year is not None else 'None'))
        print ('rating:\t' + (rating if rating is not None else 'None'))
        print ('meta:\t' + (metascore if metascore is not None else 'None'))

    # commit the insert to the database
    _db.commit()



def extract(_cursor, _db):
    GENRES = ['action', 'adventure', 'animation', 'biography', 'comedy', 'crime', 'documentary', 'drama', 'family', 'fantasy', 'film-noir', 'history', 'horror', 'music', 'musical', 'mystery', 'romance', 'sci-fi', 'sport', 'thriller', 'war', 'western']

    try:
        _cursor.execute("""
            CREATE TABLE movies (
                movie_id INT AUTO_INCREMENT,
                title VARCHAR(200),
                classification VARCHAR(15),
                genre VARCHAR(20),
                runtime INT,
                release_year INT,
                rating DECIMAL(3, 1),
                metascore INT,
                PRIMARY KEY (movie_id)
            )
        """)
        print ('Creating new table...')
        print ()
    except:
        print ('Table already exists...')
        print ()


    upper_limit = 5000

    for genre in GENRES:
        movie_count_total = setMovieCountTotal(genre)

        # get number of pages, 50 items per page
        num_pages = int(movie_count_total / 50)
        print ('Genre:\t\t' + genre)
        print ('Num Pages:\t' + str(num_pages))
        print ()

        movie_index = 1

        for i in range(0, num_pages):
            url = getUrl(movie_index, genre)

            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')

            movies_article = soup.find(class_ = 'article')
            movies_list = movies_article.findAll('div', {'class': 'lister-item mode-advanced'})

            for movie in movies_list:
                stripInfo(movie, genre, _cursor, _db)

            if movie_index < upper_limit:
                movie_index += 50
            else:
                break



if __name__ == '__main__':
    # if run on it's own, this connects the script to the database
    mydb = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        passwd = PASSWORD,
        database = 'pythondatabase',
        auth_plugin = 'mysql_native_password'
    )
    my_cursor = mydb.cursor()

    extract(my_cursor, mydb)
