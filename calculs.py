import pandas as pd
import numpy as np
from math import *

delimitations={
    "A":[11.246,13.232],
    "B":[13.232,15.264],
    "C":[15.264,17.296],
    "D":[17.296,19.328],
    "E":[19.328,22.884],
    "F":[22.884,24.916],
    "G":[24.916,26.948],
    "H":[26.948,28.98],
    "J":[28.98,31.472],
    "K":[31.472,33.964]
    }

dicoLettres={
    "A":0,
    "B":1,
    "C":2,
    "D":3,
    "F":4,
    "G":5,
    "H":6,
    "J":7,
    "K":8
    }


fullDicoLettres={
    "A":0,
    "B":1,
    "C":2,
    "D":3,
    "E":4,
    "F":5,
    "G":6,
    "H":7,
    "J":8,
    "K":9
    }

dicoClass2={
    "blindage":0,
    "crane":1,
    "fullMedevac":2,
    "hdu":3}


class CalculsLimitation():
    #ci-dessous, les constantes
    def __init__(self):
        self.typeDeVol="Logistic"

        self.apm=80000
        self.apmcg=30
        self.fuelWeight=10000
        self.fuel_conso=0
        self.version="aucune"
        self.nb_bloc=0
        self.remplissage_shear=True
        self.itemII=[1,0,0,0]
        self.poids_equipe=600
        self.ShearLoad=[0]*9
        self.maximumShearLoad=[0]*9
        self.BendingMoment=[0]*9
        self.maximumBendingMoment=[0]*9
        self.sieges=[]
        self.charges=[]
        self.poidsSectionsInit=[0]*9

        self.ZFW=0
        self.ZFWCG=0

        self.CheckPointIndex=pd.read_csv(r"CheckPointIndex.csv", sep=";")

        #typeDeVol soit Tactical soit Logistique
        #remplissage_shear vaut False si on veut rentré les shear and bendng à vide et True sinon



     #fonctions utiles
    def calculs(self):
        self.limit()
        self.charges=self.separation(self.charges)
        self.ZFW=self.zfw(self.charges)
        self.ZFWCG=self.zfwcg(self.charges)
        self.TOW=self.tow(self.charges)
        self.TOWCG=self.towcg(self.charges, self.typeDeVol)
        self.shear_lim=self.respectsShear(self.charges)
        self.bending_lim=self.respectsBending(self.charges)


    def limit(self):
        typeDeVol=self.typeDeVol
        if self.remplissage_shear:
            item=self.itemII
            poids_equipe=self.poids_equipe

            class2Shear=pd.read_csv("class2Shear.csv",sep=";")
            class2Bending=pd.read_csv("class2Bending.csv",sep=";")

            if typeDeVol=="Tactical":
                maxShear=pd.read_csv("tll1Shear.csv",sep=";")
                maxBending=pd.read_csv("tll1Bending.csv",sep=";")

            elif typeDeVol=="Logistic":
                maxShear=pd.read_csv("lhShear.csv",sep=";")
                maxBending=pd.read_csv("lhBending.csv",sep=";")

            pen_bend=item[0]*class2Bending["blindage"]+item[1]*class2Bending["crane"]+item[2]*class2Bending["fullMedevac"]+item[3]*class2Bending["hdu"]
            pen_shear=item[0]*class2Shear["blindage"]+item[1]*class2Shear["crane"]+item[2]*class2Shear["fullMedevac"]+item[3]*class2Shear["hdu"]
            for i in range(21,39):
                maxShear[str(i)]+=pen_shear
                maxBending[str(i)]+=pen_bend

            self.maximumShearLoad=maxShear
            self.maximumBendingMoment=maxBending
            self.ShearLoad=[poids_equipe]*4+[0]*5
            self.poidsSectionsInit=[poids_equipe]+[0]*8
            self.BendingMoment=[abs(deltaIndex(poids_equipe,11.246))]*4+[0]*5



    def isIn(self,point,interval):
        return (point>=interval[0] and point<=interval[1])

    def isInSection(self, h_armes):
        sectionObjet=""
        for cle,interval in delimitations.items():
            if self.isIn(h_armes,interval):
                sectionObjet=cle
                break
        return sectionObjet

    def indexFuel(self, poids,typeDeVol):
        lhFuelIndex=np.array(pd.read_csv("fuelIndex.csv",sep=";"))
        index,typeVol=0,0
        if typeDeVol=="Tactical":typeVol=2
        elif typeDeVol=="Logistic":typeVol=1
        else:raise ValueError('Type de vol non reconnu')
        for fuelData in lhFuelIndex:
            if abs(fuelData[0]-poids)<=250:
                index=fuelData[typeVol]
                break
        return index



    #sépare un objet sur plusieurs sections

    def repartition(self,h_armes,longueur,poids):
        newCharges=[]
        debutSection=self.isInSection(h_armes-longueur/2)
        finSection=self.isInSection(h_armes+longueur/2)
        for cle,valeur in fullDicoLettres.items():
            if debutSection<cle<finSection:
                newLongueur=(delimitations[cle][1]-delimitations[cle][0])
                newpoids=poids*newLongueur/longueur
                newh_armes=delimitations[cle][0]+newLongueur/2
                newCharges.append({
                "h_armes":newh_armes,"longueur":newLongueur,"poids":newpoids})
            elif cle==debutSection:
                newLongueur=delimitations[cle][1]-(h_armes-longueur/2)
                newpoids=poids*newLongueur/longueur
                newh_armes=delimitations[cle][1]-newLongueur/2
                newCharges.append({"h_armes":newh_armes, "longueur": newLongueur, "poids":newpoids})
            elif cle==finSection:
                newLongueur=h_armes+longueur/2-delimitations[cle][0]
                newpoids=poids*newLongueur/longueur
                newh_armes=delimitations[cle][0]+newLongueur/2
                newCharges.append({"h_armes": newh_armes, "longueur": newLongueur,"poids": newpoids})
        return newCharges

    def separation(self, charges):
        newChargesList=[]
        for charge in charges:
            h_armes,longueur,poids=charge["h_armes"],charge["longueur"],charge["poids"]
            section=self.isInSection(h_armes)
            if ((h_armes+longueur/2)>delimitations[section][1] or (h_armes-longueur/2)<delimitations[section][0]):
                newChargesList+=self.repartition(h_armes,longueur,poids)
            else:newChargesList+=[charge]
        return newChargesList

    #calcul des valeurs recherchées

    def zfw(self,charges):
        return sum([objet["poids"] for objet in charges])+self.apm

    def zfwcg(self,charges):
        lIndex=[deltaIndex(objet["poids"],objet["h_armes"]) for objet in charges]
        basicIndex=sum(lIndex)+basicIndex2(self.apm,self.apmcg)
        return cg(self.zfw(charges),basicIndex)

    def tow(self,charges):
        return self.fuelWeight+self.zfw(charges)

    def towcg(self, charges, typeDeVol):
        fuelIndex=self.indexFuel(self.fuelWeight,typeDeVol)
        basicIndex_zfw=basicIndex2(self.zfw(charges),self.zfwcg(charges))
        deltaIndex_fuel=deltaIndex(self.fuelWeight,h_armes(self.fuelWeight, fuelIndex))
        return cg(self.tow(charges),basicIndex_zfw+deltaIndex_fuel)


    #shear and bending

    def respectsShear(self, charges):
        poidsSections=self.poidsSectionsInit
        for charge in charges:
            if self.isInSection(charge["h_armes"])!="E":
                poidsSections[dicoLettres[self.isInSection(charge["h_armes"])]]+=charge["poids"]
        self.poidsSections=poidsSections
        for i in range(1,4):
            poidsSections[i]+=poidsSections[i-1]
        for i in range(7,3,-1):
            poidsSections[i]+=poidsSections[i+1]
        poidsSections+=self.ShearLoad
        #on a besoin du poids de chaque section pour les bending

        try:
            maximumShear=np.array(self.maximumShearLoad[str(round(self.ZFWCG))])
            diff=[x-y for x,y in zip(maximumShear, poidsSections)]
            return np.all(np.array(diff) >= 0)
        except:
            return False







    def respectsBending(self, charges):
        indexSections=[0]*9
        for charge in charges:
            if self.isInSection(charge["h_armes"])!="E":
                indexSections[dicoLettres[self.isInSection(charge["h_armes"])]]+=abs(deltaIndex(charge["poids"],charge["h_armes"]))
        for i in range(1,4):
            indexSections[i]+=indexSections[i-1]
        for i in range(7,3,-1):
            indexSections[i]+=indexSections[i-1]
        indexSections+=self.BendingMoment
        print("re")
        print(indexSections)
        for i in range(9):
            indexSections[i]=indexSections[i]-self.Check_point_index(i)
        print(indexSections)

        try:
            maximumBending=np.array(self.maximumBendingMoment[str(round(self.ZFWCG))])
            diff=[x-y for x,y in zip(maximumBending, indexSections)]
            return np.all(np.array(diff) >= 0)
        except:
            return False


    def Check_point_index(self, i):
        masse=self.poidsSections[i]
        masse=approx_masse(masse)
        #print(i,masse)
        try:
            index=self.CheckPointIndex[self.CheckPointIndex["masse"] == masse][str(i+1)]
            index=np.array(index)[0]
            #print(index)
            return index
        except:
            #print("non")
            return 0






#relations données
def deltaIndex(poids,h_armes):
    return poids*(h_armes-22.0083)/100

def cg(poids,basicIndex):
    return ((basicIndex-600)*10000)/(poids*5.671)+30

def basicIndex1(poids,h_armes):
    return poids*(h_armes-22.0083)/100+600

def basicIndex2(poids,cg):
    return poids*(cg*5.671-170.13)/10000+600

def h_armes(poids,basicIndex):
    return 100*(basicIndex-600)/poids+22.0083

def approx_masse(m):
    reste=m%200
    if reste>=100:
        m=m-reste+200
        return m
    else:
        m=m-reste
        return m


#calc=CalculsLimitation(18000, 30, 15000, "Tactical", [{"poids":120, "h_armes":22, "longueur":0.2}, {"poids":2500, "h_armes":30, "longueur":7}], [True, 500, [1,0,0,1]] )
#print(calc.TOWCG)


#calc=CalculsLimitation()
#calc.limit()
#calc.calculs()












