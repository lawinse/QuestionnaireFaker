# -*- coding:utf8 -*-

from factory import *
import os
from sklearn.externals import joblib

class Stats:
	@classmethod
	def loadData(cls):
		if not os.path.exists("../data/store.bin"):
			return False
		(Factory.fBase, Worker.wBase,\
			(Questionnaire.qBase, Questionnaire.relatedPairs,\
				Questionnaire.relationMat,Questionnaire.qusCnt,Questionnaire.minMaxSc),(Question.MAX_OP, Question.MIN_OP))\
		= joblib.load("../data/store.bin")
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

	@classmethod
	def getCor(cls):
		import numpy as np

		TOP_N = 20;

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

		facSeperate = [[] for i in range(len(Factory.fBase))]
		facTtl = []

		with open("../output/correlation.txt","w+") as f:
			for fac in Factory.fBase:
				for wid in fac.workersId:
					if (Worker.getById(wid).isInvalid):
						continue;
					facSeperate[fac.id].append(Worker.getById(wid).qn.ansList)
					facTtl.append(Worker.getById(wid).qn.ansList)
				facSeperate[fac.id] = getTopNCor(np.array(facSeperate[fac.id]),0,TOP_N, fac.id)
				printAndWriteFileLn(f,">>>>> Fac #%d with correlation ranking:" % (fac.id));
				printAndWriteFileLn(f,"\n".join([("(%d,%d) --> %.3f" % (item[0][0], item[0][1], item[1])) for item in facSeperate[fac.id]]) + "\n");

			facTtl = getTopNCor(np.array(facTtl),0,TOP_N,None)
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
			f.write("[workerCnt]:%d\n[allWorkerCnt]:%d\n[invalidCnt]:%d\n[questionnaireScoring]%d\n" \
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
	 	Stats.loadData();
		for i in range(len(Factory.fBase)):
			Stats.queryFactory(i,"../output/Queries/Factories/Factory#%d.txt" % i);
		Stats.queryFactory(-1,"../output/Queries/Factories/AllFactories.txt");

		for i in range(len(Questionnaire.qBase)):
			Stats.queryQuestion(i, "../output/Queries/Questions/Q#%d.txt" % i);
		for i in range(len(Worker.wBase)):
			Stats.queryWorker(i, "../output/Queries/Workers/Worker#%d.txt" % i);
if __name__ == '__main__':
	Stats.queryAll();
