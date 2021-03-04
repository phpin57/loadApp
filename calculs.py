import os
import inspect
#dossier=os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
#os.chdir(dossier)





import pandas as pd
import numpy as np
import json
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

h_armes_dico={
    "1":12.239,
    "2":14.248,
    "3":16.28,
    "4":18.312,
    "5":23.9,
    "6":25.932,
    "7":27.948,
    "8":30.226,
    "9":32.718,
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

#entré de l'appli provenant de apmCalc
        self.apm=80000
        self.apmcg=30
        self.li_apm=1000
        self.fuelWeight=10000
        self.fuel_conso=0
        self.maximumShearLoad=[0]*9
        self.maximumBendingMoment=[0]*9
        self.BendingMomentInit=[0]*9
        self.poidsSectionsInit=[0]*9
        self.typeDeVol=""
        self.version_sieges=""
        self.nb_bloc=""

#entré des charges provenant de main
        self.sieges=[]
        self.colis=[]
        self.charges=self.colis+self.sieges

#données de sortie à calculer
        self.ZFW=0
        self.ZFWCG=0
        self.TOW=0
        self.TOWCG=0
        self.LW=0
        self.LWCG=0
        self.ZFW_ind=0
        self.TOW_ind=0
        self.LW_ind=0
        self.LI=0
        self.masse_larguee=0
        self.shear_lim=False
        self.bending_lim=False

#ouverture des tableaux utiles
        self.CheckPointIndex=pd.read_csv(r"CheckPointIndex.csv", sep=";", index_col = 0)



     #fonctions utiles
    def calculs(self):
        self.charges=self.sieges+self.colis

        self.charges=self.separation(self.charges)
        self.ZFW=self.zfw(self.charges)
        self.ZFWCG=self.zfwcg(self.charges)
        self.TOW=self.ZFW+self.fuelWeight
        self.TOWCG=self.towcg(self.typeDeVol, self.fuelWeight)
        self.LW=self.lw()
        self.LWCG=self.lwcg(self.typeDeVol)
        self.LI=self.li()
        self.shear_lim=self.respectsShear(self.charges)
        self.bending_lim=self.respectsBending(self.charges)

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
        if typeDeVol=="TLL1" or typeDeVol=="TLL2":typeVol=2
        elif typeDeVol=="LH" or typeDeVol=="LN1":typeVol=1
        else:raise ValueError('Type de vol non reconnu')
        for fuelData in lhFuelIndex:
            if abs(fuelData[0]-poids)<=250:
                index=fuelData[typeVol]
                break
        return index



    #sépare un objet sur plusieurs sections

    def repartition(self,h_armes,longueur,poids, y_arm):
        newCharges=[]
        debutSection=self.isInSection(h_armes-longueur/2)
        finSection=self.isInSection(h_armes+longueur/2)
        for cle,valeur in fullDicoLettres.items():
            if debutSection<cle<finSection:
                newLongueur=(delimitations[cle][1]-delimitations[cle][0])
                newpoids=poids*newLongueur/longueur
                newh_armes=delimitations[cle][0]+newLongueur/2
                newCharges.append({
                "h_armes":newh_armes,"y_arm":y_arm,"longueur":newLongueur,"poids":newpoids})
            elif cle==debutSection:
                newLongueur=delimitations[cle][1]-(h_armes-longueur/2)
                newpoids=poids*newLongueur/longueur
                newh_armes=delimitations[cle][1]-newLongueur/2
                newCharges.append({"h_armes":newh_armes,"y_arm":y_arm, "longueur": newLongueur, "poids":newpoids})
            elif cle==finSection:
                newLongueur=h_armes+longueur/2-delimitations[cle][0]
                newpoids=poids*newLongueur/longueur
                newh_armes=delimitations[cle][0]+newLongueur/2
                newCharges.append({"h_armes": newh_armes,"y_arm":y_arm, "longueur": newLongueur,"poids": newpoids})
        return newCharges

    def separation(self, charges):
        newChargesList=[]
        for charge in charges:
            h_armes,longueur,poids,y_arm=charge["h_armes"],charge["longueur"],charge["poids"],charge["y_arm"]
            section=self.isInSection(h_armes)
            if ((h_armes+longueur/2)>delimitations[section][1] or (h_armes-longueur/2)<delimitations[section][0]):
                newChargesList+=self.repartition(h_armes,longueur,poids,y_arm)
            else:newChargesList+=[charge]
        return newChargesList

    #calcul des valeurs recherchées

    def zfw(self,charges):
        return sum([objet["poids"] for objet in charges])+self.apm
    def zfwcg(self,charges):
        lIndex=[deltaIndex(objet["poids"],objet["h_armes"]) for objet in charges]
        basicIndex=sum(lIndex)+basicIndex2(self.apm,self.apmcg)
        self.ZFW_ind=basicIndex
        return cg(self.ZFW,basicIndex)

    def tow(self,charges):
        return self.fuelWeight+self.zfw(charges)

    def towcg(self, typeDeVol, fuelWeight):
        fuelIndex=self.indexFuel(fuelWeight,typeDeVol)
        #basicIndex_zfw=basicIndex2(self.zfw(charges),self.zfwcg(charges))
        self.TOW_ind=self.ZFW_ind+fuelIndex
        return cg(self.TOW,self.TOW_ind)

    def lw(self):
        self.masse_larguee_calc()
        try:
            fuel_conso=int(self.fuel_conso)
            return self.TOW - fuel_conso - self.masse_larguee
        except:
            self.fuel_conso=""
            return ""

    def masse_larguee_calc(self):
        self.masse_larguee=0
        for charge in self.charges:
            try:
                if int(charge["drop"])!=0:
                    self.masse_larguee+=charge["poids"]
            except:
                pass





    def lwcg(self, typeDeVol):
        try:
            fuel_conso=int(self.fuel_conso)
            fuel=self.fuelWeight-fuel_conso
            fuelIndex=self.indexFuel(fuel, typeDeVol)
            self.LW_ind=self.ZFW_ind+fuelIndex
            return cg(self.LW,self.LW_ind)
        except:
            return ""

    def li(self):
        self.LI=self.li_apm
        for charge in self.charges:
            self.LI+=charge["y_arm"]*charge["poids"]
        return self.LI

    #shear and bending

    def respectsShear(self, charges):
        poidsSections=self.poidsSectionsInit.copy()
        for charge in charges:
            if self.isInSection(charge["h_armes"])!="E":
                poidsSections[dicoLettres[self.isInSection(charge["h_armes"])]]+=charge["poids"]
        #on a besoin du poids de chaque section pour les bending
        self.poidsSections=poidsSections.copy()
        for i in range(1,4):
            poidsSections[i]+=poidsSections[i-1]
        for i in range(7,3,-1):
            poidsSections[i]+=poidsSections[i+1]

        try:
            maximumShear=np.array(self.maximumShearLoad[str(round(self.ZFWCG))])
            self.maximumShearRes=maximumShear.copy()
            self.ShearRes=poidsSections.copy()
            diff=maximumShear- np.array(poidsSections)
            return np.all(np.array(diff) >= 0)
        except:
            return False


    def respectsBending(self, charges):
        indexSections=self.BendingMomentInit.copy()
        for charge in charges:
            if self.isInSection(charge["h_armes"])!="E":
                indexSections[dicoLettres[self.isInSection(charge[ "h_armes"])]] += abs(deltaIndex(charge["poids"],charge["h_armes"]))
        for i in range(1,4):
            indexSections[i]=(indexSections[i]+indexSections[i-1])
        for i in range(7,3,-1):
            indexSections[i]=(indexSections[i]+indexSections[i+1])
        for i in range(9):
            indexSections[i]=(indexSections[i]-self.Check_point_index(i)) *100


        try:
            maximumBending=np.array(self.maximumBendingMoment[str(round(self.ZFWCG))])
            self.maximumBendingRes=maximumBending.copy()
            self.BendingRes=indexSections.copy()
            diff=maximumBending- np.array(indexSections)
            return np.all(np.array(diff) >= 0)
        except:
            return False


    def Check_point_index(self, i):
        masse=self.poidsSections[i]
        masse1=int(masse-masse%200)
        masse2=int(masse1+200)
        try:
            index1=self.CheckPointIndex.loc[masse1,str(i+1)]
            index2=self.CheckPointIndex.loc[masse2,str(i+1)]

            di=index2-index1
            index=index1 + (masse%200)*di/200
            return index

        except:
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


def limitation(typeDeVol):
    if typeDeVol=="TLL1":
        maxShear=pd.read_csv("tll1Shear.csv",sep=";")
        maxBending=pd.read_csv("tll1Bending.csv",sep=";")

    elif typeDeVol=="LH":
        maxShear=pd.read_csv("lhShear.csv",sep=";")
        maxBending=pd.read_csv("lhBending.csv",sep=";")
    return maxShear,maxBending



class APMCalc():
    def __init__(self):
        self.sb_bool=True
        self.rapide_bool=False
        self.precis_bool=False

#données de sortie de la classe qui permettent de faire les calculs avec les charges supplémentaires
        self.maximumShearLoad=[0]*9
        self.maximumBendingMoment=[0]*9
        self.poidsSectionsInit=[0]*9 #avec les items de classe III
        self.BendingMomentInit=[0]*9 #important pour les items de classe III qui sont en cockpit
        self.APM=0
        self.APMCG=0
        self.LI=0
        self.fuel=0
        self.conso=0
        self.typeDeVolEntry=""
        #à aouter
        self.nb_bloc=""
        self.version_sieges=""

    def extraction_data(self, setup, calculs):
        if setup.methode_bool:
            self.shear(setup)
        elif (not setup.methode_bool) and setup.maniere_bool:
            self.rapide(setup)
        elif (not setup.methode_bool) and (not setup.maniere_bool):
            self.precis(setup)

        self.export_data(calculs)

    def export_data(self, calculs):
        calculs.apm=self.APM
        calculs.apmcg=self.APMCG
        calculs.li_apm=self.LI
        calculs.fuelWeight=self.fuel
        calculs.fuel_conso=self.conso
        calculs.maximumShearLoad=self.maximumShearLoad
        calculs.maximumBendingMoment=self.maximumBendingMoment
        calculs.poidsSectionsInit=self.poidsSectionsInit
        calculs.typeDeVol=self.typeDeVolEntry
        calculs.BendingMomentInit=self.BendingMomentInit


        calculs.nb_bloc=self.nb_bloc
        calculs.version_sieges=self.version_sieges


    def ouverture_limitation(self, type_vol):
        shear=pd.read_csv(type_vol.lower()+"Shear.csv",sep=";")
        bending=pd.read_csv(type_vol.lower()+"Bending.csv",sep=";")
        return shear,bending



    def shear(self, setup):
        self.ShearLoadEntry=[0]*9
        self.maximumShearLoadEntry=[0]*9
        self.BendingMomentEntry=[0]*9
        self.maximumBendingMomentEntry=[0]*9

        self.LI=float(setup.ids["LI_mprs"].text)
        self.fuel=float(setup.ids["fuel_mprs"].text)
        self.conso=float(setup.ids["conso_mprs"].text)
        self.typeDeVolEntry=setup.ids["vol_mprs"].text

        self.APM=float(setup.ids["APMentry"].text)
        self.APMCG=float(setup.ids["CGentry"].text)
        self.typeDeVol=setup.ids["type_vol_entry"].text

        for i in range(9):
            self.ShearLoadEntry[i]=float(setup.ids["shear"+str(i+1)].text)
            self.maximumShearLoadEntry[i]=float(setup.ids["shear_lim"+str(i+1)].text)
            self.BendingMomentEntry[i]=float(setup.ids["bending"+str(i+1)].text)
            self.maximumBendingMomentEntry[i]=float(setup.ids["bending_limit"+str(i+1)].text)



        maxShear,maxBending=self.ouverture_limitation(self.typeDeVol)
        shear=maxShear[str(round(self.APMCG))]
        self.BendingMomentInit=self.BendingMomentEntry
        pen_shear=np.array(self.maximumShearLoadEntry)-np.array(shear)
        pen_shear=pd.DataFrame(pen_shear, columns = ['A'])
        bending=maxBending[str(round(self.APMCG))]
        pen_bend=np.array(self.maximumBendingMomentEntry)-np.array(bending)
        pen_bend=pd.DataFrame(pen_bend, columns = ['A'])
        maxShear,maxBending=self.ouverture_limitation(self.typeDeVolEntry)
        for i in range(21,39):
            maxShear[str(i)]+=pen_shear["A"]
            maxBending[str(i)]+=pen_bend["A"]
        self.maximumShearLoad=maxShear
        self.maximumBendingMoment=maxBending
        self.poidsSectionsInit=self.ShearLoadEntry.copy()

        for i in range(3,0,-1):
            self.poidsSectionsInit[i]-=self.poidsSectionsInit[i-1]
        for i in range(4,8):
            self.poidsSectionsInit[i]-=self.poidsSectionsInit[i+1]

        manual_sh=([self.ShearLoadEntry, self.maximumShearLoadEntry, self.BendingMomentEntry, self.maximumBendingMomentEntry]).copy()
        with open("manual shear.JSON","w") as mj:
            json.dump(manual_sh, mj)


    def rapide(self, setup):
        self.APM=float(setup.ids["APM"].text)
        self.APMCG=float(setup.ids["APMCG"].text)
        self.LI=float(setup.ids["LI"].text)
        self.fuel=float(setup.ids["fuel"].text)
        if  setup.ids["fuel_conso"].text!="":
            self.conso=float(setup.ids["fuel_conso"].text)
        self.typeDeVolEntry=setup.ids["spinner_vol"].text
        self.version_sieges=setup.ids["version_lat"].text
        self.nb_bloc=setup.ids["nb_bloc"].text
        item=[setup.ids["chk_blindage"].active, setup.ids["chk_medevac"].active, setup.ids["chk_hdu"].active, setup.ids["chk_crane"].active]

        item=[(1 if bool else 0) for bool in item]
        self.nb_pil=float(setup.ids["nb_pil"].text)
        self.vrac=float(setup.ids["vrac"].text)
        self.cargo_door=float(setup.ids["cargo_door"].text)

        #partie determination des données
        self.poidsSectionsInit=[0]*9
        self.poidsSectionsInit[0]+=120*self.nb_pil+self.vrac/2
        self.poidsSectionsInit[1]+=self.vrac/2
        self.poidsSectionsInit[-1]+=self.cargo_door

        self.BendingMomentInit[0]=(120*self.nb_pil*(22.0083-7.28) + self.vrac*(22.0083-12.5)/2)/100
        self.BendingMomentInit[1]=(self.vrac*(22.0083-14)/2)/100
        self.BendingMomentInit[-1]=(self.cargo_door*(37-22.0083))/100

        maxShear,maxBending=self.ouverture_limitation(self.typeDeVolEntry)
        class2Shear=pd.read_csv("class2Shear.csv",sep=";")
        class2Bending=pd.read_csv("class2Bending.csv",sep=";")

        pen_bend=item[0]*class2Bending["blindage"]+item[1]*class2Bending["crane"]+item[2]*class2Bending["fullMedevac"]+item[3]*class2Bending["hdu"]
        pen_shear=item[0]*class2Shear["blindage"]+item[1]*class2Shear["crane"]+item[2]*class2Shear["fullMedevac"]+item[3]*class2Shear["hdu"]
        for i in range(21,39):
            maxShear[str(i)]+=pen_shear
            maxBending[str(i)]+=pen_bend

        self.maximumShearLoad=maxShear
        self.maximumBendingMoment=maxBending



    def precis(self, setup):
        self.BW=float(setup.ids["BW"].text)
        self.BWCG=float(setup.ids["BWCG"].text)
        self.LI=float(setup.ids["LI"].text)
        self.APM=self.BW
        self.fuel=float(setup.ids["fuel_precis"].text)
        self.conso=float(setup.ids["conso_precis"].text)
        self.typeDeVolEntry=setup.ids["vol_precis"].text

        penalisation=np.array([0]*18)
        #traitement des classe II
        for item in setup.liste_itemII:
            if item[0].active:
                penalisation+=item[1]

        item3=np.array([0.]*16)
        for item in setup.liste_itemIII:
            if item[0].active:
                print(item[1])
                print(len(item[1]))
                print(type(item[1]))
                item3+=item[1]

        self.poidsSectionsInit=item3[1:10].copy()
        for i in range(9):
            self.BendingMomentInit[i]=abs(self.poidsSectionsInit[i]*(22.0087-h_armes_dico[str(i+1)])/100)
        self.BendingMomentInit[0]+=item3[11]
        self.BendingMomentInit[-1]+=item3[12]

        self.poidsSectionsInit[0]+=item3[0]
        self.poidsSectionsInit[-1]+=item3[10]

        self.APM+=item3[14]
        delta_indexIII=item3[15]
        self.LI+=item3[13]

        basicIndex=delta_indexIII+basicIndex2(self.BW,self.BWCG)
        self.APMCG=cg(self.APM,basicIndex)

        maxShear,maxBending=self.ouverture_limitation(self.typeDeVolEntry)
        pen_shear=pd.DataFrame(penalisation[:9], columns = ['A'])
        pen_bend=pd.DataFrame(penalisation[9:], columns = ['A'])

        for i in range(21,39):
            maxShear[str(i)]+=pen_shear["A"]
            maxBending[str(i)]+=pen_bend["A"]
        self.maximumShearLoad=maxShear
        self.maximumBendingMoment=maxBending



class Bilbliotheque():
    def __init__(self):
        self.save_list=[]
        self.save={}
        self.nom_different=False
        self.changement=False

        try:
            with open("bibli data.JSON","r") as mj2:
                self.save_list = json.load(mj2)
        except:
            self.save_list =[]

    def liste_saved(self):
        liste=[]
        for save in self.save_list:
            liste.append(save["nom"])
        return liste


    def decodage(self, save, setup):
        if save["type setup"]=="shear":
            self.decode_shear(save, setup)
        elif save["type setup"]=="rapide":
            self.decode_rapide(save, setup)
        elif save["type setup"]=="precis":
            self.decode_precis(save, setup)

    def codage(self, setup):
        save=self.creation_save(setup)
        self.save_list.append(save.copy())
        with open("bibli data.JSON","w") as mj:
            json.dump(self.save_list, mj)

    def creation_save(self, setup):
        if setup.methode_bool:
            save=self.code_shear({}, setup)
        elif setup.maniere_bool:
            save=self.code_rapide({}, setup)
        else:
            save=self.code_precis({}, setup)
        return save.copy()

    def decode_precis(self, save, setup):
        (setup.ids["BW"].text)=save["BW"]
        (setup.ids["BWCG"].text)=save["BWCG"]
        (setup.ids["LI"].text)=save["LI"]
        (setup.ids["fuel_precis"].text)=save["fuel"]
        (setup.ids["conso_precis"].text)=save["conso"]
        setup.ids["vol_precis"].text=save["type de vol"]
        for i in range(len(setup.liste_itemII)):
            setup.liste_itemII[0].active=save["intemII"][i]
        for i in range(len(setup.liste_itemIII)):
            setup.liste_itemIII[0].active=save["intemIII"][i]

        setup.ids["methode"].value=1
        setup.ids["maniere"].value=1
        setup.ids["classe"].value=0


    def decode_shear(self, save, setup):
        setup.ids["LI_mprs"].text=save["LI"]
        setup.ids["fuel_mprs"].text=save["fuel"]
        setup.ids["conso_mprs"].text=save["conso"]
        setup.ids["vol_mprs"].text=save["vol"]

        setup.ids["APMentry"].text=save["APM"]
        setup.ids["CGentry"].text=save["APMCG"]
        setup.ids["type_vol_entry"].text=save["type de vol"]

        for i in range(9):
            setup.ids["shear"+str(i+1)].text=save["ShearLoadEntry"][i]
            setup.ids["shear_lim"+str(i+1)].text=save["maximumShearLoadEntry"][i]
            setup.ids["bending"+str(i+1)].text=save["BendingMomentEntry"][i]
            setup.ids["bending_limit"+str(i+1)].text=save["maximumBendingMomentEntry"][i]

        setup.ids["methode"].value=0



    def decode_rapide(self, save, setup):
        (setup.ids["APM"].text)=save["APM"]
        (setup.ids["APMCG"].text)=save["APMCG"]
        (setup.ids["LI"].text)=save["LI"]
        (setup.ids["fuel"].text)=save["fuel"]
        (setup.ids["fuel_conso"].text)=save["conso"]
        setup.ids["spinner_vol"].text=save["type de vol"]
        setup.ids["version_lat"].text=save["version_lat"]
        setup.ids["nb_bloc"].text=save["nb_bloc"]
        [setup.ids["chk_blindage"].active, setup.ids["chk_medevac"].active, setup.ids["chk_hdu"].active, setup.ids["chk_crane"].active]=save["item"]
        (setup.ids["nb_pil"].text)=save["nb_pil"]
        (setup.ids["vrac"].text)=save["vrac"]
        (setup.ids["cargo_door"].text)=save["cargo_door"]

        setup.ids["methode"].value=1
        setup.ids["maniere"].value=0
        setup.ids["classe"].value=0


    def code_rapide(self, save, setup):
        save["type setup"]="rapide"
        save["nom"]=self.nom

        save["APM"]=(setup.ids["APM"].text)
        save["APMCG"]=(setup.ids["APMCG"].text)
        save["LI"]=(setup.ids["LI"].text)
        save["fuel"]=(setup.ids["fuel"].text)
        save["conso"]=(setup.ids["fuel_conso"].text)
        save["type de vol"]=setup.ids["spinner_vol"].text
        save["version_lat"]=setup.ids["version_lat"].text
        save["nb_bloc"]=setup.ids["nb_bloc"].text
        save["item"]=[setup.ids["chk_blindage"].active, setup.ids["chk_medevac"].active, setup.ids["chk_hdu"].active, setup.ids["chk_crane"].active]
        save["nb_pil"]=(setup.ids["nb_pil"].text)
        save["vrac"]=(setup.ids["vrac"].text)
        save["cargo_door"]=(setup.ids["cargo_door"].text)

        return save

    def code_precis(self, save, setup):
        save["type setup"]="precis"
        save["nom"]=self.nom

        save["BW"]=(setup.ids["BW"].text)
        save["BWCG"]=(setup.ids["BWCG"].text)
        save["LI"]=(setup.ids["LI"].text)
        save["fuel"]=(setup.ids["fuel_precis"].text)
        save["conso"]=(setup.ids["conso_precis"].text)
        save["type de vol"]=setup.ids["vol_precis"].text
        save["intemII"]=[{}]*len(setup.liste_itemII)
        for i in range(len(setup.liste_itemII)):
            save["intemII"][i]=setup.liste_itemII[0][0].active
        save["intemIII"]=[{}]*len(setup.liste_itemIII)
        for i in range(len(setup.liste_itemIII)):
            save["intemIII"][i]=setup.liste_itemIII[0][0].active


        return save


    def code_shear(self, save, setup):
        save["type setup"]="shear"
        save["nom"]=self.nom

        save["LI"]=setup.ids["LI_mprs"].text
        save["fuel"]=setup.ids["fuel_mprs"].text
        save["conso"]=setup.ids["conso_mprs"].text
        save["vol"]=setup.ids["vol_mprs"].text
        save["APM"]=setup.ids["APMentry"].text
        save["APMCG"]=setup.ids["CGentry"].text
        save["type de vol"]=setup.ids["type_vol_entry"].text

        save["ShearLoadEntry"]=[0]*9
        save["maximumShearLoadEntry"]=[0]*9
        save["BendingMomentEntry"]=[0]*9
        save["maximumBendingMomentEntry"]=[0]*9
        for i in range(9):
            save["ShearLoadEntry"][i]=setup.ids["shear"+str(i+1)].text
            save["maximumShearLoadEntry"][i]=setup.ids["shear_lim"+str(i+1)].text
            save["BendingMomentEntry"][i]=setup.ids["bending"+str(i+1)].text
            save["maximumBendingMomentEntry"][i]=setup.ids["bending_limit"+str(i+1)].text


        return save















#calc=CalculsLimitation(18000, 30, 15000, "Tactical", [{"poids":120, "h_armes":22, "longueur":0.2}, {"poids":2500, "h_armes":30, "longueur":7}], [True, 500, [1,0,0,1]] )
#print(calc.TOWCG)


#calc=CalculsLimitation()
#calc.limit()
#calc.calculs()


