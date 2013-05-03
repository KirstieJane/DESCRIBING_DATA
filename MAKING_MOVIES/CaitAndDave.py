#/usr/bin/env python
"""
A silly little gift for Caitlin and Dave.
Kx
May 3rd 2013
"""

#==============================================================================
# IMPORTS
#==============================================================================
import matplotlib.animation as animation
import numpy as np
import matplotlib.pylab as plt
import os
import scipy

#==============================================================================
# FUNCTIONS
#==============================================================================
def ani_frame():
    """
    This one is the important one but it really needs to be
    re-written to be more flexible in other instances.
    Love it though!
    Stole it from:
        http://stackoverflow.com/a/13983801/2316203
    
    Kirstie Whitaker
    May 3rd 2013
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_aspect('equal')
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    
    im = ax.imshow(np.random.random(mask.shape)*mask,cmap='Reds')
    im.set_clim([0,1])
    
    text = ax.text(0.5, 0.5, 'hello',
        horizontalalignment='center',
        verticalalignment='baseline',
        transform = ax.transAxes ,
        fontsize = 32 )
            
    fig.set_size_inches([5,5])

    plt.tight_layout()

    def update_img(n):
        if n%15 == 0:
            print n
            tmp = np.random.random(mask.shape) * mask
            im.set_data(tmp)
            text.set_text(words[n/15])
            #text.set_x(np.random.random()*0.8 + 0.1)
            #text.set_y(np.random.random()*0.8 + 0.1)
        if congratulations_marker <= n/15 < congratulations_marker + 4:
            x_pos = np.random.random()
            if x_pos < 0.5:
                    x_pos = x_pos * 0.8
            else:
                x_pos = x_pos * 0.8 + 0.2
            y_pos = np.random.random()
            if y_pos < 0.5:
                    y_pos = y_pos * 0.8
            else:
                y_pos = y_pos * 0.8 + 0.2
            ax.text(x_pos, y_pos,
                    'Congratulations',
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform = ax.transAxes ,
                    fontsize = 12 ,
                    rotation = np.random.random()*360)

            return im

    ani = animation.FuncAnimation(fig,update_img,len(words)*15,interval=30)
    writer = animation.writers['ffmpeg'](fps=30)
    ani.save('CaitAndDave_reds.avi', writer=writer, dpi=dpi)

    return ani

#==============================================================================
# HERE'S THE REAL STUFF:
#==============================================================================
# Create Heart Mask

# I stole this formula from 
# http://stackoverflow.com/questions/4478078/how-to-draw-a-heart-with-pylab
x = scipy.linspace(-3,3,1000)
y1 = scipy.sqrt(1-(abs(x)-1)**2)
y2 = -3*scipy.sqrt(1-(abs(x)/2)**0.5)

# Create an array of zeros
heart = np.ones([len(x), len(x)]) * 0

# Fill it in where the heart should be
for i in range(len(x)):
    for j in range(len(x)):
        if (y2[j] < x[i] < y1[j]):
            heart[i,j]=1
            
# Flip it upside down
heart = np.flipud(heart)            

# Convert it to a boolean mask
mask = heart==1

# Reshape the mask so there is equal white space
# top and bottom
mask = mask[300:, 150:(-150)]

#------------------------------------------------------------------------------
# Define your sentence

sentence = ( 'Hello!  I learned how to make movies in matplotlib today ' +
           'and I thought I would use these new skills to say . .. ... ' +
           'CONGRATULATIONS CONGRATULATIONS CONGRATULATIONS ' +
           'to Caitlin and Dave on their engagement!   ' +
           'Lots of love Kx' )

# Leave in a space if there are two together
words = sentence.split(' ')

# Keep the last word on the screen for a little bit
words.append(words[-1])
words.append(words[-1])
words.append(words[-1])

# Mark the first "CONGRATULATIONS"
congratulations_marker = words.index('CONGRATULATIONS')

# Set your dpi
dpi = 100

# Make sure you're in the right place
# (if anyone is reading this - don't worry who steve was
# I bought my computer second hand and I'm assuming that the dude
# I bought it from was called steve. I don't remember....
# Super bugs me that I can't change it though.)
os.chdir('C://Users//steve//Drivers//FFmpeg')

# And GO!
ani = ani_frame()
