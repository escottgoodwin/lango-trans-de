**BROWSING HISTORY FOREIGN LANGUAGE RECOMMENDATIONS**

Generate foreign language recommendations based on a user's browsing history. 

**Process**

1. Get links from user's browsing history (stored in database) 
2. Download articles from the user's links. 
3. Filter articles by length, file type, domain.
4. Make filtered articles monolingual in user's native language. 
5. Vectorize articles with a Doc2Vec model of user's native language. 
6. Cluster vectors to find semantic topics of interests. Choose number of clusters
7. Get most popular clusters (clusters with the most articles in the cluster) - eg top 25% 
8. Translate the articles in the most popular clusters into the target foreign language. 
9. Vectorize translated articles using a Doc2Vec model of the target language. 
10. Find the mean of the vectors in each cluster - the center 'point' of the all the vectors in that cluster.
11. Use the center point of each cluster to find the n most similar articles using the target language Doc2Vec model - outputs list of art_ids of articles in the database used to create the Doc2Vec model. 
12. Store the most similar article recommendations in the database according to user and date - art_id, userid, date, cluster number and target language.
