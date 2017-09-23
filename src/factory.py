# -*- coding:utf8 -*-
from questionnaire import *
import random
from base import *


class Factory:
	fBase = []
	def __init__(self,_id,_wc,_sc,_invR,_awc,_gl,_bl):
		self.id = _id;
		self.workerCnt = _wc; # refer to number of conducting questionnaire
		self.score = _sc;
		self.workersId = [0 for i in range(_wc)]
		self.invRatio = _invR;
		self.goodList = _gl;
		self.badList = _bl;
		self.allWorkerCnt = _awc;

	def isInvalid(self):
		return (random.random() < self.invRatio); 

	@classmethod
	def addFactory(cls, f):
		cls.fBase.append(f);
	@classmethod
	def getById(cls, fid):
		return cls.fBase[fid];
	@classmethod
	def getAllWorkersId(cls):
		ret = []
		for fac in cls.fBase:
			ret += [wid for wid in fac.workersId];
		return ret;



class Worker:
	wBase = []

	GEN_INFO = ["gender","age","degree","marriageState","careerLength","depart","position","workType","bonusRatio","allWorkerCntLvl"]

	GENDER = ["male", "female"];
	AGE = [(18,29),(29,39),(39,49),(49,59),(59,69),(69,70)]
	MARRIAGESTATE = ["Single","Married", "Divorced", "Else"]
	DEGREE = ["junH","senH","bachelor","master+"]
	CAREERLENGTH = [(0,1),(1,2),(3,5),(6,10),(11,15),(16,100)]
	DEPART = ["ShengChan", "PinGuan", "CaiGou", "WuKong", "CaiWu", "BanGong", "XiaoShou", "JiShu","Else"]
	POSITION = ["Chuji", "JianDu", "GuanLi", "DongShi"]
	WORKTYPE = ["hours", "pt<1yrs","pt>1yrs","ft"]
	BONUSRATIO = [0,10,20,30,40,50,60,70,80,90,100]
	ALLWORKERCNTLVL = [(0,50), (51,100), (101,200),(201,300),(301,400),(401,500),(500,10000)]

	GENDER_R = [0.58,0.42];
	AGE_R = [0.11,0.29,0.32,0.25,0.03,0.0]
	MARRIAGESTATE_R = [0.15,0.74,0.08,0.03]
	WORKTYPE_R = [0.03,0.02,0,0.95]


	def __init__(self,_id,_fid):
		self.id = _id;
		self.qn = Questionnaire(_id,_id);
		self.factoryId = _fid;
		self.char = rangeGauss(-0.1,0.1);
		self.isInvalid = Factory.getById(self.factoryId).isInvalid();
		self.isInvalidMarked = 0;

		# General
		self.gender = 0;
		self.age = 0;
		self.degree = 0;
		self.marriageState = 0;
		self.careerLength = 0;
		self.depart = 0;
		self.position = 0;
		self.workType = 0;
		self.bonusRatio = 0;
		self.allWorkerCntLvl = 0;

	def getFactory(self):
		return Factory.getById(self.factoryId);
	def conduct(self):
		self.preFillInGeneralInfo();
		self.qn.fillIn(Worker.getScore(Factory.getById(self.factoryId).score,self.char), self.isInvalid);
		self.postFillInGernaralInfo();
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

	def preFillInGeneralInfo(self):	
		self.gender = getRandomByRatio(Worker.GENDER, Worker.GENDER_R);
		self.age = getRandomByRatio(Worker.AGE, Worker.AGE_R);
		self.marriageState = getRandomByRatio(Worker.MARRIAGESTATE, Worker.MARRIAGESTATE_R);
		self.workType = getRandomByRatio(Worker.WORKTYPE, Worker.WORKTYPE_R);

	def postFillInGernaralInfo(self):
		# Gen depart depneds on Q139
		q139Ans = self.qn.ansList[139];
		if (int(round(q139Ans)) in [1,2]):
			if (random.random() < 0.98):
				idx = max(min(rangeGauss(2,9),9),1)-1
			else:
				idx = max(min(rangeGauss(0,2.5),9),1)-1
		else:
			if (random.random() < 0.95):
				idx = max(min(rangeGauss(0,2.5),9),1)-1
			else:
				idx = max(min(rangeGauss(1,9),9),1)-1
		self.depart = Worker.DEPART[int(round(idx))]

		# Gen degree
		li = [self.qn.ansList[i] for i in [90,92,96,98,100,101]];
		aver = sum(li)/len(li)/Question.MAX_OP*4;
		self.degree = Worker.DEGREE[4-int(round(aver))]

		# Gen POS
		li = [self.qn.ansList[i] for i in [90,92,96,98,101]];
		aver = sum(li)/len(li)
		fsLike = (-aver + 4) /3.0
		sug = 2.0/(1.0/self.qn.ansList[100] + 1.0/self.qn.ansList[129])
		ans = Question(-1,-1).fillWithSuggest(sug,fsLike);
		self.position = max(1,min(ans/7.0*4.0,4))



		# Gen Careerlength
		pos = int(round(self.position))
		if (pos == 2):
			self.careerLength = getRandomByRangeRatio([(1.5,3.5),(3.5,4.5),(4.5,6)],[0.72,0.23,0.05])
		elif (pos == 3) :
			self.careerLength = getRandomByRangeRatio([(3.5,4.5),(4.5,5.5),(5.5,6)],[0.15,0.45,0.4])
		elif (pos == 4) :
			self.careerLength = getRandomByRangeRatio([(4.5,6.5),(3,4.5)], [0.94, 0.06])
		else:
			self.careerLength = rangeGauss(1,3)
		self.careerLength = Worker.CAREERLENGTH[int(round(self.careerLength))-1];

		# Gen Bonus
		pos = self.position;
		center = (pos*0.25)*7;
		self.bonusRatio = Worker.BONUSRATIO[int(round(rangeGuassWithCenter(center,1,1,7,)))-1]

		self.position = Worker.POSITION[int(round(self.position))-1]

		awc = self.getFactory().allWorkerCnt;
		for item in Worker.ALLWORKERCNTLVL:
			if (awc >= item[0] and awc < item[1]):
				self.allWorkerCntLvl = item;
				break;












