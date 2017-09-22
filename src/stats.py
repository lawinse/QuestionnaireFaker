# -*- coding:utf8 -*-

from factory import *
import os
from sklearn.externals import joblib
from matplotlib import pyplot
import numpy as np
import sys


class Stats:
	IS_DATA_LOADED = False;
	@classmethod
	def loadData(cls):
		if cls.IS_DATA_LOADED:
			return True;
		if not os.path.exists("../data/store.bin"):
			return False
		(Factory.fBase, Worker.wBase,\
			(Questionnaire.qBase, Questionnaire.relatedPairs,\
				Questionnaire.relationMat,Questionnaire.qusCnt,Questionnaire.minMaxSc),(Question.MAX_OP, Question.MIN_OP))\
		= joblib.load("../data/store.bin")
		cls.IS_DATA_LOADED = True;
		return True

	@classmethod
	def persistData(cls):
		joblib.dump((Factory.fBase, Worker.wBase,\
			(Questionnaire.qBase, Questionnaire.relatedPairs,\
				Questionnaire.relationMat,Questionnaire.qusCnt,Questionnaire.minMaxSc),(Question.MAX_OP, Question.MIN_OP)),\
		"../data/store.bin", compress = 3);

	@classmethod
	def genCsv(cls):
		for root, dirs, files in os.walk("../output/"):
			for name in files:
				os.remove(os.path.join(root, name))
		with open("../output/Factory_summary.csv", "w+") as fttl:
			generalInfo = Worker.GEN_INFO			
			fttl.write("worker_id,"+",".join(["Q"+str(i) for i in range(Questionnaire.qusCnt)] + generalInfo + ["validOrNot"])+"\n")
			for i in range(len(Factory.fBase)):
				fac = Factory.fBase[i]
				with open("../output/Factory_%d_result.csv" % (fac.id), "w+")as f:
					f.write("worker_id,"+",".join(["Q"+str(i) for i in range(Questionnaire.qusCnt)] + generalInfo + ["validOrNot"])+"\n")
					for wid in fac.workersId:
						wkr = Worker.getById(wid)
						qn = wkr.qn;
						gi = [str(wkr.__dict__[k]).replace(",","~") for k in generalInfo]
						f.write(str(wid)+","+",".join([str(item) for item in qn.ansList] + gi + ["True" if not wkr.isInvalid else "False"])+"\n")
						fttl.write(str(wid)+","+",".join([str(item) for item in qn.ansList] + gi + ["True" if not wkr.isInvalid else "False"])+"\n")

	@classmethod
	def scoring(cls):
		for fac in Factory.fBase:
			sc = 0;
			for wid in fac.workersId:
				wsc = Worker.getById(wid).qn.scoring();
				sc += wsc
				# print "Worker #%d (score: %0.2f) with selection:\t%s" % (wid,wsc,str(Worker.getById(wid).qn.ansList));
			print ">>>>> Fac #%d with aver score: %0.2f\n" % (fac.id,sc*1.0/fac.workerCnt);

	@staticmethod
	def getTopNCor(arr, rowvar, n, facId):
		from Queue import PriorityQueue
		cormat = np.corrcoef(arr, rowvar=rowvar);
		if facId == None:
			joblib.dump(cormat,"../data/cormat.bin",compress = 3);
		pq = PriorityQueue();
		for r in range(cormat.shape[0]):
			for c in range(cormat.shape[1]):
				if (c <= r):
					continue;

				if pq.qsize() < n:
					pq.put((abs(cormat[r,c]),(r,c)))
				else:
					curMin = pq.get();
					if curMin[0] > abs(cormat[r,c]):
						pq.put(curMin)
					else:
						pq.put((abs(cormat[r,c]),(r,c)))
		ansli = []
		while not pq.empty():
			ansli.append(pq.get())
		ansli = [(item[1], cormat[item[1]]) for item in ansli][::-1]
		return ansli

	@classmethod
	def getCor(cls):

		TOP_N = 20;

		facSeperate = [[] for i in range(len(Factory.fBase))]
		facTtl = []

		with open("../output/correlation.txt","w+") as f:
			for fac in Factory.fBase:
				for wid in fac.workersId:
					if (Worker.getById(wid).isInvalid):
						continue;
					facSeperate[fac.id].append(Worker.getById(wid).qn.ansList)
					facTtl.append(Worker.getById(wid).qn.ansList)
				facSeperate[fac.id] = Stats.getTopNCor(np.array(facSeperate[fac.id]),0,TOP_N, fac.id)
				printAndWriteFileLn(f,">>>>> Fac #%d with correlation ranking:" % (fac.id));
				printAndWriteFileLn(f,"\n".join([("(%d,%d) --> %.3f" % (item[0][0], item[0][1], item[1])) for item in facSeperate[fac.id]]) + "\n");

			facTtl = Stats.getTopNCor(np.array(facTtl),0,TOP_N,None)
			joblib.dump((facSeperate,facTtl), "../data/topcor.bin", compress = 3);
			printAndWriteFileLn(f, ">>>>> All fac with correlation ranking:");
			printAndWriteFileLn(f, "\n".join([("(%d,%d) --> %.3f" % (item[0][0], item[0][1], item[1])) for item in facTtl]));

	@classmethod
	def getDistribution(cls):
		facSeperate = [[[0 for k in range(Question.MAX_OP+1)] \
			for j in range(Questionnaire.qusCnt)] for i in range(len(Factory.fBase))]
		facTtl = [[0 for k in range(Question.MAX_OP+1)] for j in range(Questionnaire.qusCnt)]

		with open("../output/distribution.txt","w+") as f:
			for fac in Factory.fBase:
				for wid in fac.workersId:
					if (Worker.getById(wid).isInvalid):
						continue;
					for (qid, sel) in enumerate(Worker.getById(wid).qn.ansList):
						facSeperate[fac.id][qid][sel] += 1
						facTtl[qid][sel] += 1
				for i in range(len(facSeperate[fac.id])):
					aver = sum([idx*item for (idx, item) in enumerate(facSeperate[fac.id][i])])*1.0/sum(facSeperate[fac.id][i])
					facSeperate[fac.id][i] = ["%.2f%%" % (item*1.0/sum(facSeperate[fac.id][i])*100) for item in facSeperate[fac.id][i]]
					facSeperate[fac.id][i][0] = "Q%d: \t%s \twith aver. %.2f" % \
						(i, ",\t".join(["%d:%s" % (idx, facSeperate[fac.id][i][idx]) for idx in range(1,len(facSeperate[fac.id][i]))]),aver)
				printAndWriteFileLn(f,">>>>> Fac #%d with distribution:" % (fac.id))
				printAndWriteFileLn(f,"\n".join([item[0] for (item) in facSeperate[fac.id]]) + "\n")

			for i in range(len(facTtl)):
				aver = sum([idx*item for (idx, item) in enumerate(facTtl[i])])*1.0/sum(facTtl[i])
				facTtl[i] = ["%.2f%%" % (item*1.0/sum(facTtl[i])*100) for item in facTtl[i]]
				facTtl[i][0] = "Q%d: \t%s \twith aver. %.2f" % \
					(i, ",\t".join(["%d:%s" % (idx, facTtl[i][idx]) for idx in range(1,len(facTtl[i]))]), aver)
			joblib.dump((facSeperate,facTtl), "../data/distribution.bin", compress = 3);
			printAndWriteFileLn(f,">>>>> All fac with distribution:");
			printAndWriteFileLn(f, "\n".join([item[0] for (item) in facTtl]) + "\n");


	@classmethod
	def queryFactory(cls, fid, fname):
		distribution = joblib.load("../data/distribution.bin")[0][fid] if fid >=0 else joblib.load("../data/distribution.bin")[1]
		cor = joblib.load("../data/topcor.bin")[0][fid] if fid>= 0 else joblib.load("../data/topcor.bin")[1]
		
		workersId = []
		workerCnt = 0;
		allWorkerCnt = 0;

		if fid < 0 :
			workersId = [i for i in range(len(Worker.wBase))]
			workerCnt = sum([f.workerCnt for f in Factory.fBase])
			allWorkerCnt = sum([f.allWorkerCnt for f in Factory.fBase])
		else:
			fac = Factory.getById(fid)
			workersId = fac.workersId
			workerCnt = fac.workerCnt
			allWorkerCnt = fac.allWorkerCnt
		invalidCnt = sum([int(Worker.getById(wid).isInvalid) for wid in workersId])
		sc = 0;
		for wid in workersId:
			wsc = Worker.getById(wid).qn.scoring();
			sc += wsc
		sc /= float(len(workersId))
		def summarize(_item, _workersId):
			li = Worker.__dict__[_item.upper()]
			cnt = dict.fromkeys(li,0)
			for wid in _workersId:
				wkr = Worker.getById(wid)
				cnt[wkr.__dict__[_item]] += 1;
			return "[%s]: %s" % (_item,", ".join(["%s:%d" % (k,cnt[k]) for k in li]))
		generalInfo = [summarize(item, workersId) for item in Worker.GEN_INFO]

		with open(fname, "w+") as f:
			f.write("Basic Info of " + ("Factory #%d" %(fid) if fid >= 0 else "All Factories") + "\n\n")
			f.write("[workerCnt]:%d\n[allWorkerCnt]:%d\n[invalidCnt]:%d\n[questionnaireScoring]:%.2f\n" \
				% (workerCnt, allWorkerCnt, invalidCnt, sc))
			f.write("[GeneralInfo]:\n\t" + "\n\t".join(generalInfo) + "\n")
			f.write("[Distribution]:\n\t")
			f.write("\n\t".join([item[0] for (item) in distribution]) + "\n");
			f.write("[TopCor]:\n\t")
			f.write("\n\t".join([("(%d,%d) --> %.3f" % (item[0][0], item[0][1], item[1])) for item in cor]));


	@classmethod
	def queryQuestion(cls, qid, fname):
	 	qus = Questionnaire.getById(qid)
	 	distrib = joblib.load("../data/distribution.bin")[1][qid]
	 	relation = Questionnaire.relationMat.get(qid,{})
	 	corMat = list(joblib.load("../data/cormat.bin")[qid]);
	 	li = zip(corMat,[i for i in range(len(corMat))])
	 	li = sorted(li,reverse=True,key = lambda i:abs(i[0]))
	 	del li[0]
	 	with open(fname, "w+") as f:
	 		f.write(("Basic Info of Q%d" % qid) + "\n\n");
	 		f.write("[Distribution]:\n" + distrib[0] + "\n")
	 		f.write("[Relation set by user]:\n\t");
	 		f.write("\n\t".join(["~ %d relation: %.3f" % (k,v) for (k,v) in relation]) + "\n")
	 		f.write("[Top 40 Cor (Cov metrics)]:\n\t")
	 		f.write("\n\t".join(["~ %d cov: %.3f" % (v,k) for (k,v) in li[:40]]))

	@classmethod
	def queryQuestionPair(cls, pa, pb):
		from matplotlib.colors import LogNorm
		corrcoef = joblib.load("../data/cormat.bin")[pa][pb];
		palist = [Worker.getById(wid).qn.ansList[pa] for wid in Factory.getAllWorkersId()];
		pblist = [Worker.getById(wid).qn.ansList[pb] for wid in Factory.getAllWorkersId()];
		pyplot.hist2d(palist, pblist,bins=20, norm=LogNorm() , cmap = pyplot.get_cmap('binary'))
		pyplot.colorbar();
		pyplot.xlabel("Q#%d" % (pa));
		pyplot.ylabel("Q#%d" % (pb));
		pyplot.title('Realtionship between Q#%d and Q#%d -- corrcoef %.2f' % (pa,pb, corrcoef));
		pyplot.show()

	@classmethod
	def queryWorker(cls, wid, fname):
	 	wkr = Worker.getById(wid);
	 	fac = wkr.getFactory();
	 	generalInfo = ["%s: %s" % (item, str(wkr.__dict__[item])) for item in Worker.GEN_INFO]
	 	qn = wkr.qn

	 	with open(fname, "w+") as f:
	 		f.write(("Basic Info of Worker#%d" % wid) + "\n\n");
	 		f.write("[Factory]: # %d\n" % fac.id )
	 		f.write("[ValidOrNot]: %s\n" % ("False" if wkr.isInvalid else "True"));
	 		f.write("[GeneralInfo]:\n\t" + "\n\t".join(generalInfo) + "\n")
	 		f.write("[Questionnaire]: scoring: %.2f\n" % qn.scoring())
	 		f.write("\n".join(["Q%d: %d" % (i,ans) for (i, ans) in enumerate(qn.ansList)]))

	@classmethod
	def queryAll(cls):
	 	cls.loadData();
		for i in range(len(Factory.fBase)):
			Stats.queryFactory(i,"../output/Queries/Factories/Factory#%d.txt" % i);
		Stats.queryFactory(-1,"../output/Queries/Factories/AllFactories.txt");

		for i in range(len(Questionnaire.qBase)):
			Stats.queryQuestion(i, "../output/Queries/Questions/Q#%d.txt" % i);
		for i in range(len(Worker.wBase)):
			Stats.queryWorker(i, "../output/Queries/Workers/Worker#%d.txt" % i);

	@classmethod
	def invalidEvaluation(cls):
		from sklearn import mixture
		from sklearn.cluster import KMeans
		import math
		cls.loadData();

		def get_score(evaluator_):
			all_score_ = [];
			valid_score_ = [];
			invalid_score_ = [];
			evs_ = []
			for wid in Factory.getAllWorkersId():
				wkr = Worker.getById(wid);
				ev = evaluator_.evaluate(wkr);
				evs_.append(ev);
				if wkr.isInvalid:
					invalid_score_.append(ev);
				else:
					valid_score_.append(ev);
			all_score_ = invalid_score_ + valid_score_;
			return all_score_,invalid_score_,valid_score_, evs_;

		# InvalidEvaluator1:
		curMax,curTn = (-sys.maxint, -1);
		for tn in range (10,90):
			# evaluator = InvalidEvaluator1(topN=50, threshold=0.0, binary=False);
			evaluator = InvalidEvaluator1(topN=tn, threshold=0.0);
			all_score,invalid_score,valid_score,evs = get_score(evaluator);
			model = mixture.GaussianMixture(n_components = 2,covariance_type = 'full',n_init = 3);
			model.fit([[item] for item in all_score]);
			prob_prod = 0.0
			for ev in evs:
				prob_prod += math.log(diff2(model.predict_proba(ev)[0]))
			if prob_prod > curMax:
				curMax = prob_prod
				curTn = tn;


		all_score,invalid_score,valid_score,evs = get_score(evaluator.set(tn=curTn));
		print "ALL_SCORE aver. %.2f,\nVALID_SCORE aver. %.2f\nINVALID_SCORE aver. %.2f" % \
			(getListAver(all_score), getListAver(valid_score), getListAver(invalid_score))
		print "valid_range:(%.2f, %.2f)\tinvalid_range:(%.2f,%.2f)" % (min(valid_score), max(valid_score),\
				min(invalid_score),max(invalid_score));


		#GMM
		model = mixture.GaussianMixture(n_components = 2,covariance_type = 'full',n_init = 10);

		model.fit([[item] for item in all_score]);
		miscnt = 0
		ans = [0,0];
		prob_prod = 0.0
		for wid in Factory.getAllWorkersId():
			wkr = Worker.getById(wid);
			ev = evaluator.evaluate(wkr)
			p = model.predict(ev)[0]
			prob_prod += math.log(diff2(model.predict_proba(ev)[0]))
			if wkr.isInvalid != p:
				miscnt += 1;
			ans[p] += 1;
		print "prob_prod: ",prob_prod
		print "Using GMM with (topN=%d) to predict: miss %d comparing to groud truth" % (curTn,min(miscnt, len(all_score)-miscnt));

		sigma0 = model.covariances_[0,0]**0.5;
		sigma1 = model.covariances_[1,0]**0.5;
		mu0 = model.means_[0];
		mu1 = model.means_[1];

		pyplot.hist(all_score,100, normed=True);
		pyplot.xlabel('Invalid-Value')
		pyplot.ylabel('Freq')
		pyplot.title('Invalid value distribution with N(%.2f,%.2f), N(%.2f,%.2f)' % (mu0, sigma0, mu1, sigma1))
		bins = [i for i in range(int(min(valid_score)), int(max(invalid_score)), 1)]
		pyplot.plot(bins, model.weights_[0]/(np.sqrt(2*np.pi)*sigma0)*np.exp(-(bins-mu0)**2/(2*sigma0**2)), lw=2, c='r')
		pyplot.plot(bins, model.weights_[1]/(np.sqrt(2*np.pi)*sigma1)*np.exp(-(bins-mu1)**2/(2*sigma1**2)), lw=2, c='y')
		pyplot.show();


class InvalidEvaluator1:
	import sys
	def __init__(self, topN=sys.maxint, threshold=0.5, binary=True):
		self.relationList = []
		self.topN = topN;
		self.thd = threshold;
		self.bin = binary;
		for (a, rel_a) in Questionnaire.relationMat.items():
			for (b, val) in rel_a:
				if a > b:
					continue;
				else:
					self.relationList.append((-abs(val), val, a,b));
		self.relationList.sort();
	def set(self, tn=None, thd=None, binary=None):
		if tn != None:
			self.topN = tn;
		if thd != None:
			self.threshold = thd;
		if binary!=None:
			self.bin = binary;
		return self;

	def evaluate(self, wkr):      # the less, the better
		qn = wkr.qn.ansList;
		ret = 0;
		for (minus_abs_val, val, a,b) in self.relationList[:self.topN]:
			if (-minus_abs_val < self.thd):
				break;
			ret += (1 if self.bin else val) * abs(qn[a]-qn[b]);
		return ret;

class InvalidEvaluator2:
	import sys
	def __init__(self, topN=sys.maxint, threshold=0.5):
		self.relationList = Stats.getTopNCor(np.array([Worker.getById(wid).qn.ansList for wid in Factory.getAllWorkersId()]),0,topN,None)
		self.topN = topN;
		self.thd = threshold;


	def evaluate(self, wkr):      # the less, the better
		qn = wkr.qn.ansList;
		ret = 0;
		for ((a,b),val) in self.relationList[:self.topN]:
			if (abs(val) < self.thd):
				break;
			ret += val * abs(qn[a]-qn[b]);
		return ret;

	def set(self, tn=None, thd=None):
		if tn != None:
			self.topN = tn;
		if thd != None:
			self.threshold = thd;

		return self;




if __name__ == '__main__':
	Stats.loadData();
	Stats.invalidEvaluation();
