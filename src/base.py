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

if __name__ == '__main__':
	print rangeGuassWithCenter(3,1,2,6)