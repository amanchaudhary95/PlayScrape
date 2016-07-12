#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import Queue


count = 0;
q = Queue.Queue()
s = {"com.outfit7.mytalkingtomfree"}
q.put("com.outfit7.mytalkingtomfree")
#q.put("com.greedygame.deathsprint")
#q.put("com.outfit7.mytalkingtomfree")
#q.put("com.FDGEntertainment.redball4.gp")

def get_page(pkg_name):
	base_url = "https://play.google.com/store/apps/details?id="
	r = requests.get(base_url + pkg_name)
	return r.status_code, r.text
def get_similar_page(pkg_name):
	base_url = "https://play.google.com/store/apps/similar?id="
	r = requests.get(base_url + pkg_name)
	return r.status_code, r.text	


while not q.empty():
	temp=q.get()
	status, page_text = get_page(temp)
	if status == requests.codes.ok:
		count=count+1
		print count,"\n"
		soup = BeautifulSoup(page_text)
		soup.prettify()
		g_title = soup.find_all("div", {"class" : "id-app-title"} )[0].text
		print "TITLE :", g_title
		g_publisher = soup.find_all("span",{"itemprop":"name"})[0].text
		print "PUBLISHER :", g_publisher
		g_url = "https:"+soup.find_all("div",{"class":"cover-container"})[0].find_all("img",{"class":"cover-image"},{"itemprop":"image"})[0].get("src")  
		print "URL :",g_url
		g_rating = soup.find_all("div",{"class":"score"})[0].text
		print "RATING :",g_rating
		g_raters = soup.find_all("span",{"class":"reviews-num"})[0].text
		print "RATERS :",g_raters
		for downloads in soup.find_all("div",{"itemprop":"numDownloads"}):
			num_download = downloads.text.split(' ')
			print "MIN DOWNLOADS :",int(num_download[2].replace(',',''))
			print "MAX DOWNLOADS :",int(num_download[4].replace(',',''))
		g_update = soup.find_all("div",{"itemprop":"datePublished"})[0].text
		print "UPDATED :",g_update
		for g_size in soup.find_all("div",{"itemprop":"fileSize"}):
			print "SIZE :",g_size.text
		for g_version  in soup.find_all("div",{"itemprop":"softwareVersion"}):
			print "CURRENT VERSION :",g_version.text
		for top_dev in soup.find_all("span",{"class":"badge-title"}):
			print "TOP_DEV :", top_dev.text	
				
		status1, similar_page = get_similar_page(temp)
		if status1 == requests.codes.ok:
			soup = BeautifulSoup(page_text)
			soup.prettify()
			for link in soup.find_all("div",{"class":"card no-rationale square-cover apps small"}):
				temp=link.get("data-docid")
				if(temp not in s):
					s.add(temp)
					q.put(temp)
    
		print "\n-----*****-----*****-----*****-----*****----",len(s),"\n"


			       

    		
