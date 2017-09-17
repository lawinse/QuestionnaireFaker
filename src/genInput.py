# -*- coding:utf8 -*-

from base import *
import os


def main():
	with open("../input/factories.txt", "w+") as f:
		facCnt = random.randint(6,10);
		f.write('# This text provides raw data of factories.\n'+
			'# All the lines blank or started with "#" will be ignored.\n\n'+
			'# Firstly, one line with the number of factories\n')
		f.write(str(facCnt)+ "\n")
		f.write('\n# Then {#factories} lines indicate the detail by '+
			'"factory_id workers_number score (~[0,1]) invalidRatio(~[0,1)) all_workers_cnt good_list bad_list", factory_id must be continous.\n')

		for i in range(facCnt):
			wCnt = random.randint(50,200);
			fS = rangeGauss(0.4,1.0)
			invR = rangeGauss(0,0.15)
			f.write("%d %d %.2f %.4f 1000 [] []" % (i, wCnt, fS, invR)+"\n")

	with open("../input/questions.txt", "w+") as f:
		qusCnt = random.randint(70,120)
		f.write('# This text provides raw data of questions.\n'+
			'# All the lines blank or started with "#" will be ignored.\n\n'+
			'# First one line with the count of questions\n')
		f.write(str(qusCnt) + "\n")

		qusAttri = [random.choice([-1,-1,0,1,1]) for i in range (qusCnt)]
		f.write('# Followed by {#questions} lines with syntax "question_id question_attribute '+
			'(vary from {-1,0,1})" per line, question_id must be continous.\n')
		f.writelines([("%d %d\n" %(i,qusAttri[i])) for i in range(qusCnt)])

		pairCnt = random.randint(20,80);
		f.write('# Then goes one line indicates the count of pair relationship\n')
		f.write(str(pairCnt) + '\n')
		st = set()

		f.write('# Last {#pair relationship} lines with syntax '+
			'"question_id1 question_id2 degree_of_relationship ~ [-1,1]"\n')
		for i in range(pairCnt):
			a = 0;
			b = 0;
			while True:
				while True:
					a = random.randint(0,qusCnt-1);
					if (qusAttri[a] != 0):
						break;
				while True:
					b = random.randint(0,qusCnt-1);
					if (qusAttri[b] != 0 and a != b):
						break;
				if a > b:
					a,b = b,a;
				if (a,b) not in st:
					break;
			st.add((a,b))
			relation = qusAttri[a] * qusAttri[b] * rangeGauss(0.0001,1);
			f.write("%d %d %.3f\n" % (a,b,relation));



if __name__ == '__main__':
	main()