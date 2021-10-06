import leancloud
from logging import basicConfig,DEBUG,INFO,info,error
from requests import *
from http.server import BaseHTTPRequestHandler,HTTPServer
from json import dumps
basicConfig(level=INFO);
from os import environ
leancloud.init(environ["APPID"], master_key=environ["MASTERKEY"]);
ArticleObj = leancloud.Object.extend("Article");

def GetLatestArticles():
    ArticleObj.query.limit(1000);
    qlist = ArticleObj.query.find();
    res = []
    for i in qlist:
        rc = {
            "title":i.get('title'),
            "time":str(int(float(i.get("time")))),
            "summary":i.get("summary"),
            "link":i.get("link"),
            "avatar":i.get("avatar"),
            "author":i.get("author")
        };
        res.append(rc);
    res.sort(key=lambda x:x["time"])
    res.reverse();
    return dumps(res).encode('utf-8').decode('unicode_escape');

# pprint(GetLatestArticles(),depth=1);
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200);
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header("Access-Control-Allow-Origin","*")
        self.end_headers();
        self.wfile.write(GetLatestArticles().encode("utf-8"));
