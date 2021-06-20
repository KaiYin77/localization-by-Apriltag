import numpy as np
import math
from sklearn.neighbors import LocalOutlierFactor

nd = np.load("../output/p.npz")
a = nd['a'].reshape(-1,3)
b = nd['b'].reshape(-1,3)
c = nd['c'].reshape(-1,3)
d = nd['d'].reshape(-1,3)
e = nd['e'].reshape(-1,3)

tag1 = np.load("../output/tag1.npy")[:3]
# print(tag1)

c_min = 100.
for i in c:
    dis = math.sqrt((tag1[0]-i[0])*(tag1[0]-i[0]) + (tag1[1]-i[1])*(tag1[1]-i[1]) + (tag1[2]-i[2])*(tag1[2]-i[2]))
    if dis<c_min:
        c_min = dis

dele = []
# print(dele)
for i in range(len(c)):
    dis = math.sqrt((tag1[0]-c[i][0])*(tag1[0]-c[i][0]) + (tag1[1]-c[i][1])*(tag1[1]-c[i][1]) + (tag1[2]-c[i][2])*(tag1[2]-c[i][2]))
    if dis > c_min+0.3:
        dele.append(i)
# print(dele)
# print(c)
# print(np.delete(c,dele,0))
# print(c_min)

c = np.delete(c,dele,0)

# print(len(a))
# print(len(b))
# print(len(c))
# print(len(d))
# print(len(e))
nn = [a,b,c,d,e]
for i in nn:
    if len(i)<2:
        i=np.append(i,i[0])
        i=np.append(i,i[0])

clf = LocalOutlierFactor(n_neighbors=(int)(len(a)/10)+2)
a_pred = clf.fit_predict(a)
clf = LocalOutlierFactor(n_neighbors=(int)(len(b)/10)+2)
b_pred = clf.fit_predict(b)
clf = LocalOutlierFactor(n_neighbors=(int)(len(c)/10)+2)
c_pred = clf.fit_predict(c)
clf = LocalOutlierFactor(n_neighbors=(int)(len(d)/10)+2)
d_pred = clf.fit_predict(d)
clf = LocalOutlierFactor(n_neighbors=(int)(len(e)/10)+2)
e_pred = clf.fit_predict(e)

an = bn = cn = dn = en =0
a_fin = np.zeros(3)
for i in range(len(a_pred)):
    if a_pred[i]==1 :
        # print(a[i])
        a_fin += a[i]
        an+=1
b_fin = np.zeros(3)
for i in range(len(b_pred)):
    if b_pred[i]==1 :
        # print(b[i])
        b_fin += b[i]
        bn+=1
c_fin = np.zeros(3)
for i in range(len(c_pred)):
    if c_pred[i]==1 :
        # print(c[i])
        c_fin += c[i]
        cn+=1
d_fin = np.zeros(3)
for i in range(len(d_pred)):
    if d_pred[i]==1 :
        # print(d[i])
        d_fin += d[i]
        dn+=1
e_fin = np.zeros(3)
for i in range(len(e_pred)):
    if e_pred[i]==1 :
        # print(e[i])
        e_fin += e[i]
        en+=1

a_fin/=an
b_fin/=bn
c_fin/=cn
d_fin/=dn
e_fin/=en
print("ans")
print(a_fin)
print(b_fin)
print(c_fin)
print(d_fin)
print(e_fin)
    
file = open("../output/pyrobot_outlier.txt","w")
list = [a_fin, b_fin, c_fin, d_fin, e_fin]
for element in list:
    file.write(str(element[0]) + " ")
    file.write(str(element[1]) + " ")
    file.write(str(element[2]) + "\n")
file.close()