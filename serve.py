import os
import datetime
import json
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
    html = "<h1 style='color:blue'>Recommendation - Translation - German</h1>"
    for link in routelinks:
        html += '<P><H3>'+link+'</H3></P>'
    
    return html

@application.route("/get_recs", methods=['POST'])
def link_search_pg():
    trans_lang = request.json['trans_lang']
    uid = request.json['uid']
    rec_num = request.json['rec_num']
    pop_clusters=request.json['pop_clusters']

    data = {
        "trans_lang":trans_lang,
        "uid":uid,
        "rec_num":15,
        }
    print(data)
    generation_times = generate_recs(pop_clusters,uid, trans_lang, rec_num)
    return json.dumps(generation_times)

if __name__ == '__main__':
    application.run(debug=True,host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))