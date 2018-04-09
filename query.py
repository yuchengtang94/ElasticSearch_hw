
import re
from flask import *
from index import Movie
from pprint import pprint
from elasticsearch_dsl import Q
from elasticsearch_dsl.utils import AttrList


app = Flask(__name__)

# Initialize global variables for rendering page
tmp_text = ""
tmp_title = ""
tmp_star = ""
# add by me
tmp_runtime = ""
tmp_language = ""
tmp_country = ""
tmp_director = ""
tmp_location = ""
tmp_time = ""
tmp_categories = ""
#
tmp_min = ""
tmp_max = ""
gresults = {}

@app.route("/")
def search():
    return render_template('page_query.html')

def extract_phrase(text_query):
    return re.findall('\"(.*?)\"', text_query), re.sub('\".*?\"', '', text_query)

@app.route("/results", defaults={'page': 1}, methods=['GET','POST'])
@app.route("/results/<page>", methods=['GET','POST'])
def results(page):
    global tmp_text
    global tmp_title
    global tmp_star
    # add by me
    # global tmp_runtime
    global tmp_language
    global tmp_country
    global tmp_director
    global tmp_location
    global tmp_time
    global tmp_categories

    # global tmp_phrase


    global tmp_min
    global tmp_max
    global gresults
    
    if type(page) is not int:
        page = int(page.encode('utf-8'))    
    # if the method of request is post, store query in local global variables
    # if the method of request is get, extract query contents from global variables  
    if request.method == 'POST':
        text_query = request.form['query']
        star_query = request.form['starring']
        # add by me
        # runtime_query = request.form['runtime']
        language_query = request.form['language']
        country_query = request.form['country']
        director_query = request.form['director']
        location_query = request.form['location']
        time_query = request.form['time']
        categories_query = request.form['categories']


        #
        mintime_query = request.form['mintime']
        if len(mintime_query) is 0:
            mintime = 0
        else:
            mintime = int(mintime_query)
        maxtime_query = request.form['maxtime']
        if len(maxtime_query) is 0:
            maxtime = 99999
        else: 
            maxtime = int(maxtime_query)

        # update global variable template date
        tmp_text = text_query
        tmp_star = star_query
        tmp_min = mintime
        tmp_max = maxtime

        # add by me

        # tmp_runtime = runtime_query
        tmp_language = language_query
        tmp_country = country_query
        tmp_director = director_query
        tmp_location = location_query
        tmp_time = time_query
        tmp_categories = categories_query
        #
    else:
        text_query = tmp_text
        star_query = tmp_star
        mintime = tmp_min
        if tmp_min > 0:
            mintime_query = tmp_min
        else:
            mintime_query = ""
        maxtime = tmp_max
        if tmp_max < 99999:
            maxtime_query = tmp_max
        else:
            maxtime_query = ""
        # add by me
        # runtime_query = tmp_runtime
        language_query = tmp_language
        country_query = tmp_country
        director_query = tmp_director
        location_query = tmp_location
        time_query = tmp_time
        categories_query = tmp_categories

    # add by me
    phrase_query, word_query = extract_phrase(text_query)
    # store query values to display in search box while browsing
    shows = {}
    shows['text'] = text_query
    shows['star'] = star_query
    # add by me
    # shows['runtime'] = runtime_query
    shows['language'] = language_query
    shows['country'] = country_query
    shows['director'] = director_query
    shows['location'] = location_query
    shows['time'] = time_query
    shows['categories'] = categories_query
    #
    shows['maxtime'] = maxtime_query
    shows['mintime'] = mintime_query
       
    # search
    search = Movie.search()
    
    # search for tuntime
    s = search.query('range', runtime={'gte':mintime, 'lte':maxtime})

    # search for matching text query
    # first : search for all word query(single word with no phrase)

    if len(word_query) > 0:
        s = s.query('multi_match', query=word_query, type='cross_fields', fields=['title', 'text'], operator='and')

        # s = s.query('match_phrase', title = text_query)
    # second : search for all phrase_query

    if len(phrase_query) > 0:
        for str in phrase_query:
            s = s.query('bool', should = [{'match_phrase': {'title' : str}}, {'match_phrase': {'text' : str}}], minimum_should_match = 1)

    # search for matching stars
    # You should support multiple values (list)
    if len(star_query) > 0:
        s = s.query('match', starring=star_query)

    if len(language_query) > 0:
        s = s.query('match', language=language_query)

    if len(country_query) > 0:
        s = s.query('match', country=country_query)

    if len(director_query) > 0:
        s = s.query('match', director=director_query)

    if len(location_query) > 0:
        s = s.query('match', location=location_query)

    if len(time_query) > 0:
        s = s.query('match', time=time_query)

    if len(categories_query) > 0:
        s = s.query('match', categories=categories_query)


    # highlight
    s = s.highlight_options(pre_tags='<mark>', post_tags='</mark>')
    s = s.highlight('text', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('title', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('language', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('country', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('director', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('location', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('time', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('categories', fragment_size=999999999, number_of_fragments=1)

    # extract data for current page
    start = 0 + (page-1)*10
    end = 10 + (page-1)*10

    # execute search
    response = s[start:end].execute()

    # insert data into response
    resultList = {}
    for hit in response.hits:
        result={}
        result['score'] = hit.meta.score

        if 'highlight' in hit.meta:
            if 'title' in hit.meta.highlight:
                result['title'] = hit.meta.highlight.title[0]
            else:
                result['title'] = hit.title

            if 'text' in hit.meta.highlight:
                result['text'] = hit.meta.highlight.text[0]
            else:
                result['text'] = hit.text
            ## add by me
            if 'language' in hit.meta.highlight:
                result['language'] = hit.meta.highlight.language[0]
            else:
                result['language'] = hit.language

            if 'country' in hit.meta.highlight:
                result['country'] = hit.meta.highlight.country[0]
            else:
                result['country'] = hit.country

            if 'director' in hit.meta.highlight:
                result['director'] = hit.meta.highlight.director[0]
            else:
                result['director'] = hit.director

            if 'location' in hit.meta.highlight:
                result['location'] = hit.meta.highlight.location[0]
            else:
                result['location'] = hit.location

            if 'time' in hit.meta.highlight:
                result['time'] = hit.meta.highlight.time[0]
            else:
                result['time'] = hit.time

            if 'categories' in hit.meta.highlight:
                result['categories'] = hit.meta.highlight.categories[0]
            else:
                result['categories'] = hit.categories
            #

        else:
            result['title'] = hit.title
            result['text'] = hit.text
            ## add by me
            result['language'] = hit.language
            result['country'] = hit.country
            result['director'] = hit.director
            result['location'] = hit.location
            result['time'] = hit.time
            result['categories'] = hit.categories
            ##

        resultList[hit.meta.id] = result

    gresults = resultList
    
    # get the number of results
    result_num = response.hits.total
      
    # if we find the results, extract title and text information from doc_data, else do nothing
    if result_num > 0:
        return render_template('page_SERP.html', results=resultList, res_num=result_num, page_num=page, queries=shows)
    else:

        message = []
        if len(text_query) > 0:
            message.append('Unknown search term: '+text_query)
        if len(star_query) > 0:
            message.append('Cannot find star: '+star_query)
        if len(language_query) > 0:
            message.append('Cannot find language: '+language_query)
        if len(country_query) > 0:
            message.append('Cannot find country: '+country_query)
        if len(director_query) > 0:
            message.append('Cannot find director: '+director_query)
        if len(location_query) > 0:
            message.append('Cannot find location: '+location_query)
        if len(time_query) > 0:
            message.append('Cannot find time: '+time_query)
        if len(categories_query) > 0:
            message.append('Cannot find categories: '+categories_query)
        
        return render_template('page_SERP.html', results=message, res_num=result_num, page_num=page, queries=shows)


@app.route("/documents/<res>", methods=['GET'])
def documents(res):
    global gresults
    film = gresults[res.encode('utf-8')]
    filmtitle = film['title']
    for term in film:
        if type(film[term]) is AttrList:
            s = "\n"
            for item in film[term]:
                s += item + ",\n "
            film[term] = s
    movie = Movie.get(id=res, index='sample_film_index')
    filmdic = movie.to_dict()
    film['runtime'] = str(filmdic['runtime']) + " min"
    return render_template('page_targetArticle.html', film=film, title=filmtitle)

if __name__ == "__main__":
    app.run()
