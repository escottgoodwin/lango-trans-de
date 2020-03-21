import os
import datetime
import json
from datetime import datetime,timedelta
from flask import Flask, request
from generate_recs import gen_recs
from email_recs import send_emails

application = Flask(__name__)

def list_routes():
    return ['%s' % rule for rule in application.url_map.iter_rules()]

@application.route("/")
def routes():
    routelinks = list_routes()
    html = "<h1 style='color:blue'>Generate Recommendation - User</h1>"
    for link in routelinks:
        html += '<P><H3>'+link+'</H3></P>'
    
    return html

@application.route("/get_recs", methods=['POST'])
def link_search_pg():
    user_id = request.json['user_id']
    clust_num = request.json['clust_num']
    percent = request.json['percent']
    rec_num = request.json['rec_num']

    generation_times = gen_recs(user_id,rec_num,clust_num,percent)
    send_emails(user_id)
    return generation_times
    
if __name__ == '__main__':
    application.run(debug=True,host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))