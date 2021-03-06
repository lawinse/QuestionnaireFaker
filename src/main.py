# -*- coding:utf8 -*-
from factory import *
from sklearn.externals import joblib
from stats import Stats

def _readline(fs):
	s = ""
	while True:
		s = fs.readline().strip();
		if (len(s) != 0 and s[0] != '#'):
			break;
	return s;

def readInData():
	# first read questions.txt

	# SYNTAX:
	# cnt
	# id score (repeated)
	# pair Cnt
	# id1 id2 relation 
	qCnt = 0;
	pairCnt = 0;
	with open("../input/questions.txt") as f1:
		Questionnaire.qusCnt = qCnt = eval(_readline(f1));
		for i in range(qCnt):
			li = _readline(f1).split();
			Questionnaire.addQ(Question(eval(li[0]),eval(li[1])));
		pairCnt = eval(_readline(f1));
		for i in range(pairCnt):
			li = _readline(f1).split();
			Questionnaire.addRelation(eval(li[0]),eval(li[1]),eval(li[2]));

	if (not Questionnaire.validateRelation()):
		print "failed at validate Relation ..."
		exit(0)

	# then read factories.txt

	# SYNTAX:
	# fac_cnt
	# id worker_cnt scoring invRatio (repeated)

	facCnt = 0;
	wCnt = 0;

	with open("../input/factories.txt") as f1:
		facCnt = eval(_readline(f1))
		for i in range(facCnt):
			li = _readline(f1).split();
			f = Factory(eval(li[0]), eval(li[1]), eval(li[2]),eval(li[3]), eval(li[4]), eval(li[5]), eval(li[6]));
			f.workersId = [wid for wid in range(wCnt, wCnt+eval(li[1]))] 
			Factory.addFactory(f)
			for j in range(wCnt, wCnt+eval(li[1])):
				Worker.addWorker(Worker(j,eval(li[0])));
			wCnt += eval(li[1]);


def generate():
	for fac in Factory.fBase:
		print ">>>>> Processing Fac #%d with %d workers (set %.2f%% invalid) " % (fac.id, fac.workerCnt, fac.invRatio*100);
		sc = 0;
		for wid in fac.workersId:
			Worker.getById(wid).conduct();

def persistData():
	Stats.persistData();

def loadData():
	return Stats.loadData();

def analysis():
	Stats.markInvalid();

	Stats.genCsv();
	Stats.scoring();
	Stats.getCor()
	Stats.getDistribution()
	Stats.queryAll();

def main():
	if (not loadData()):
		readInData();
		generate();
		persistData();
	analysis();

if __name__ == '__main__':
	main()