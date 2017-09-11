# -*- coding:utf8 -*-

from factory import *
import os

class Stats:
	@classmethod
	def genCsv(cls):
		for root, dirs, files in os.walk("../output/"):
			for name in files:
				os.remove(os.path.join(root, name))
		with open("../output/Factory_summary.csv", "w+") as fttl:
			fttl.write("worker_id,"+",".join(["Q"+str(i) for i in range(Questionnaire.qusCnt)])+"\n")
			for i in range(len(Factory.fBase)):
				fac = Factory.fBase[i]
				with open("../output/Factory_%d_result.csv" % (fac.id), "w+")as f:
					f.write("worker_id,"+",".join(["Q"+str(i) for i in range(Questionnaire.qusCnt)])+"\n")
					for wid in fac.workersId:
						qn = Worker.getById(wid).qn;
						f.write(str(wid)+","+",".join([str(item) for item in qn.ansList])+"\n")
						fttl.write(str(wid)+","+",".join([str(item) for item in qn.ansList])+"\n")

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

		def getTopNCor(arr, rowvar, n):
			from Queue import PriorityQueue
			cormat = np.corrcoef(arr, rowvar=rowvar);
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
			ansli = ansli[::-1]
			ansli = [(item[1], cormat[item[1]]) for item in ansli]
			return ansli

		facSeperate = [[] for i in range(len(Factory.fBase))]
		facTtl = []

		for fac in Factory.fBase:
			for wid in fac.workersId:
				facSeperate[fac.id].append(Worker.getById(wid).qn.ansList)
				facTtl.append(Worker.getById(wid).qn.ansList)
			facSeperate[fac.id] = getTopNCor(np.array(facSeperate[fac.id]),0,TOP_N)
			print ">>>>> Fac #%d with correlation ranking:" % (fac.id)
			print "\n".join([str(item) for item in facSeperate[fac.id]]) + "\n"

		facTtl = getTopNCor(np.array(facTtl),0,TOP_N)
		print ">>>>> All fac with correlation ranking:"
		print "\n".join([str(item) for item in facTtl])







