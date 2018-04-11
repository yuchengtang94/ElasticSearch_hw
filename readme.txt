# Running Instruction
You should start elastic search service first and run this project with following command
```
python index.py 
python query.py 
```
# Files in the folder

#### index.py
Build index for elastic search and provide analyzers, preprocess data.
#### query.py
Run python flask service and provide a simple web page for user to search
#### film_corpus.json
A data file
#### database.db
Database file

## New Function in the program

### index.py 
### get_runtime(runtime)
Transform runtime text to int

### query.py

### extract_phrase(text_query)
Extract phrase in text query before search

### my_highliter(query, origin_text)
a highliter defined by myself to enable highlight the hit in list object (the original highlighter can't do this, may leave out some list element when highlighting)


### Choice for different fields

I created several different analyzers for each field. And create a custom function to highlight those fields might have list object.

#### Analyzer

```
# Define analyzers

title_text_analyzer = analyzer('custom', tokenizer='whitespace')
starring_analyzer = analyzer('custom', tokenizer='pattern', filter=['lowercase', 'stop'])
language_analyzer = analyzer('custom', tokenizer='standard', filter=['lowercase'])
my_analyzer = analyzer('custom', tokenizer = 'standard', filter=['lowercase'], char_filter =['html_strip'])

categories_analyzer = analyzer('custom', tokenizer='pattern', filter=['lowercase'], char_filter =['html_strip'])
# --- Add more analyzers here ---

# Define document mapping
# You can use existed analyzers or use ones you define yourself as above
class Movie(DocType):
    title = Text(analyzer=title_text_analyzer)
    text = Text(analyzer=title_text_analyzer)
    starring = Text(analyzer=starring_analyzer)
    language = Text(analyzer=language_analyzer)
    country = Text(analyzer=my_analyzer)
    director = Text(analyzer=my_analyzer)
    location = Text(analyzer=my_analyzer)
    time = Text(analyzer=my_analyzer)
    categories = Text(analyzer=categories_analyzer)
```

#### custom highlighter
For starring, language, country, director,location, category
```
# This is my custom highlighter for list in elastic search
def my_highliter(query, origin_text):

    if type(origin_text) is not types.UnicodeType:
        for text in query.split(' '):
            for i in range(1, len(origin_text)):
                origin_text[i] = re.sub(text, '<mark>' + text + '</mark>', origin_text[i])

        # print(highlited_result)
    else:
        for text in query.split(' '):
            origin_text = re.sub(text, '<mark>' + text + '</mark>', origin_text)

    return origin_text
```

### conjunctive | disconjunctive search switch

I define a function in query.py to enable this two search. If a conjunctive search can't get a result, it will switch to disconjunctive search in the end and try to get a result.

```
def search_result(is_conjunctive):

....

this is too long


### here is the search part

result_num, resultList = search_result(True)
    gresults = resultList
      
    # if we find the results, extract title and text information from doc_data, else do nothing
    if result_num > 0:
        return render_template('page_SERP.html', results=resultList, res_num=result_num, page_num=page, queries=shows)
    else:
        message = []
        result_num, resultList = search_result(False)
        gresults = resultList

        if result_num > 0 :

            return render_template('page_SERP.html', results=resultList, res_num=result_num, page_num=page,
                                   queries=shows, one_term = True)
        else:
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


```

### phrase query search

first we should extract phrase query

```
def extract_phrase(text_query):
    return re.findall('\"(.*?)\"', text_query), re.sub('\".*?\"', '', text_query)

```
In query search part, we should seperate phrase and word query search
```
            if len(word_query) > 0:
                s = s.query('multi_match', query=word_query, type='cross_fields', fields=['title', 'text'], operator='and')

                # s = s.query('match_phrase', title = text_query)
            # second : search for all phrase_query

            if len(phrase_query) > 0:
                for str in phrase_query:
                    s = s.query('bool', should = [{'match_phrase': {'title' : str}}, {'match_phrase': {'text' : str}}], minimum_should_match = 1)
```


### runtime transformation
Use some regular expression to extract hour and minutes, it is easy.

```
def get_runtime(runtime):
    print(runtime)
    # some runtime box is list type, so we should make a judgement here
    if type(runtime) is not types.ListType:

        minutes = re.findall('(\d+) *min', runtime, flags=re.I)

        hours = re.findall('(\d+) *h', runtime, flags=re.I)

        time_minutes = 0
        for min in minutes:
            time_minutes = time_minutes + int(min)

        for hour in hours:
            time_minutes = time_minutes + 60 * int(hour)

        print(time_minutes)

        return time_minutes
    else:
        time_minutes = 0
        for run_time in runtime:
            time_minutes = time_minutes + get_runtime(run_time)
        print(time_minutes)
        return time_minutes
        
```

#### Running time

```
=== Built index in 1.38510704041 seconds ===
```

And the search speed is very quick.

# Package Used
#### index.py
```
import json
import re
import time
import types

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch_dsl import Index, DocType, Text, Keyword, Integer
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import tokenizer, analyzer
from elasticsearch_dsl.query import MultiMatch, Match
```
#### query.py

```

import re
from flask import *
from index import Movie
from pprint import pprint
from elasticsearch_dsl import Q
from elasticsearch_dsl.utils import AttrList
import types
```

# Test queries examples

Note: Since it is very quick to search in full data file, and it is more convenient for testing. I used full data file to test correctness of my program.

##### simple query
![image](https://lh3.googleusercontent.com/4u2IIngz_wwtTt9QcbPkkZZ7Z1V6y0I1zIu5BDpAlNlTSO23ynFUZdz_rGXgw6SaLewt7ibcYQy91XQqT3rhwFx-gVk6p9_X6YY6whifseDYY6KLL4_60tt1cxO15R1G4JYaUIR_9mAu1aZ831xze4Ij6UVh99u1x1nEuDwngoxR9cjEdItNNi2ZlhKlR8FvAe7AOVCEui82KmlnDt6apiyrmYKX5sCR2lil-ViftJFu5qdHIyWvjEOrEs2QeNyU34r3bUbNJR1sruoCb8uKkEBlKaDyubJ8xkZwpuJ-cNudy_XRiNtWoOuO2BwlTDiWU_qRQhsTpaJiu4c5lBz1Q2k82HU3UWo7cFnFDhO1UNQTS2ZCaYqHBFLjvj6qto5ZKntUjsgMa_IzTcx6MLt5tc5Jo9VU_zzEEMK9Mj_fi9274TJjwBbEHoikJrAJDPpwvwAH7qGzGrcxpry5-_JtApIQVFrXFvUkQbSGG8kzpqDxzIHMLcnLX9WB45iASTYvf2V1-Htf5O-jcoKjWn5Bzr0d2ZGwYDEiCvd-Q0tdckqcgouwPrhZ1zC5f6D7KdHEciIK5cv0MkQ2IYuJC_VyVIkJoJrsaxhGlHUH9m4=w388-h220-no)

As we can see, there are 85 hits in the search result.
All contains query.
Seems good.

### Add some unkown words in it.

![image](https://lh3.googleusercontent.com/_bFIutWJQh5j5nWxRcakDDWIlDFN_N2Tfi65LskGLGbQ7w4oSLCQn8UbuHOJcqdyJY6I5DOtj9hQyopsTBO1jP91cmGGEq6rwSHbQSVukJ4y_5PlopR2ZLNB2sT5SHvRnGwidI9-_VzhXYMEf52iOI0hopG7szWzj_PVRWV2Tc1dOUe6xRapZ-75AavRdKgEKM3qH4wXqAhSFTzSJGXtRc4VyRhKAsx7oStuwWqWdg00y0PFNZuK8sh0DrwIsafPmmCyl1YbwEs0SGquaKZkX7NzHqm4ke4pdV5OJfj8x8fVCp82-V3Fq_oOsqHzYrk60TpjoV2a2vNMCwkD1GG_TC18zezP5G1lJU0pjFxnl_2y7GZdqBCVgk-Dx2cdKv7MMroLOyuC6YLR8gIxYlSJH4pZssg5yNxZrGsrz-BKezp-ylOt9bGZqpB1swirIfR5f_PooD8rMU0bm1is4h4oycbQSmX7hd4aGCUyVHdRi9Cf7H3VbpkdU2jxu_fBAhrlXA2WIqAHRxN6rFdm9QFxbyaDDJqhWNNOeN0WQM35zJYk_NKNyQu3te5v1loDe7TuGGkZNfBaVBgXfCQLvNOySlg6bhqzWTq3KWXxBco=w3124-h1952-no)

It can do disjunctive search correctly and give user hint.

### phrase query vs non - phrase query:

non phrase query 50 correct hits

![image](https://lh3.googleusercontent.com/R6XQxmoSuBlA7JP0IImzn1kg9ENoiz3z3kGmGIlm0WYmUrgAR73e61ve5JVIvubxfdKSCyvU1OtcYGb6yT8rg8aJ1YoTPtwW0TltAgSnmCez671EsXAMN9TPXzB7XUqJDkXUkB963lPXRnOP_gdBaveZ0yM0LLEvaZKtWMg3D4OhVy1OsjNR-p5MmOJNKsEVISzMtvCnCL5Grw29cJzoIppfG-bRZVSiapiWH_SfdcroeVdCzKFyE9ASHUeLllDwOCb4fxZiCkWQq6b9dGxKDNKPdTKb5l1W0Sq3rzzQbSlCGvegOzTqFnVP_Oam4caZ2tm-dIW7i683Nbbtz_35n9x7_Es7aOg8zC1Am1nVZZPKg5anfe9L_UeDLJPeyXmN4Kmf3hyENo3bgtrGr5eZQaaKYGO7iFKd90i3qCR_cAX4NXWuXCpK90C8EL7wq7O8dtmr_-HirsBmMHUMR1At3o0YMAW-LqoYHy4M8k1QR3fnl7GePh1HfjyNQTA__oXLrzt7ZEmvRJaEXui8wyK9B_pRDAeTGhabwfrQz37E7K8Yz0wDHgBdFB1-xXyIlNr1C3xUSAF18nOP6AjX6-6jZCsCdrwqaFEqLpCv1ww=w3124-h1952-no)

phrase query 5 correct hits with highlight

![image](https://lh3.googleusercontent.com/M87M8goXSCk2tMqhqss9y0dQLaJ8MqJFu8gwGh28dhP02-oAlm-HPqCiQVHrPvPx_MMDTbNRzHcyn7UOrHIaxqku0HF5XlLoUi2GAjdZQzzu9LAPZMUbCBm4Vp3XldM6j1j3s7d7UAK-kQ_Nxcc7DHKPkgE5qrVAdk89p1rXMW-mL7-2C-f3TR0OO9riC6-iBoQvoXOyOA1utmL6qAFo2wp-H-Pol3V7X_wkVuz9DBRTzm5enun47jF_FV_pyPtVaMnz3V9rru9EHcRzAKmTaZE2RubXTDS6Vp6x8i3rcS51ixeUS8qoO4VntmsexpJrRefamsoFgiTLFut6SPc6luNzPdMbn0PIfXrew4mw0s5y5UW3vA_rUWyMlu4MH56rWM-m2LBaMdIX6tYhhVVlx3XGX06MKvUPVoKyMf-3PWrJH_mKN5GWmeXfYHqa4G_6H33QD7UYv2iC2p_oGXroIy4sxq9tUEMBsOmRg9GF5rbBmZcDVSYL9s1sJ22qG_8MzwA8BRf09KWzNl60mDJZCKkw4ZTF3ChYXIqrQP9AW6OYlK8i1hfKiQRfiWnmA9n7M7XHq-0al41bq67fhTVPnYHjeqPUK5pwPSubT00=w3124-h1952-no)


we can see it can handle phrase query effectively

Still good!

### Highlight

Query:
text : market
starring : Jurdi


we will get only one result:

![image](https://lh3.googleusercontent.com/UxU3aeQSFSMGHtH-a2EFwICz52LdNVsufuY7BiNJs7tUQlSDUqLZb2YgBOD6C689Za1P5813amKJq6RrKsG53YRkkB6Qwb3X0kFWW1_62Npi1SzErCje62IGnpN2FSZMEKIZMMq9uT8vnhMXGUnmdrAsKkZgJq8uTc_qH5OY86SAcGWE381Z_AUT2Pplyjvrif2hD5q1Lc8vT7thc6HBF8MgKyOefLjM2AG7E0_Um1Yg_Y7aboDAqaHdmxP9PSfouVltDmWtci-bEpbUKLdlePKW7DXWcWYIWHmX87WuSgRJ45iMQ14M3XxWdjC7wUVu_gQquOnuAYUI2mipz2b4tTd6LVCr3s-XiL316llBV-ztn4H0MBYivTvPe36s2kKbhe6QG6hYN4F-tR_UWDKDrZnf3nMWubJHacgmkrzD_MF2J_QwlPtlnff02Lodn0mVc7s9SIZS_P9IVRUww1Ic0rniuOw-ULntjGq4nXfUaJyKFYm7yluvjpNIimUj7iVXT1DLhKoj88InH7PfJu7Orhj1k06VAXZ7Rij3FkDa1PxtOvijf4_KDUN_oEPY7eFbjv0fQGTs0g9NQ6yKOHu_v1bgQozRdRr2Fcf6X5Y=w3338-h1514-no)

It is highlighted correctly.

If you test for more example in different fields, it also work correctly. Here I just pick some important part to show.

### After testing, we verify our search engine works correctly! That's great!!

# notes & thoughts

In this program, I established a fantastic elastic search system, and I found it very powerful. But there is still space to improve. Like enable first name, last name search for starring and director, or improve for some other specific fields with different search techniques. But those are difficult to implement. I've also try to use whitespace tokenizer to solve the problem that some text with hyphen and apostrophe boundaries maybe split, but however I still can't solve this problem.

This project is interesting and looks like a real application, it is great.