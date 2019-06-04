from tkinter import *
from tkinter import ttk
from adjust_calc import km_to_au,au_to_km
def manual():
    data=[]
    last="C"
    print('Manual entry engaged.')
    while last!="F":
        print('Please enter coordinates (x,y,z)')
        xyz=(float(n) for n in input().split())
        print('Please enter velocity (vx,vy,vz)')
        v=(float(n) for n in input().split())
        print('Please enter mass parameter')
        gm=float(input())
        data.append((xyz,v,gm))
        print('[C]ontinue or [F]inish')
        last=input()
    return data
def from_file():
    pass
def manual_gui(root):
    pass
def data_divide(raw,km=False):
    #JPL data: 21 sig figs
    #This computer: 15 sig figs
    #Excel: 3 sig figs
    n=0
    dat=[]
    #indiv=[]
    xyz=[]
    v=[]
    x=[[float(z) for z in y.split(",")] for y in raw.splitlines()]
    if km:
        x=[km_to_au(y) for y in x]
    for n in range(len(x)*7):
        if n%7<3:
            xyz.append(x[n//7][n%7])
        elif n%7<6:
            v.append(x[n//7][n%7])
        else:
            dat.append([xyz,v,x[n//7][n%7]])
            xyz=[]
            v=[]
    return dat

