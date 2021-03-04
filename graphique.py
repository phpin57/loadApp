import numpy as np
import matplotlib.pyplot as plt
import json

import os
import inspect

dossier=os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
os.chdir(dossier)

class Graphique():
    def __init__(self):
        self.base()
        self.test=True

    def base(self): #base du graphique (lignes grises + échelle)
        self.fig = plt.figure(figsize=(10,6))

        #création de la base du graphique (échelle à gauche + en bas)
        self.ax1 = self.fig.add_subplot()
        plt.xlim(15,43)
        plt.ylim(70,150)
        plt.xlabel("% MAC")
        plt.ylabel("Weight (x1000kg)")


        #ajout axe du haut
        self.ax2 = self.ax1.twiny()

        echelle=([((i-600)*10000/(70000*5.671)+30) for i in range(100,1200,100)])
        self.ax2.set_xlim(self.ax1.get_xlim())
        self.ax2.set_xticks(echelle)
        self.ax2.set_xticklabels([i for i in range(100,1200,100)])
        plt.xlabel("Balance Scale (I.U.)")

        with open("graph.JSON","r") as mj: #import des données des lignes grises
            lignes = json.load(mj)

        for ligne in lignes:
            self.ax1.plot(ligne[0], ligne[1], color="grey", linewidth=0.5, linestyle="-")


    def enveloppe(self, calculs):   #enveloppe de vol (trait épais noir)
        if calculs.typeDeVol=="LH":
            cg=np.array([23,24.4,27,35.8,36.74,23,22.07,20,20,22.32,39,39,39,39.5,39.5,37.44,37.06,36.1,35.8,36.74,37.11,39,37.11,27.67,22.07])
            m=np.array([123,139.5,141,141,123,123,114,98,90,78,78,94,78,78,93,117.1,123,141,141,123,117.1,94,117.1,117.1,114])
            cg_70=m*1000*(cg*5.671-170.13)/(70000*5.671)+30
            self.ax1.plot(cg_70, m, color="black", linewidth=2.0, linestyle="-")
        else :
            cg=np.array([23,24.4,27,35.8,36.74,23,22.07,20,20,22.32,39,39,39,39.5,39.5,37.44,37.06,36.1,35.8,36.74,37.11,39,37.11,27.67,22.07])
            m=np.array([123,139.5,141,141,123,123,114,98,90,78,78,94,78,78,93,117.1,123,141,141,123,117.1,94,117.1,117.1,114])
            cg_70=m*1000*(cg*5.671-170.13)/(70000*5.671)+30
            self.ax1.plot(cg_70, m, color="black", linewidth=2.0, linestyle="-")


    def fuel(self, calculs): #ligne rouge (CG=f(conso))
        poids=[calculs.ZFW+calculs.fuelWeight]
        bi_fuel=[calculs.ZFW_ind+calculs.indexFuel(calculs.fuelWeight, calculs.typeDeVol)]

        debut=int(calculs.fuelWeight-int(calculs.fuelWeight)%200)
        for masse in range(debut, 0, -200):
            poids.append(calculs.ZFW+masse)
            bi_fuel.append(calculs.ZFW_ind+calculs.indexFuel(masse,calculs.typeDeVol))
        poids.append(calculs.ZFW)
        bi_fuel.append(calculs.ZFW_ind)

        poids=np.array(poids)/1000
        bi_fuel=np.array(bi_fuel)
        cg_fuel_70=(bi_fuel-600)*10000/(70000*5.761)+30

        self.ax1.plot(cg_fuel_70, poids, color="red", linewidth=2, linestyle="-")
        #détermination des coordonnée du point de landing
        cg_plot_lwcg=calculs.ZFW_ind+calculs.indexFuel(calculs.fuelWeight-calculs.fuel_conso,calculs.typeDeVol)
        cg_plot_lwcg=(cg_plot_lwcg-600)*10000/(70000*5.761)+30
        self.ax1.scatter(cg_fuel_70[0],poids[0],marker="o",color="blue",label="TOW")
        self.ax1.scatter(cg_plot_lwcg,calculs.LW/1000,marker="o",label="LW")
        self.ax1.scatter(cg_fuel_70[-1],calculs.ZFW/1000,marker="o",label="ZFW")

        self.ax1.legend()



    def maj(self, calculs, feuille):  #remplace le graphique en cas de changement
        self.enveloppe(calculs)
        self.fuel(calculs)


        if self.test:
            plt.savefig("graph.png")
            feuille.ids["graphe"].source="graph.png"
        else:
            plt.savefig("graph.jpeg")
            feuille.ids["graphe"].source="graph.jpeg"
        self.test=(not self.test)
