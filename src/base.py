# -*- coding:utf8 -*-
import random

def rangeGauss(l,r):
	sigma = (r-l)/5.0;
	val = random.gauss((l+r)*0.5,sigma);
	val = min(r,val);
	val = max(l,val);
	return val;

def rangeGuassWithCenter(center, sigma, l, r):
	val = 0;
	while True:
		val = random.gauss(center,sigma)
		if (val >= l and val <= r):
			break
	return val;

def printAndWriteFileLn(f,s):
	print s;
	f.write(s+"\n")

def getRandomByRatio(li,ratio):
	a = random.random();
	i = 0;
	while True:
		a -= ratio[i];
		if (a <= 0):
			break;
		i += 1
	return li[i];

def getRandomByRangeRatio(li,ratio):
	(a,b) = getRandomByRatio(li,ratio)
	return random.uniform(a,b);

if __name__ == '__main__':
	print rangeGuassWithCenter(3,1,2,6)