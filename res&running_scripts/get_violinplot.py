#!/usr/bin/env python
from matplotlib2tikz import save as tikz_save
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

#data = pd.read_csv('_10_1_300_5_static.csv')
#data.boxplot()
#plt.xticks((1, 2, 3, 4 ), ('k=1 - ave time', 'k=1 - min time', 'k=5 - ave time', 'k=5 - min time', ))
#plt.show()

k = int(input("Define k: "))
print(k)

pp = int(input("Define nr of distinct configurations: "))

ticks = []
for i in range(pp):
    ticks.append('C'+str(i))

fig, axes = plt.subplots(1, 2, sharey=True)
j=1
data_1at = []
data_1mt = []
data_kat = []
data_kmt = []
kat = str(k) + 'AT'
kmt = str(k) + 'MT'

for i in range(pp):
    data = pd.read_csv('_10_' + str(j) +'_300_'+str(k)+'_static.csv', names=['1AT', '1MT', kat, kmt])
    data_1at.append([x for x in data['1AT']])
    data_1mt.append([x for x in data['1MT']])
    data_kat.append([x for x in data[kat]])
    data_kmt.append([x for x in data[kmt]])
    j += 3

#data = pd.read_csv('_10_100_300_'+str(k)+'_static.csv', names=['1AT', '1MT', kat, kmt])
#data_1at.append([x for x in data['1AT']])
#data_1mt.append([x for x in data['1MT']])
#data_kat.append([x for x in data[kat]])
#data_kmt.append([x for x in data[kmt]])

#data = pd.read_csv('_10_200_300_'+str(k)+'_static.csv', names=['1AT', '1MT', kat, kmt])
#data_1at.append([x for x in data['1AT']])
#data_1mt.append([x for x in data['1MT']])
#data_kat.append([x for x in data[kat]])
#data_kmt.append([x for x in data[kmt]])

data_1at = np.array(data_1at)
data_1mt = np.array(data_1mt)
data_kat = np.array(data_kat)
data_kmt = np.array(data_kmt)

axes[0].violinplot(np.transpose(data_1at))
axes[0].set_title('Average Time to Coverage k=1')
axes[0].grid()

axes[1].violinplot(np.transpose(data_kat))
axes[1].set_title('Average Time to Coverage k='+str(k))
axes[1].grid()

for x in range(2):
    axes[x].set_xlabel("Configurations")
axes[0].set_ylabel("Time")

plt.setp(axes, xticks=[b+1 for b in range(pp)], xticklabels=ticks)
tikz_save('staticVP_at'+str(k)+'.tex')

fig, axes = plt.subplots(1, 2, sharey=True)
axes[0].violinplot(np.transpose(data_1mt))
axes[0].set_title('Minimum Time to Coverage k=1')
axes[0].grid()

axes[1].violinplot(np.transpose(data_kmt))
axes[1].set_title('Minimum Time to Coverage k='+str(k))
axes[1].grid()

for x in range(2):
    axes[x].set_xlabel("Configurations")

axes[0].set_ylabel("Time")

plt.setp(axes, xticks=[b+1 for b in range(pp)], xticklabels=ticks)

tikz_save('staticVP_mt'+str(k)+'.tex')
plt.show()
############################# Combined Coverage #################################
ticks = []
for i in range(pp):
    ticks.append('C'+str(i))

fig, axes = plt.subplots(1, 2, sharey=True)
j=1
data_1at = []
data_1mt = []
data_kat = []
data_kmt = []
kat = str(k) + 'AT'
kmt = str(k) + 'MT'

for i in range(pp):
    data = pd.read_csv('_10_' + str(j) +'_300_'+str(k)+'_combined_static.csv', names=['1AT', '1MT', kat, kmt])
    data_1at.append([x for x in data['1AT']])
    data_1mt.append([x for x in data['1MT']])
    data_kat.append([x for x in data[kat]])
    data_kmt.append([x for x in data[kmt]])
    j += 3

#data = pd.read_csv('_10_100_300_'+str(k)+'_combined_static.csv', names=['1AT', '1MT', kat, kmt])
#data_1at.append([x for x in data['1AT']])
#data_1mt.append([x for x in data['1MT']])
#data_kat.append([x for x in data[kat]])
#data_kmt.append([x for x in data[kmt]])

#data = pd.read_csv('_10_200_300_'+str(k)+'_combined_static.csv', names=['1AT', '1MT', kat, kmt])
#data_1at.append([x for x in data['1AT']])
#data_1mt.append([x for x in data['1MT']])
#data_kat.append([x for x in data[kat]])
#data_kmt.append([x for x in data[kmt]])

data_1at = np.array(data_1at)
data_1mt = np.array(data_1mt)
data_kat = np.array(data_kat)
data_kmt = np.array(data_kmt)

axes[0].violinplot(np.transpose(data_1at))
axes[0].set_title('Combined Average Time to Coverage k=1')
axes[0].grid()

axes[1].violinplot(np.transpose(data_kat))
axes[1].set_title('Combined Average Time to Coverage k='+str(k))
axes[1].grid()

for x in range(2):
    axes[x].set_xlabel("Configurations")
axes[0].set_ylabel("Time")

plt.setp(axes, xticks=[b+1 for b in range(pp)], xticklabels=ticks)
tikz_save('combined_staticVP_at'+str(k)+'.tex')

fig, axes = plt.subplots(1, 2, sharey=True)
axes[0].violinplot(np.transpose(data_1mt))
axes[0].set_title('Minimum Time to Coverage k=1')
axes[0].grid()

axes[1].violinplot(np.transpose(data_kmt))
axes[1].set_title('Minimum Time to Coverage k='+str(k))
axes[1].grid()

for x in range(2):
    axes[x].set_xlabel("Configurations")

axes[0].set_ylabel("Time")

plt.setp(axes, xticks=[b+1 for b in range(pp)], xticklabels=ticks)

tikz_save('combined_staticVP_mt'+str(k)+'.tex')
plt.show()



###############################################################################
######################################DYNAMIC##################################
fig1, axes1 = plt.subplots(1, 2)

j=1
data_at = []
data_aa = []
kaa = str(k) + 'AA'
for i in range(pp):
    data = pd.read_csv('_10_' + str(j) +'_300_'+str(k)+'_dynamic.csv', names=[kat, kaa])
    data_at.append([x for x in data[kat]])
    data_aa.append([x for x in data[kaa]])
    j += 3

data = pd.read_csv('_10_100_300_'+str(k)+'_dynamic.csv', names=[kat, kaa])
data_at.append([x for x in data[kat]])
data_aa.append([x for x in data[kaa]])

#data = pd.read_csv('_10_200_300_'+str(k)+'_dynamic.csv', names=[kat, kaa])
#data_at.append([x for x in data[kat]])
#data_aa.append([x for x in data[kaa]])

data_at = np.array(data_at)
data_aa = np.array(data_aa)

axes1[0].violinplot(np.transpose(data_at))
axes1[0].set_title('Average Coverage Time k='+str(k))
axes1[0].grid()
axes1[0].set_ylabel("Time")

axes1[1].violinplot(np.transpose(data_aa))
axes1[1].set_title('Average Agents per Target k='+str(k))
axes1[1].grid()
axes1[1].set_ylim(1,6)
axes1[1].set_ylabel("Agents")

axes1[1].yaxis.tick_right()
axes1[1].yaxis.set_label_position("right")

for x in range(2):
    axes1[x].set_xlabel("Configurations")

plt.setp(axes1, xticks=[b+1 for b in range(pp)], xticklabels=ticks)
tikz_save('dynamic'+str(k)+'VP.tex')
plt.show()

###################### Pasive coverage ###############################################
fig1, axes1 = plt.subplots(1, 2)

j=1
data_at = []
data_aa = []
kaa = str(k) + 'AA'
for i in range(pp):
    data = pd.read_csv('_10_' + str(j) +'_300_'+str(k)+'_combined_dynamic.csv', names=[kat, kaa])
    data_at.append([x for x in data[kat]])
    data_aa.append([x for x in data[kaa]])
    j += 3

data = pd.read_csv('_10_100_300_'+str(k)+'_combined_dynamic.csv', names=[kat, kaa])
data_at.append([x for x in data[kat]])
data_aa.append([x for x in data[kaa]])

#data = pd.read_csv('_10_200_300_'+str(k)+'_combined_dynamic.csv', names=[kat, kaa])
#data_at.append([x for x in data[kat]])
#data_aa.append([x for x in data[kaa]])

data_at = np.array(data_at)
data_aa = np.array(data_aa)

axes1[0].violinplot(np.transpose(data_at))
axes1[0].set_title('Combined Average Coverage Time k='+str(k))
axes1[0].grid()
axes1[0].set_ylabel("Time")

axes1[1].violinplot(np.transpose(data_aa))
axes1[1].set_title('Combined Average Agents per Target k='+str(k))
axes1[1].grid()
axes1[1].set_ylim(1,6)
axes1[1].set_ylabel("Agents")

axes1[1].yaxis.tick_right()
axes1[1].yaxis.set_label_position("right")

for x in range(2):
    axes1[x].set_xlabel("Configurations")

plt.setp(axes1, xticks=[b+1 for b in range(pp)], xticklabels=ticks)
tikz_save('combined_dynamic'+str(k)+'VP.tex')
plt.show()
