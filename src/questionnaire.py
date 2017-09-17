# -*- coding:utf8 -*-
import random
import Queue
from base import *

def sgn(a):
	return 1 if a>=0 else -1;

class Question:
	# MAX: totally disagree; MIN: totally agree
	MAX_OP = 7;  
	MIN_OP = 1;

	@classmethod
	def getOpps(cls, score):
		return (cls.MAX_OP + cls.MIN_OP) - score;

	@classmethod
	def getRandomAns(cls):
		return random.randint(cls.MIN_OP, cls.MAX_OP);
	@classmethod
	def getGaussAns(cls, center, sigma):
		return rangeGuassWithCenter(center, sigma, cls.MIN_OP, cls.MAX_OP);

	@classmethod
	def getSigmaFromRelation(cls,relation):
		re_abs = abs(relation);
		# relation  1   ==>   0
		# 2 ~ 2*2sigma   ==>  (MAX_OP - MIN_OP) ~ 2*2sigma 
		minSigma = 0.5;
		maxSigma = (cls.MAX_OP-cls.MIN_OP)*0.20

		return 0.5+(1-re_abs)*(maxSigma-minSigma)

	def __init__(self, _id, _score):
		self.id = _id;
		self.score = _score;
	def fillIndepent(self, factoryScore):
		if (self.score == 0):
			return Question.getRandomAns();
		else:
			center = Question.MIN_OP+(1-factoryScore)*(Question.MAX_OP-Question.MIN_OP);
			if (self.score < 0):
				center = Question.MAX_OP - center;
			return Question.getGaussAns(center, (Question.MAX_OP-Question.MIN_OP)*0.2);
	def fillWithSuggest(self, suggest, factoryScore):
		if (self.score == 0) :
			return Question.getGaussAns(suggest, (Question.MAX_OP-Question.MIN_OP)*0.45);
		else:
			center = suggest - (2*factoryScore-1)*self.score;
			return Question.getGaussAns(center,(Question.MAX_OP-Question.MIN_OP)*0.1);

	@classmethod
	def getSuggest(cls, pairScore, relation, isInvalid):

		if isInvalid == True or relation == 0:
			return cls.getRandomAns();
		else:
			sugCenter = pairScore if relation > 0 else cls.getOpps(pairScore);
			return cls.getGaussAns(sugCenter, Question.getSigmaFromRelation(relation));


class Questionnaire:
	qBase = []
	relatedPairs = {}; #(a,b)-->10
	relationMat = {};
	qusCnt = 0;

	#calculable
	minMaxSc = None;

	def __init__(self, _id,_wid):
		self.id = _id;
		self.score = 0;
		self.qCnt = Questionnaire.qusCnt;
		self.ansList = [0 for i in range(self.qCnt)];
		self.workerId = _wid

	def getWorker(self):
		from factory import Worker
		return Worker.getById(self.workerId);

	@classmethod
	def getMinMaxSc(cls):
		if cls.minMaxSc != None:
			return cls.minMaxSc;
		mi = 0;
		ma = 0;
		for q in cls.qBase:
			if (q.score == 1) :
				mi += Question.MIN_OP;
				ma += Question.MAX_OP;
			elif (q.score == -1) :
				mi += -Question.MAX_OP;
				ma += -Question.MIN_OP;
		cls.minMaxSc = (mi,ma);
		return cls.minMaxSc;

	def scoring(self):
		ret = 0;
		for i in range(len(self.ansList)):
			ret += Questionnaire.getById(i).score*Question.getOpps(self.ansList[i]);
		(mi,ma) = Questionnaire.getMinMaxSc();
		return (ret-mi)*1.0/(ma-mi)*100

	def finish(self):
		self.ansList = [int(round(i)) for i in self.ansList]

	@classmethod
	def addQ(cls,_q):
		cls.qBase.append(_q);
	@classmethod 
	def getById(cls, qid):
		return cls.qBase[qid];

	@classmethod
	def addRelation(cls, a,b, val):
		if (val == 0):
			return 
		if (b<a):
			a,b = b,a;
		cls.relatedPairs[(a,b)] = val;

	@classmethod
	def validateRelation(cls):
		clusterCnt = 0;
		cluster = {} # mark per question belongs to which cluster
		clusterRelation = {} # mark cluster pair-relationship
		cls.relationMat = {}


		for (pair, val) in cls.relatedPairs.items():

			a = pair[0];
			b = pair[1];
			score_a = cls.qBase[a].score;
			score_b = cls.qBase[b].score;
			if (score_a*score_b*val < 0):   # same type of questions should be postive-related
				print "question relationship validation failed at (%d,%d)..." % (a,b);
				return False;
			# deal a has cluster but b not
			if cluster.has_key(a) and not cluster.has_key(b):
				cluster[b] = cluster[a];
				clusterRelation[cluster[a]][b] = sgn(val)*clusterRelation[cluster[a]][a];

			# deal b has cluster but a not
			elif cluster.has_key(b) and not cluster.has_key(a):
				cluster[a] = cluster[b];
				clusterRelation[cluster[b]][a] = sgn(val)*clusterRelation[cluster[b]][b];
			elif not cluster.has_key(a) and not cluster.has_key(b):
				cluster[a] = cluster[b] = clusterCnt;
				clusterCnt += 1;
				clusterRelation[cluster[a]] = {a:1, b:sgn(val)};
			else:
				ca = cluster[a]
				cb = cluster[b]
				if ca == cb:
					if (clusterRelation[ca][a] * clusterRelation[cb][b] * val < 0):
						print "question relationship validation failed at (%d,%d) on %s..." % (a,b,str(clusterRelation[ca]));
						return False;
				else:
					for (k,v) in clusterRelation[cb].items():
						clusterRelation[ca][k] = sgn(v)*sgn(val)*sgn(clusterRelation[cb][b]*clusterRelation[ca][a]);
						cluster[k] = ca;
					clusterRelation.pop(cb);

				if (cls.relationMat.has_key(a)):
					cls.relationMat[a].append((b,val));
				else:
					cls.relationMat[a] = [(b,val)];

			if (cls.relationMat.has_key(b)):
				cls.relationMat[b].append((a,val));
			else:
				cls.relationMat[b] = [(a,val)];
		return True

	@staticmethod
	def testValidateRelation():
		Q = Questionnaire(121,3);
		Q.addQ(Question(0,1));
		Q.addQ(Question(1,1));
		Q.addQ(Question(2,-1));

		Q.addRelation(0,1,10);
		Q.addRelation(1,2,-5);
		Q.addRelation(0,2,-5);
		print Q.validateRelation();

	def getNewFactoryScore(self, oldFs, qid):
		fac = self.getWorker().getFactory();
		bl,gl = fac.badList,fac.goodList;
		if (qid in bl):
			return min(1.0,oldFs*1.1);
		elif (qid in gl):
			return oldFs*0.9;
		else:
			return oldFs;


	def fillIn(self, factoryScore, isInvalid = False):
		unfilled = set([i for i in range(self.qCnt)]);
		while (len(unfilled) > 0) :
			beg = random.choice(list(unfilled));
			Q = Queue.Queue();
			Q.put((beg,None))
			unfilled.remove(beg)
			while (not Q.empty()):
				(cur,suggest) = Q.get();
				fs = self.getNewFactoryScore(factoryScore, cur)
				if suggest == None:
					self.ansList[cur] = Questionnaire.qBase[cur].fillIndepent(fs);
				else:
					self.ansList[cur] = Questionnaire.qBase[cur].fillWithSuggest(suggest, fs);
				if Questionnaire.relationMat.has_key(cur):
					random.shuffle(Questionnaire.relationMat[cur])
					for (k,v) in Questionnaire.relationMat[cur]:
						if k in unfilled:
							sug = Question.getSuggest(self.ansList[cur],v,isInvalid);
							Q.put((k,sug));
							unfilled.remove(k);

if __name__ == '__main__':
	Questionnaire.testValidateRelation();
