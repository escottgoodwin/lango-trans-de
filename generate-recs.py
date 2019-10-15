from gensim.models.doc2vec import Doc2Vec,TaggedDocument
import datetime
import json
from textblob import TextBlob
import pandas as pd
from sklearn.cluster import KMeans
from stop_words import get_stop_words
import os
import re
import sys 
import numpy as np 
import psycopg2
import requests
from bs4 import BeautifulSoup
import traceback
from dotenv import load_dotenv

load_dotenv()

user = os.getenv('PGCONNECT_USER')
password = os.getenv('PGCONNECT_PASSWORD')
host = os.getenv('PGCONNECT_HOST')
port = os.getenv('PGCONNECT_PORT')
dbname = os.getenv('PGCONNECT_DBNAME')

def fetch_user_links(uid):
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port, sslmode='require')
    cur = conn.cursor()
    sql = f"SELECT link FROM user_links WHERE uid LIKE '{uid}'"
    cur.execute(sql)
    links  = cur.fetchall()
    conn.close()
    newlinks = [x[0] for x in links]
    return newlinks

def get_feed_articles(links,lang,min_len=2000,max_len=50000):
    count = 0
    articles = []
    for link in links:
        try:
            art = art_parser(link)
            if (min_len <= len(art) <= max_len):
                articles.append(art)
        except Exception:
            print(link)
            traceback.print_exc()
            pass
        count += 1
        pct = count / len(links)
        print(pct, end='\r')
        sys.stdout.flush()
    return articles

def art_parser(link):
    r = requests.get(link)
    page = r.text
    soup = BeautifulSoup(page,"lxml")
    for x in soup('script'):
        x.decompose()
    for x in soup('link'):
        x.decompose()
    for x in soup('meta'):
        x.decompose()
    paras = soup('p')
    if soup.title is None:
        prep_art = ''
        title = ''
        return prep_art
    else:
        title = soup.title.string
        atriclestrip = [art.get_text() for art in paras]
        prep_art = ' '.join(atriclestrip)
        return prep_art

def one_lang(arts,native):
    arts1_cur_1lang = []
    for x in arts:
        art = TextBlob(x)
        if art.detect_language() != native:
            trans = art.translate(to=native)
            arts1_cur_1lang.append(str(trans))
        else:
            arts1_cur_1lang.append(x)
    return arts1_cur_1lang

def clean_arts(arts,native):
    no_pdf = [x for x in arts if not x.startswith("%PDF-")]
    one_lang1 = one_lang(no_pdf, native)
    return one_lang1

def article_vec(article,lang_model,lang):
    stop_words = get_stop_words(lang)
    histnostop = [i for i in article.lower().split() if i not in stop_words]
    vec = lang_model.infer_vector(histnostop)
    return vec

def cluster_articles(articles,vecs,clust_num):
    km = KMeans(n_clusters=clust_num)
    km.fit(vecs)
    cluster_labels = km.labels_.tolist()
    df = pd.DataFrame(cluster_labels,columns=['cluster']) 
    df['native_vector'] = vecs 
    df['native_article'] = articles 
    cluster_grps = [df.loc[df['cluster'] == x]['native_article'].tolist() for x in range(clust_num)]
    return cluster_grps

def popular_clusters(cluster_grps,percent):
    sorted_clusters= sorted(cluster_grps, key=len,reverse=True)
    pop_length = int(len(cluster_grps)*percent)
    return sorted_clusters[:pop_length]

def trans_vec_centers(cluster, trans_lang_model, trans_lang):
    trans_vecs=[]
    for art in cluster:
        try:
            trans_art = str(TextBlob(art).translate(to=trans_lang))
            trans_vec = article_vec(trans_art, trans_lang_model, trans_lang)
            trans_vecs.append(trans_vec)
        except Exception:
            traceback.print_exc()
            pass
            
    vec_center = np.mean(trans_vecs, axis = 0)
    return vec_center

def get_recs(vec_centers,lang_model,rec_num):
    recs = [lang_model.docvecs.most_similar([vec_centers[i]], topn=rec_num) for i, x in enumerate(vec_centers)]
    return [[x[0] for x in rec] for rec in recs]

def store_recs(uid, recs, trans_lang, cluster):
    now = datetime.datetime.now()
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port, sslmode='require')
    cur = conn.cursor() 
    for art_id in recs:
        data = (uid, art_id, now, trans_lang, cluster)
        query = 'INSERT INTO recommendations (uid, art_id, rec_date, lang, cluster_num) VALUES (%s,%s,%s,%s,%s)'
        conn.commit()
        cur.execute(query,data)
    conn.close()

def generate_recs(native_lang,trans_lang,uid,clust_num,percent,rec_num):
    native_lang_model_path=f'{native_lang}model3.model'
    trans_lang_model_path=f'{trans_lang}model3.model'

    t0=datetime.datetime.now()
    native_lang_model = Doc2Vec.load(native_lang_model_path)
    trans_lang_model = Doc2Vec.load(trans_lang_model_path)
    t1= datetime.datetime.now()
    print('loaded models '+ str(t1-t0))

    t2=datetime.datetime.now()
    links = fetch_user_links(uid)
    t3=datetime.datetime.now()
    print('loaded links '+ str(len(links)) + ' ' + str(t3-t2))
    
    t4=datetime.datetime.now()
    articles = get_feed_articles(links, native_lang, min_len=2000, max_len=50000)
    t5=datetime.datetime.now()
    print('loaded arts ' + str(len(articles)) + ' ' + str(t5-t4))

    t6=datetime.datetime.now()
    cleaned_arts = clean_arts(articles,native_lang)
    t7=datetime.datetime.now()
    print('cleaned arts ' + str(len(cleaned_arts)) + ' ' + str(t7-t6))

    t8=datetime.datetime.now()
    native_art_vecs =[article_vec(article,native_lang_model,native_lang) for article in cleaned_arts]
    t9=datetime.datetime.now()
    print('native vec arts '+str(t9-t8))

    t10=datetime.datetime.now()
    cluster_grps = cluster_articles(cleaned_arts, native_art_vecs, clust_num)
    t11=datetime.datetime.now()
    print('cluster native arts '+ str(t11-t10))

    t12=datetime.datetime.now()
    pop_clusters = popular_clusters(cluster_grps, percent)
    t13=datetime.datetime.now()
    print('popular native clusters '+ str(t13-t12))

    t14=datetime.datetime.now()
    trans_lang_vec_centers = [trans_vec_centers(cluster,trans_lang_model,trans_lang) for cluster in pop_clusters]
    t15=datetime.datetime.now()
    print('translate and vec to trans lang'+ str(t15-t14))

    t16=datetime.datetime.now()
    recs = get_recs(trans_lang_vec_centers, trans_lang_model, rec_num)
    t17=datetime.datetime.now()
    print('get trans lang recs' + str(t17-t16))

    t18=datetime.datetime.now()
    [store_recs(uid, recs, trans_lang, i) for i,recs in enumerate(recs)]
    t19=datetime.datetime.now()
    print('store recs' + str(t19-t18))

    print('total'+str(t19-t0))

def main():
    native_lang = 'en'
    trans_lang = 'fr'
    uid = '3736ENQJEUavLjKX8ufPf5zfKl62'
    clust_num=15
    percent=.33
    rec_num=20 

    generate_recs(native_lang,trans_lang,uid,clust_num,percent,rec_num)

if __name__ == '__main__':
    main()
