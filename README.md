# XRR thin film thickness finder GUI
A Python graphical user interface was developed for quick analysis of metal thin film thicknesses. The interface streamlines the fitting procedures of determining Bragg peaks of XRR data on single layer thin films.

![screen-gif](XRR_GUI_zoomed.gif)

I wrote this GUI as I needed to quickly find the thickness of some metal thin films I had grown using electron beam evaporation in order to calibrate the quartz crystal models which measure the rate of film growth (important to know when you want to grow thicknesses with an accuracy of < 1 Å). Instead of loading the data in to an X-ray fitting software such as GenX or Refl1D and having to build a model, this Python GUI allows you to pick the Bragg peaks in the XRR scan and calculates the thickness from those. The underlying maths is below:

From Bragg's law we know:

(1)&nbsp;   $n\lambda = 2d\sin(\theta_n)$

where $n$ is the diffraction order, $\lambda$ is the wavelength of the X-rays (in this case we use Cu K-alpha -  1.54 Å), $d$ is the thickness of our thin film, $\theta_n$ is the angle at which the X-rays are constructively interferred i.e the centre of the Bragg peak.

If we compare the next peak at $n+1$ the equation becomes:

(2)&nbsp;   $(n+1)\lambda = 2d\sin(\theta_{n+1})$

Subtracting equation 1 and 2 means we can find a relation between $d$ and $\theta$ for $n,n+1, n+2,..., n+n'$ diffraction orders: 

(3)&nbsp;   $(n+1)^2 - n^2 = 4d^2(\sin(\theta_{n+1})^2-\sin(\theta_n)^2)$

Now rearranging for $d$:

(4)&nbsp;   $d=\left (\frac{(2n+1)\lambda^2}{4(\sin(\theta_{n+1})^2-\sin(\theta_n)^2)}\right )^{1/2}$

Therefore in plotting $((2n+1)\lambda^2)^{1/2}$ vs $(4(\sin(\theta_{n+1})^2-\sin(\theta_n)^2))^{1/2}$ we find the gradient is equal to $d$ i.e. the thickness of our thin film

## Benefits
- Can quickly determine thickness of single thin film 
- Takes far less time to setup and use and requires almost no disk space compared to complicated X-ray fitting software
- Allows for user to define Bragg peak centres, rather than using automated Guassian peaks to fit them (such as scipy), which is difficult to achieve when there is a high signal to noise ratio
- Can use save function in toolbars of plots to quickly save figures to any desired location 

## Requirements
- Python 3.6
- matplotlib
- numpy
- tkinter
- wx
- ctypes

## Instructions
- Run main.py
- Choose X-ray data file (theta/2theta scan) using file browser popup
- Click 'plot' button to produce GUI of data
- Instructions on how to identify Bragg peaks and place markers are at top of GUI
- Click 'enter' when identified peaks
- Figure showing calculation of film thickness is produced, this can be saved  



