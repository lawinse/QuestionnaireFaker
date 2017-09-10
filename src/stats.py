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
			print ">>>>> Fac #%d with aver score: %0.2f" % (fac.id,sc*1.0/fac.workerCnt);

