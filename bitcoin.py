import requests
import csv
import numpy as np 
import codecs 
from sklearn.svm import SVR 
from contextlib import closing 
import matplotlib.pyplot as plt
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_pymongo import PyMongo
import json


app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'albythoconnect'
app.config['MONGO_URI'] = 'mongodb://albytho:Brownknight97@ds143151.mlab.com:43151/albythoconnect'
mongo = PyMongo(app)
stocks = []

def get_data():
	choice = input('Stocks or Bitcoin? (s/b): ')
	prices_of_stocks = []
	dates_of_stocks = []

	if choice is "b":
		dates = []
		prices = []
		with open('bitcoin_price.csv') as csvfile:
			readCSV = csv.reader(csvfile, delimiter=',')
			index = 0
			for row in readCSV:
				if index>0:
					dates.append(index)
					prices.append(row[1])
					if index is 201:
						break;
				index = index + 1
	else:
		stocks.clear()
		while(True):
			stock = input("Enter Stock Name:")
			if stock == "":
				break;
			else:
				stocks.append(stock)

		for i in stocks:
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


		print("Predicted Price of",stocks[i],"After One Day:",svr_rbf.predict(x)[0])

		new_dates_local = [x[0] for x in dates_local.tolist()]
		new_dates_of_stocks_local.append(new_dates_local)
		new_prices_of_stocks_local.append(prices_local.tolist())
		new_predicted_prices_of_stocks_local.append(svr_rbf.predict(dates_local).tolist())

	return new_dates_of_stocks_local, new_prices_of_stocks_local, new_predicted_prices_of_stocks_local

@app.route('/')
def home():

	dates_of_stocks,prices_of_stocks = get_data()
	new_dates_of_stocks,new_prices_of_stocks,new_predicted_prices_of_stocks = predict_prices(dates_of_stocks,prices_of_stocks,len(dates_of_stocks[0])+1)

	return render_template('index.html',dates=json.dumps(new_dates_of_stocks),prices=json.dumps(new_prices_of_stocks),predicted_prices=json.dumps(new_predicted_prices_of_stocks))

if __name__ == '__main__':
    app.run(threaded=True, debug=True)


