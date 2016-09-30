import urllib2,cookielib,re,socket
import bs4 as BeautifulSoup
import HTMLParser
import nltk as nltk
from nltk.tag import pos_tag
from nltk import FreqDist
from nltk.corpus import stopwords
from nltk import WordNetLemmatizer
from nltk.collocations import *

lmtzr = WordNetLemmatizer()

def import_data(num_blogs):
	with open("blog_data.txt", "wt") as data_file:
		pass
	with open("blog_urls.txt") as blog_urls:
		i = 0
		for url in list(blog_urls)[:num_blogs]:
			print str(i)
			i = i + 1
			req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})
			try:
				blog = urllib2.urlopen(url, timeout=4)
				soup = BeautifulSoup.BeautifulSoup(blog.read(), 'html.parser')

				link = soup.find('link', type='application/rss+xml')

				if link is not None:
					rss = urllib2.urlopen(link['href'], timeout=4).read()
					soup = BeautifulSoup.BeautifulSoup(rss, 'html.parser')
					description = soup.find_all('description')
					cleanHTML = HTMLParser.HTMLParser().unescape(str(description))
					clean_data = re.sub('<[^>]*>', '', cleanHTML)  
					clean_data = re.sub('[^a-zA-Z0-9 \n\.]', ' ', clean_data)

					with open("blog_data.txt", "a") as data_file:
						data_file.write('{}\n'.format(clean_data))

			except urllib2.HTTPError, e:
				print "error"
				continue
			except urllib2.URLError, e:
				print "error"
				continue
			except socket.timeout, e:
				print "timeout"
				continue
			except ValueError, e:
				print 'Error: Invalid URL'
			
def tag():
	print "POS tagging"
	i = 0
	with open("blog_data.txt", "r") as raw_text:
		print i
		i = i + 1
		raw_text = raw_text.read()
		text = nltk.word_tokenize(raw_text)
		tokens = [t.lower() for t in text]
		tagged_sent = pos_tag(tokens)
		return tagged_sent

def get_names(tagged_data):
	nouns = []
	for word,pos in tagged_data:
		if pos in ['NN', 'NNP', 'NNS']:
			nouns.append(word)
	for noun in nouns:
		if noun in stopwords.words('english'):
			nouns.remove(noun)
	nouns_new = []
	for noun in nouns:
		noun = noun.replace('.','')
		noun = lmtzr.lemmatize(noun)
		nouns_new.append(noun)

	freq_nouns = FreqDist(nouns_new)
	print freq_nouns
	print " Top 10 occuring nouns : \n"
	for w in freq_nouns.keys()[:10]:
		print freq_nouns[w],w

def get_words(tagged_data):
	words = []
	for word,pos in tagged_data:
		if pos in ['NN', 'NNP', 'NNS', 'NNPS', 'JJ', 'JR', 'JJS', 'VB', 'VBD', 'VBG', 'VBP', 'RB']:
			words.append(word)
	for word in words:
		if word in stopwords.words('english'):
			words.remove(word)
	words_new = []
	for word in words:
		word = word.replace('.','')
		word = lmtzr.lemmatize(word)
		words_new.append(word)

	freq_words = nltk.FreqDist(words_new)
	print " Top 10 occuring words : \n"
	for w in freq_words.keys()[:10]:
		print freq_words[w],w

def collocation():
	with open("blog_data.txt") as raw_text:
		text = raw_text.read()
		unicode(text, 'ascii', 'ignore')
		text = text.split()
		text_new = []
		for t in text:
			if t in stopwords.words('english'):
				text.remove(t)
		for t in text:
			t = lmtzr.lemmatize(t)
			text_new.append(t)

		bigram_measures = nltk.collocations.BigramAssocMeasures()
		trigram_measures = nltk.collocations.TrigramAssocMeasures()

		finder2 = BigramCollocationFinder.from_words(text_new)
		finder3 = TrigramCollocationFinder.from_words(text_new)
		finder2.apply_freq_filter(3) #Remove those whose freq is less than 3
		finder3.apply_freq_filter(3)
		print "Two word collocations : "
		print finder2.nbest(bigram_measures.pmi, 10)
		print "Three word collocations : "
		print finder3.nbest(trigram_measures.pmi, 10)


if __name__ == '__main__':

	num_blogs = int(raw_input("Enter the number of blogs(between 1-500) to be analyzed: "))
	import_data(num_blogs)

	tagged_data = tag()

	collocation()

	get_names(tagged_data)

	get_words(tagged_data)



