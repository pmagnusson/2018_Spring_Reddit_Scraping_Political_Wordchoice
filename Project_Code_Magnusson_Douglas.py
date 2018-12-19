# -*- coding: utf-8 -*-

# Project Code
# Patrick Magnusson & Kathy Douglas
# IS 6713 Data Foundations
# Spring 2018, Bachura

import urllib.request
import urllib.parse
from bs4 import BeautifulSoup as soup
import json
import csv
import praw
import requests
import requests.auth
import re

import nltk
import codecs
from nltk.corpus import webtext
from nltk.corpus import nps_chat
from nltk.corpus import gutenberg
from nltk import word_tokenize
from nltk.corpus import stopwords

import pandas as pd

import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

import random
from wordcloud import WordCloud
#nltk.download()


##### ADAPTED ERIC BACHURA CODE BLOCK ######
def is_absolute(url):
    return bool(urllib.parse.urlparse(url).netloc)  # True/False boolean to determine if net location is valid

def getsubreddit(url):
    subreddit = (urllib.parse.urlparse(url).path).split("/")[2]  
    # reddit subreddit URLs are set up reddit.com/r/___ or redit.com/u/___ for users, so [2] element is the ___
    return subreddit

def getsource(incoming):
    req=urllib.request.Request(incoming, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}) #sends GET request to URL
    uClient=urllib.request.urlopen(req)
    page_html=uClient.read() #reads returned data and puts it in a variable
    uClient.close() #close the connection
    page_soup=soup(page_html,"html.parser")
    return page_soup

# edited to remove default reddit.com etc etc
def getapiUsers(subreddit):
    r = str(getsource(subreddit + "/about/.json"))
    data = json.loads(r)                                                            # Said "load s", not "loads"
    subscribers = data.get("data").get("subscribers")
    # = data.get("data").get("accounts_active")
    #print([str(subscribers), str(active)])
    return [str(subscribers)]

def getapiActive(subreddit):
    r = str(getsource(subreddit + "/about/.json"))
    data = json.loads(r)                                                            # Said "load s", not "loads"
    #subscribers = data.get("data").get("subscribers")
    active = data.get("data").get("accounts_active")
    return [str(active)]

#############################################



### Pulling list of URLs for popular political subreddits (from a post suggesting them) ###
yankURL = "https://www.reddit.com/r/redditlists/comments/josdr/list_of_political_subreddits/"
    # this list is possibly temporary if we find the subs unsatisfactory
is_absolute(yankURL)
listOfLinks = []
def pullURLS(webPage):
    sections = webPage.findAll("div",{"class","md"})
    for section in sections:
        links = section.findAll("a")   
        for link in links:
            linkToUse = link.get("href")
            if is_absolute(linkToUse):
                print(linkToUse)
                listOfLinks.append(linkToUse)
            else: continue

pullURLS(getsource(yankURL))
print(listOfLinks)
listOfLinks = listOfLinks[1:174] # the first and last, 0 and 175 were invalid, linked to external web app
print(listOfLinks)


   
subListFinal = ' '.join(listOfLinks).replace('http://www.reddit.com/r/','').split()
subListFinal = ' '.join(subListFinal).replace('http://reddit.com/r/','').split()
subListFinal = ' '.join(subListFinal).replace('/','').split()
print(subListFinal)
    
with open('listLocal.txt', 'w') as file:
    for item in subListFinal:
        file.write("%s\n" % item)




### Reddit API scraping ###
        
        
# Run this auth block solo
        
client_auth = requests.auth.HTTPBasicAuth('wfQf1yeCA_kFjw','RUfiva9xh70FKdIRhjAqyFJ85ow')
post_data = {'grant_type':'password','username':'dataFoundationsGroup','password':'bachura'}
headers = {"User-Agent":"python:dataFoundationsApp (by pat&kat)"}
response = requests.post("https://www.reddit.com/api/v1/access_token", auth = client_auth, data = post_data, headers = headers)
response.json()

# Paste token received above after bearer below

headers = {"Authorization": "bearer jZWz7-Fv2vHIxhqyLO7NlUOOSI8", "User-Agent": "python:dataFoundationsApp (by pat&kat)"}
response = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers)
response.json()


# Initiate Reddit instance

reddit = praw.Reddit(client_id = 'wfQf1yeCA_kFjw',
                     client_secret = 'RUfiva9xh70FKdIRhjAqyFJ85ow',
                     user_agent = 'python:dataFoundationsApp (by pat&kat)')

# scrape from subreddit instances within reddit instance, using subreddit list

for sub in subListFinal:
    try:
        sub_name = sub
        subreddit = reddit.subreddit(str(sub))
        titleList = []
        scoreList = []
        commentList = []
        #print(subreddit.description)
        for submission in subreddit.hot(limit=1000):
            titleList.append(submission.title)
            scoreList.append(submission.score)
            commentList.append(submission.num_comments)
        csvFile = open("RedditScrape.csv", 'a', newline='')
        try:
            writer = csv.writer(csvFile)
            #writer.writerow(('subreddit', 'post title', 'score','num_comments'))   
            for post in range(1,len(titleList)):
                writer.writerow((str(sub),titleList[post],scoreList[post],commentList[post]))              
        finally:
            csvFile.close()
    except:
        print(sub,"failed to export!")




### Create Subreddit-Word Pairs for Conditional Frequency Distribution ###

# The following code block created with assistance of Professor Eric Bachura --- {

df = pd.read_csv('RedditScrape3.csv', encoding = 'ISO-8859-1')
subRedditTokens = {}
subRedditFreqs = {}
rsqm = '’'

for myIndex,myRow in df.iterrows():
    line = myRow[1].replace('\n','').replace(rsqm,'\'').replace('\'','').replace("'","")
    words = [nltk.WordNetLemmatizer().lemmatize(w.strip().lower().replace("'","")) for w in re.findall(r'([^\W\d\']+$)',line)]
    if myRow[0] in subRedditTokens:
        subRedditTokens[myRow[0]] += words
    else:
        subRedditTokens[myRow[0]] = words
    

# ------------ }




##### WordCloud Procedure #######
# Kathy version

def show_wordcloud(data, title = None):
   wordcloud = WordCloud(
       background_color='lightblue',
       stopwords=stopwords.words('english'),
       max_words=200,
       max_font_size=40, 
       scale=3,
       random_state=1 # chosen at random by flipping a coin; it was heads
   ).generate(str(data).replace(rsqm,'\'').replace('\'',''))
   plt.figure(figsize=(20,10))
   fig = plt.imshow(wordcloud)
   plt.axis('off')
   if title: 
       plt.suptitle(title, fontsize=20)
       #plt.subplots_adjust(top=2.3)
   #fig = plt.imshow(wordcloud).figure(1, figsize=(12, 12))   
   plt.savefig(title + ".png")
   plt.show()

print(subRedditTokens.values())
show_wordcloud(subRedditTokens.values())

for sr in subRedditTokens:
    show_wordcloud(subRedditTokens[sr], title=sr)
    
    



### Export top 25 words per subreddit for final chart ###

topListSubs = []
topListWords = []
topListCounts = []
    
for subreddit,text in subRedditTokens.items():
    text = nltk.Text(w for w in text if w not in stopwords.words('english'))
    textFreqs = nltk.FreqDist(text)
    subRedditFreqs[subreddit]=textFreqs
    for i in range (0,25):
        try:
            topListWords.append(textFreqs.most_common(25)[i][0])
            topListCounts.append(textFreqs.most_common(25)[i][1])
            topListSubs.append(subreddit)
        except: continue
    
csvFile2 = open("Top25bySub.csv", 'a', newline='')
writer2 = csv.writer(csvFile2)
writer2.writerow(('subreddit', 'word', 'count'))   
for pair in range(0,len(topListWords)):
    writer2.writerow((topListSubs[pair],topListWords[pair],topListCounts[pair]))              
csvFile2.close()






# ------------------------------------------------------------------------------

# All code below is previous version of section Reddit Scraping, maintain for reference ---------------------------------



## subscriber and active sub numbers for each subreddit (we will weight against as %)
## collect and dump to file
#
#dictUsers = {}
#dictActive= {}
#for sub in listOfLinks:
#    try: 
#        name = sub
#        #print(name)
#        users = int(getapiUsers(sub)[0])
#        #print(users)
#        active = int(getapiActive(sub)[0])
#        #print(active)
#        dictUsers[name] = users
#        dictActive[name] = active
#    except: pass
#
#import csv
#csvFile = open("usersLocal.csv", 'w+')
#try:
#    writer = csv.writer(csvFile)
#    writer.writerow(('subreddit', 'users', 'active'))
#    for key,value in dictUsers.items():
#        writer.writerow((key,value,dictActive[key]))
#finally:
#    csvFile.close()
#
#
## in loop:  appending to the end of the URL ?count=25 lets you start the page at given #
## iterate by 25 
## (first page is count = 0)
## &limit=100 lets you have 100 posts on the page, only need 10 passes per sub
# 
#listPosts = []
#for sub in listOfLinks[5:10]:
#    #while (count < 1100):
#    url = str(sub)+"/?limit=100"
#    source = getsource(url)
#    titles = source.findAll("a",{"class","title may-blank outbound"})
#    for title in titles:
#        print(title.text)
#        listPosts.append(title.text)
##        titles2 = source.findAll("a",{"class","title may-blank"})
##        for title in titles2:
##            listPosts.append(title.text)
##        print(listPosts)
#
#
#count = 1
#while count < 1100:
#    print(count)
#    count+=100
#
#
#
## target a class "title may-blank outbound" & "title may-blank"
#    # may take out loggedin if we scrape logged out
#
#        Pseudo code approximating scrape operation:
#loop thru list urls
#    for each URL, open w/ limit = 100 and count = 0
#    +100 to count each pass, append to URL (stop at 1000)
#    at each page visit, findAll <a> class = "title may-blank loggedin outbound" & "title may-blank loggedin"
#    store Titles, Comment Count, and Upvote Count in lists named for subreddit
#    save list to flat file (.csv)
#
#Next steps are parsing each CSV using text analysis to associate the words with activity levels
#
#    
# -----------------------------------------------------------------------------------
#
#    
## #####start of CSV version #
#        
#stopwords = list(set(stopwords.words('english')))
#stopwords.append(['!','#','$','%','&',"''",'(',')','+','+++'])
#
#csvDict = csv.DictReader(open('RedditScrape3.csv', 'r', encoding='utf8'), delimiter= ",",quotechar = '"')
#lines = list(csvDict)
#subreddit = [l['subreddit'] for l in lines]
#titles = [l['post_title'] for l in lines]



## from raw text to bad all-combos Pairs version #
# 
#
#txt = codecs.open('allPosts.txt', 'r', encoding='utf8')
#postsRaw = txt.read()
#postsLower = str.lower(postsRaw)
#postsLower = postsLower.replace("'","")
#postsLower = postsLower.replace("*","")
#postsLower = postsLower.replace("-","")
#postsLower = postsLower.replace(".","")
#postsLower = postsLower.replace("+","")
#postsLower = postsLower.replace("`","")
#
#postsToken = word_tokenize(postsLower)
#postsToken = sorted(postsToken)
#                  
#postsFiltered = []
#for word in postsToken:
#    if word not in stopwords:
#        postsFiltered.append(word)
#
#
#postsTokenUnique = list(set(postsFiltered))
#postsTokenUnique = sorted(postsTokenUnique)
#postsTokenUnique = postsTokenUnique[5119:]
#
#sub_word = [(sub, word)
#     for sub in subListFinal
#     for word in postsTokenUnique]
#
#CFD = nltk.ConditionalFreqDist(sub_word)