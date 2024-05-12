#what should this script do?
#given an amazon bestsellers snapshot, it should generate:
#	most popular title terms per category + overall

#ok then what
#	do this to each dataset collected, place results in a folder and add them to the site with some explanations
#	consider finding which product listings include the most favored terms and list em?

from sklearn.feature_extraction.text import TfidfVectorizer
import json
import sys
import os
import pandas as pd
path = sys.argv[-1]
if ".json" not in path:
	raise Exception("Path to product list json file must be provided.")
output_filename_start = path[:-27] 

data = json.load(open(path))


vectorizer = TfidfVectorizer(max_df=.7, min_df=1)
def tf_idf(documents):
	transformed_documents = vectorizer.fit_transform(documents)
	transformed_documents_as_array = transformed_documents.toarray()

	tfidf_results = []
	for doc in transformed_documents_as_array:
	    tf_idf_tuples = list(zip(vectorizer.get_feature_names_out(), doc))
	    one_doc_as_df = pd.DataFrame.from_records(tf_idf_tuples, columns=['term', 'score']).sort_values(by='score', ascending=False).reset_index(drop=True)
	    tfidf_results.append(one_doc_as_df)
	r = pd.concat(tfidf_results)
	return r.sort_values(by=['score'], ascending=False)


all_titles = []
cat_tfidfs = {}

for category in data: 
	cat_titles = []
	if len(data[category]) == 0:
		continue
	titles_string = ''
	for product in data[category]:
		title = product[0]
		if title == None or not type(title) is str:
			continue
			#skip any where title was not scraped
		cat_titles.append(title)
		titles_string += ' ' + title
	all_titles.append(titles_string)

	category = category.replace('&amp;', '&')
	cat_tfidfs[category] = tf_idf(cat_titles).term.unique().tolist()[:10]	
	
cat_tfidfs['overall_terms'] = tf_idf(all_titles).term.unique().tolist()[:10]

with open(output_filename_start + '_term_analysis.json', 'w') as f:
	f.write(json.dumps(cat_tfidfs))

folder = output_filename_start.rsplit('/')[0]
#generates a list of analysis files for frontend to read
os.system('ls ' + folder + '| grep "analysis" > ' + folder + '/index')
