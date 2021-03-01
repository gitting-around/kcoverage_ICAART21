#!/usr/bin/env python
from matplotlib2tikz import save as tikz_save
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
#from pandas.plotting import table
import seaborn as sns
from scipy.stats import friedmanchisquare
import sys
#sns.set(font_scale=1.5, rc={'text.usetex' : True})
from matplotlib import rc
rc('text', usetex=True)
mpl.rcParams['text.latex.preamble'] = [r'\usepackage{amsmath}']
#np.seterr(all='raise')
#data = pd.read_csv('_10_1_300_5_static.csv')
#data.barplot()
#plt.xticks((1, 2, 3, 4 ), ('k=1 - ave time', 'k=1 - min time', 'k=5 - ave time', 'k=5 - min time', ))
#plt.show()

""" k = int(input("Define k: "))
print(k)

pp = int(input("Define nr of distinct scenarios: "))

reps = int(input("Define nr of repetitions: "))

what2run = int(input("0 for all, 1 for static, 2 for dynamic: "))
 """
if len(sys.argv) < 6:
	print("Usage: python3 ./get_boxplot.py coverage distinct_scenarios repetitions what2run (0 all, 1 static, 2 dynamic) amIequal(0,1)")
	sys.exit()
else:
	k = int(sys.argv[1])
	pp = int(sys.argv[2])
	reps = int(sys.argv[3])
	what2run = int(sys.argv[4])
	amIequal = int(sys.argv[5])

#methods =          ['000', '001',    '010',   '020',   '030',   '040',   '310',   '320',   '330',   '340']
#methods_notation = ['W', 'RandFoll', 'BC-NN', 'BC-AV', 'BC-GR', 'BC-RE', 'RA-NN', 'RA-AV', 'RA-GR', 'RA-RE']

methods =          ['000', '010', '020',   '030',   '040',   '310',   '320',   '330',   '340']
methods_notation = ['W', 'BC-NN', 'BC-AV', 'BC-GR', 'BC-RE', 'RA-NN', 'RA-AV', 'RA-GR', 'RA-RE']

#methods = ['000', '010', '020', '040', '310', '320', '340']
#methods_notation = ['W', 'BC-NN', 'BC-AV', 'BC-RE', 'RA-NN', 'RA-AV', 'RA-RE']

ticks = []
markers = ['^', '+', 'o', '<', '>', 'x', '*']
for i in range(pp):
    ticks.append('S'+str(i))
    #markers.append(i)

if what2run == 0 or what2run == 1:
	
	data_1at = []
	data_1mt = []
	data_kat = []
	data_kmt = []
	data_1at_fchs = []
	data_1mt_fchs = []
	data_kat_fchs = []
	data_kmt_fchs = []
	kat = str(k) + 'AT'
	kmt = str(k) + 'MT'

	for rr in methods:
		j=1
		data_1at_fchs.append([])
		data_kat_fchs.append([])
		data_1mt_fchs.append([])
		data_kmt_fchs.append([])
		for i in range(pp):
			data = pd.read_csv('_10_' + str(j) +'_300_'+str(k)+'_static_'+rr+'.csv', names=['1AT', '1MT', kat, kmt])
			data_1at += [x for x in data['1AT']]
			data_1mt += [x for x in data['1MT']]
			data_kat += [x for x in data[kat]]
			data_kmt += [x for x in data[kmt]]

			data_1mt_fchs[-1] += [x for x in data['1MT']]
			data_1at_fchs[-1] += [x for x in data['1AT']]

			data_kat_fchs[-1] += [x for x in data[kat]]
			data_kmt_fchs[-1] += [x for x in data[kmt]]
			j += 3

	data_1at = np.array(data_1at)
	data_1at_fchs = np.transpose(np.array(data_1at_fchs))
	pd.DataFrame(data_1at_fchs).to_csv("static_1at_"+str(k)+".csv")

	data_kat = np.array(data_kat)
	data_kat_fchs = np.transpose(np.array(data_kat_fchs))
	pd.DataFrame(data_kat_fchs).to_csv("static_kat_"+str(k)+".csv")

	data_1mt = np.array(data_1mt)
	data_1mt_fchs = np.transpose(np.array(data_1mt_fchs))
	pd.DataFrame(data_1mt_fchs).to_csv("static_1mt_"+str(k)+".csv")
	
	data_kmt = np.array(data_kmt)
	data_kmt_fchs = np.transpose(np.array(data_kmt_fchs))
	pd.DataFrame(data_kmt_fchs).to_csv("static_kmt_"+str(k)+".csv")

	print(np.shape(data_1at_fchs))
	'''
	pvalue_table = [[],[],[],[]]
	print("FRIEDMAN test for 1at")
	data = []
	for y in range(pp):
		data_1at_fchs = np.array(data_1at_fchs)
		tyty = [data_1at_fchs[pp*x+y] for x in range(len(methods))]
		res = friedmanchisquare(tyty[0], tyty[1], tyty[2], tyty[3], tyty[4], tyty[5], tyty[6], tyty[7], tyty[8])
		print("Number of targets: " + str(y+1))
		print("chis: " + str(res.statistic))
		print("pvalue: " + str(res.pvalue) + "\n")
		data.append(res.pvalue)
	pvalue_table[0] += data
	data = []
	'''
	#df = pd.DataFrame(pvalue_table, index=["ave_time k=1","ave_time k="+str(k),"min_time k=1","min_time k="+str(k)], columns=ticks)
	#df.to_csv("static_pvalues_"+str(k)+".csv")

	#res = friedmanchisquare(tyty[0], tyty[1], tyty[2])
	#print(res.statistic)
	data_1mt = np.array(data_1mt)
	data_kat = np.array(data_kat)
	data_kmt = np.array(data_kmt)
	
	'''
	fig, axes = plt.subplots(1, 2, sharey=True)
	sns.set(style="whitegrid")

	at1 = {'method': [ x for x in methods_notation for z in range(reps*len(ticks))],
		'scenario': [y for x in methods for y in ticks for z in range(reps)],
		'at': data_1at
			}
	
	print(at1)
	df = pd.DataFrame(at1, columns = ['method', 'scenario', 'at'])

	#sns.barplot(x="scenario", y="at", hue="method", data=df, palette="muted", ci='sd', ax=axes[0]).set_title("average time to coverage k=1")
	sns.barplot(x='scenario', y='at', hue='method', data=df, palette='muted', ci=0.0, ax=axes[0]).set_title("average time to coverage k=1")
	axes[0].legend(loc='upper left',prop={'size': 7}).remove()
	atk = {'method': [ x for x in methods_notation for z in range(reps*len(ticks))],
		'scenario': [y for x in methods for y in ticks for z in range(reps)],
		'at': data_kat
			}

	df = pd.DataFrame(atk, columns = ['method', 'scenario', 'at'])

	sns.barplot(x="scenario", y="at", hue="method", data=df, palette="muted", ci=0.0, ax=axes[1]).set_title("average time to coverage k="+str(k))
	#fname = "ave_exectime_"+str(task_instance)
	plt.ylim(0,310)
	axes[1].legend(loc='upper left',prop={'size': 7}, bbox_to_anchor=(1, 1))

	fname = "static_ave2cov_"+str(k)
	plt.tight_layout()
	plt.savefig(fname, dpi=300, facecolor='w', edgecolor='w',
			orientation='portrait', papertype=None, format=None,
			transparent=False, bbox_inches=None, pad_inches=0.1,
			frameon=None, metadata=None)

	fig, axes = plt.subplots(1, 2, sharey=True)

	mt1 = {'method': [ x for x in methods_notation for z in range(reps*len(ticks))],
		'scenario': [y for x in methods for y in ticks for z in range(reps)],
		'mt': data_1mt
			}
	print(mt1)
	df = pd.DataFrame(mt1, columns = ['method', 'scenario', 'mt'])

	sns.barplot(x="scenario", y="mt", hue="method", data=df, palette="muted", ci=0.0, ax=axes[0]).set_title("minimum time to coverage k=1")
	axes[0].legend(loc='upper left',prop={'size': 7}).remove()

	mtk = {'method': [ x for x in methods_notation for z in range(reps*len(ticks))],
		'scenario': [y for x in methods for y in ticks for z in range(reps)],
		'mt': data_kmt
			}

	df = pd.DataFrame(mtk, columns = ['method', 'scenario', 'mt'])

	sns.barplot(x="scenario", y="mt", hue="method", data=df, palette="muted", ci=0.0, ax=axes[1]).set_title("minimum time to coverage k="+str(k))
	#fname = "ave_exectime_"+str(task_instance)
	plt.ylim(0,310)
	axes[1].legend(loc='upper left',prop={'size': 7})
	fname = "mintime2cov_"+str(k)
	plt.legend(loc='upper left',prop={'size': 7}, bbox_to_anchor=(1, 1))
	plt.tight_layout()
	plt.savefig(fname, dpi=300, facecolor='w', edgecolor='w',
			orientation='portrait', papertype=None, format=None,
			transparent=False, bbox_inches=None, pad_inches=0.1,
			frameon=None, metadata=None)
	'''

	fig, axes = plt.subplots(1, 1)
	combined_data = {'method': [ x for x in methods_notation for z in range(reps*len(ticks))],
		'scenario': [y for x in methods for y in ticks for z in range(reps)],
		'kmt': data_kmt,
		'mt': data_1mt,
		'at': data_1at,
		'kat': data_kat
			}
	markers_data = [y for x in methods for y in markers for z in range(reps)]
	df = pd.DataFrame(combined_data, columns = ['method', 'scenario', 'kmt', 'mt', 'kat', 'at'])

	df_means = df.groupby(['method', 'scenario']).mean().reset_index()
	df_std = df.groupby(['method', 'scenario']).std().reset_index()
	print(df_means)
	print(df_std)

	#sns.scatterplot(x='kmt', y='kat', hue='method', style='scenario', data=df_means, ax=axes).set_title('Ave2Cov-Min2Cov k>='+str(k))
	sns.scatterplot(x='kmt', y='kat', hue='method', style='scenario', data=df_means, ax=axes)
	axes.set_xlabel(r'$t^{(\kappa)}_{\text{min}}$')
	axes.set_ylabel(r'$t^{(\kappa)}_{\text{avg}}$')
	axes.grid()
	axes.set_xlim(left=0)
	axes.set_ylim(bottom=0)
	#axes.set_xlim(0,310)
	#axes.set_ylim(0,300)
	#Plot the pareto frontier for each scenario - we're looking for the minimum along both axes
	for conf in ticks:
		tt = df_means.loc[df_means['scenario']==conf]
		xypoint = [[row['kmt'], row['kat']] for i, row in tt.iterrows()]
		sort_byX = sorted(xypoint)

		pareto_frontier = [sort_byX[0]]
		for pair in sort_byX:
			if pair[1]<=pareto_frontier[-1][1]:
				pareto_frontier.append(pair)

		#plot the line
		pfx = [pair[0] for pair in pareto_frontier]
		pfy = [pair[1] for pair in pareto_frontier]
		
		p = plt.step(pfx, pfy, where='post', lw=0.5)
		
		pfx = [0] + pfx
		pfx.append(pfx[-1])
		pfy = [pfy[0]] + pfy
		pfy.append(0)

		print(conf)
		print("SPARTA: "+str(pfx))
		print("SPARTA: "+str(pfy))
		plt.plot(pfx[0:2], pfy[0:2], lw=0.5, color=p[0].get_color())
		plt.plot(pfx[-2:], pfy[-2:], lw=0.5, color=p[0].get_color())

	axes.legend(loc='upper left',prop={'size': 7}, bbox_to_anchor=(1, 1))
	if amIequal==0:
		fname = "static_scatter_k_>="+str(k)
	else:
		fname = "static_scatter_k__=="+str(k)

	plt.tight_layout()
	plt.legend(loc='upper left',prop={'size': 7}, bbox_to_anchor=(1, 1))
	tikz_save(fname+'.tex')
	plt.savefig(fname, dpi=300, facecolor='w', edgecolor='w',
			orientation='portrait', papertype=None, format=None,
			transparent=False, bbox_inches=None, pad_inches=0.1,
			frameon=None, metadata=None)
	#plot error bars
	# Defining the figure, and figure size
	for cnf in range(pp):
		fig, ax = plt.subplots(figsize=(10, 6))
		X = [row['kmt'] for i, row in df_means.loc[df_means['scenario']==ticks[cnf]].iterrows()]
		labels = [row['method'] for i, row in df_means.loc[df_means['scenario']==ticks[cnf]].iterrows()]
		colors = ['red', 'green', 'blue', 'cyan', 'magenta', 'maroon', 'dodgerblue', 'goldenrod', 'darkorange']
		print(df_means.loc[df_means['scenario']==ticks[cnf]])
		print(labels)
		Y = [row['kat'] for i, row in df_means.loc[df_means['scenario']==ticks[cnf]].iterrows()]
		X_error = [row['kmt'] for i, row in df_std.loc[df_std['scenario']==ticks[cnf]].iterrows()]
		Y_error = [row['kat'] for i, row in df_std.loc[df_std['scenario']==ticks[cnf]].iterrows()]
		# Plotting the error bars
		for i in range(len(X)):
			ax.errorbar(X[i], Y[i], xerr=X_error[i], yerr=Y_error[i], fmt='o', color=colors[i],
					ecolor=colors[i], capsize=2, label=labels[i])
		ax.set_title("Average and Std for scenario "+str(cnf))
		ax.set_xlabel('Minimum Time to k>='+str(k)+' Coverage')
		ax.set_ylabel('Average Time to k>='+str(k)+' Coverage')
		ax.grid()
		ax.legend()
		if amIequal==0:
			fname = "C"+str(cnf)+"_static_scatter_k_>="+str(k)
		else:
			fname = "C"+str(cnf)+"_static_scatter_k_=="+str(k)

		plt.savefig(fname, dpi=300, facecolor='w', edgecolor='w',
			orientation='portrait', papertype=None, format=None,
			transparent=False, bbox_inches=None, pad_inches=0.1,
			frameon=None, metadata=None)
		#plt.show()

	fig, axes = plt.subplots(1, 1)
	#sns.scatterplot(x='mt', y='at', hue='method', style='scenario', data=df_means, ax=axes, ci='sd').set_title('Ave2Cov-Min2Cov k>=1')
	sns.scatterplot(x='mt', y='at', hue='method', style='scenario', data=df_means, ax=axes, ci='sd')
	axes.set_xlabel(r'$t^{(\kappa)}_{\text{min}}$')
	axes.set_ylabel(r'$t^{(\kappa)}_{\text{avg}}$')
	axes.grid()
	axes.set_xlim(left=0)
	axes.set_ylim(bottom=0)
	#axes.set_xlim(0,310)
	#axes.set_ylim(0,300)

	#Plot the pareto frontier for each scenario - we're looking for the minimum along both axes
	for conf in ticks:
		tt = df_means.loc[df_means['scenario']==conf]
		xypoint = [[row['mt'], row['at']] for i, row in tt.iterrows()]
		sort_byX = sorted(xypoint)

		pareto_frontier = [sort_byX[0]]
		for pair in sort_byX:
			if pair[1]<=pareto_frontier[-1][1]:
				pareto_frontier.append(pair)

		#plot the line
		pfx = [pair[0] for pair in pareto_frontier]
		pfy = [pair[1] for pair in pareto_frontier]
		
		p = plt.step(pfx, pfy, where='post', lw=0.5)

		pfx = [0] + pfx
		pfx.append(pfx[-1])
		pfy = [pfy[0]] + pfy
		pfy.append(0)

		print(conf)
		print("SPARTA: "+str(pfx))
		print("SPARTA: "+str(pfy))
		plt.plot(pfx[0:2], pfy[0:2], lw=0.5, color=p[0].get_color())
		plt.plot(pfx[-2:], pfy[-2:], lw=0.5, color=p[0].get_color())

	axes.legend(loc='upper left',prop={'size': 7}, bbox_to_anchor=(1, 1))
	
	if amIequal==0:
		fname = "static_scatter_1_>="+str(k)
	else:
		fname = "static_scatter_1__=="+str(k)
	
	plt.tight_layout()
	plt.legend(loc='upper left',prop={'size': 7}, bbox_to_anchor=(1, 1))
	tikz_save(fname+'.tex')
	plt.savefig(fname, dpi=300, facecolor='w', edgecolor='w',
			orientation='portrait', papertype=None, format=None,
			transparent=False, bbox_inches=None, pad_inches=0.1,
			frameon=None, metadata=None)

	#plot error bars
	# Defining the figure, and figure size
	for cnf in range(pp):
		fig, ax = plt.subplots(figsize=(10, 6))
		X = [row['mt'] for i, row in df_means.loc[df_means['scenario']==ticks[cnf]].iterrows()]
		labels = [row['method'] for i, row in df_means.loc[df_means['scenario']==ticks[cnf]].iterrows()]
		colors = ['red', 'green', 'blue', 'cyan', 'magenta', 'maroon', 'dodgerblue', 'goldenrod', 'darkorange']
		print(df_means.loc[df_means['scenario']==ticks[cnf]])
		print(labels)
		Y = [row['at'] for i, row in df_means.loc[df_means['scenario']==ticks[cnf]].iterrows()]
		X_error = [row['mt'] for i, row in df_std.loc[df_std['scenario']==ticks[cnf]].iterrows()]
		Y_error = [row['at'] for i, row in df_std.loc[df_std['scenario']==ticks[cnf]].iterrows()]
		# Plotting the error bars
		for i in range(len(X)):
			ax.errorbar(X[i], Y[i], xerr=X_error[i], yerr=Y_error[i], fmt='o', color=colors[i],
					ecolor=colors[i], capsize=2, label=labels[i])
		ax.set_title("Average and Std for scenario "+str(cnf))
		ax.set_xlabel('Minimum Time to k>=1 Coverage')
		ax.set_ylabel('Average Time to k>=1 Coverage')
		ax.grid()
		ax.legend()

		if amIequal==0:
			fname = "C"+str(cnf)+"_static_scatter_1_>="+str(k)
		else:
			fname = "C"+str(cnf)+"_static_scatter_1_=="+str(k)
		plt.savefig(fname, dpi=300, facecolor='w', edgecolor='w',
			orientation='portrait', papertype=None, format=None,
			transparent=False, bbox_inches=None, pad_inches=0.1,
			frameon=None, metadata=None)
	#plt.show()


###############################################################################
######################################DYNAMIC##################################
if what2run == 0 or what2run == 2:

	data_at = []
	data_aa = []
	data_at_fchs = []
	data_aa_fchs = []
	kaa = str(k) + 'AA'
	kat = str(k) + 'AT'

	for rr in methods:
		j=1
		data_at_fchs.append([])
		data_aa_fchs.append([])
		for i in range(pp):
			data = pd.read_csv('_10_' + str(j) +'_300_'+str(k)+'_dynamic_'+rr+'.csv', names=[kat, kaa])
			data_at += [x for x in data[kat]]
			data_aa += [x for x in data[kaa]]
			data_at_fchs[-1] += [x for x in data[kat]]
			data_aa_fchs[-1] += [x for x in data[kaa]]
			j += 3
			
	data_at_fchs = np.transpose(np.array(data_at_fchs))
	pd.DataFrame(data_at_fchs).to_csv("dynamic_at_active_"+str(k)+".csv")
	data_aa_fchs = np.transpose(np.array(data_aa_fchs))
	pd.DataFrame(data_aa_fchs).to_csv("dynamic_aa_active_"+str(k)+".csv")
	
	'''
	pvalue_table = [[],[]]
	data = []
	
	print("FRIEDMAN test for at")
	for y in range(pp):
		data_at_fchs = np.array(data_at_fchs)
		tyty = [data_at_fchs[pp*x+y] for x in range(len(methods))]
		res = friedmanchisquare(tyty[0], tyty[1], tyty[2], tyty[3], tyty[4], tyty[5], tyty[6], tyty[7], tyty[8])
		print("Number of targets: " + str(y+1))
		print("chis: " + str(res.statistic))
		print("pvalue: " + str(res.pvalue) + "\n")
		data.append(res.pvalue)
	pvalue_table[0] += data
	data = []
	print("FRIEDMAN test for aa")
	for y in range(pp):
		data_aa_fchs = np.array(data_aa_fchs)
		tyty = [data_aa_fchs[pp*x+y] for x in range(len(methods))]
		res = friedmanchisquare(tyty[0], tyty[1], tyty[2], tyty[3], tyty[4], tyty[5], tyty[6], tyty[7], tyty[8])
		print("Number of targets: " + str(y+1))
		print("chis: " + str(res.statistic))
		print("pvalue: " + str(res.pvalue) + "\n")
		data.append(res.pvalue)
	pvalue_table[1] += data
	data = []
	'''

	#df = pd.DataFrame(pvalue_table, index=["ave_time k=3","ave_agents k=3"], columns=ticks)
	#df.to_csv("dynamic_pvalues_"+str(k)+".csv")

	data_at = np.array(data_at)
	data_aa = np.array(data_aa)
	if amIequal == 1:
		data_aa = [k for el in range(len(data_at))]

	'''
	fig, axes = plt.subplots(1, 2)
	at = {'method': [ x for x in methods_notation for z in range(reps*len(ticks))],
		'scenario': [y for x in methods for y in ticks for z in range(reps)],
		'at': data_at
			}

	df = pd.DataFrame(at, columns = ['method', 'scenario', 'at'])

	sns.barplot(x="scenario", y="at", hue="method", data=df, palette="muted", ci=0.0, ax=axes[0]).set_title('Average Coverage Time k='+str(k))
	
	#fname = "ave_exectime_"+str(task_instance)
	plt.ylim(0,310)
	axes[0].legend(loc='upper left',prop={'size': 7}).remove()
	axes[0].grid()
	axes[0].set_ylabel("Time")

	aa = {'method': [ x for x in methods_notation for z in range(reps*len(ticks))],
		'scenario': [y for x in methods for y in ticks for z in range(reps)],
		'aa': data_aa
			}

	df = pd.DataFrame(aa, columns = ['method', 'scenario', 'aa'])

	sns.barplot(x="scenario", y="aa", hue="method", data=df, palette="muted", ci=0.0, ax=axes[1]).set_title('Average Agents per Target k='+str(k))
	#fname = "ave_exectime_"+str(task_instance)
	plt.ylim(0,310)
	axes[1].legend(loc='upper left',prop={'size': 7}, bbox_to_anchor=(1, 1))
	axes[1].grid()
	axes[1].set_ylim(1,10.5)
	axes[1].set_ylabel("Agents")

	fname = "dynamic-active_"+str(k)
	plt.tight_layout()
	plt.legend(loc='upper left',prop={'size': 7}, bbox_to_anchor=(1, 1))
	plt.savefig(fname, dpi=300, facecolor='w', edgecolor='w',
			orientation='portrait', papertype=None, format=None,
			transparent=False, bbox_inches=None, pad_inches=0.1,
			frameon=None, metadata=None)
	#tikz_save(rr+'_dynamic'+str(k)+'VP.tex')
	'''
	#plt.show()
	fig, axes = plt.subplots(1, 1)
	combined_data = {'method': [ x for x in methods_notation for z in range(reps*len(ticks))],
		'scenario': [y for x in methods for y in ticks for z in range(reps)],
		'aa': data_aa,
		'at': data_at
			}
	markers_data = [y for x in methods for y in markers for z in range(reps)]
	df = pd.DataFrame(combined_data, columns = ['method', 'scenario', 'aa', 'at'])
	print(df.loc[df['method']=='W'])
	df_means = df.groupby(['method', 'scenario']).mean().reset_index()
	df_std = df.groupby(['method', 'scenario']).std().reset_index()

	print(df_means)
	print(df_std)

	#sns.scatterplot(x='at', y='aa', hue='method', style='scenario', data=df_means, ax=axes).set_title('AveCov-AveAge k>='+str(k))
	sns.scatterplot(x='at', y='aa', hue='method', style='scenario', data=df_means, ax=axes)
	
	axes.set_xlabel(r'Average Coverage Time $\kappa \geq {}$'.format(k))
	axes.set_ylabel(r'Average Agents per Target $\kappa \geq {}$'.format(k))
	axes.set_xlim(left=0)
	if k==3:
		axes.set_ylim(2.2,4.8)
	else:
		axes.set_ylim(2.5,6.5)
	axes.grid()
	#axes.set_xlim(0,300)
	if amIequal == 1:
		axes.set_ylim(0,k+1)

	#Plot the pareto frontier for each scenario - we're looking for the minimum along both axes
	if amIequal == 0:
		for conf in ticks:
			tt = df_means.loc[df_means['scenario']==conf]
			xypoint = [[row['at'], row['aa']] for i, row in tt.iterrows()]
			sort_byX = sorted(xypoint, reverse=True)

			pareto_frontier = [sort_byX[0]]
			for pair in sort_byX:
				if pair[1]>=pareto_frontier[-1][1]:
					pareto_frontier.append(pair)

			#plot the line
			pfx = [pair[0] for pair in pareto_frontier]
			pfy = [pair[1] for pair in pareto_frontier]
			
			p = plt.step(pfx, pfy, lw=0.5, where='post')
			pfx = [pfx[0]] + pfx
			pfx.append(0)
			pfy = [0] + pfy
			pfy.append(pfy[-1])

			print(conf)
			print("SPARTA: "+str(pfx))
			print("SPARTA: "+str(pfy))
			plt.plot(pfx[0:2], pfy[0:2], lw=0.5, color=p[0].get_color())
			plt.plot(pfx[-2:], pfy[-2:], lw=0.5, color=p[0].get_color())

	axes.legend(loc='upper left',prop={'size': 7}, bbox_to_anchor=(1, 1))

	if amIequal==0:
		fname = "dynamic-active_scatter_k_>="+str(k)
	else:
		fname = "dynamic-active_scatter_k_=="+str(k)
	plt.tight_layout()
	plt.legend(loc='upper left',prop={'size': 7}, bbox_to_anchor=(1, 1))
	tikz_save(fname+'.tex')
	plt.savefig(fname, dpi=300, facecolor='w', edgecolor='w',
			orientation='portrait', papertype=None, format=None,
			transparent=False, bbox_inches=None, pad_inches=0.1,
			frameon=None, metadata=None)

	for cnf in range(pp):
		fig, ax = plt.subplots(figsize=(10, 6))
		X = [row['at'] for i, row in df_means.loc[df_means['scenario']==ticks[cnf]].iterrows()]
		labels = [row['method'] for i, row in df_means.loc[df_means['scenario']==ticks[cnf]].iterrows()]
		colors = ['red', 'green', 'blue', 'cyan', 'magenta', 'maroon', 'dodgerblue', 'goldenrod', 'darkorange']
		print(df_means.loc[df_means['scenario']==ticks[cnf]])
		print(labels)
		Y = [row['aa'] for i, row in df_means.loc[df_means['scenario']==ticks[cnf]].iterrows()]
		X_error = [row['at'] for i, row in df_std.loc[df_std['scenario']==ticks[cnf]].iterrows()]
		Y_error = [row['aa'] for i, row in df_std.loc[df_std['scenario']==ticks[cnf]].iterrows()]
		# Plotting the error bars
		for i in range(len(X)):
			ax.errorbar(X[i], Y[i], xerr=X_error[i], yerr=Y_error[i], fmt='o', color=colors[i],
					ecolor=colors[i], capsize=2, label=labels[i])
		ax.set_title("Average and Std for scenario "+str(cnf))
		ax.set_xlabel('Average Coverage Time')
		ax.set_ylabel('Average Agents per Target')
		ax.grid()
		ax.legend()
		if amIequal==0:
			fname = "C"+str(cnf)+"_dynamic-active_scatter_k_>="+str(k)
		else:
			fname = "C"+str(cnf)+"_dynamic-active_scatter_k_=="+str(k)
		plt.savefig(fname, dpi=300, facecolor='w', edgecolor='w',
			orientation='portrait', papertype=None, format=None,
			transparent=False, bbox_inches=None, pad_inches=0.1,
			frameon=None, metadata=None)
	#plt.show()

	###################### Pasive coverage ###############################################
	

	data_at = []
	data_aa = []
	data_at_fchs = []
	data_aa_fchs = []
	kaa = str(k) + 'AA'

	for rr in methods:
		j=1
		data_at_fchs.append([])
		data_aa_fchs.append([])
		for i in range(pp):
			data = pd.read_csv('_10_' + str(j) +'_300_'+str(k)+'_combined_dynamic_'+rr+'.csv', names=[kat, kaa])
			data_at += [x for x in data[kat]]
			data_aa += [x for x in data[kaa]]

			data_at_fchs[-1] += [x for x in data[kat]]
			data_aa_fchs[-1] += [x for x in data[kaa]]
			j += 3
			
	data_at_fchs = np.transpose(np.array(data_at_fchs))
	pd.DataFrame(data_at_fchs).to_csv("dynamic_at_passive_"+str(k)+".csv")
	data_aa_fchs = np.transpose(np.array(data_aa_fchs))
	pd.DataFrame(data_aa_fchs).to_csv("dynamic_aa_passive_"+str(k)+".csv")

	data_at = np.array(data_at)
	data_aa = np.array(data_aa)

	if amIequal == 1:
		data_aa = [k for el in range(len(data_at))]

	'''
	fig, axes = plt.subplots(1, 2)
	at = {'method': [ x for x in methods_notation for z in range(reps*len(ticks))],
		'scenario': [y for x in methods for y in ticks for z in range(reps)],
		'at': data_at
			}

	df = pd.DataFrame(at, columns = ['method', 'scenario', 'at'])

	sns.barplot(x="scenario", y="at", hue="method", data=df, palette="muted", ci=0.0, ax=axes[0]).set_title('Combo Ave-Cov Time k='+str(k))
	#fname = "ave_exectime_"+str(task_instance)
	plt.ylim(0,310)
	axes[0].legend(loc='upper left',prop={'size': 7}).remove()
	axes[0].grid()
	axes[0].set_ylabel("Time")

	aa = {'method': [ x for x in methods_notation for z in range(reps*len(ticks))],
		'scenario': [y for x in methods for y in ticks for z in range(reps)],
		'aa': data_aa
			}

	df = pd.DataFrame(aa, columns = ['method', 'scenario', 'aa'])

	sns.barplot(x="scenario", y="aa", hue="method", data=df, palette="muted", ci=0.0, ax=axes[1]).set_title('Combo Ave-Age per Target k='+str(k))
	#fname = "ave_exectime_"+str(task_instance)
	plt.ylim(0,310)
	axes[1].legend(loc='upper left',prop={'size': 7}, bbox_to_anchor=(1, 1))
	axes[1].grid()
	axes[1].set_ylim(1,10.5)
	axes[1].set_ylabel("Agents")

	fname = "dynamic-passive_"+str(k)
	plt.tight_layout()
	plt.legend(loc='upper left',prop={'size': 7}, bbox_to_anchor=(1, 1))
	plt.savefig(fname, dpi=300, facecolor='w', edgecolor='w',
			orientation='portrait', papertype=None, format=None,
			transparent=False, bbox_inches=None, pad_inches=0.1,
			frameon=None, metadata=None)
	#tikz_save(rr+'_dynamic'+str(k)+'VP.tex')
	plt.show()
	'''
	fig, axes = plt.subplots(1, 1)
	combined_data = {'method': [ x for x in methods_notation for z in range(reps*len(ticks))],
		'scenario': [y for x in methods for y in ticks for z in range(reps)],
		'aa': data_aa,
		'at': data_at
			}
	df = pd.DataFrame(combined_data, columns = ['method', 'scenario', 'aa', 'at'])
	df_means = df.groupby(['method', 'scenario']).mean().reset_index()
	df_std = df.groupby(['method', 'scenario']).std().reset_index()
	print(df_means)
	#sns.scatterplot(x='at', y='aa', hue='method', style='scenario', data=df_means, ax=axes).set_title('AveCov-AveAge k>='+str(k))
	sns.scatterplot(x='at', y='aa', hue='method', style='scenario', data=df_means, ax=axes)
	axes.set_xlabel(r'Average Coverage Time $\kappa \geq {}$'.format(k))
	axes.set_ylabel(r'Average Agents per Target $\kappa \geq {}$'.format(k))
	axes.set_xlim(left=0)
	if k==3:
		axes.set_ylim(2.2,4.8)
	else:
		axes.set_ylim(2.5,6.5)
	axes.grid()
	#axes.set_xlim(0,300)
	if amIequal == 1:
		axes.set_ylim(0,k+1)

		#Plot the pareto frontier for each scenario - we're looking for the minimum along both axes
	if amIequal == 0:
		for conf in ticks:
			tt = df_means.loc[df_means['scenario']==conf]
			xypoint = [[row['at'], row['aa']] for i, row in tt.iterrows()]
			sort_byX = sorted(xypoint, reverse=True)

			pareto_frontier = [sort_byX[0]]
			for pair in sort_byX:
				if pair[1]>=pareto_frontier[-1][1]:
					pareto_frontier.append(pair)

			#plot the line
			pfx = [pair[0] for pair in pareto_frontier]
			pfy = [pair[1] for pair in pareto_frontier]
			
			p = plt.step(pfx, pfy, lw=0.5, where='post')
			pfx = [pfx[0]] + pfx
			pfx.append(0)
			pfy = [0] + pfy
			pfy.append(pfy[-1])

			print(conf)
			print("SPARTA: "+str(pfx))
			print("SPARTA: "+str(pfy))
			plt.plot(pfx[0:2], pfy[0:2], lw=0.5, color=p[0].get_color())
			plt.plot(pfx[-2:], pfy[-2:], lw=0.5, color=p[0].get_color())

	axes.legend(loc='upper left',prop={'size': 7}, bbox_to_anchor=(1, 1))

	if amIequal==0:
		fname = "dynamic-passive_scatter_k_>="+str(k)
	else:
		fname = "dynamic-passive_scatter_k_=="+str(k)
	plt.tight_layout()
	plt.legend(loc='upper left',prop={'size': 7}, bbox_to_anchor=(1, 1))
	tikz_save(fname+'.tex')
	plt.savefig(fname, dpi=300, facecolor='w', edgecolor='w',
			orientation='portrait', papertype=None, format=None,
			transparent=False, bbox_inches=None, pad_inches=0.1,
			frameon=None, metadata=None)

	for cnf in range(pp):
		fig, ax = plt.subplots(figsize=(10, 6))
		X = [row['at'] for i, row in df_means.loc[df_means['scenario']==ticks[cnf]].iterrows()]
		labels = [row['method'] for i, row in df_means.loc[df_means['scenario']==ticks[cnf]].iterrows()]
		colors = ['red', 'green', 'blue', 'cyan', 'magenta', 'maroon', 'dodgerblue', 'goldenrod', 'darkorange']
		print(df_means.loc[df_means['scenario']==ticks[cnf]])
		print(labels)
		Y = [row['aa'] for i, row in df_means.loc[df_means['scenario']==ticks[cnf]].iterrows()]
		X_error = [row['at'] for i, row in df_std.loc[df_std['scenario']==ticks[cnf]].iterrows()]
		Y_error = [row['aa'] for i, row in df_std.loc[df_std['scenario']==ticks[cnf]].iterrows()]
		# Plotting the error bars
		for i in range(len(X)):
			ax.errorbar(X[i], Y[i], xerr=X_error[i], yerr=Y_error[i], fmt='o', color=colors[i],
					ecolor=colors[i], capsize=2, label=labels[i])
		ax.set_title("Average and Std for scenario "+str(cnf))
		ax.set_xlabel('Average Coverage Time')
		ax.set_ylabel('Average Agents per Target')
		ax.grid()
		ax.legend()
		if amIequal==0:
			fname = "C"+str(cnf)+"_dynamic-passive_scatter_k_>="+str(k)
		else:
			fname = "C"+str(cnf)+"_dynamic-passive_scatter_k_=="+str(k)
		plt.savefig(fname, dpi=300, facecolor='w', edgecolor='w',
			orientation='portrait', papertype=None, format=None,
			transparent=False, bbox_inches=None, pad_inches=0.1,
			frameon=None, metadata=None)
	#plt.show()