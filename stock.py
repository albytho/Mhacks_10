import requests
import csv
import numpy as np 
import codecs 
from sklearn.svm import SVR 
from contextlib import closing 
import matplotlib.pyplot as plt
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
import json
import tweepy
from textblob import TextBlob


consumer_key = 'ZT3teoSauRNfVkIvaBWg1CGBH'
consumer_secret = 'qWwBp5BFAGubIeHKKSqKGCgFGXMG5AE2rAzm4LWIjJZ8uUmOy0'

access_token = '128648452-aCcCcHoM8EhGud0F6DgQ98tOS5mcAhMMEEXaEauz'
access_token_secret = 'EuNSIt3SEQw1IDPEEPiTii5s2OHzticaWzUIG8EIWMSnj'

auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token,access_token_secret)

api = tweepy.API(auth)

app = Flask(__name__)

def get_data(array_of_stock_names):
	prices_of_stocks = []
	dates_of_stocks = []

	for i in array_of_stock_names:
		dates = []
		prices = []
		url = 'http://www.google.com/finance/historical?q=NASDAQ%3A'+i+'&output=csv%27&output=csv'
		with closing(requests.get(url, stream=True)) as r:
			reader = csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'))
			reader.__next__()

			index = 1
			for row in reader:
				prices.append(float(row[1]))
				dates.append(index)
				index = index + 1
				if index is 201:
					break;

		prices.reverse()
		dates_of_stocks.append(dates)
		prices_of_stocks.append(prices)

	return dates_of_stocks,prices_of_stocks

def predict_prices(dates_of_stocks_local,prices_of_stocks_local,x):
	new_dates_of_stocks_local = []
	new_prices_of_stocks_local = []
	new_predicted_prices_of_stocks_local = []
	results = []

	for i in range(0,len(dates_of_stocks_local)):
		dates_local = dates_of_stocks_local[i]
		prices_local = prices_of_stocks_local[i]

		dates_local = np.reshape(dates_local,(len(dates_local),1))
		prices_local = np.array(prices_local)
		prices_local = prices_local.astype(np.float)
		
		svr_rbf = SVR(kernel='rbf',C=1e3, gamma=0.1)
		svr_rbf.fit(dates_local,prices_local)
		plt.scatter(dates_local,prices_local,color='black')
		plt.plot(dates_local,svr_rbf.predict(dates_local),color='red')


		results.append(svr_rbf.predict(x)[0])

		new_dates_local = [x[0] for x in dates_local.tolist()]
		new_dates_of_stocks_local.append(new_dates_local)
		new_prices_of_stocks_local.append(prices_local.tolist())
		new_predicted_prices_of_stocks_local.append(svr_rbf.predict(dates_local).tolist())

	return new_dates_of_stocks_local, new_prices_of_stocks_local, new_predicted_prices_of_stocks_local, results

def get_sentiment(array_of_stock_names):
	stock_sentiment = []
	for i in array_of_stock_names:
		public_tweets = api.search(i)
		analysis = 0
		count = 0
		for tweet in public_tweets:
			count = count + 1
			analysis = analysis + TextBlob(tweet.text).sentiment.polarity
		stock_sentiment.append(analysis/count)
	return stock_sentiment



@app.route('/')
def home():
	return render_template('index.html')


@app.route('/send',methods=['GET','POST'])
def send():
	if request.method == 'POST':
		list_of_stocks =  request.form['list_of_stocks']
		array_of_stock_names = list_of_stocks.split(",")

		dates_of_stocks,prices_of_stocks = get_data(array_of_stock_names)
		new_dates_of_stocks,new_prices_of_stocks,new_predicted_prices_of_stocks,results = predict_prices(dates_of_stocks,prices_of_stocks,len(dates_of_stocks[0])+1)
		stock_sentiment = get_sentiment(array_of_stock_names)



		return render_template('index.html',dates=new_dates_of_stocks,prices=new_prices_of_stocks,predicted_prices=new_predicted_prices_of_stocks,stock_names=array_of_stock_names,results=results,stock_sentiment=stock_sentiment)


if __name__ == '__main__':
    app.run(threaded=True, debug=True)


