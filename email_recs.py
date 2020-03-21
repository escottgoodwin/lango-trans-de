import os
import psycopg2
from dotenv import load_dotenv
import pandas as pd
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import datetime

load_dotenv()

dbname=os.environ['PGCONNECT_DBNAME']
user=os.environ['PGCONNECT_USER']
password=os.environ['PGCONNECT_PASSWORD']
host= os.environ['PGCONNECT_HOST']
port=os.environ['PGCONNECT_PORT']
    
def fetch_cur_recs(user_id):
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port, sslmode='require')
    cur = conn.cursor()

    sql = "select art_id, title, lang from recommendations where date_trunc('day', rec_date) = current_date AND user_id = %s"
    
    cur.execute(sql,(user_id,))
    recommendations = cur.fetchall()
    conn.close()
    return recommendations

def get_lang(lang):
    if lang == 'es': 
        return "Spanish"
    if lang == 'fr':  
        return "French"
    if lang == 'de':  
        return "German"
    if lang == 'en': 
        return "English"

def listToString(s):  
    str1 = "</p><p>" 
    return (str1.join(s)) 

def lang_section(recommendations,lang):
    language = get_lang(lang)
    df = pd.DataFrame(data=recommendations)
    langrecs=df[df[2]==lang]
    topten = list(langrecs[:10][1])
    count = langrecs[0].count()
    htmllang = f'<a href="https://lango-mui.firebaseapp.com/" ><h3> {count} {language} Articles</a> </h3> <p>'
    htmltitles = listToString(topten)
    full = htmllang+ htmltitles + '</p>'
    return full

def get_user(user_id):
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port, sslmode='require')
    cur = conn.cursor()
    sql = "select name,email, langs from users where id = %s"
    cur.execute(sql,(user_id,))
    user1 = cur.fetchall()
    conn.close()
    return user1[0]

def gen_email(user_id):
    rec_user = get_user(user_id)
    recommendations = fetch_cur_recs(user_id)
    print(len(recommendations))
    htmlhead = f'<p><h1>{rec_user[0]} you have new <a href="https://lango-mui.firebaseapp.com/" >Langa Learn</a> articles!</h1><p>'
    allsecs = listToString([lang_section(recommendations,x) for x in rec_user[2]])
    fullmsg = htmlhead + allsecs
    return rec_user[1], fullmsg

def send_emails(user_id):
    today = datetime.date.today()
    datestr=today.strftime("%B %d %Y")
    subject=f'New Langa Learn Recommendations for {datestr}'
    email, htmlmessage = gen_email(user_id)
    message = Mail(
        from_email='recommendations@langalearn.com',
        to_emails=email,
        subject=subject,
        html_content=htmlmessage)

    sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
    

def main():
    apikey = os.environ['SENDGRID_API_KEY']
    print(apikey)
    user_id=22
    send_emails(user_id)

if __name__ == '__main__':
    main()