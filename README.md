# yahoo_news_crawler

爬蟲yahoo新聞文章，並將結果儲存於mysql database

## 使用方式
在Config.ini設定
1. mysql連線方式
2. 要抓取新聞的類別
3. mysql 的 create schema(table名稱articles)

執行
`python3 yahoo_news_crawler.py`


## 開發環境
- python3.9.1
- request 2.26.0
- bs4 0.0.1
- mysql.connector 2.2.9
