from gensim.models.doc2vec import Doc2Vec,TaggedDocument
import datetime
import json
from textblob import TextBlob
import pandas as pd
from sklearn.cluster import KMeans
from stop_words import get_stop_words
from urllib.parse import urlparse
import sqlite3
import urllib3
import urllib.request
from shutil import copy2
from art_scrape2 import get_feed_articles
from create_d2v import create_doc2vec_model
import os
import re
from sys import platform
from cold_start_flask import start_flask
#from flask import Flask, flash, redirect, render_template, request, session, abort
#import webbrowser,threading

def get_history(filters,days_ago):
    ## copies database with browsing data (browser databases are often not accessible while browser is in use)
    if platform == "darwin":
        user = os.environ['USER']
        if not os.path.exists('chrome_history'):
            os.makedirs('chrome_history')
        copy2(r"/Users/" + user + "/Library/Application Support/Google/Chrome/Default/History","chrome_history")
        db = sqlite3.connect('chrome_history/History')
    ###
    elif platform == "win32":
        user = os.environ['USER']
        data_path = os.path.expanduser("~") + r"\AppData\Local\Google\Chrome\User Data\Default"
        files = os.listdir(data_path)
        history_db = os.path.join(data_path, 'history')
        if not os.path.exists('chrome_history'):
            os.makedirs('chrome_history')
        copy2(history_db,"chrome_history")
        db = sqlite3.connect('chrome_history/history')
    ###
    cursor = db.cursor()
    ## sql query pulls date,url,title,visit count from database
    cursor.execute('''
    select datetime(last_visit_time/1000000-11644473600,'unixepoch') ,url,title,visit_count from urls order by last_visit_time desc
    ''')
    all_rows = cursor.fetchall()
    ## pandas dataframe of browsing history
    df_hist = pd.DataFrame(all_rows,columns=['datetime', 'url','title','visits'])
    ## filtes out irrevelvant sites from a list of strings - any partial match with string in list removes item
    df_hist_clean = df_hist[-df_hist['url'].str.contains('|'.join(filters))]
    today = datetime.date.today()
    ## produces df of links from the past num of days sumbitted - days_ago = 2 - all links browsed in the past 2 days
    state_date = today - datetime.timedelta(days=days_ago)
    time_frame_df = df_hist_clean[df_hist_clean['datetime']>str(state_date)]
    return time_frame_df

def one_lang(arts,native):
    ## makes sure articles are monolingual by translated all native langauge articles  in collection into the native langauge
    ## doc2vec models need to be monolingual for best results
    arts1_cur_1lang = []
    for x in arts:
        art = TextBlob(x)
        if art.detect_language() != native:
            trans = art.translate(to=native)
            arts1_cur_1lang.append(str(trans))
        else:
            arts1_cur_1lang.append(x)
    return arts1_cur_1lang

def article_vecs1(justarticles,name,lang):
    ## loads doc2vec model to use in inferring vectos
    model_name = name + 'model.model'
    lang_model = Doc2Vec.load(model_name)
    ## preprocess articles and tag them for input into doc2vec
    stop_words = get_stop_words(lang)
    histnostop = [[i for i in doc.lower().split() if i not in stop_words] for doc in justarticles]
    dlhist_tagged = [TaggedDocument(doc,[i]) for i,doc in enumerate(histnostop)]
    ## infer vectors from current doc2model
    vecs = [lang_model.infer_vector(doc.words) for doc in dlhist_tagged]
    return vecs

def cluster_articles(articles,vecs,clust_num):
    ## create chose number of Kmeans clusters from the inferred doc2vec vectors
    km = KMeans(n_clusters=clust_num)
    km.fit(vecs)
    ## list of cluster number for each article
    cluster_labels = km.labels_.tolist()
    ## centers for each cluster - this will provide our user model to provide recommendations from the corpus
    ## centers represents points in the corpus where users have interest based on articles browsed in a certain timeframe
    centers = km.cluster_centers_
    ## create df of cluster/vec/article for each article in user's browser history
    df = pd.DataFrame(cluster_labels,columns=['cluster'])
    df['native_vector'] = vecs
    df['native_article'] = articles
    ## sort df by clusters with the most articles
    ## this is a proxy for user interest - the more articles there are in a cluster, the more interest a use has in the 'topic' represented by that cluster
    sorted_clusters = df.groupby(['cluster']).size().sort_values(ascending=False)
    return df,sorted_clusters,centers

def get_popular(df,clusters,centers,percent):
    ## get the top percent of clusters - default 50% - termed popular clusters
    cutoff = int(len(clusters)*percent)
    ## get the centers of the most popular clusters to use in recommendations
    popcenters = [centers[x] for x in clusters.index[:cutoff]]
    ##df of all rows in only the popular clusters
    df_pop = df.loc[df['cluster'].isin(clusters.index[clusters.index[:cutoff]])]
    return popcenters,df_pop

def get_pop_vecs(model_name,native,days,clust_num=10,percent=.5):
    ## sample filter to remove irrevelvant sites - generally non-news oriented sites
    filters2 = [
    'duolingo','file://','instagram','twitter','localhost','google','collegeofthedesert','youtube','starbucks','sbux-portal','toyota','quicklaunchsso','github','bankofamerica','plex','hbogo','showtime','netflix','thepiratebay','facebook','tvguide','customwebauth','t.co',
    'aws','azure','127.0.0.1:5000','paperspace','floydhub','feedly','chrome-extension','downgradepc','.pdf'
    ]
    t0 = datetime.datetime.now()
    ## get urls of browser history (filtered)
    hist_cur = get_history(filters2,days)
    ## filter out base urls - only want urls with a path, signifying a unique article that will provide info about user interest
    withpath = [url for url in hist_cur['url'] if len(urlparse(url).path) > 4]
    ## get articles from the urls - articles longer than 2000 chars
    arts_cur = get_feed_articles(withpath,2000)
    arts1_cur = [x['article'] for x in arts_cur]
    ## filter out pdfs
    arts2_cur = [x for x in arts1_cur if not x.startswith("%PDF-")]
    t1 = datetime.datetime.now()
    print('loaded arts ',len(arts2_cur),str(t1-t0))
    ## make aritcles monolingual
    arts_onelang = one_lang(arts2_cur,native)
    t2 = datetime.datetime.now()
    print('arts translated to native', str(t2-t1))
    ##vectorize articles
    art_vecs = article_vecs1(arts_onelang,model_name,native)
    t3 = datetime.datetime.now()
    print('vecs created',str(t3-t2))
    ## get clusters and df of browsing history
    ## submit optional num of clusters - 20 clusters - cluster_articles(arts_onelang,art_vecs,20)
    df,sorted_clusters,centers = cluster_articles(arts_onelang,art_vecs,clust_num)
    t4 = datetime.datetime.now()
    print('vecs clustered',str(t4-t3))
    ## get centers and df of articles in the most popular clusters
    ## optional submission of percentage for cutoff - get top 30% clusters - get_popular(df,sorted_clusters,centers,.3)
    popcenters_cur,df_pop = get_popular(df,sorted_clusters,centers,percent)
    t5 = datetime.datetime.now()
    print('pop vecs created',str(t5-t4))
    print('total time to get popular vecs',str(t5-t0))
    return popcenters_cur,df_pop

def get_recs(corpus,vecs,model_name,rec_num):
    ## load doc2vec created from the article corpus
    model_name = model_name + 'model.model'
    lang_model = Doc2Vec.load(model_name)
    ## get the rec_num most similar articles to the list of vecs submitted
    ## rec_num=10 will produce list of 10 most similar articles inv sorted by simscore in form of (articleindex,sim score) sim score=0-1
    ## [(2334,.087),(355,.75),(2325,.63)...]
    sims = [lang_model.docvecs.most_similar([vec], topn=rec_num)for vec in vecs]
    ## get the link and article from the corpus by indexes from list of sims (indexes,sim score) for each popular cluster
    sim_links_art = [[[corpus[x[0]]['link'],corpus[x[0]]['article']] for x in y] for y in sims]
    ## list of just links for each popular clusters
    sim_links = [[x[0] for x in cluster] for cluster in sim_links_art]
    sim_links = [list(set(cluster)) for cluster in sim_links]
    ## list of just articles
    sim_articles = [[x[1] for x in cluster] for cluster in sim_links_art]
    return sim_links,sim_articles,sim_links_art

def main():
    t0 = datetime.datetime.now()
    lang = 'en'
    model_name = 'news'
    article_file = model_name + '_arts.txt'
    t1 = datetime.datetime.now()
    if not os.path.exists(article_file):
        print('downloading corpus')
        urllib.request.urlretrieve('https://www.dropbox.com/s/m25u619i207r7f2/news_arts1.txt?dl=1', article_file)
        print('corpus downloaded ',str(t1-t0))
    t2 = datetime.datetime.now()
    if not os.path.exists(model_name + 'model.model'):
        corpus = json.load(open(article_file))
        print('creating doc2vec model')
        create_doc2vec_model(corpus,model_name)
        print('doc2vec model created: ' + model_name + 'model.model ', str(t2-t1))
    print('analzying browser history')
    pop_vecs,_ = get_pop_vecs(model_name,lang,2,15,.33)
    print('making recommendations')
    corpus = json.load(open(article_file))
    link_recs,art_recs,sim_links_art = get_recs(corpus,pop_vecs,model_name,20)
    t3 = datetime.datetime.now()
    print('recs made: ', str(t3-t2))
    output_name = re.sub('[^0-9]','', str(str(datetime.datetime.now())))
    art_file = 'art__recs_' + output_name + '.txt'
    link_file = 'link_recs.txt'
    with open(link_file, 'w') as outfile:
        json.dump(link_recs, outfile)
    with open(art_file, 'w') as outfile:
        json.dump(art_recs, outfile)
    print('rec links created ' + link_file)
    print('rec articles created ' + art_file)
    print('total time:',str(t3-t0))

    saved_recs = json.load(open('link_recs.txt'))
    start_flask(saved_recs)


if __name__ == '__main__':
    main()
