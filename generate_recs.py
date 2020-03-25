import datetime
import json
import os
import re
import sys 
import psycopg2
import requests
import traceback
from requests.exceptions import HTTPError

cloud_link = os.getenv('GCLOUD_LINK')

def get_user(user_id):
    user = os.getenv('PGCONNECT_USER')
    password = os.getenv('PGCONNECT_PASSWORD')
    host = os.getenv('PGCONNECT_HOST')
    port = os.getenv('PGCONNECT_PORT')
    dbname = os.getenv('PGCONNECT_DBNAME')
    
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port, sslmode='require')
    cur = conn.cursor()


    sql = "SELECT native_lang, es_rec,fr_rec,de_rec,en_rec,langs FROM users WHERE id = %s"
    cur.execute(sql,(user_id,))
    user  = cur.fetchall()
    conn.close()
    return user[0]

def cluster_arts(native_lang,user_id,clust_num,percent):

    cluster_link = f'https://lango-rec-{native_lang}-v26nfpfxqq-uc.a.run.app/cluster'

    try:
        cluster = requests.post(cluster_link, json={
                "native_lang": native_lang,
                "user_id":user_id,
                "clust_num":clust_num,
                "percent":percent
            })
        pop_clusters=cluster.json()
        print(len(pop_clusters))
        for cluster in pop_clusters:
            print(len(cluster))
        return pop_clusters
    except:
        print('error')


def get_recs(pop_clusters,user_id,rec_num,trans_lang):

    trans_links = f'https://lango-rec-{trans_lang}-v26nfpfxqq-uc.a.run.app/get_recs'

    response = requests.post(trans_links, json={
        "trans_lang": trans_lang,
        "user_id":user_id,
        "rec_num":rec_num,
        "pop_clusters":pop_clusters
    })
    print(response)

def gen_recs(user_id,rec_num,clust_num,percent):
    t18=datetime.datetime.now()
    user1 = get_user(user_id)

    native_lang=user1[0]
    es_rec=user1[1]
    fr_rec=user1[2]
    de_rec=user1[3]
    en_rec=user1[4]
    langs=user1[5]

    pop_clusters = cluster_arts(native_lang,user_id,clust_num,percent)

    rec_times = {}
        
    if es_rec:
        t0=datetime.datetime.now()
        print('es_rec generate')
        get_recs(pop_clusters,user_id,rec_num,'es')
        t1=datetime.datetime.now()
        es_rec_time='es_rec' + str(t1-t0)
        rec_times['es_rec_time'] = es_rec_time
        print(es_rec_time)
    
    if de_rec:
        t2=datetime.datetime.now()
        print('de_rec generate')
        get_recs(pop_clusters,user_id,rec_num,'de')
        t3=datetime.datetime.now()
        de_rec_time='de_rec' + str(t3-t2)
        rec_times['de_rec_time'] = de_rec_time
        print(de_rec_time)
    
    if fr_rec:
        t4=datetime.datetime.now()
        print('fr_rec generate')
        get_recs(pop_clusters,user_id,rec_num,'fr')
        t5=datetime.datetime.now()
        fr_rec_time='fr_rec' + str(t5-t4)
        rec_times['fr_rec_time'] = fr_rec_time
        print(fr_rec_time)
    
    if en_rec:
        t6=datetime.datetime.now()
        print('en_rec generate')
        get_recs(pop_clusters,user_id,rec_num,'en')
        t7=datetime.datetime.now()
        en_rec_time='en_rec' + str(t7-t6)
        rec_times['en_rec_time'] = en_rec_time
        print(en_rec_time)
    
    t19=datetime.datetime.now()
    store_recs1='store recs' + str(t19-t18)
    rec_times['store recs'] = store_recs1
    print(store_recs1)
    print(rec_times)
    
    return 'All recs uploaded'

def main():
    user_id=22
    t18=datetime.datetime.now()

    user1 = get_user(user_id)
    print(user1)
    
    native_lang=user1[0]
    es_rec=user1[1]
    fr_rec=user1[2]
    de_rec=user1[3]
    en_rec=user1[4]

    clust_num=15
    percent=0.33
    rec_num=20

    print('clustering')
    pop_clusters = cluster_arts(native_lang,user_id,clust_num,percent)
    
    if es_rec:
        print('es_rec generate')
        get_recs(pop_clusters,user_id,rec_num,'es')
    
    if de_rec:
        print('de_rec generate')
        get_recs(pop_clusters,user_id,rec_num,'de')
    
    if fr_rec:
        print('fr_rec generate')
        get_recs(pop_clusters,user_id,rec_num,'fr')
    
    if en_rec:
        print('en_rec generate')
        get_recs(pop_clusters,user_id,rec_num,'es')

    t19=datetime.datetime.now()
    store_recs1='store recs' + str(t19-t18)
    print(store_recs1)

if __name__ == '__main__':
    main()
