
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
tmp_min = ""
tmp_max = ""
gresults = {}

@app.route("/")
def search():
    return render_template('page_query.html')

@app.route("/results", defaults={'page': 1}, methods=['GET','POST'])
@app.route("/results/<page>", methods=['GET','POST'])
def results(page):
    global tmp_text
    global tmp_title
    global tmp_star
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
    
    # store query values to display in search box while browsing
    shows = {}
    shows['text'] = text_query
    shows['star'] = star_query
    shows['maxtime'] = maxtime_query
    shows['mintime'] = mintime_query
       
    # search
    search = Movie.search()
    
    # search for tuntime
    s = search.query('range', runtime={'gte':mintime, 'lte':maxtime})
    
    # search for matching text query
    if len(text_query) > 0:
        s = s.query('multi_match', query=text_query, type='cross_fields', fields=['title', 'text'], operator='and')
    
    # search for matching stars
    # You should support multiple values (list)
    if len(star_query) > 0:
        s = s.query('match', starring=star_query)
    
    # highlight
    s = s.highlight_options(pre_tags='<mark>', post_tags='</mark>')
    s = s.highlight('text', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('title', fragment_size=999999999, number_of_fragments=1)
    
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
                
        else:
            result['title'] = hit.title
            result['text'] = hit.text
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