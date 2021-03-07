########Written By Jonathan Pinna 27/12/2019#############################################
####Programma che implementa una web automation per scaricare i dati da Helium10#################

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException
import time
import os
import shutil
import datetime
import sys
import re
import csv

resume=0
today=datetime.date.today()
colonne=['Categoria','Fulfillment','RevenueMin','RevenueMax','PriceMin','PriceMax','ReviewsMin','ReviewsMax']
#Preleva i valori dal file config per capire da dove ripartire con la ricerca
config_file="C:\\Tools\\helium-python-2.0.3\\examples\\Download_products_amzH10_prod\\config.csv"
#Path file di log
path_log="C:\Tools\helium-python-2.0.3\examples\Download_products_amzH10_prod\logs"
filename_log="Log-search-" + str(today.year) + "-" + str(today.month) + "-" + str(today.day) + ".log"
logfile=os.path.join(path_log,filename_log)

#Redireziona tutto lo standard output su un file di log
old_stdout = sys.stdout
logfile=open(logfile,"w")
sys.stdout = logfile

prices_min=["5.00","15.10","25.20","35.30","45.40"]
prices_max=["15.00","25.10","35.20","45.30","55.40"]
categories=["Valigeria","Sport e tempo libero","Prodotti per animali domestici","Giardino e giardinaggio","Casa e cucina","Auto e moto","Sport e tempo libero","Prima infanzia","Bellezza","Fai da te","Commercio, industria e scienza","Giochi e giocattoli","Salute e cura della persona","Strumenti musicali"]
fulfillments=["FBA", "FBM", "Amazon"]
max_revenue_limit=20000
max_reviews_limit=100
#Path dove posizionare i file
base_path="Z:\\AUTOMATION\\CATEGORIE"
#Path download dove vengono scaricati i dati
path="Inserisci il path dove vanno a finire i file scaricati"
filename="helium10-black-box-www.amazon.it-" + str(today.year) + "-" + str(today.month) + "-" + str(today.day) + ".csv"
file_download=path + filename

#controlla se il contenuto del file è vuoto
if os.path.getsize(config_file) > 0:
    #Preleva i valori dal file di config
    file = open(config_file)
    csv_file=csv.reader(file,delimiter=',')
    data=list(csv_file)
    file.close()
    #Controlla se il ciclo di ricerca è terminato altrimenti setta i valori del file di config per riprendere la ricerca
    if(data[1].count("Completato")==0):
        resume=1
        category=data[2][0]
        i=categories.index(category)
        fulfillment=data[2][1]
        j=fulfillments.index(fulfillment)
        revenue_min=int(data[2][2])
        revenue_max=int(data[2][3])
        p=prices_max.index(data[2][5])
        reviews_min=int(data[2][6])
        reviews_max=int(data[2][7])
    else:
        revenue_min=1
        revenue_max=1000
        reviews_min=1
        reviews_max=10
        i=0
        j=0
        p=0

class Helium:
    def __init__(self, email, password, base_url):
        self.email=email
        self.password=password
        self.base_url=base_url

    def OpenChrome(self):
        #INIZIALIZZAZIONE DEL DRIVER CHROME
        self.driver=webdriver.Chrome(executable_path="C:\Tools\chromedriver.exe")
        #ESPANDE LA FINESTRA DEL BROWSER
        self.driver.maximize_window()
        #TEMPO DI CARICAMENTO DA ATTENDERE TRA UN COMANDO E L'ALTRO
        self.driver.implicitly_wait(20)
        #EFFETTUA LA RICHIESTA
        self.driver.get(self.base_url)

    def LogIn(self):
        #LOGIN IN HELIUM10
        form=self.driver.find_element_by_id("login-form")
        textbox_email=self.driver.find_element_by_id("loginform-email")
        textbox_email.clear()
        textbox_email.send_keys(self.email)
        textbox_password=self.driver.find_element_by_id("loginform-password")
        textbox_password.clear()
        textbox_password.send_keys(self.password)
        form.submit()
        #VAI SULLA PAGINA DI BLACK BOX PER LA RICERCA
        self.driver.get("https://members.helium10.com/black-box")
    
    def SelectMarketplace(self):
        #SELEZIONA IL MARKETPLACE TARGET
        self.driver.find_element_by_id("marketplace-select").click()
        self.driver.find_element_by_id("marketplace-APJ6JRA9NG5V4").click()
    
    def Set_Revenue_Min(self,revenue_min):
        #IMPOSTA IL FILTRO REVENUE MINIMO
        textbox_revenue_min=self.driver.find_element_by_id("filter-monthlyRevenue-min")
        textbox_revenue_min.send_keys(revenue_min)
    
    def Set_Revenue_Max(self,revenue_max):
        #IMPOSTA IL FILTRO REVENUE MAX
        textbox_revenue_min=self.driver.find_element_by_id("filter-monthlyRevenue-max")
        textbox_revenue_min.send_keys(revenue_max)
    
    def Set_Price(self,price_min,price_max):
        #IMPOSTA L'INTERVALLO DI PREZZO DEL PRODOTTO 
        textbox_price_min=self.driver.find_element_by_id("filter-price-min")
        textbox_price_min.send_keys(price_min)
        textbox_price_max=self.driver.find_element_by_id("filter-price-max")
        textbox_price_max.send_keys(price_max)
    
    def Reviews_CountMax(self,reviews_max):
        #IMPOSTA IL NUMERO MASSIMO DI RECENSIONI
        textbox_review_max=self.driver.find_element_by_id("filter-reviewCount-max")
        textbox_review_max.send_keys(reviews_max)
    
    def Reviews_CountMin(self,reviews_min):
        #IMPOSTA IL NUMERO MINIMO DI RECENSIONI
        textbox_review_max=self.driver.find_element_by_id("filter-reviewCount-min")
        textbox_review_max.send_keys(reviews_min)

    def Set_Category(self,category):
        #SELEZIONO LE CATEGORIE CHE MI INTERESSANO
        self.driver.find_element_by_xpath('//*[@title="None selected"]').click()
        self.driver.find_element_by_xpath('//*[@title="'+category+'"]').click()
    
    def Set_Fulfillment(self,fulfillment):
        #SELEZIONA LA SIZE
        self.driver.find_element_by_xpath('//*[@title="None selected"]').click()
        self.driver.find_element_by_xpath('//*[@title="Small Standard-Size"]').click()
        self.driver.find_element_by_class_name("panel-title-with-chevron").click()
        self.driver.find_element_by_xpath('//*[@title="None selected"]').click()
        self.driver.find_element_by_xpath('//label[@title="'+fulfillment+'"]//input[@type="checkbox"][@name="filter-seller-type"]').click()
        #DESELEZIONA LA SIZE 
        self.driver.find_element_by_xpath('//*[@title="Small Standard-Size"]').click()
        self.driver.find_element_by_xpath('//label[@title="Small Standard-Size"]//input[@type="checkbox"][@name="filter-size-tiers"]').click()

    def Search(self):
        #EFFETTUA LA RICERCA
        self.driver.find_element_by_class_name("action-search").click()
    
    def ClearFilters(self):
        #PULISCI I FILTRI
        self.driver.find_element_by_class_name("action-clear-filters").click()

    def Download(self):
        #DOWNLOAD
        try:
            self.driver.find_element_by_class_name("action-download-csv").click()
            return 0
        except NoSuchElementException as exception:
            print("Eccezione elemento non trovato!")
            return 1
        except ElementNotVisibleException as exception:
            print("Eccezione elemento non visibile!")
            return 1

    def CloseChrome(self):
        self.driver.close()

def CreateDir(path,directory):
    path_new=os.path.join(path,directory)
    if not os.path.exists(path_new):
        os.mkdir(path_new)
    return path_new

print ("LOG - Inizio Web automation " + str(datetime.datetime.now()))
#Crea l'istanza dell'oggetto
s1=Helium("Inserisci username dell'account HELIUM10","Inserisci password dell'account HELIUM10","https://members.helium10.com/user/signin")
#Apre Chrome
s1.OpenChrome()
print("LOG - Apro Chrome")
#Si logga all'interno di Helium10
s1.LogIn()
print("LOG - LogIn all'interno di Helium10")

try:
    #cicla le categorie
    while i<(len(categories)):
        category=categories[i]
        #crea la diretory categoria se non esiste
        path_category=CreateDir(base_path,category)
        print("LOG - Creazione directory categoria " + category)
        if(resume==0):
            p=0
        while p<(len(prices_max)):
            price_min=prices_min[p]
            price_max=prices_max[p]
            if(resume==0):
                j=0
            #cicla per i tre tipi di vendita
            while j<(len(fulfillments)):
                fulfillment=fulfillments[j]
                #crea la directory fulfillment se non esiste
                path_fulfillment=CreateDir(path_category,fulfillment)
                print("LOG - Creazione directory venditore " + fulfillment)
                path_revenues=CreateDir(path_fulfillment,"REVENUE")
                if(resume==0):
                    revenue_min=1
                    revenue_max=1000
                #cicla finchè non arriva a 20000
                while revenue_max <= max_revenue_limit:
                    r=str(revenue_max)
                    path_revenue=CreateDir(path_revenues,r)
                    print("LOG - Creazione directory revenue " + r)
                    path_reviews=CreateDir(path_revenue,"REVIEWS")
                    if(resume==1):
                        resume=0
                    else:
                        reviews_min=1
                        reviews_max=10
                    #cicla finchè non arriva a 100 recensioni 
                    while reviews_max <= max_reviews_limit:
                        r=str(reviews_max)
                        path_review=CreateDir(path_reviews,r)
                        #se all'interno della review è già presente un file allora aggiorna scarica i dati altrimenti incrementa passa al successivo
                        print("LOG - Creazione directory reviews " + r)
                        print("LOG - Setto i filtri")
                        s1.SelectMarketplace()
                        time.sleep(3)
                        s1.Set_Category(category)
                        s1.Set_Revenue_Min(revenue_min)
                        s1.Set_Revenue_Max(revenue_max)
                        s1.Set_Price(price_min,price_max)
                        s1.Reviews_CountMin(reviews_min)
                        s1.Reviews_CountMax(reviews_max)
                        s1.Set_Fulfillment(fulfillment)
                        s1.Search()
                        time.sleep(4)
                        check=s1.Download()
                        time.sleep(4)
                        if(check==0):
                            #crea la directory prezzomin-max sotto review
                            path_price=CreateDir(path_review,"PREZZO" + price_min.split('.')[0] + "-" + price_max.split('.')[0])
                            path_dest=path_price+"\\"+filename
                            if os.path.exists(file_download):
                                print("LOG - File" + file_download + "trovato")
                                #copia il file sotto download in share
                                shutil.copyfile(file_download,path_dest)
                                #rimuove il file sotto download in modo da non prelevare sempre lo stesso
                                os.remove(file_download)
                                #pulisce i filtri della pagina
                                s1.ClearFilters()
                            else:
                                print("LOG - File" + file_download + "NON trovato")
                        else:
                            print("LOG - Non è presente nessun risultato nella ricerca")
                        s1.ClearFilters()
                        #incrementa le reviews per definire il nuovo range
                        reviews_max=reviews_max+10
                        reviews_min=reviews_min+10
                    #incrementa il revenue per definire il nuovo range
                    if(revenue_max>=10000):
                        revenue_min=revenue_max
                        revenue_max=revenue_max+2000
                    else:
                        revenue_min=revenue_min+1000
                        revenue_max=revenue_max+1000
                    
                j=j+1
            p=p+1
        i=i+1
    #Se sei arrivato fino a qui significa che sono stati tirati giù i dati di ogni categoria per ogni fulfillment con il range di prezzo settato
    data=['Completato']
    if os.path.exists(config_file):
        os.remove(config_file)
    with open(config_file,'w') as file:
        wr=csv.writer(file)
        wr.writerow(colonne)
        wr.writerow(data)
        file.close()
    #Chiusura del driver 
    s1.CloseChrome()
    #Eliminazione oggetto
    del s1
except Exception as ex:
    if os.path.exists(config_file):
        os.remove(config_file)
    data=[]
    data.append(category)
    data.append(fulfillment)
    data.append(revenue_min)
    data.append(revenue_max)
    data.append(price_min)
    data.append(price_max)
    data.append(reviews_min)
    data.append(reviews_max)
    with open(config_file,'w') as file:
        wr=csv.writer(file)
        wr.writerow(colonne)
        wr.writerow(data)
        file.close()
    #message = template.format(type(ex).__name__, ex.args)
    #print message
    #Chiusura del driver 
    #s1.CloseChrome()
    #Eliminazione oggetto
    #del s1