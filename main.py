import os
import inspect
#dossier=os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
#os.chdir(dossier)



import re
import json
import calculs as calc
import graphique as graphique
import pandas as pd
import numpy as np
from math import *
#import de kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button

from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
class BlackHole(object): #fonction ajoutée lors de la transition vers python 3
    def __init__(self, **kwargs):
        super(BlackHole,self).__init__()


class Driver(Screen, BlackHole):
    def __init__(self,**kwargs):
        super(Driver,self).__init__(**kwargs)

    def on_enter(self):
        self.update_cg()
        self.update_siege()
        self.update_colis()

    def update_cg(self):
        try:
            calculs.calculs()
            self.ids["APM_driver"].text=str(round(calculs.apm))
            self.ids["ZFW_driver"].text=str(round(calculs.ZFW))
            self.ids["ZFWCG_driver"].text=str(round(calculs.ZFWCG, 2))
            if calculs.bending_lim and calculs.shear_lim:
                self.ids["S&B_driver"].text="True"
            else:
                self.ids["S&B_driver"].text="False"
        except:
            self.ids["ZFW_driver"].text="Eror"
            self.ids["ZFWCG_driver"].text="Eror"
            self.ids["S&B_driver"].text="Eror"
            self.ids["APM_driver"].text="Eror"

    def update_siege(self):
        self.ids["avion"].clear_widgets()
        for siege in calculs.sieges:
            if siege["poids"]!=0:
                x=(siege["h_armes"]-11.246-0.5/2)/22.718
                y=((-siege["y_arm"]+2.5-0.5)/5)/2+0.5
                btn = Button(background_color =(0, 0, 1, 1), background_normal= "", size_hint =(0.022, 0.05), pos_hint ={'x':x, 'y':y})
                try:
                    if int(siege["drop"])!=0:
                        btn.text="L"
                except:
                    pass
                self.ids["avion"].add_widget(btn)
    def update_colis(self):
        for coli in calculs.colis:
            if coli["poids"]!=0:
                x=(coli["h_armes"]-11.246-coli["longueur"]/2)/22.718
                y=((-coli["y_arm"]+2.5-0.5)/5)/2+0.5
                btn = Button(background_color =(1, 0, 0, 1), background_normal= "", size_hint =(coli["longueur"]/22.718, 0.1), pos_hint ={'x':x, 'y':y})
                self.ids["avion"].add_widget(btn)



class Setup(Screen, BlackHole):
    def __init__(self,**kwargs):
        super(Setup,self).__init__(**kwargs)
        self.methode_bool=False
        self.maniere_bool=True
        self.classe_bool=True

        classe2=pd.read_csv("classe II.csv", sep=";")
        self.liste_itemII=[]
        for item in classe2:
            liste=["","",""]
            liste[0]=CheckBox(active=False, size_hint_x=0.5)
            liste[1]=np.array(classe2[item])
            liste[2]=item
            self.liste_itemII.append(liste.copy())
            self.ids["classeII"].add_widget(liste[0])
            self.ids["classeII"].add_widget(Label(text=item, font_size= 20, size_hint_x=1.5, halign='left'))


        classe3=pd.read_csv("classe III.csv", sep=";")
        classe3=classe3.drop(columns=["nom"])
        self.liste_itemIII=[]
        for item in classe3:
            liste=["",""]
            liste[0]=CheckBox(active=False, size_hint_x=0.5)
            liste[1]=np.array(classe3[item])
            self.liste_itemIII.append(liste.copy())
            self.ids["classeIII"].add_widget(liste[0])
            self.ids["classeIII"].add_widget(Label(text=item, font_size= 20, size_hint_x=5, halign='left'))
        self.test2()
        #remplissage avec les dernieres valeurs renseignées
        try:
            with open("manual shear.JSON","r") as mj2:
                entry = json.load(mj2)
            for i in range(9):
                self.ids["shear"+str(i+1)].text=str(entry[0][i])
                self.ids["shear_lim"+str(i+1)].text=str(entry[1][i])
                self.ids["bending"+str(i+1)].text=str(entry[2][i])
                self.ids["bending_limit"+str(i+1)].text=str(entry[3][i])
        except:
            pass
        try:
            with open("save dernier setup.JSON","r") as mj2:
                save = json.load(mj2)
            bibli.decodage(save, self)
        except:
            pass



    def on_enter(self):
        if bibli.changement:
            #save est l'objet à décoder
            bibli.decodage(bibli.save,self)
            self.maj_bool()
            bibli.changement=False


    def maj_bool(self):
        self.methode_bool=(self.ids["methode"].value==0)
        self.classe_bool=(self.ids["classe"].value==0)
        self.maniere_bool=(self.ids["maniere"].value==0)
        self.test2()


    def test2(self):
        if (not self.methode_bool) and (not self.maniere_bool) and ( self.classe_bool):
            self.ids["scroll1"].size_hint_y=1
        else : self.ids["scroll1"].size_hint_y=0

        if (not self.methode_bool) and (not self.maniere_bool) and (not  self.classe_bool):
            self.ids["scroll2"].size_hint_y=1
        else : self.ids["scroll2"].size_hint_y=0

        if (not self.methode_bool) and (self.maniere_bool):
            self.ids["scroll3"].size_hint_y=0.5
            if self.classe_bool:
                self.ids["scroll31"].size_hint_y=0.5
                self.ids["scroll32"].size_hint_y=0
            else:
                self.ids["scroll31"].size_hint_y=0
                self.ids["scroll32"].size_hint_y=0.5
        else :
            self.ids["scroll3"].size_hint_y=0
            self.ids["scroll31"].size_hint_y=0
            self.ids["scroll32"].size_hint_y=0

        if self.methode_bool:
            self.ids["scroll4"].size_hint_y=1
            self.ids["maniere_box"].opacity=0
        else :
            self.ids["scroll4"].size_hint_y=0
            self.ids["maniere_box"].opacity=1

        if (not self.methode_bool) and (not self.maniere_bool):
            self.ids["scroll12"].size_hint_y=1
        else : self.ids["scroll12"].size_hint_y=0

    def save_config(self):
        show=NomPopup()
        popupWindow = Popup(title ="Popup Window", content = show, size_hint =(None, None), size =(200, 300))
        #on affecte à la variable show l'objet popup que l'on va afficher
        show.popup = popupWindow
        show.setup=self
        # open popup window
        popupWindow.open()

    def valider(self):
        try:
            apm.extraction_data(self, calculs)
            bibli.nom="re"
            save=bibli.creation_save(self)
            with open("save dernier setup.JSON","w") as mj:
                json.dump(save, mj)
            self.manager.current = 'driver'
        except:
            pass

class NomPopup(FloatLayout):
    popup = ObjectProperty(None)
    setup = ObjectProperty(None)
    def valider(self, nom):
        test=False
        if nom=="":
            test=True
        else:
            for save in bibli.save_list:
                if save["nom"]==nom:
                    test=True
                    break
        if not test:
            bibli.nom=nom
            bibli.codage(self.setup)
            self.popup.dismiss()

class Bibliotheque(Screen, BlackHole):
    def __init__(self,**kwargs):
        super(Bibliotheque,self).__init__(**kwargs)


    def on_enter(self):
        self.ids["setup_save"].values=bibli.liste_saved()

    def supprimer(self, nom):
        bibli.save_list=[save for save in bibli.save_list if save["nom"]!=nom]
        self.ids["setup_save"].text=""
        self.on_enter()
        with open("bibli data.JSON","w") as mj:
            json.dump(bibli.save_list, mj)



    def valider(self):
        nom=self.ids["setup_save"].text
        for save in bibli.save_list:
            if save["nom"]==nom:
                bibli.changement=True
                bibli.save=save
                self.manager.current = 'setup'


class Chargement(Screen, BlackHole):
    def __init__(self,**kwargs):
        super(Chargement,self).__init__(**kwargs)
        self.colis=[]


    def on_enter(self):
        self.update_cg()

    def update_cg(self):
        try:
            calculs.calculs()
            self.ids["APM_driver"].text=str(round(calculs.apm))
            self.ids["ZFW_driver"].text=str(round(calculs.ZFW))
            self.ids["ZFWCG_driver"].text=str(round(calculs.ZFWCG, 2))
            if calculs.bending_lim and calculs.shear_lim:
                self.ids["S&B_driver"].text="True"
            else:
                self.ids["S&B_driver"].text="False"
        except:
            self.ids["ZFW_driver"].text="Eror"
            self.ids["ZFWCG_driver"].text="Eror"
            self.ids["S&B_driver"].text="Eror"
            self.ids["APM_driver"].text="Eror"

    def ajout(self,poids, h_armes, longueur, drop, y_armes):
        try:
            charge={"poids":float(poids),
                "h_armes":float(h_armes),
                "y_arm":float(y_armes),
                "longueur":float(longueur),
                "drop":drop,
                "siege_num":None}
            self.colis.append(charge)
            calculs.colis=self.colis.copy()
            liste_colis=self.text()
            self.ids["data_value"].text = liste_colis
            self.update_cg()
        except:
            pass

    def text(self):
        string=""
        for charge in self.colis:
                string += "poids:"+str(charge["poids"])+",   H-armes:"+str(charge["h_armes"])+",   longueur:"+str(charge["longueur"]) + ",   drop:"+charge["drop"]+"\n"
        return string


    def supprimer(self):
        if len(self.colis)>0:
            self.colis.pop()
            calculs.colis=self.colis
            liste_colis=self.text()
            self.ids["data_value"].text = liste_colis
            self.update_cg()





class AvionLog(Screen, BlackHole):
    def __init__(self,**kwargs):
        super(AvionLog,self).__init__(**kwargs)
        self.liste_bouton=[]
        self.button_color=[0.95,0.95,0.95,0.95]
        self.sieges_vide=[3,28,29,30,31,102,103,104]
        self.button_color_larg=[0.95,0.95,0.95,0.95]
        self.dico_poids={"passenger 1":80,
        "passenger 2":80,
        "passenger 3":80,
        "paratrooper 1":100,
        "paratrooper 2":100,
        "paratrooper 3":100,
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


    def on_enter(self):
        self.version_sieges()
        self.update_cg()

    def version_sieges(self):
        if calculs.version_sieges=="aucune":
            colonne=1
            siege_vide=[1,2,3,4]
            self.ids["type_version"].text="Avions para pas de version"
        elif calculs.version_sieges=="version log":
            with open("version log.JSON","r") as mj:
                self.sieges = json.load(mj)
            colonne=31
            siege_vide=[3,28,29,30,31,122,123,124]
            self.ids["type_version"].text="Avions para version log"
        elif calculs.version_sieges=="6*25":
            with open("version 25.JSON","r") as mj:
                self.sieges = json.load(mj)
            colonne=26
            siege_vide=[24,25,26,52,78,103]
            self.ids["type_version"].text="Avions para version 6*25"
        elif calculs.version_sieges=="6*29":
            with open("version 29.JSON","r") as mj:
                self.sieges = json.load(mj)
            colonne=25
            siege_vide=[21,22,23,24,25,97,98,99]
            self.ids["type_version"].text="Avions para version 6*29"
        else:
            colonne=1
            siege_vide=[1,2,3,4]
            self.ids["type_version"].text="Avions para pas de version"

        if colonne!=self.ids["avion"].cols:
            self.ids["avion"].clear_widgets()

            self.ids["avion"].cols=colonne
            self.liste_bouton=[]
            for i in range(1,colonne*4+1):
                if len([j for j in siege_vide if i==j])==0:
                    btn = Button(background_color =(0.95, 0.95, 0.95, 0.95), background_normal= "")
                    btn.bind(on_press = self.color)
                    self.ids["avion"].add_widget(btn)
                    self.liste_bouton.append(btn)
                else:
                    btn = Button(background_color =(0.95, 0.95, 0.95, 0))
                    self.ids["avion"].add_widget(btn)
                    self.liste_bouton.append(btn)


    def color(self, btn):
        if self.ids["but_poids"].active:
            if btn.background_color==self.button_color:
                btn.background_color=(0.95, 0.95, 0.95, 0.95)
            else:
                btn.background_color=self.button_color
        if self.ids["but_largage"].active :
            btn.text=self.ids["largage"].text
        self.update_cg()

    def tout_color(self):
        if self.ids["but_poids"].active:
            for btn in self.liste_bouton:
                if btn.background_color[-1]!=0:
                    btn.background_color=self.button_color
            self.update_cg()
    def tout_larguer(self):
        if self.ids["but_largage"].active :
            for btn in self.liste_bouton:
                if btn.background_color[-1]!=0:
                     btn.text=self.ids["largage"].text

    def update_cg(self):
        try:
            self.save_sieges()
            calculs.sieges=self.sieges
            calculs.calculs()
            self.ids["ZFW_res"].text=str(round(calculs.ZFW))
            self.ids["ZFWCG_res"].text=str(round(calculs.ZFWCG, 2))
            self.ids["shear_lim"].text=str(calculs.shear_lim)
            self.ids["bending_lim"].text=str(calculs.bending_lim)
        except:
            self.ids["ZFW_res"].text="Eror"
            self.ids["ZFWCG_res"].text="Eror"
            self.ids["shear_lim"].text="Eror"
            self.ids["bending_lim"].text="Eror"

#fonction qui fait que le texte de présentation de la check box est cliquable
    def chkb_label(self, id):
        bool=self.ids[id].active
        if bool:
            self.ids[id].active=False
        else:
            self.ids[id].active=True


    def couleur(self, id):
        self.button_color=self.dico_color[id]
        self.ids["poids_para_txt"].text=str(self.dico_poids[id])
        self.ids["ref_color"].background_color=self.dico_color[id]


    def poids(self, poids, couleur):
        if couleur!="vide":
            try:
                self.dico_poids[couleur]=float(poids)
            except:
                self.ids["poids_para_txt"].text=str(self.dico_poids[couleur])

        else:
            self.ids["poids_para_txt"].text="0"
        self.update_cg()



    def save_sieges(self):
        for siege in self.sieges:
            i=siege["siege_num"]
            col=self.liste_bouton[i-1].background_color
            if col[-1]!=0:
                col=str(col)
                col=self.dico_pax[col]
                siege["poids"]=float(self.dico_poids[col])
                siege["drop"]=self.liste_bouton[i-1].text
            else:
                siege["poids"]=0


    def valider(self):
        #liste des dicos des sièges
        self.save_sieges()
        with open("version log.JSON","w") as mj:
            json.dump(self.sieges, mj)
        self.manager.current = 'chargement'


class Resultats(Screen, BlackHole):
    def __init__(self,**kwargs):
        super(Resultats,self).__init__(**kwargs)

    def on_enter(self):
        try:
            calculs.calculs()
            self.ids["ZFW_res"].text=str(int(calculs.ZFW))
            self.ids["ZFWCG_res"].text=str(round(calculs.ZFWCG,2))
            self.ids["ZFW_index"].text=str(round(calculs.ZFW_ind,2))
            self.ids["TOW_res"].text=str(int(calculs.TOW))
            self.ids["TOWCG_res"].text=str(round(calculs.TOWCG,2))
            self.ids["TOW_index"].text=str(round(calculs.TOW_ind,2))
            self.ids["LW_res"].text=str(int(calculs.LW))
            self.ids["LWCG_res"].text=str(round(calculs.LWCG,2))
            self.ids["LW_index"].text=str(round(calculs.LW_ind,2))
            self.ids["shear_res"].text=str(calculs.shear_lim)
            self.ids["bending_res"].text=str(calculs.bending_lim)
            self.ids["li_res"].text=str(round(calculs.LI,2))
            self.ids["drop_res"].text=str(round(calculs.masse_larguee,2))
        except:
            pass


class ResultatsShear(Screen, BlackHole):
    def __init__(self,**kwargs):
        super(ResultatsShear,self).__init__(**kwargs)

    def on_enter(self):
        try:
            for i in range(9):
                self.ids["shear"+str(i+1)].text=str(int(calculs.ShearRes[i]))
                self.ids["shear_lim"+str(i+1)].text=str(int(calculs.maximumShearRes[i]))

                if int(calculs.maximumShearRes[i])>int(calculs.ShearRes[i]):
                    self.ids["shear"+str(i+1)].background_color=[1,1,1,1]
                else:
                    self.ids["shear"+str(i+1)].background_color=[1,0,0,1]


                self.ids["bending"+str(i+1)].text= str( int( calculs.BendingRes[i]))
                self.ids["bending_limit"+str(i+1)].text= str( int( calculs.maximumBendingRes[i]))

                if int(calculs.maximumBendingRes[i])> int( calculs.BendingRes[i]):
                    self.ids["bending"+str(i+1)].background_color=[1,1,1,1]
                else:
                    self.ids["bending"+str(i+1)].background_color=[1,0,0,1]
        except:
            pass

class Graphe(Screen, BlackHole):
    def __init__(self,**kwargs):
        super(Graphe,self).__init__(**kwargs)

    def on_enter(self):
        #if calculs.typeDeVol=="LH":
        #    self.ids["graphe"].source="lhGraph.png"
        #else:
        #    self.ids["graphe"].source="tll1Graph.png"
        #with self.ids["test"].canvas:
         #   svg = Svg("graph.svg")
        #self.ids["graphe"].source="graph.jpeg"
        graphique.maj(calculs, self)



class MyApp(App):
    def build(self):
        #création d'un gestionnaire d'écran pour toutes les fenêtres de l'application
        sm = ScreenManager(transition=SlideTransition(direction='up'))
        # Appel de la classe qui lit kv
        sm.add_widget(Driver(name='driver'))
        sm.add_widget(Setup(name='setup'))
        sm.add_widget(Bibliotheque(name='bibli'))
        sm.add_widget(Chargement(name='chargement'))
        sm.add_widget(AvionLog(name='avion_log'))
        #sm.add_widget(Avion25(name='avion_25'))
        #sm.add_widget(Avion29(name='avion_29'))
        sm.add_widget(Resultats(name='resultats'))
        sm.add_widget(ResultatsShear(name='resultats_sh'))
        sm.add_widget(Graphe(name='graphe'))
        return sm

apm=calc.APMCalc()
calculs=calc.CalculsLimitation()
bibli=calc.Bilbliotheque()
graphique=graphique.Graphique()
if __name__ == '__main__':
    MyApp().run()
