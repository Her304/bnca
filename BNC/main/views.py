from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
import psycopg2
import markdown


def home(response):
    return render(response, "main/home.html", {})

def news(response):
    #connect to the database
    conn = psycopg2.connect(
        dbname="news_db",
        user="hercules",
        password="",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    #get all th info from database
    cur.execute("SELECT * FROM news_articles ORDER BY published_date DESC")
    rows = cur.fetchall()

    today_news = {}
    for i in rows:
        title = i[1]
        summary = i[2]
        url = i[3]
        date = i[4]
        analysis_text = i[5]

        #change the markdown text into html text
        if analysis_text:
            html_analysis = markdown.markdown(analysis_text)
        else:
            html_analysis = "We apologise for missing the analysis"

        today_news[title] = [summary, url, date, html_analysis]
    
    cur.close()
    conn.close()
    
    return render(response, "news.html", {"today_news":today_news})


