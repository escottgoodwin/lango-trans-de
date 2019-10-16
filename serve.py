import os
import datetime
from datetime import datetime,timedelta
from flask import Flask, request
from generate_recs import generate_recs

application = Flask(__name__)

lang = 'de'

def list_routes():
    return ['%s' % rule for rule in application.url_map.iter_rules()]

@application.route("/")
def routes():
    routelinks = list_routes()
    html = "<h1 style='color:blue'>German Routes</h1>"
    for link in routelinks:
        html += '<P><H3>'+link+'</H3></P>'
    
    return html

@application.route("/get_recs", methods=['POST'])
def link_search_pg():
    native_lang = request.json['native_lang']
    trans_lang = request.json['trans_lang']
    uid = request.json['uid']
    clust_num = request.json['clust_num']
    percent = request.json['percent']
    rec_num = request.json['rec_num']

    generate_recs(native_lang,trans_lang,uid,clust_num,percent,rec_num)

    return 'recommendations uploaded'

if __name__ == '__main__':
    application.run(debug=True,host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))