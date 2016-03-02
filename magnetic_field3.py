#! /usr/bin/env python 

# import matplotlib
import numpy as np
import matplotlib.pyplot as plt

#  Area of integration
L = 1.0
W = 1.0

# Size of output magnetic field plot
Nplt = 16
# Plot every skip point in each direction must be an integer >= 1
skip = 5
# Median over these points in finding derivatives for added robustness
smooth = 4   #

# Make NxN array for the total calculation bigger, because of edge effects.
N = skip*(Nplt + 2) 

# Size of nxn array that bounds the magnet
n = 30

# Define Maximum and minimum area of the magnet
X_max = W/2.0
X_min = -1*W/2.0
Y_max = L/2.0
Y_min = -1*L/2.0

# Define Maximum and minimum area of the calculation

scale =( N + 2*smooth )/(N.__float__() - 1.0)

x_max = 1.0*scale
x_min = -1.0*scale
y_max = 1.0*scale
y_min = -1.0*scale

# Define the x and y 2D arrays
x, y = np.meshgrid(np.linspace(x_min,x_max,num=N),np.linspace(y_min,y_max,num=N))
# Define the X and Y 1 D arrays
X = np.linspace(X_min,X_max,num=n)
Y = np.linspace(Y_min,Y_max,num=n)

# And corresponing 2D arrays
XX, YY = np.meshgrid(X,Y)

# Define dx, dy, dX, dY, dR
dx = x[N/2+1,N/2+1] - x[N/2,N/2]
dy = y[N/2+1,N/2+1] - y[N/2,N/2]
dX = X[n/2+1] - X[n/2]
dY = Y[n/2+1] - Y[n/2]
dR = np.sqrt(dX**2 + dY**2)

# Find Magnetization 
#    '''Here is where to put in an interesting shape magnet
#    Define the magnetization array initially in y-hat direction
#   So it is a rectangular bar magnet of dimensions L X W unless changed.'''

My = 1.0 * ( np.logical_and((np.abs(YY) <= L/2.0),(np.abs(XX) <= W/2.0)) )
Mx = 0.0 * My  
M = np.sqrt(Mx**2 + My**2)
# initialize dA as an n x n x N x N array
dAz = np.zeros((n,n,N,N))
# initialize N x N matrixes
rR2  =  np.zeros((N,N))
Bx   =  np.zeros((N,N))
By   =  np.zeros((N,N))
Az   =  np.zeros((N,N))
# We need to make sure that we are not integrating at distances smaller than the
# gridsize, otherwise the vector potential may depend on how the two grids line up.
dR2  = dR**2   #  The X Y diagonal gridsize spacing squared
rR2max = (x_max-x_min+X_max-X_min)**2 + (y_max-y_min+Y_max-Y_min)**2

#  Find dA(x,y,X,Y)
pi = 3.14159265359
i = 0
while i < n:  # The X Loop
    j = 0
    while j < n:  # The Y Loop
        rR2 = (x-X[i])**2 + (y-Y[j])**2
        rR2 = rR2.clip(2*dR2, 10*rR2max)  #  Clip at two grid spacing, and large distances
        dAz[j,i,:,:] = (0.5/pi) * ( Mx[j,i]*(y-Y[j]) - My[j,i]*(x - X[i]) ) / rR2
        j += 1
    i += 1
# End Looping

# Numerically integrate
Az = np.trapz(np.trapz(dAz, Y, axis=0), X, axis=0)

# Now we find the curl of Az in order to find Bx, By
# Initiate the Dx and Dy arrays
Dx   =  np.zeros(smooth-2)
Dy   =  np.zeros(smooth-2)
i = smooth
while i < N-smooth:  # The x Loop
    j = smooth
    while j < N-smooth:  # The y Loop
        k = 2
        while k < smooth:   #  This loop is to add robustness by calculating multiple derivatives
            Dx[k-2] =    (Az[j,i+k+1] - Az[j,i-k])/(x[j,i+k+1] - x[j,i-k])
            Dy[k-2] =    (Az[j+k+1,i] - Az[j-k,i])/(y[j+k+1,i] - y[j-k,i])
            k += 1
        Bx[j,i] = np.median(Dy)
        By[j,i] = -1*np.median(Dx)
        j += 1
    i += 1
# End Looping

# Make smaller arrays to plot the magnetic field
step = skip
start = (N-skip*Nplt)/2 + 2
stop = (N+skip*(Nplt-1))/2 + 1
BpltX   =  Bx[start:stop:step,start:stop:step]
BpltY   =  By[start:stop:step,start:stop:step]
xplt    =  x[start:stop:step,start:stop:step]
yplt    =  y[start:stop:step,start:stop:step]

#  The arrow scale factor -- notice the bigger it is the smaller the arrow
scale = np.max(np.sqrt(BpltX**2 + BpltY**2)) * Nplt * 1.01

###########################
#  Plotting
###########################

# First we close and open a plot window, and set the axes and labels.

plt.close()
plt.box(on='on')
plt.axis('scaled')
plt.axis((-1.1, 1.1, -1.1, 1.1))    
plt.xlabel(r'$\bf x$', fontsize=20)
plt.ylabel(r'$\bf y$', fontsize=20)
TITLE ="A 2D Square Magnet"
plt.title(TITLE, weight='bold')

# First we will make a grayscale plot of the vector potential: 

plt.gray()
plt.pcolor(x,y,Az, alpha=1.0, zorder=0)

filename = TITLE.replace(' ','_') + "_plot_1" + ".png"
plt.savefig(filename, bbox_inches='tight')
temp = raw_input('hit return to show next plot')

# Alpha represents the opacity, and zorder represents what layer this represents.

# Now we will plot a box to represent the magnet.

box1x = (-1*L/2.0,L/2.0,L/2.0,-1*L/2.0)
box1y = (-1*W/2.0,-1*W/2.0,W/2.0,W/2.0)
plt.fill(box1x,box1y, facecolor='silver', edgecolor='None', alpha=0.5 , zorder=2)

filename = filename.replace('plot_1','plot_2')
plt.savefig(filename, bbox_inches='tight')
temp = raw_input('hit return to show next plot')

# Now, we will make a colorful filled contour plot of the vector potential, 
# and plot it underneath the box, but on top of boring gray scale plot we made. 
# We will also include a colorbar.

plt.spectral()
plt.contourf(x,y,Az,20, alpha=1.0, zorder=1)
plt.colorbar(orientation='vertical')
plt.figtext(0.92, 0.35, 'The Vector Potential', rotation=-90, weight='bold')

filename = filename.replace('plot_2','plot_3')
plt.savefig(filename, bbox_inches='tight')
temp = raw_input('hit return to show next plot')

#  Now, let's plot white magnetic field vectors on top of the 
# vector potential plot. We will also make sure that the longest 
# arrow length is the grid spacing.

scale = np.max(np.sqrt(BpltX**2 + BpltY**2)) * Nplt  # The bigger the scale, the shorter the arrow
plt.quiver(xplt,yplt,BpltX,BpltY,pivot='middle',units='height', scale=scale, 
    zorder=4, color='white')

filename = filename.replace('plot_3','plot_4')
plt.savefig(filename, bbox_inches='tight')
