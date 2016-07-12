#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import Queue
import multiprocessing
import MySQLdb

cal = {'January':'1','February':'2','March':'3','April':'4','May':'5','June':'6','July':'7','August':'8','September':'9','October':'10','November':'11','December':'12'}
queue = multiprocessing.Queue()
max_workers=4;
s = {"com.gameloft.android.ANMP.GloftA8HM"}
done = {"first"}
err = {"first"}
queue.put("com.gameloft.android.ANMP.GloftA8HM")
#queue.put("com.outfit7.mytalkingtomfree")
#queue.put("com.FDGEntertainment.redball4.gp")

def get_page(pkg_name):
    base_url = "https://play.google.com/store/apps/details?id="
    r = requests.get(base_url + pkg_name)
    return r.status_code, r.text
def get_similar_page(pkg_name):
    base_url = "https://play.google.com/store/apps/similar?id="
    r = requests.get(base_url + pkg_name)
    return r.status_code, r.text    

def work(q,proc_num):

 print proc_num,"Hello!"
 proc_counter=0;
 db = MySQLdb.connect("localhost","appuser","appuser123","apps")
 if(db):
    print "connected to database :",proc_num
 cursor = db.cursor()  
 while True:
    temp=q.get()
    status, page_text = get_page(temp)
    if status == requests.codes.ok:
        g_package=temp
        g_version = 'NULL'
        g_top_dev = 0
        g_size = 0
        if(temp not in done): 
            if(temp not in err):  
                proc_counter=proc_counter+1
                #print "inside loop :",proc_num
                soup = BeautifulSoup(page_text, "html.parser")
                soup.prettify()
                g_title = soup.find_all("div", {"class" : "id-app-title"} )[0].text 
                g_publisher = soup.find_all("span",{"itemprop":"name"})[0].text
                g_url = "https:"+soup.find_all("div",{"class":"cover-container"})[0].find_all("img",{"class":"cover-image"},{"itemprop":"image"})[0].get("src")
                for rating in soup.find_all("div",{"class":"score"}):
                    #print "RATING :", rating.text
                    g_rating = rating.text
                    g_rating = float(g_rating)
                    g_rating = g_rating*10
                    g_rating = int(g_rating)
                for raters in soup.find_all("span",{"class":"reviews-num"}):
                    #print "RATERS :", raters.text
                    g_raters = raters.text
                    g_raters = g_raters.replace(',','')
                    g_raters = int(g_raters)
                for downloads in soup.find_all("div",{"itemprop":"numDownloads"}):
                    num_download = downloads.text.split(' ')
                    #print "MIN DOWNLOADS :",int(num_download[2].replace(',',''))
                    #print "MAX DOWNLOADS :",int(num_download[4].replace(',',''))
                    g_minD = int(num_download[2].replace(',',''))
                    g_maxD = int(num_download[4].replace(',',''))
                for update in soup.find_all("div",{"itemprop":"datePublished"}):
                    #print "UPDATED :", update.text
                    g_update = update.text.replace(',','')
                    g_update = g_update.split(' ')
                    g_update[0] = cal.get(g_update[0])
                    date = g_update[2]+" "+g_update[0]+" "+g_update[1]
                    date = date.split(' ')
                    g_update = '-'.join(date)
                for size in soup.find_all("div",{"itemprop":"fileSize"}):
                    #print "SIZE :", size.text
                    if(size.text is "Varies with device"):
                        g_size = 0
                    if(size.text.find('M') != -1):
                        g_size = int(filter(str.isdigit,str(size.text)))
                        g_size = g_size*1024 
                    if(size.text.find('K') != -1):
                        g_size = int(filter(str.isdigit,str(size.text)))
                    if(size.text.find('G') != -1):
                        g_size = int(filter(str.isdigit,str(size.text)))
                        g_size = g_size*1024*1024            
                for version in soup.find_all("div",{"itemprop":"softwareVersion"}):
                    #print "CURRENT VERSION :", version.text
                    g_version = version.text
                for top_dev in soup.find_all("span",{"class":"badge-title"}):
                        if(top_dev.text):
                            g_top_dev = 1                      
                sql = "INSERT INTO game_details VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                try:
                    data = (g_package,g_title,g_publisher,g_url,g_rating,g_raters,g_minD,g_maxD,g_update,g_size,g_top_dev,g_version)
                    cursor.execute(sql,data)
                    db.commit()
                    print g_title,g_size,"........success  ",len(s)
                    done.add(temp) 
                except:
                    print g_title,g_size,"...............Error  ",len(s)
                    err.add(temp)
                    db.rollback()
                status1, similar_page = get_similar_page(temp)
                if status1 == requests.codes.ok:
                    soup = BeautifulSoup(page_text,"html.parser")
                    soup.prettify()
                    for link in soup.find_all("div",{"class":"card no-rationale square-cover apps small"}):
                        temp=link.get("data-docid")
                        if(temp not in s):
                            s.add(temp)
                            q.put(temp)
            
 db.close()

for i in range(max_workers): multiprocessing.Process(target=work, args=(queue,i)).start()
            

            
