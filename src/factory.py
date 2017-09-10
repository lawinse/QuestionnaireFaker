# -*- coding:utf8 -*-
from questionnaire import *
import random
from base import *


class Factory:
	fBase = []
	def __init__(self,_id,_wc,_sc = 0):
		self.id = _id;
		self.workerCnt = _wc;
		self.score = _sc;
		self.workersId = [0 for i in range(_wc)]
		self.invRatio = 0;

	def isInvalid(self):
		return (random.random() < self.invRatio); 

	@classmethod
	def addFactory(cls, f):
		cls.fBase.append(f);
	@classmethod
	def getById(cls, fid):
		return cls.fBase[fid];



class Worker:
	wBase = []
	def __init__(self,_id,_fid):
		self.id = _id;
		self.qn = Questionnaire(_id);
		self.factoryId = _fid;
		self.char = rangeGauss(-0.1,0.1);
		self.isInvalid = Factory.getById(self.factoryId).isInvalid();
	def conduct(self):
		self.qn.fillIn(Worker.getScore(Factory.getById(self.factoryId).score,self.char), self.isInvalid);
		self.qn.finish();
	@staticmethod
	def getScore(factoryScore, char):
		return min(max(factoryScore + char,0.05),0.95);
	@classmethod
	def addWorker(cls, w):
		cls.wBase.append(w);
	@classmethod
	def getById(cls, wid):
		return cls.wBase[wid];

