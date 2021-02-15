import os
import inspect
import datetime
import subprocess
dossier=os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
os.chdir(dossier)

import calculs as c
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate,Table,TableStyle, Paragraph, Image, PageBreak
from reportlab.lib import colors,utils
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet

width,height=letter


filename="Loadsheet"
title="LOADSHEET"


#les données

charges=c.charges

flightID='HORUS 25'
airportDep="LFOJ"
airportArr="LFOJ"
acRegisteration="F-RBAQ"

basicWeight=83136
basicWeightCG=34.90
C3Weight=1.856

apmWeight=84992
apmCG=34.65
payloadWeight=2260
zfwWeight=87252
zfwCG=30.88

LandingData=[
[85000,30],
[83000,29.5]
]

toFuelWeight=30000
toWeight=117252
towCG=32.5

tripFuel=6000
airdropPayload=0
landingWeight=111252
landingCG=32.81

peopleTO=7
peopleLanding=7

towLimit=''
lwLimit=''

shearCheck="Not Passed"
bendingCheck="Passed"

prepName='SGC SOCHET'
prepFunction='LM'

crewName='CNE POURQUIER'
crewFunction='CAPTAIN'
date=datetime.date.today().strftime('%d/%m/%Y')


#tableau déduits

idTable1=[['Flight ID : '+flightID,'Date : '+date, 'From : '+airportDep]]
idTable2=[['To : '+airportArr,'A/C Registration : '+acRegisteration,'']]

zfwTable=[
['','Weight[kg]','CG[%]'],
['Basic Weight',basicWeight,basicWeightCG],
['Class III Items Weight',C3Weight,'--'],
['A/C Prepared for Mission',apmWeight,apmCG],
['Payload',payloadWeight,'--'],
['Zero Fuel Weight',zfwWeight,zfwCG],
['Take-off Fuel',toFuelWeight,'--'],
['Take-off Weight',toWeight,towCG],
['Trip Fuel',tripFuel,'--'],
['Airdrop Payload',airdropPayload,'--'],
['Landing Weight',landingWeight,landingCG]
]

peopleTable=[
['At take-off : ',peopleTO,'','At landing : ',peopleLanding]
]

limitingData=[
['TOW',towLimit,'','LW',lwLimit]
]

shearbendingData=[
['Shear load checked : ',shearCheck,'','Bending moment checked : ',bendingCheck]
]

#models

def transformation(charges):
    table=[['#',"Weight[kg]","H-arm[m]",'#',"Weight[kg]","H-arm[m]",'#',"Weight[kg]","H-arm[m]"]]
    for i in range(1,9):
        table+=[[i,"","",i+8,"","",i+16,"",""]]
    for j in range(len(charges)):
        charge=charges[j]
        if j<8:
            table[j+1][1]=charge["masse"]
            table[j+1][2]=charge["H_arm"]
        if 7<j<16:
            table[j-7][4]=charge["masse"]
            table[j-7][5]=charge["H_arm"]
        if 15<j<24:
            table[j-15][7]=charge["masse"]
            table[j-15][8]=charge["H_arm"]
    return table


def subtitle(pdf,text,y):
    pdf.setFont('Times-Bold',12)
    pdf.setFillColor(colors.darkblue)
    pdf.rect(70,y-3,460,15)
    pdf.drawCentredString(290,y,text)
    pdf.setFont('Times-Roman',12)
    pdf.setFillColor(colors.black)

def get_image(path, width):
    img = utils.ImageReader(path)
    iw, ih = img.getSize()
    aspect = ih / float(iw)
    return Image(path, width=width, height=(width * aspect))

def boldTable(pdf,data,boldValues):
    n=len(data)
    t=Table(data,colWidths=[280,90,90])
    style=TableStyle([
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('GRID',(0,0),(-1,-1),1,colors.grey),
        ('BACKGROUND',(0,5),(2,5),colors.lightgrey),
        ('BACKGROUND',(0,7),(2,7),colors.lightgrey),
        ('BACKGROUND',(0,10),(2,10),colors.lightgrey)
    ])
    for pos in boldValues:
        style.add('FONT',pos,pos,'Times-Bold')
    t.setStyle(style)
    return t

def miniTable(pdf,data):
    t=Table(data,colWidths=[125,64,80,127,64])
    t.setStyle(TableStyle([
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('GRID',(0,0),(-1,-1),1,colors.grey),
        ('BACKGROUND',(2,0),(2,0),colors.grey),
    ]))
    return t

def signBox(pdf,name,function,date):
    data=[
    ['Document prepared by : '+name,'Function : '+function],
    ['Signed :', 'Date :'+date]]
    t=Table(data,colWidths=[260,200],rowHeights=[20,40])
    t.setStyle(TableStyle([
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('GRID',(0,0),(-1,-1),1,colors.grey),
    ]))
    return t

pdf=canvas.Canvas(filename+'.pdf')
pdf.setTitle(title)

"""
pdf.drawString(100,810,'x100')
pdf.drawString(200,810,'x200')
pdf.drawString(300,810,'x300')
pdf.drawString(400,810,'x400')
pdf.drawString(500,810,'x500')

pdf.drawString(10,100,'y100')
pdf.drawString(10,200,'y200')
pdf.drawString(10,300,'y300')
pdf.drawString(10,400,'y400')
pdf.drawString(10,500,'y500')
pdf.drawString(10,600,'y600')
pdf.drawString(10,700,'y700')
pdf.drawString(10,800,'y800')
"""
table1=Table(idTable1,colWidths=[160,150,150])
table1.setStyle(TableStyle([
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('GRID',(0,0),(-1,-1),1,colors.grey),
    ]))

table2=Table(idTable2,colWidths=[160,240,60])
table2.setStyle(TableStyle([
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('GRID',(0,0),(-1,-1),1,colors.grey),
    ]))

table3=Table(transformation(charges),colWidths=[16,68,68,18,68,68,18,68,68],rowHeights=20)
table3.setStyle(TableStyle([
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('GRID',(0,0),(-1,-1),1,colors.grey),
        ('BACKGROUND',(0,1),(0,8),colors.lightgrey),
        ('BACKGROUND',(3,1),(3,8),colors.lightgrey),
        ('BACKGROUND',(6,1),(6,8),colors.lightgrey)
    ]))

t1=boldTable(pdf,zfwTable,[(1,0),(2,0),(0,5),(0,7),(0,10)])
t2=miniTable(pdf,peopleTable)
t3=miniTable(pdf,shearbendingData)
t4=signBox(pdf,prepName,prepFunction,date)
t5=signBox(pdf,crewName,crewFunction,date)
t6=miniTable(pdf,limitingData)


#contenu
#page 1
Yref=780

pdf.setFont('Times-Roman',24)
pdf.drawCentredString(300,Yref,title)
Yref-=50

table1.wrapOn(pdf, width, height)
table1.drawOn(pdf, 70, Yref)
Yref-=18

table2.wrapOn(pdf, width, height)
table2.drawOn(pdf, 70, Yref)
Yref-=200

table3.wrapOn(pdf, width, height)
table3.drawOn(pdf, 70, Yref)


Yref-=380
if c.typeDeVol=="Tactical":
    get_image("tll1Graph.png",460).drawOn(pdf,70,Yref)
elif c.typeDeVol=="Logistic":
    get_image("lhGraph.png",460).drawOn(pdf,70,Yref)

pdf.showPage()
#page 2

Yref=750

subtitle(pdf,'Weight and balance',Yref)
Yref=Yref-220
t1.wrapOn(pdf, width, height)
t1.drawOn(pdf, 70, Yref)

Yref-=25

subtitle(pdf,'Total People on Board',Yref)
Yref-=23
t2.wrapOn(pdf, width, height)
t2.drawOn(pdf, 70, Yref)

Yref-=20

subtitle(pdf,'Limiting Traffic Load',Yref)
Yref-=23
t6.wrapOn(pdf, width, height)
t6.drawOn(pdf, 70, Yref)

Yref-=20

subtitle(pdf,'Shear load and bending moment',Yref)
Yref-=23
t3.wrapOn(pdf, width, height)
t3.drawOn(pdf, 70, Yref)


Yref-=80

t4.wrapOn(pdf, width, height)
t4.drawOn(pdf, 70, Yref)

Yref-=70

t5.wrapOn(pdf, width, height)
t5.drawOn(pdf, 70, Yref)

Yref-=40



pdf.save()
subprocess.Popen([filename+'.pdf'], shell=True)