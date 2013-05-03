import matplotlib.pylab as plt
import scipy
import numpy as np

x = scipy.linspace(-3,3,1000)
y1 = scipy.sqrt(1-(abs(x)-1)**2)
y2 = -3*scipy.sqrt(1-(abs(x)/2)**0.5)

heart = np.ones([len(x), len(x)]) * 0
print heart.shape
noise = np.random.random(heart.shape)

for i in range(len(x)):
    for j in range(len(x)):
        if (y2[j] < x[i] < y1[j]):
            heart[i,j]=1
            
heart = np.flipud(heart)            

mask = heart==1

plt.imshow(noise[300:, :]*mask[300:, :])
#plt.xlim([-2.5, 2.5])
plt.show()