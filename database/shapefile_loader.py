import requests
import pandas as pd
import csv
import numpy as np
import geopandas as gpd
import zipfile38 as zipfile
import os
import pickle
import shutil
    


dir_path = '../database/'


def shapefile_loader(city):
    ville_INS(city)
    
    nis = int(ville_INS(city))
    save(nis, city)
    
    file = f'{dir_path}/{city}_L72_2020.zip'
    dezip(file, city)
    os.remove(f'{dir_path}/Belgique.csv')



def ville_INS(city):
    city = city.capitalize()
    with open(f'{dir_path}/Belgique.csv', 'wb') as fp:
        req = requests.get(f'https://statbel.fgov.be/sites/default/files/Over_Statbel_FR/Nomenclaturen/REFNIS_2019.csv')
        fp.write(req.content)
    f = open(f"{dir_path}/Belgique.csv")
    belgique = pd.read_csv(f, sep = ';')
    if city in belgique['Entités administratives']:
        return belgique[belgique['Entités administratives']==city].iloc[0, 0]
    else:
        return belgique[belgique['Administratieve eenheden']==city].iloc[0, 0]



def save(nis, city):
    with open(f'{dir_path}/{city}_L72_2020.zip', 'wb') as fp:
        req = requests.get(f'https://eservices.minfin.fgov.be/myminfin-rest/cadastral-plan/cadastralPlan/2021/{nis}/72')
        fp.write(req.content)
        

def dezip(file, city):
    with zipfile.ZipFile(file, 'r') as zip:
        extract_files('Bpn_CaPa', zip, city)
        extract_files('Bpn_CaBu', zip, city)
        extract_files('Bpn_ReBu', zip, city)
        extract_files('Apn_CaDi', zip, city)
    os.remove(file)

def extract_files(filename, zip, city):
    if f'{filename}.shp' in zip.namelist():
            zip.extract(f'{filename}.dbf', f'{dir_path}/{city}_L72_2020')
            zip.extract(f'{filename}.prj', f'{dir_path}/{city}_L72_2020')
            zip.extract(f'{filename}.shp', f'{dir_path}/{city}_L72_2020')
            zip.extract(f'{filename}.sbn', f'{dir_path}/{city}_L72_2020')
            zip.extract(f'{filename}.sbx', f'{dir_path}/{city}_L72_2020')
            zip.extract(f'{filename}.shx', f'{dir_path}/{city}_L72_2020')
    
    


    
