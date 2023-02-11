#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Created on Sat Dec 29 18:23:33 2018

@author: Daniel Bromley


'''

#import matplotlib
#matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
from matplotlib.figure import Figure
import tkinter as tk
import sys
import ctypes
#from tkinter import filedialog
from os.path import basename, splitext

import wx


def file_finder():
    '''
    Inputs:
            
            N/A
       
    Description:
            
                Uses wxPython library to create a dialog box allowing for the choosing of files for data analysis
     
    Returns:
            
            'path' - this is the path of the data file that will be analysed
    '''
    
    
    app = wx.App(None)
    style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
    dialog = wx.FileDialog(None, 'Open', style=style)
    if dialog.ShowModal() == wx.ID_OK:
        path = dialog.GetPath()
    else:
        path = None
    dialog.Destroy()
    
    print('path = ', path)
    return path  

def datacollector(filename):
    
    """
        Inputs:
            
            'filename' - the filename of the file you want to extract data from
    
        
        Description:
            
            Uses np.genfromtext to extract data from a file - IN NEAR FUTURE - will determine delimiter and not need to be told 
            
        Returns:
            
            'data' - this is the data in the file
            'label' - this is a list of the data headers - must contain 'Time', change if 'Time' not a column
            
            
        NEEDS SOME ERROR TESTING STUFF try except etc
            
        
    """
        
    with open(filename, 'r') as datafile:
        
        delimit = None
                
        for line in datafile:
                if 'I' in line or 'Angle' in line: #these are commonly used column headers in xray files for intensity and angle
                    if ',' in line:
                        delimit = ',' #CSV file delimiter
                    
                    if '	' in line:
                        delimit = '	' #txt files delimiter
                    
                    labels=line.rstrip() #removes \n from last label
                    labels = labels.split(delimit)
                    
                    break 
                else:
                    continue
                    
        data = np.genfromtxt(datafile,delimiter=delimit,skip_header=0,filling_values="nan")
            
    return data,labels
 


class mclass:
    
    def __init__(self,  window, data):
        """
        Inputs: 
        'self' - This produces an instance for the class
        'window' - The main window i.e GUI
        'data' - Xray data found using datacollector    
        
        Description:
            __init__ sets up the class so that it acts on each instance i.e. self, giving it different
            attributes such as window, box, button, data etc
        
        
        """
        self.window = window
        self.box = tk.Entry(window)
        self.plotter
        self.button = tk.Button(window, text="plot", command=self.plotter)
        #self.box.pack()
        self.button.pack()
        self.data = data
        self.plus_minus_clicks = 1
    
    

    def plotter(self):
        """
        This plots the XRR data along with a navigation toolbar
        """
        #Data is separated into angle and intensity
        angle = data[:,0]
        intensity = data[:,1]
        
        #Figure is produced of specified size and is plotted
        fig = Figure(figsize=(7,7))
        self.fig = fig
        global a #making this global allows them to be plotted on later with markers

        a = fig.add_subplot(111)
        a.plot(angle,intensity,color='red')

        #Titles, axes labels and scales are set here
        title = basename(filename)#uses os.path.basename to find the filename from the total path        
        a.set_title (title, fontsize=16)
        a.set_ylabel('Intensity (arb units)', fontsize=14)
        a.set_xlabel(r'2$\vartheta$', fontsize=14)
        a.set_yscale('log')
        a.tick_params(direction='in',which='both',bottom=True,top=True,left=True,right=True)

        #Here the canvas is produced and rendered
        global canvas #making this global allows them to have the interactive markers plotted on top

        canvas = FigureCanvasTkAgg(fig, master=self.window)
        canvas.get_tk_widget().pack()
        #Navigation toolbar is produced hear via the matplotlib.backends.backend_tkagg library
        NavigationToolbar2Tk(canvas, window) 

        
        #fig.canvas.mpl_connect('button_press_event', self.on_pick)
        fig.canvas.mpl_connect('key_press_event', self.on_key)

        
        canvas.draw()
        
        
    global coords
    coords = []
    


    def on_key(self, event):
        """Press 'x' to make a cross marker where your mouse is, if that is not the expected point, press 'backspace' and it
        will be deleted from the 2theta data.
        Press 'enter' to leave the window and calculate the thickness"""
        
        if 'x' == event.key:
            
            self.plus_minus_clicks = 1 #restart the up_click counter for each marker
            
            
            ix, iy = event.xdata, event.ydata
                                    
            coords.append(np.array([ix, iy]))
           
            a.plot(np.array(coords)[:,0][-1],np.array(coords)[:,1][-1],'|',c='b',markersize=50) #this plots the vertical part of the cross
            a.plot(np.array(coords)[:,0][-1],np.array(coords)[:,1][-1],'_',c='b',markersize=50) #this plots the horizontal part of the cross

            canvas.draw()
            
             
            if len(np.asarray(coords)[:,0]) != len(set(np.asarray(coords)[:,0])):
            #If you select a 2theta twice value by accident, the code will let you know and delete it
            
                del coords[-1]
                ctypes.windll.user32.MessageBoxW(0, 'Selecting the same 2theta value twice will give an inf value', "", 1) 
                #The above line produces a pop-up box
        
        
        
        if '+' == event.key: #this if statement increases the size of the marker
            
            
            
            self.plus_minus_clicks+=1
            
            markersize_counter = self.plus_minus_clicks*50 #each click will increase the marker by 50

            
            if 1 < len(a.axes.lines): #make sure there is a marker to increase the size of
                a.axes.lines[-1].remove() #these remove the incorrect marker
                a.axes.lines[-1].remove()
                 
                a.plot(np.array(coords)[:,0][-1],np.array(coords)[:,1][-1],'|',c='b',markersize=markersize_counter) #this plots the vertical part of the cross
                a.plot(np.array(coords)[:,0][-1],np.array(coords)[:,1][-1],'_',c='b',markersize=markersize_counter) #this plots the horizontal part of the cross

                canvas.draw()
            else:
                pass
            
        
        if '-' == event.key and 1<self.plus_minus_clicks:  #this if statement increases the size of the marker and makes sure you dont 
                                                      #reduce it to 0
            
            self.plus_minus_clicks-=1 

            
            markersize_counter = self.plus_minus_clicks*50 #each click will decrease the marker by 50

            
            if 1 < len(a.axes.lines):
                a.axes.lines[-1].remove() #these remove the incorrect marker
                a.axes.lines[-1].remove()
                
                a.plot(np.array(coords)[:,0][-1],np.array(coords)[:,1][-1],'|',c='b',markersize=markersize_counter) #this plots the vertical part of the cross
                a.plot(np.array(coords)[:,0][-1],np.array(coords)[:,1][-1],'_',c='b',markersize=markersize_counter) #this plots the horizontal part of the cross

                canvas.draw()
            else:
                pass
            
            
            canvas.draw()
            
            return markersize_counter
            
            
        if 'left' == event.key: #this if statement increases the size of the marker
            
            
            
            markersize_counter = self.plus_minus_clicks*50


            
            if 1 < len(a.axes.lines): #make sure there is a marker to increase the size of
                a.axes.lines[-1].remove() #these remove the incorrect marker
                a.axes.lines[-1].remove()
                
                a.plot(coords[-1][0]-twotheta_click_step,np.array(coords)[:,1][-1],'|',c='b',markersize=markersize_counter) #this plots the vertical part of the cross
                a.plot(coords[-1][0]-twotheta_click_step,np.array(coords)[:,1][-1],'_',c='b',markersize=markersize_counter) #this plots the horizontal part of the cross

                coords[-1][0] = coords[-1][0]-twotheta_click_step #sets the nex x value and stores it
                
                canvas.draw()
            else:
                pass
            
        if 'right' == event.key: #this if statement increases the size of the marker
            
            markersize_counter = self.plus_minus_clicks*50


            
            if 1 < len(a.axes.lines): #make sure there is a marker to increase the size of
                a.axes.lines[-1].remove() #these remove the incorrect marker
                a.axes.lines[-1].remove()
                
                a.plot(coords[-1][0]+twotheta_click_step,np.array(coords)[:,1][-1],'|',c='b',markersize=markersize_counter) #this plots the vertical part of the cross
                a.plot(coords[-1][0]+twotheta_click_step,np.array(coords)[:,1][-1],'_',c='b',markersize=markersize_counter) #this plots the horizontal part of the cross

                coords[-1][0] = coords[-1][0]+twotheta_click_step #sets the nex x value and stores it
                
                canvas.draw()
            else:
                pass
            
        
        
        if 'up' == event.key: #this if statement moves the marker up
            
            markersize_counter = self.plus_minus_clicks*50


            
            if 1 < len(a.axes.lines): #make sure there is a marker to increase the size of
                a.axes.lines[-1].remove() #these remove the incorrect marker
                a.axes.lines[-1].remove()
                
                a.plot(coords[-1][0],np.array(coords)[:,1][-1]*1.05,'|',c='b',markersize=markersize_counter) #this plots the vertical part of the cross
                a.plot(coords[-1][0],np.array(coords)[:,1][-1]*1.05,'_',c='b',markersize=markersize_counter) #this plots the horizontal part of the cross
                
                coords[-1][1] = coords[-1][1]*1.05 #moves the marker up by 5% of the current y value

                
                canvas.draw()
            else:
                pass
            
        
        if 'down' == event.key:  #this if statement moves the marker down
            
            
            markersize_counter = self.plus_minus_clicks*50


            
            if 1 < len(a.axes.lines): #make sure there is a marker to increase the size of
                a.axes.lines[-1].remove() #these remove the incorrect marker
                a.axes.lines[-1].remove()
           
                a.plot(coords[-1][0],np.array(coords)[:,1][-1]*0.95,'|',c='b',markersize=markersize_counter) #this plots the vertical part of the cross
                a.plot(coords[-1][0],np.array(coords)[:,1][-1]*0.95,'_',c='b',markersize=markersize_counter) #this plots the horizontal part of the cross
                
                coords[-1][1] = coords[-1][1]*0.95 #moves the marker down by 5% of the current y value
                
                canvas.draw()
            else:
                pass
        
        
                
        if 'backspace' == event.key:
            
            if len(coords) != 0:
                del coords[-1] #delete the last coordinates recorded

     
            if 1 < len(a.axes.lines):
                a.axes.lines[-1].remove() #these remove the incorrect marker
                a.axes.lines[-1].remove()
                
            else:
                ctypes.windll.user32.MessageBoxW(0, 'No more markers to delete', "", 1) 

                pass
            
            canvas.draw()
        
        if 'enter' == event.key:
            if len(coords) < 6:#checks there are enough data points to fit and get an error using np.polyfit
                ctypes.windll.user32.MessageBoxW(0, "You need at least 6 peaks to fit xray data and get error.\nIf you cannot find another peak"+\
                                                 "and don't want to continue fitting, click ok and then exit using the top right cross.", "", 1) 
            else:
                window.destroy()
                
            return
        
        if 'escape' == event.key:
            
            window.destroy()#destroying the window first stops tkinter from crashing
            sys.exit('You have closed the program.')#shut the code down
            
            return

        
        

def theta_convert(coords):
    '''
    This takes the actual 2theta values found in the coords list and calculates the 
    thickness from them, using the equation below:
        
        n*lambda = 2*d*sin(theta_n)
        (n+1)*lambda = 2*d*sin(theta_n+1)
        ((n+1)^2 - n^2)*lambda^2 = 4*d^2*(sin(theta_n+1)^2-sin(theta_n)^2)
        
        ==> d = sqrt((2n+1)*lambda^2/4((sin(theta_n+1)^2-sin(theta_n)^2)))
        
        
    '''
    if len(coords)<6: #checks there are enough peaks before fitting the data
        sys.exit('Not enough peaks to fit data')
        
    theta = coords[:,0]/2.0
    
    theta = np.sort(theta)#sorts the theta values in ascending order so that they can be fit and dont produce negative squareroots
    
    top_list = []
    bottom_list = [] #plotting the top against the bottom will mean we can fit to find d

    for i in range(0,len(theta)-1):
        
        top = np.sqrt((2*(i+1)+1)*wavelength**2.0)
        top_list.append(top)
   
        bottom =  np.sqrt(4*(np.sin(np.deg2rad(theta[i+1]))**2.0 - np.sin(np.deg2rad(theta[i]))**2.0))
        bottom_list.append(bottom)
        
    return top_list, bottom_list
        
def d_fit(top_list,bottom_list):
    '''
    This fits the top and bottom parts of the d equations in order to produce a final d with an error
    np.polyfit doesn't work unless there 5 or more data points i.e. 6 peaks on a graph
    '''
    ds = np.polyfit(bottom_list,top_list,deg=1,cov=True)
    err = np.sqrt(np.diag(ds[1]))
    
    return ds, err


def d_plot(top_list,bottom_list,ds,err,filename):
    '''
    Here we plot the top and bottom lists with the fit and the calculated value of d with corresponding
    errors
    '''
    
    #top_list = top_list/1e-10 #convert to angstroms
    
    
    #fig, ax = plt.subplots
    
    plt.figure(dpi=100)
    plt.plot(bottom_list,top_list,linestyle='none',c='k',marker='o',markerfacecolor='none',\
             markeredgecolor='k',markersize = 8) #plot the raw data
    
    x_min = np.nanmin(bottom_list)
    x_max = np.nanmax(bottom_list)
    x = np.linspace(x_min-(0.1*x_max),1.1*x_max,1000)
    y = ds[0][0]*x+ds[0][1]
    y_max = np.nanmax(ds[0][0])*x_max + ds[0][1]

    plt.plot(x,y,c='k')#plot the straight line fit
    plt.ylabel(r'$\sqrt{(2n+1)\lambda^2}$ ($\mathring{A}$)',fontsize=14)
    plt.xlabel(r'$\sqrt{4(\sin{\vartheta_{n+1}}^2 - \sin{\vartheta_{n}}^2)}$',fontsize=14)

    title = splitext(basename(filename))[0]#uses os.path.basename and os.path.splitext to find the filename from the total path

    plt.title (title, fontsize=14)
    
    plt.text(x_min-(0.1*x_max),y_max, 'd = {:1.1f} +/- {:1.1f}'.format(ds[0][0]/1e-10,err[0]/1e-10)\
             + r' $\mathring{A}$', fontsize=14, bbox=dict(facecolor='white'))
    #        verticalalignment='top')#bbox=props)
    
    plt.tick_params(direction='in',which='both',bottom=True,top=True,left=True,right=True)
 
    plt.tight_layout()
    plt.show()


        



if __name__ == '__main__':
    
    wavelength = 1.54E-10 #CU K alpha xray wavelength

    twotheta_click_step = 0.005#resolution for 2theta movement when placing peak markers
    
    filename = file_finder() #try and find an interactive way to choose filepaths the above root doesn't work
    
    data, labels = datacollector(filename) #gets data using datacollector - change this to yours
    
    window = tk.Tk()
    start= mclass(window,data)
    
    T = tk.Text(window, height=6, width=80) #makes text pane in main window
    
    instructions = 'Save raw xray data with the save button on the toolbar\nx = place marker where mouse\nshift and + = increase marker size\n-'\
    +' = decrease marker size\nup,down,left,right = moves marker\nenter = find thickness when peaks chosen\nesc = close window'
    
    T.pack()
    T.insert(tk.END, instructions) #puts the text in the window
    window.mainloop()
    
    
    coords = np.array(coords)
    top, bottom = theta_convert(coords)
    d,error = d_fit(top,bottom)
    d_plot(top,bottom,d,error,filename)
    
    

    

    
    


