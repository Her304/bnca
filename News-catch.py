import psycopg2
from newscatcher import Newscatcher
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

#load the api keys from .env
load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

DATABASE_URL = os.environ.get('DATABASE_URL')

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("Successfully connected to the Railway database!")
except Exception as e:
    print(f"Database connection failed: {e}")




#connect to database
cur = conn.cursor()

#catch the news
nc = Newscatcher(website = 'cnbc.com', topic = "business")
results = nc.get_news()

    # results.keys()
    # 'url', 'topic', 'language', 'country', 'articles'

# Get the articles
articles = results['articles']

#dictionary for today news, for storing top 10 business news from all the news
today_news = {}

for i in range(0,10):
    #format the date
    p_date = articles[i].get('published_parsed')
    if p_date:
        p_date= datetime(*p_date[:6])
    else:
        p_date= None
    today_news[f"{articles[i]['title']}"] = [f"{articles[i]['summary']}", f"{articles[i]['link']}", p_date]

    #title : [summary, full url, date]

p_news = today_news.items()

#save all the news into database
for i in p_news:
    title = i[0]
    summary= i[1][0]
    url=i[1][1]
    date=i[1][2]
    
    analysis_text = None
    retries = 0
    max_retries = 4

    #ask ai to gen summary and save it
    while analysis_text is None and retries < max_retries:
        #ask ai to generate the summary
        ai_response = client.responses.create(
                    model="gpt-4.1-nano",
                    input= f"Analyze this news as a business professor: {title}. Summary: {summary}. Please apply different model, including but not limited on: SWOT, key success factors, PEST, diamond-E etc. limited you response with 300 words and divide different part of model, no any greeting words, thanks for help "
                )
        #abstract the text from all the data
        analysis_text = ai_response.output_text
        retries += 1
        if not analysis_text:
            print(f"analysis is not working, trying the {retries+1} times")


    #save all the info into db    
    cur.execute("""INSERT INTO news_articles (title, summary, url, published_date, analysis) VALUES (%s, %s, %s, %s, %s)""", (title, summary, url, date, analysis_text))
    if analysis_text:
        print(f"saved:{title}")
    else:
        print(f"fail to anaylsis{title}")
        

conn.commit()
cur.close()
conn.close()

print("News articles saved to database successfully")


