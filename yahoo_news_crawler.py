#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup
import mysql.connector
import configparser
import sys
import datetime

def crawler(cate,cate_id,conn):
    baseurl = 'https://tw.news.yahoo.com'
    url = baseurl + '/' + cate_id +'/archive'
    r = requests.get(url)
    
    if r.status_code == requests.codes.ok:
      soup = BeautifulSoup(r.text, 'html.parser')
      stories = soup.find_all('div', 'Py(14px) Pos(r)')
      for s in stories:
        news = []
        #cate_id
        news.append("'"+cate_id+"'")
        
        #author
        newsfrom = s.find("div", class_ = "C(#959595) Fz(13px) C($c-fuji-grey-f) Fw(n)! Mend(14px)! D(ib) Mb(6px)").string
        news.append("'"+newsfrom.split(' • ')[0].replace("'","\\'")+"'")
        
        #title
        title = s.find("h3", class_ = "Mb(5px)").text 
        news.append("'"+title.replace("\u3000"," ").replace("'","\\'")+"'") 

        #brief
        content = s.find("p", class_ = "Mt(8px) Lh(1.4) Fz(16px) C($c-fuji-grey-l) LineClamp(2,44px) M(0)").string
        try:
            content.replace("'","\\'")
            news.append("'"+content.replace("'","\\'")+"'")
        except Exception as e:
            news.append("''")

        
        #url/nid
        link = s.find("a", class_ = "Fw(b) Fz(20px) Lh(23px) Fz(17px)--sm1024 Lh(19px)--sm1024 mega-item-header-link Td(n) C(#0078ff):h C(#000) LineClamp(2,46px) LineClamp(2,38px)--sm1024 not-isInStreamVideoEnabled").get('href')
        nid = link[link.rfind('-')+1:].replace('.html','')
        print(nid,title)
        news.append(nid)
        link = baseurl + link
        news.append("'"+link+"'")

        #get content
        article = requests.get(link)
        if article.status_code == requests.codes.ok:
            singlenews = BeautifulSoup(article.text, 'html.parser')
            #time
            t = singlenews.find("time").get("datetime")
            t1 = datetime.datetime.strptime(t, '%Y-%m-%dT%H:%M:%S.000Z') + datetime.timedelta(hours=8)
            news.append("'"+t1.strftime("%Y-%m-%d %H:%M:%S")+"'")
            
            #content
            body = singlenews.find("div", class_ = "caas-body").find_all("p")
            content = []
            for p in body:
            	if p.find('span') == None:
            		content.append(p.text.replace("'","\\'"))
            news.append("'"+"\n".join(content)+"'")

        #insert to db
        insert_query = "insert into articles values (%s)" % (','.join(news))
        execquery(conn,insert_query)
    return conn  


def execquery(conn,query):
    cur = conn.cursor() 
    try:
        cur.execute(query) 
    except Exception as e:
        print('mysql execute error:',e)
        print('error query:',query)
    cur.close() 





conf = configparser.ConfigParser()
conf.read('Config.ini')
db_host = conf['database']['host']
db_port = conf['database']['port']
db_db = conf['database']['db']
db_user = conf['database']['user']
db_pwd = conf['database']['pwd']
conn = mysql.connector.connect(host=db_host,database=db_db,port=db_port,user = db_user,password = db_pwd)
cursor = conn.cursor(buffered=True)
create_cmd = conf['cmd']['create']
try:
    cursor.execute(create_cmd)
except Exception as e:
    None
for cate in conf['categories']:
    print("======="+cate+"=======")
    cateid = conf['categories'][cate]
    crawler(cate,cateid,conn)
cursor.close()
conn.close()

