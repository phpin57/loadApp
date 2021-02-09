import re
import json
import calculs as calc
#import de kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox

class BlackHole(object): #fonction ajoutée lors de la transition vers python 3
    def __init__(self, **kwargs):
        super(BlackHole,self).__init__()

class Setup(Screen, BlackHole):
    def __init__(self,**kwargs):
        super(Setup,self).__init__(**kwargs)

    def valider(self):
        if self.ids["chk_shear"].active and self.donnees1():
            self.save_data1()
            calculs.remplissage_shear=False
            if calculs.maximumBendingMoment==[0]*9 or calculs.maximumShearLoad ==[0]*9:
                self.manager.current = 'shear'
            else :
                calculs.calculs()
                self.manager.current = 'avion_log'

        elif self.donnees1() and re.match("\d+[.]?\d*\Z",self.ids["equipement"].text):
            self.save_data1()
            self.save_data2()
            calculs.calculs()
            self.manager.current = 'avion_log'

    def shearing_and_bending(self):
        value=self.ids["chk_shear"].active
        if value and self.donnees1():
            self.save_data1()
            calculs.remplissage_shear=False
            self.manager.current = 'shear'
        else:
            calculs.remplissage_shear=True
            self.ids["chk_shear"].active=False


    def save_data1(self):
        calculs.apm=float(self.ids["APM"].text)
        calculs.apmcg=float(self.ids["APMCG"].text)
        calculs.fuelWeight=float(self.ids["fuel"].text)
        calculs.version=self.ids["version_lat"].text
        calculs.nb_bloc=int(self.ids["nb_bloc"].text)
        try:
            calculs.fuel_conso=int(self.ids["fuel_conso"].text)
        except:
            calculs.fuel_conso=self.ids["fuel_conso"].text
        if self.ids["spinner_vol"].text=="LH":
            calculs.typeDeVol="Logistic"
        else :calculs.typeDeVol="Tactical"

    def save_data2(self):
        calculs.poids_equipe=float(self.ids["equipement"].text)
        calculs.itemII=[0,0,0,0]
        if self.ids["chk_blindage"].active:
            calculs.itemII[0]=1
        if self.ids["chk_crane"].active:
            calculs.itemII[1]=1
        if self.ids["chk_medevac"].active:
            calculs.itemII[2]=1
        if self.ids["chk_hdu"].active:
            calculs.itemII[3]=1

    def donnees1(self):
        pattern=re.compile("\d+[.]?\d*\Z")
        if re.match(pattern,self.ids["APM"].text) and re.match(pattern,self.ids["APMCG"].text) and re.match(pattern,self.ids["fuel"].text) and re.match("\d*[.]?\d*\Z",self.ids["fuel_conso"].text):
            if self.ids["spinner_vol"].text != "" and self.ids["version_lat"].text != "" and self.ids["nb_bloc"].text != "":
                return True
        return False

class Chargement(Screen, BlackHole):
    def __init__(self,**kwargs):
        super(Chargement,self).__init__(**kwargs)
        self.charges=[]

    def ajout(self,poids, h_armes, longueur, drop):
        if re.match("\d+[.]?\d*\Z",poids) and re.match("\d+[.]?\d*\Z",h_armes) and re.match("\d+[.]?\d*\Z",longueur):

            charge={"poids":poids,
                "h_armes":h_armes,
                "longueur":longueur,
                "drop":drop,
                "siege_num":None}
            self.charges.append(charge)

            liste_charges=self.text()
            self.ids["data_value"].text = liste_charges

    def text(self):
        string=""
        for charge in self.charges:
                string += "poids:"+charge["poids"]+",   H-armes:"+charge["h_armes"]+",   longueur:"+charge["longueur"] + ",   drop:"+charge["drop"]+"\n"
        return string


    def supprimer(self):
        if len(self.charges)>0:
            self.charges.pop()
            liste_charges=self.text()
            self.ids["data_value"].text = liste_charges


class ShearingAndBending(Screen, BlackHole):
    def __init__(self,**kwargs):
        super(ShearingAndBending,self).__init__(**kwargs)
    def valider(self):
        self.save_data()
        if calculs.maximumBendingMoment!=[0]*9 and calculs.maximumShearLoad!=[0]*9:
            calculs.calculs()
            self.manager.current = 'avion_log'
    def retour(self):
        try:
            self.save_data()
        except:
            pass
        self.manager.current = 'setup'
    def save_data(self):
        for i in range(0,9):
            try:
                calculs.ShearLoad[i]=float(self.ids["shear"+str(i+1)].text)
                calculs.maximumShearLoad[i]=float(self.ids["shear_lim"+str(i+1)].text)
                calculs.BendingMoment[i]=float(self.ids["bending"+str(i+1)].text)
                calculs.maximumBendingMoment[i]=float(self.ids["maximumBendingMoment"+str(i+1)].text)
            except:self.manager.current = 'shear'


class AvionLog(Screen, BlackHole):
    def __init__(self,**kwargs):
        super(AvionLog,self).__init__(**kwargs)
        self.button_color=[0.95,0.95,0.95,0.95]
        self.sieges_vide=[3,28,29,30,31,102,103,104]
        self.button_color_larg=[0.95,0.95,0.95,0.95]
        self.dico_poids={"passenger 1":"80",
        "passenger 2":"80",
        "passenger 3":"80",
        "paratrooper 1":"100",
        "paratrooper 2":"100",
        "paratrooper 3":"100",
        "vide":"0"}
        self.dico_color={"passenger 1":[1,1,0,1],
        "passenger 2":[1,0,0,1],
        "passenger 3":[0,1,1,1],
        "paratrooper 1":[0,1,0,1],
        "paratrooper 2":[0,0,1,1],
        "paratrooper 3":[1,0,1,1],
        "vide":[0.95,0.95,0.95,0.95]}
        self.dico_pax={"[1, 1, 0, 1]":"passenger 1",
        "[1, 0, 0, 1]":"passenger 2",
        "[0, 1, 1, 1]":"passenger 3",
        "[0, 1, 0, 1]":"paratrooper 1",
        "[0, 0, 1, 1]":"paratrooper 2",
        "[1, 0, 1, 1]":"paratrooper 3",
        "[0.95, 0.95, 0.95, 0.95]":"vide"}
        with open("version log.JSON","r") as mj:
            self.sieges = json.load(mj)

    def color(self, id):
        if self.ids["but_poids"].active:
            self.ids[id].background_color=self.button_color
        if self.ids["but_largage"].active :
            self.ids[id].text=self.ids["largage"].text
        self.update_cg()

    def update_cg(self):
        self.save_sieges()
        calculs.charges=self.sieges
        calculs.calculs()
        self.ids["ZFW_res"].text=str(calculs.ZFW)
        self.ids["ZFWCG_res"].text=str(calculs.ZFWCG)
        self.ids["shear_lim"].text=str(calculs.shear_lim)
        self.ids["bending_lim"].text=str(calculs.bending_lim)


#fonction qui fait que le texte de présentation de la check box est cliquable
    def chkb_label(self, id):
        bool=self.ids[id].active
        if bool:
            self.ids[id].active=False
        else:
            self.ids[id].active=True


    def couleur(self, id):
        self.button_color=self.dico_color[id]
        self.ids["poids_para_txt"].text=self.dico_poids[id]
        self.ids["ref_color"].background_color=self.dico_color[id]


    def poids(self, poids, couleur):
        if couleur!="vide":
            self.dico_poids[couleur]=poids

        else:
            self.ids["poids_para_txt"].text="0"
        self.update_cg()


    def modif_siege(self, num, couleur):
        j=num-1-len([i for i in self.sieges_vide if i<num])
        try:
            poids=self.dico_poids[couleur]
        except:
            poids="0"
        self.sieges[j]["poids"]=poids


    def save_sieges(self):
        for siege in self.sieges:
            i=siege["siege_num"]
            col=self.ids[str(i)].background_color
            if col[-1]!=0:
                col=str(col)
                col=self.dico_pax[col]
                siege["poids"]=float(self.dico_poids[col])
                siege["drop"]=self.ids[str(i+1)].text

    def valider(self):
        #liste des dicos des sièges
        self.save_sieges()
        with open("version log.JSON","w") as mj:
            json.dump(self.sieges, mj)
        self.manager.current = 'chargement'


class Resultats(Screen, BlackHole):
    def __init__(self,**kwargs):
        super(Resultats,self).__init__(**kwargs)


class MyApp(App):
    def build(self):
        #création d'un gestionnaire d'écran pour toutes les fenêtres de l'application
        sm = ScreenManager(transition=SlideTransition(direction='up'))
        # Appel de la classe qui lit kv
        sm.add_widget(Setup(name='setup'))
        sm.add_widget(Chargement(name='chargement'))
        sm.add_widget(ShearingAndBending(name='shear'))
        sm.add_widget(AvionLog(name='avion_log'))
        #sm.add_widget(Avion25(name='avion_25'))
        #sm.add_widget(Avion29(name='avion_29'))
        sm.add_widget(Resultats(name='resultats'))
        return sm


calculs=calc.CalculsLimitation()
if __name__ == '__main__':
    MyApp().run()
