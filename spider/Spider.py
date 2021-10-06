import leancloud
from feedparser import *
from requests import *
from logging import basicConfig,DEBUG,INFO,info,error
from http.client import RemoteDisconnected
from re import sub
from pprint import pprint
basicConfig(level=INFO);
from os import environ
from time import time,mktime,gmtime
leancloud.init(environ["APPID"], master_key=environ["MASTERKEY"]);
ArticleObj = leancloud.Object.extend("Article");

def GetFlink():
    info("获取友链列表")
    return get(environ["FLINK_API"]).json();

def GetRSSLink(link):
    link = link.replace("https://","").replace("/",'');
    r_link = ""
    try:
        if head("https://"+link+"/feed/",headers={
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.17 Safari/537.36 Edg/95.0.1020.9"
        }).status_code<400:
            r_link = "https://"+link+"/feed/";
        elif head("https://"+link+"/atom.xml",headers={
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.17 Safari/537.36 Edg/95.0.1020.9"
        }).status_code<400:
            r_link = "https://"+link+"/atom.xml"
        elif head("https://"+link+"/rss.xml",headers={
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.17 Safari/537.36 Edg/95.0.1020.9"
        }).status_code<400:
            r_link = "https://"+link+"/rss.xml"
        elif head("https://"+link+"/rss2.xml",headers={
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.17 Safari/537.36 Edg/95.0.1020.9"
        }).status_code<400:
            r_link = "https://"+link+"/rss2.xml"
        elif head("https://"+link+"/blog/atom.xml",headers={
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.17 Safari/537.36 Edg/95.0.1020.9"
        }).status_code<400:
            r_link = "https://"+link+"/blog/atom.xml";
    except RemoteDisconnected as e:
        return "";
    finally:
        return r_link;
    

def GetRecentLink(rss,author):#得到最近6个月内的文章
    rss = parse(rss,agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.17 Safari/537.36 Edg/95.0.1020.9").entries;
    artical_list = [];
    for i in rss:
        rc={
            "title":i.title.replace('"','').replace('\n',''),
            "time":mktime(i.published_parsed)*1000.0,
            "summary": sub('<[^<]+?>', '', i.summary[:200]).replace('\\', '\\\\').strip().replace('"','').replace('\n', ''),
            "link":i.link,
            "author":author
        };
        tim = mktime(i.published_parsed);
        timen=time();
        lastime = gmtime(timen-tim);
        if lastime.tm_year==1970: 
            if lastime.tm_mon<=3:
                artical_list.append(rc);
    return artical_list;

def GetALLLink():
    flink = GetFlink();
    info("成功")
    for i in flink:
        if i["sort"]=="ten":
            info("获取 "+i["url"]+" 链接")
            rss = GetRSSLink(i["url"]);
            if rss!="":
                info("成功 "+rss);
                info("开始获取"+i["url"]+" 的文章")
                try:
                    result = GetRecentLink(rss,i["name"]);
                    for j in result:
                        info("上传中 "+j["title"])
                        art = ArticleObj();
                        art.set("avatar",i['image'])
                        for key in j:
                            art.set(key,str(j[key]));
                        art.save();
                    info("获取 "+i['url']+' 成功，开始获取下一个')
                except Exception as e:
                    error("获取 "+i['url']+' 失败，开始获取下一个')
                finally:
                    pass
            else:
                error("rss出问题了!")


def SaveLink():
    Article = ArticleObj();
    info("删除之前文章中") 
    ArticleObj.query.limit(1000);
    qlist = ArticleObj.query.find();
    for i in qlist:
        det = ArticleObj.create_without_data(i.get("objectId"))
        det.destroy()
    GetALLLink();
    info("成功")

if __name__ == "__main__":
    SaveLink()