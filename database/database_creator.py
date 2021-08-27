from shapefile_loader import shapefile_loader
from tiff_loader import tiff_loader
import shutil
import urllib.request
import zipfile38 as zipfile
import os
import geopandas as gpd
from tiff_splitter import city_folder_creator



dirpath = '../database/'

def database_creation(cities, auto_finder=True , tiff_numbers={}):
    for city in cities:
        shapefile_loader(city)
        tiff_loader(city, auto_finder, tiff_numbers[city])
    adresses = adress_collector(cities)
    city_folder_creator(cities, adresses)
    cleaner(cities)


def adress_collector(cities):
    url = "https://downloadagiv.blob.core.windows.net/crab-adressenlijst/Shapefile/CRAB_Adressenlijst_Shapefile.zip"
    zip_name = f'{dirpath}/CRAB_Adressenlijst_Shapefile.zip'
    urllib.request.urlretrieve(url, zip_name)
    with zipfile.ZipFile(zip_name, 'r') as zip: 
        zip.extractall(f"{dirpath}/CRAB_Adressenlijst_Shapefile")
    os.remove(zip_name)
    addresses =  f"{dirpath}/CRAB_Adressenlijst_Shapefile/Shapefile/CrabAdr.shp"
    addresses = gpd.read_file(addresses)
    addresses = addresses[(addresses.GEMEENTE.isin([city.capitalize() for city in cities]))]  
    return addresses

def cleaner(cities):
    for city in cities:
        os.remove(f'{dirpath}/dsm_{city}.tiff')
        os.remove(f'{dirpath}/dtm_{city}.tiff')
        shutil.rmtree(f'{dirpath}/{city.upper()}_L72_2020')
        shutil.move(f'{dirpath}/{city}', f'../flask_app/static/{city}')
    shutil.rmtree(f'{dirpath}/CRAB_Adressenlijst_Shapefile')
    

def launcher():
    print('ready')
    with open(f'{dirpath}/cities', 'r') as file:
        build = file.readline().strip('\n')
        if build!='build':
            return
        autofinder = (file.readline().strip('\n')!='pre-computed')
        city = file.readline().strip('\n')
        cities = []
        tiff_numbers = {}
        while city!='':
            city = city.split(',')
            cities.append(city[0])
            tiff_numbers[city[0]] = [int(i) for i in city[1:]] if not autofinder else []
            city = file.readline().strip('\n')
        database_creation(cities, autofinder, tiff_numbers) 
    with open(f'{dirpath}/cities', 'w') as file:
        file.write('database ready')

#example of cities file to create database for cities of Leuven and Oostkamp: 
#build
#pre-computed
#OOSTKAMP,12,13,20,21  
#LEUVEN,24,32 
#
# 24, 32 are the tiff-file that are needed to get all adress in Leuven.
# For other cities one can check manually required file at https://download.vlaanderen.be/Producten/Detail?id=939&title=Digitaal_Hoogtemodel_Vlaanderen_II_DTM_raster_1_m
#or replace pre-computed by an empty line
if __name__=='__main__':
    launcher()


    

