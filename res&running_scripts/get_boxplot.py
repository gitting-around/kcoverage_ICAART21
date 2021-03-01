#!/usr/bin/env python
from matplotlib2tikz import save as tikz_save
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

import seaborn as sns

#data = pd.read_csv('_10_1_300_5_static.csv')
#data.barplot()
#plt.xticks((1, 2, 3, 4 ), ('k=1 - ave time', 'k=1 - min time', 'k=5 - ave time', 'k=5 - min time', ))
#plt.show()

k = int(input("Define k: "))
print(k)

pp = int(input("Define nr of distinct configurations: "))

reps = int(input("Define nr of repetitions: "))

what2run = int(input("0 for all, 1 for static, 2 for dynamic: "))

models = ['000', '010', '020', '030', '040', '310', '320', '330', '340']
models_notation = ['W', 'BC-NN', 'BC-AV', 'BC-GR', 'BC-RE', 'RA-NN', 'RA-AV', 'RA-GR', 'RA-RE']

ticks = []
for i in range(pp):
    ticks.append('C'+str(i))

if what2run == 0 or what2run == 1:
	fig, axes = plt.subplots(1, 2, sharey=True)

	data_1at = []
	data_1mt = []
	data_kat = []
	data_kmt = []
	kat = str(k) + 'AT'
	kmt = str(k) + 'MT'

	for rr in models:
		j=1
		for i in range(pp):
			data = pd.read_csv('_10_' + str(j) +'_300_'+str(k)+'_static_'+rr+'.csv', names=['1AT', '1MT', kat, kmt])
			data_1at += [x for x in data['1AT']]
			data_1mt += [x for x in data['1MT']]
			data_kat += [x for x in data[kat]]
			data_kmt += [x for x in data[kmt]]
			j += 3

	data_1at = np.array(data_1at)
	data_1mt = np.array(data_1mt)
	data_kat = np.array(data_kat)
	data_kmt = np.array(data_kmt)

	sns.set(style="whitegrid")
	at1 = {'model': [ x  for z in range(reps) for x in models_notation for y in range(len(ticks))],
		'configuration': [y for z in range(reps) for x in models for y in ticks ],
		'at': data_1at
			}

	df = pd.DataFrame(at1, columns = ['model', 'configuration', 'at'])

	sns.barplot(x="configuration", y="at", hue="model", data=df, palette="muted", ci='sd', ax=axes[0]).set_title("average time to coverage k=1")
	axes[0].legend(loc='upper left',prop={'size': 7}).remove()
	atk = {'model': [ x  for z in range(reps) for x in models_notation for y in range(len(ticks))],
		'configuration': [y for z in range(reps) for x in models for y in ticks ],
		'at': data_kat
			}

	df = pd.DataFrame(atk, columns = ['model', 'configuration', 'at'])

	sns.barplot(x="configuration", y="at", hue="model", data=df, palette="muted", ci='sd', ax=axes[1]).set_title("average time to coverage k=3")
	#fname = "ave_exectime_"+str(task_instance)
	plt.ylim(0,310)
	axes[1].legend(loc='upper left',prop={'size': 7}, bbox_to_anchor=(1, 1))

	'''plt.savefig(fname, dpi=300, facecolor='w', edgecolor='w',
			orientation='portrait', papertype=None, format=None,
			transparent=False, bbox_inches=None, pad_inches=0.1,
			frameon=None, metadata=None)'''

	fig, axes = plt.subplots(1, 2, sharey=True)

	mt1 = {'model': [ x  for z in range(reps) for x in models_notation for y in range(len(ticks))],
		'configuration': [y for z in range(reps) for x in models for y in ticks ],
		'mt': data_1mt
			}
	print(mt1)
	df = pd.DataFrame(mt1, columns = ['model', 'configuration', 'mt'])

	sns.barplot(x="configuration", y="mt", hue="model", data=df, palette="muted", ci='sd', ax=axes[0]).set_title("minimum time to coverage k=1")
	axes[0].legend(loc='upper left',prop={'size': 7}).remove()

	mtk = {'model': [ x  for z in range(reps) for x in models_notation for y in range(len(ticks))],
		'configuration': [y for z in range(reps) for x in models for y in ticks ],
		'mt': data_kmt
			}

	df = pd.DataFrame(mtk, columns = ['model', 'configuration', 'mt'])

	sns.barplot(x="configuration", y="mt", hue="model", data=df, palette="muted", ci='sd', ax=axes[1]).set_title("minimum time to coverage k=3")
	#fname = "ave_exectime_"+str(task_instance)
	plt.ylim(0,310)
	axes[1].legend(loc='upper left',prop={'size': 7})
	plt.legend(loc='upper left',prop={'size': 7}, bbox_to_anchor=(1, 1))
	'''plt.savefig(fname, dpi=300, facecolor='w', edgecolor='w',
			orientation='portrait', papertype=None, format=None,
			transparent=False, bbox_inches=None, pad_inches=0.1,
			frameon=None, metadata=None)'''


	tikz_save(rr+'_staticVP_mt'+str(k)+'.tex')
	plt.show()
	############################# Combined Coverage #################################
	fig, axes = plt.subplots(1, 2, sharey=True)

	data_1at = []
	data_1mt = []
	data_kat = []
	data_kmt = []
	kat = str(k) + 'AT'
	kmt = str(k) + 'MT'

	for rr in models:
		j=1
		for i in range(pp):
			data = pd.read_csv('_10_' + str(j) +'_300_'+str(k)+'_combined_static_'+rr+'.csv', names=['1AT', '1MT', kat, kmt])
			data_1at += [x for x in data['1AT']]
			data_1mt += [x for x in data['1MT']]
			data_kat += [x for x in data[kat]]
			data_kmt += [x for x in data[kmt]]
			j += 3

	data_1at = np.array(data_1at)
	data_1mt = np.array(data_1mt)
	data_kat = np.array(data_kat)
	data_kmt = np.array(data_kmt)

	sns.set(style="whitegrid")
	at1 = {'model': [ x  for z in range(reps) for x in models_notation for y in range(len(ticks))],
		'configuration': [y for z in range(reps) for x in models for y in ticks ],
		'at': data_1at
			}

	df = pd.DataFrame(at1, columns = ['model', 'configuration', 'at'])

	sns.barplot(x="configuration", y="at", hue="model", data=df, palette="muted", ci='sd', ax=axes[0]).set_title("combo ave time to coverage k=1")
	axes[0].legend(loc='upper left',prop={'size': 7}).remove()
	atk = {'model': [ x  for z in range(reps) for x in models_notation for y in range(len(ticks))],
		'configuration': [y for z in range(reps) for x in models for y in ticks ],
		'at': data_kat
			}

	df = pd.DataFrame(atk, columns = ['model', 'configuration', 'at'])

	sns.barplot(x="configuration", y="at", hue="model", data=df, palette="muted", ci='sd', ax=axes[1]).set_title("combo ave time to coverage k=3")
	#fname = "ave_exectime_"+str(task_instance)
	plt.ylim(0,310)
	axes[1].legend(loc='upper left',prop={'size': 7}, bbox_to_anchor=(1, 1))

	'''plt.savefig(fname, dpi=300, facecolor='w', edgecolor='w',
			orientation='portrait', papertype=None, format=None,
			transparent=False, bbox_inches=None, pad_inches=0.1,
			frameon=None, metadata=None)'''

	fig, axes = plt.subplots(1, 2, sharey=True)

	mt1 = {'model': [ x  for z in range(reps) for x in models_notation for y in range(len(ticks))],
		'configuration': [y for z in range(reps) for x in models for y in ticks ],
		'mt': data_1mt
			}
	print(mt1)
	df = pd.DataFrame(mt1, columns = ['model', 'configuration', 'mt'])

	sns.barplot(x="configuration", y="mt", hue="model", data=df, palette="muted", ci='sd', ax=axes[0]).set_title("combo min time to coverage k=1")
	axes[0].legend(loc='upper left',prop={'size': 7}).remove()

	mtk = {'model': [ x  for z in range(reps) for x in models_notation for y in range(len(ticks))],
		'configuration': [y for z in range(reps) for x in models for y in ticks ],
		'mt': data_kmt
			}

	df = pd.DataFrame(mtk, columns = ['model', 'configuration', 'mt'])

	sns.barplot(x="configuration", y="mt", hue="model", data=df, palette="muted", ci='sd', ax=axes[1]).set_title("combo min time to coverage k=3")
	#fname = "ave_exectime_"+str(task_instance)
	plt.ylim(0,310)
	axes[1].legend(loc='upper left',prop={'size': 7}, bbox_to_anchor=(1, 1))
	plt.legend(loc='upper left',prop={'size': 7})
	'''plt.savefig(fname, dpi=300, facecolor='w', edgecolor='w',
			orientation='portrait', papertype=None, format=None,
			transparent=False, bbox_inches=None, pad_inches=0.1,
			frameon=None, metadata=None)'''


	tikz_save(rr+'_staticVP_mt'+str(k)+'.tex')
	plt.show()



###############################################################################
######################################DYNAMIC##################################
elif what2run == 0 or what2run == 2:
	fig, axes = plt.subplots(1, 2)

	data_at = []
	data_aa = []
	kaa = str(k) + 'AA'
	kat = str(k) + 'AT'

	for rr in models:
		j=1
		for i in range(pp):
			data = pd.read_csv('_10_' + str(j) +'_300_'+str(k)+'_dynamic_'+rr+'.csv', names=[kat, kaa])
			data_at += [x for x in data[kat]]
			data_aa += [x for x in data[kaa]]
			j += 3

	data_at = np.array(data_at)
	data_aa = np.array(data_aa)

	at = {'model': [ x  for z in range(reps) for x in models_notation for y in range(len(ticks))],
		'configuration': [y for z in range(reps) for x in models for y in ticks ],
		'at': data_at
			}

	df = pd.DataFrame(at, columns = ['model', 'configuration', 'at'])

	sns.barplot(x="configuration", y="at", hue="model", data=df, palette="muted", ci='sd', ax=axes[0]).set_title('Average Coverage Time k='+str(k))
	
	#fname = "ave_exectime_"+str(task_instance)
	plt.ylim(0,310)
	axes[0].legend(loc='upper left',prop={'size': 7}).remove()
	axes[0].grid()
	axes[0].set_ylabel("Time")

	aa = {'model': [ x  for z in range(reps) for x in models_notation for y in range(len(ticks))],
		'configuration': [y for z in range(reps) for x in models for y in ticks ],
		'aa': data_aa
			}

	df = pd.DataFrame(aa, columns = ['model', 'configuration', 'aa'])

	sns.barplot(x="configuration", y="aa", hue="model", data=df, palette="muted", ci='sd', ax=axes[1]).set_title('Average Agents per Target k='+str(k))
	#fname = "ave_exectime_"+str(task_instance)
	plt.ylim(0,310)
	axes[1].legend(loc='upper left',prop={'size': 7}, bbox_to_anchor=(1, 1))
	axes[1].grid()
	axes[1].set_ylim(1,6)
	axes[1].set_ylabel("Agents")

	tikz_save(rr+'_dynamic'+str(k)+'VP.tex')
	plt.show()

	###################### Pasive coverage ###############################################
	fig, axes = plt.subplots(1, 2)

	data_at = []
	data_aa = []
	kaa = str(k) + 'AA'

	for rr in models:
		j=1
		for i in range(pp):
			data = pd.read_csv('_10_' + str(j) +'_300_'+str(k)+'_combined_dynamic_'+rr+'.csv', names=[kat, kaa])
			data_at += [x for x in data[kat]]
			data_aa += [x for x in data[kaa]]
			j += 3

	data_at = np.array(data_at)
	data_aa = np.array(data_aa)

	at = {'model': [ x  for z in range(reps) for x in models_notation for y in range(len(ticks))],
		'configuration': [y for z in range(reps) for x in models for y in ticks ],
		'at': data_at
			}

	df = pd.DataFrame(at, columns = ['model', 'configuration', 'at'])

	sns.barplot(x="configuration", y="at", hue="model", data=df, palette="muted", ci='sd', ax=axes[0]).set_title('Combo Ave-Cov Time k='+str(k))
	#fname = "ave_exectime_"+str(task_instance)
	plt.ylim(0,310)
	axes[0].legend(loc='upper left',prop={'size': 7}).remove()
	axes[0].grid()
	axes[0].set_ylabel("Time")

	aa = {'model': [ x  for z in range(reps) for x in models_notation for y in range(len(ticks))],
		'configuration': [y for z in range(reps) for x in models for y in ticks ],
		'aa': data_aa
			}

	df = pd.DataFrame(aa, columns = ['model', 'configuration', 'aa'])

	sns.barplot(x="configuration", y="aa", hue="model", data=df, palette="muted", ci='sd', ax=axes[1]).set_title('Combo Ave-Age per Target k='+str(k))
	#fname = "ave_exectime_"+str(task_instance)
	plt.ylim(0,310)
	axes[1].legend(loc='upper left',prop={'size': 7}, bbox_to_anchor=(1, 1))
	axes[1].grid()
	axes[1].set_ylim(1,6)
	axes[1].set_ylabel("Agents")

	tikz_save(rr+'_dynamic'+str(k)+'VP.tex')
	plt.show()