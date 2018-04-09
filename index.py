import json
import re
import time

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch_dsl import Index, DocType, Text, Keyword, Integer
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import tokenizer, analyzer
from elasticsearch_dsl.query import MultiMatch, Match


# Connect to local   host server
connections.create_connection(hosts=['127.0.0.1'])

# Establish elasticsearch
es = Elasticsearch()

# Define analyzers

my_analyzer = analyzer('custom',
                       tokenizer='standard',
                       filter=['lowercase', 'stop'])
# --- Add more analyzers here ---

# Define document mapping
# You can use existed analyzers or use ones you define yourself as above
class Movie(DocType):
    title = Text(analyzer=my_analyzer)
    text = Text(analyzer='simple')
    starring = Text(analyzer=my_analyzer)
    language = Text(analyzer=my_analyzer)
    country = Text(analyzer=my_analyzer)
    director = Text(analyzer=my_analyzer)
    location = Text(analyzer=my_analyzer)
    time = Text(analyzer=my_analyzer)
    categories = Text(analyzer=my_analyzer)

    runtime = Integer()
    # --- Add more fields here ---
    
    class Meta:
        index = 'sample_film_index'
        doc_type = 'movie'

    def save(self, *args, **kwargs):
        return super(Movie, self).save(*args, **kwargs)

# Populate the index
def buildIndex():
    film_index = Index('sample_film_index')
    if film_index.exists():
        film_index.delete()  # Overwrite any previous version
    film_index.doc_type(Movie) # Set doc_type to Movie
    film_index.create()
    
    # Open the json film corpus
    with open('films_corpus.json') as data_file:
        movies = json.load(data_file)
        size = len(movies)
    
    # Action series for bulk loading
    actions = [
        {
            "_index": "sample_film_index",
            "_type": "movie",
            "_id": mid,
            "title":movies[str(mid)]['title'],
            "text":movies[str(mid)]['text'],
            "starring":movies[str(mid)]['starring'],
            "runtime": "0", #movies[str(mid)]['runtime'] # You would like to convert runtime to integer (in minutes)
            # --- Add more fields here ---
            "language": movies[str(mid)]['language'],
            "country": movies[str(mid)]['country'],
            "director": movies[str(mid)]['director'],
            "location": movies[str(mid)]['location'],
            "time": movies[str(mid)]['time'],
            "categories": movies[str(mid)]['categories']
        }
        for mid in range(1, size+1)
    ]
    
    helpers.bulk(es, actions) 
    
def main():
    start_time = time.time()
    buildIndex()
    print("=== Built index in %s seconds ===" % (time.time() - start_time))
        
if __name__ == '__main__':
    main()   