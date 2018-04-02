**COLD START D2V**

This package is a demonstration of a 'cold start' article recommendation system that utilizes a user's browsing history to perform Kmeans clustering of Doc2Vec vectors. 

From the browsing history, the recommender generates a profile of the user's most important, recent interests. The recommender system can then use the profile to make article recommendations that most closely match the user's interest from a given article corpus . 

![Screen Shot
](https://github.com/escottgoodwin/cold_start_d2v/blob/master/static/screenshot.png)

**BACKGROUND**

Many article recommendation systems currently use collaborative or content-based filtering or other methods that make recommendations based on the user's interaction with the site.  

**Collaborative Filter**

A collaborative filter recommendation system would create a user profile from the users previous interactions with the site and make recommendations based on the user profile's similarity to other user profiles. A collaborative system would recommend articles that other similar users had clicked on and/or rated, but which had not yet been viewed by the user. 

**Content Based**

Content based systems compare the similarity of articles, often based on article tags. If a user clicks on article with tags 'business,'marketing','sales', a content based recommender system would recommend articles with the similar tags. Relying on tagging in this way is a major limitation for content based systems in two ways. First, having to provide tags can be burdensome. Secondly, a collection of tags may not accurately represent an article's subject matter. An article may have too few tags to convey the nuance of it's subject matter, or the tags themselves may be too general to use in making recommendations. Also, basic tagging systems weight all tags equally, so we may not get a sense of what the article is really about. A marketing article may use a example from baseball in one paragraph, but be tagged 'maketing', 'baseball.' This could lead a content based recommender to recommend articles about baseball, even though the article is really about marketing. 

 **Latent Dirichlet Allocation (LDA)**

Some content based recommenders have attempted to use latent Dirichlet allocation (LDA), such as LDA2VEC, to provide tag weighting to more accurately represent what percentage of each subject is in a given article. However, even this method is limited by the need to specify a certain number of topics to represent the article. 

The main obstacle facing both systems is the need for user interaction before the system can make useful recommendations tailored to the user's interests, which is often referred to as the 'cold start problem.' 

**COLD START D2V**

This recommender system attempts to solve that problem by modeling a user's interests based on recent browsing history. 

**TO RUN**

    1. cd into cold_start_d2v directory
    2. run - python cold_start.py

Once recommendations are generated, you can run the flask server to get the last set of recommendations by running `python cold_start_flask.py`.

Running the script will perform the following operations. 

**1.  Download Corpus**

Download a corpus of a week's worth of news articles retrieved from a variety of newspapers and popular blogs that represent a wide variety of topics(business,politics,sports,technology,entertainment etc). (237 MB). 

To keep this demonstration package self contained with minimal additional set up, the corpus is a text file. In production, the corpus articles would likely be stored in a database. 

**2. Create a Doc2Vec model from this corpus.** 

Every article is represented by a 100 dimensional vector and occupies a 'point' in a vector space. The vector space represents a continuous space of semantic 'meanings' or 'topics' contained in the corpus. Broadly human intelligible topics - such as business, sports etc -  will occupy an 'area' within the vector space and articles related to a given topic will be located near other articles related to the same topic. 

**3. Download Browsing History**
 
 Download the user's chrome history for a given number of days - default 2 days. (This package only works for Mac and Windows chrome browsers for demo purposes). 

**4.  Filter Browsing History**

Filter the user history for articles that provide information about a user's interest. 

This filters out base web addresses, on the theory that specific articles on a site will better indicate a user's interest. There are also a number of hardcoded filters in this demo. 

**5. Download History Articles**

Download all the articles in user's filtered history. These articles will also be translated into the user's native language. Since Doc2Vec relies on a comprehensive vocabulary of the corpus to create the semantic vector space (topic/subject space), it is important that the browsing history articles are monolingual. We don't want business articles in German to occupy a different vector space 'area' than business articles in English when modeling user interests. For the purpose of modelling user interests, all business articles should be located near one another in the vector space. In certain use cases, however, one may want to keep interests in one language separate from interests in another language. 

**6. Generate Vectors for  Articles in History**

Create vectors for the articles in the user's filtered history using the Doc2Vec model created from the corpus. 

**7. Cluster History Vectors**

Use KMeans clustering to cluster the vectors from the user's history. (Default 15 clusters). 

**8. Get Popular Clusters**

Get the most 'popular' vector clusters, as determined by the clusters with the greatest number of articles in them. 

The number of articles in a cluster serves as a representation for the level of user interest in the 'topic' of that cluster. The default identifies the top 33% of clusters with the most articles. (With defaults, the 5 most popular clusters of 15 clusters). 

**9. Popular Cluster Vector Centers**

Determine the vector centers of the most popular clusters. 

**11. Recommend Articles From Popular Vector Centers**

Use the most popular vector centers to make article recommendations (links) for each cluster from the corpus using Doc2Vec's built-in similarity function, which uses cosine distance to determine similarity. (Default 20 articles per cluster). 

Duplicate links are filtered out. Recommended links are saved in a text file. 

**12. Display Recommendations in Flask Website**

A flask server will start automatically and open a webpage with the recommended links for each category cluster links in a new tab/window. A histogram with the number of articles in every cluster appears at the bottom. 

Terminal Output 

The terminal should output the time required for step 

**Runtime**

Runtime will depend on connection speed. First run will be considerably longer because it requires downloading the corpus and the creation of the Doc2Vec model. Subsequent runs will be quicker because only the articles from the user history will be downloaded. With common consumer connection and computing speeds, first run will take about 15-20 minutes and subsequent runs will be about 5-8 minutes. 

According to gensim's documentation, using a C compiler would significantly optimize training and speedup model generation by a factor of 70. A model that took 8 minutes to generate would take only about 7 seconds after optimization.

**Number of Recommendation Clusters**

The ideal number of recommendation clusters for a given corpus and a given number of articles in user history can be investigated with the Elbow method, or other cluster evaluation methods mentioned in [ Determining The Optimal Number Of Clusters: 3 Must Know Methods](http://www.sthda.com/english/articles/29-cluster-validation-essentials/96-determining-the-optimal-number-of-clusters-3-must-know-methods/#elbow-method). Example - for 100 articles, 10 clusters, for 500 articles, 20 clusters etc. 

Adjusting the number of clusters in this way relies on an assumption that, as the number of articles increases, there will likely be a larger number of user interests represented in the history, or that a user's interests are more 'fine grained' within a given broad topic. Getting the number of 'interests' and 'granularity' right will improve the quality of recommendations. 

**USING A CUSTOM ARTICLE CORPUS**

You can use a custom corpus of articles in the following format:

    [
    {'article':'article1 text string','date':date1 string','link':'http://www.link1.com'},
    {'article':'article2 text string','date':date2 string','link':'http://www.link2.com'},
    ...
    ]

It is important to have links for each article. 

Then, in the main function, change the `corpus_url` variable to the location of your properly formatted corpus. 

    def main():
    	corpus_url = 'http://location_of_your_corpus'

**KEY ADVANTAGES**

**1. No user interaction required.** 

A user's interest profile can be modeled from their browser history and 'projected' into a given corpus. In practice, browser history could be obtained from browser plugin a user voluntary installs or from a vendor that tracks browsing behaviour through cookies. 

**2. User Interests in a Continuous Vector Space**

User interests exist in the continuous semantic space of the corpus. No tags, no trying to determine the distribution percentage  of an arbitrary number of 'topics' - 20% Marketing, 45% Sales, 30% Data Science, 5% Hospitals. 

The continuous nature of the semantic space leads to recommendations that are related to various aspects within the subject article that are not clear, discrete human intelligible topics. This sort of recommending would prove to be more difficult with discrete topics, such as tags, chosen by a rater. 

**Example**

For example, an article about instituting a 'sin tax' on alcohol and tobacco sales, will result in article recommendations about:

1. Other sin taxes in that geographic region.
2. Levels of alcohol and tobacco use and attempts to control it. 
3. Dangers and costs related to alcohol and tobacco use. 
4. How consumers respond to price changes. 
5. Other hazardous consumer products and attempts to regulate them to enhance safety. 

The continuous nature of the vector space enhances the recommender's ability to make recommendations of articles containing 'topics' most central to the article without the need to arbitrarily determine discrete, human intelligible topics. In a continuous space, the 'topics' need not be human intelligible in order to be useful. While it is quite easy to grasp intuitively what the 'sin tax' article is generally about, modeling it with a mix of discrete categories - especially categories that could hold for a corpus covering a wide-range of topics -  would be more difficult and, I suspect, lead to less effective recommendations. 

The recommender may recommend articles 'tangential' to the central 'topic' of the subject article. These tangential aspects can provide a different perspective regarding the 'topic' of the article and may spur further investigation in directions that may not have been readily apparent. Often, this leads to recommendations with a serendipitous quality and a multifaceted representation of the article's subject matter.

**AREAS FOR FURTHER INVESTIGATION**

**1. Integration With Other Types of Recommenders** 

Once a user begins interacting with a site, this cold start clustering method could be integrated and/or refined with collaborative filtering methods based on user profiles generated from website interaction data. 

**2. Updating Doc2Vec Model**

Continuous Update of Corpus Doc2Vec Model. Currently, every time articles are added to the corpus, the entire Doc2Vec model must be generated from scratch. Developing a continuous updating method where new articles can be added to an existing Doc2Vec model would lead to significant improvements in speed. 

**4. Pre-Trained Word Vectors**

Using pre-trained word vectors, such as FastText, with Doc2Vec. 

**5. Article Recommendations by Date** 

Get recommendations by date. Only recommend articles in the corpus that are recent. 

**6. Ideal Number of Recommendation Category Clusters**

Develop/Integrate a method to automatically determine ideal number of clusters for corpus/number of articles on the fly. 

**7. Master User Interest Profile** 

Currently, a user's interests are only modeled from past X number of days of browsing history. While a user's most recent interests are important for getting and maintaining interest in a given corpus at a given moment in time, developing a master profile including all the user's browsing history would be valuable as well. One could then make additional recommendations based on 'long tail' interests. 

A master interest profile developed from this model may differ from a user interest profile generated purely from user interactions with the subject website and, therefore, provide additional insights into the subject website's user base. Executives could better understand their users' long-term or recurrent interests and use that knowledge to determine editorial direction and inform various strategic business initiatives, such as market positioning. 

**8. Single Rank of Recommendations For All Category Clusters**

Individual article recommendations could be ranked in a single list by taking the cosine distance and weighting it by the popularity of the cluster the article belongs to. Links with high cosine similarity scores (or small cosine distances) are considered highly related to the 'center' of user's interest. However, some interests are more popular or more important than others. Therefore,  a master ranking could be developed, for example, where the first recommendation in the fourth most popular category cluster would be listed above the fifteenth recommendation from the most popular category cluster. 



<!--stackedit_data:
eyJoaXN0b3J5IjpbMTM2ODc1MDIyOF19
-->