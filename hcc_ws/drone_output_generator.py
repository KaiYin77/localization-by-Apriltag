import numpy as np
import math
from sklearn.neighbors import LocalOutlierFactor

nd = np.load("../output/drone_pkg.npz")
a = nd['a'].reshape(-1,3)
b = nd['b'].reshape(-1,3)
c = nd['c'].reshape(-1,3)
d = nd['d'].reshape(-1,3)

print(len(a))
print(len(b))
print(len(c))
print(len(d))
nn = [a,b,c]
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

an = bn = cn = dn = 0
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

a_fin/=an
b_fin/=bn
c_fin/=cn

d_min = 50.
for i in d:
    dis = math.sqrt((c_fin[0]-i[0])*(c_fin[0]-i[0])
                  + (c_fin[1]-i[1])*(c_fin[1]-i[1]) 
                  + (c_fin[2]-i[2])*(c_fin[2]-i[2]))
    if dis<d_min:
        d_min = dis

dele = []
# print(dele)
for i in range(len(d)):
    dis = math.sqrt((c_fin[0]-d[i][0])*(c_fin[0]-d[i][0]) 
                  + (c_fin[1]-d[i][1])*(c_fin[1]-d[i][1]) 
                  + (c_fin[2]-d[i][2])*(c_fin[2]-d[i][2]))
    if dis > d_min+0.3:
        dele.append(i)
# print(dele)
# print(c)
# print(np.delete(c,dele,0))
# print(c_min)

d = np.delete(d, dele, 0)
if len(d) < 2:
        d = np.append(d, d[0])
        d = np.append(d, d[0])

clf = LocalOutlierFactor(n_neighbors=(int)(len(d)/10)+2)
d_pred = clf.fit_predict(d)

d_fin = np.zeros(3)
for i in range(len(d_pred)):
    if d_pred[i] == 1 :
        # print(d[i])
        d_fin += d[i]
        dn += 1

d_fin/=dn

print("ans")
print(a_fin)
print(b_fin)
print(c_fin)
print(d_fin)
    
file = open("../output/drone_outlier_2.txt","w")
list = [a_fin, b_fin, c_fin, d_fin]
for element in list:
    file.write(str(element[0]) + " ")
    file.write(str(element[1]) + " ")
    file.write(str(element[2]) + "\n")
file.close()
