import json
import time
from stop_words import get_stop_words
from gensim.models.doc2vec import Doc2Vec,TaggedDocument

def create_doc2vec_model(articles,name,vector_size=100,epochs=10,lang='en'):
    # import stopwords for specific language of model
    stop_words = get_stop_words(lang)
    ## list of just articles (str)
    justarticles = [x['article'] for x in articles]
    #strip stopwords article docs
    nostop = [[i for i in doc.lower().split() if i not in stop_words] for doc in justarticles]
    #tokenize article docs and convert to doc2vec tagged docs - each article has an index number and list of tokens - taggedoc(['token1','token2',[1]])
    tagged = [TaggedDocument(doc,[i]) for i,doc in enumerate(nostop)]
    # instantiate doc2vec model with parameters - size = # of nums representing each doc (100), min_count - occurences of words in vocab (filter out rare words), iter - passes to create vectors
    model = Doc2Vec(vector_size=vector_size, min_count=2, epochs=epochs)
    ## build vocab from all tagged docs
    model.build_vocab(tagged)
    ## train model on tagged docs - total examples - total # of docs
    model.train(tagged,total_examples=model.corpus_count,epochs=epochs)
    # save model with language - eg esmodel.model for spanish docs
    model_name = name + 'model.model'
    model.save(model_name)
    model.delete_temporary_training_data(keep_doctags_vectors=True, keep_inference=True)
    print('saved as: ' + model_name)

def format_arts(articles):
    ## takes a list of articles (str) and puts in the dict form required to make the doc2vec models with dummy entries
    ## {'article':'article text string','date':'today's date string','link':'http://www.nolink.com'}
    from datetime import date
    date,link = [date.today(),'http://www.nolink.com']
    format_arts = [{'article':article,'date':str(date),'link':link} for article in articles]
    return format_arts

def main():
    ## sample of aobut a week of articles (approx 50,000) from a variety of english language news sources
    ## articles are a dict = {'article':'article text string','date':'date string','link':'link string'}
    model_name = 'news'
    ## creates doc2vec model from english news articles named 'newsmodel.model'
    create_doc2vec_model(articles,model_name)

if __name__ == '__main__':
    main()
