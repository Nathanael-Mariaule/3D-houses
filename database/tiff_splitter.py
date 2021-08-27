import rasterio
import rioxarray
import geopandas as gpd
import shapely
from shapely.geometry import Polygon, Point
from shapely.ops import cascaded_union
import numpy as np
import pickle
import os
import shutil
from zipfile import ZipFile


dir_path = '../database/'

def city_folder_creator(cities, adresses):
    for city in cities:
        adresses_city = adresses[(adresses.GEMEENTE==f'{city.capitalize()}')]
        cadastre =  shapefile_collector("Bpn_CaPa", city)
        cadi = shapefile_collector("Apn_CaDi", city)
        cabu = shapefile_collector("Bpn_CaBu", city)
        rebu = shapefile_collector("Bpn_ReBu", city)
        district_database(city, adresses_city, cadastre)
        dsm, dtm = get_dsm_and_dtm(city)
        district_filer(city, adresses_city, cadastre, cadi, cabu, rebu, dsm, dtm)

def get_dsm_and_dtm(city):
    dsm = rioxarray.open_rasterio(f'{dir_path}/dsm_{city}.tiff', masked=True)
    dtm = rioxarray.open_rasterio(f'{dir_path}/dtm_{city}.tiff', masked=True)
    return dsm, dtm

def district_database(city_name, adresses, cadastre):
    print('collecting capakey')
    adresses['adresses'] = adresses.HUISNR+", "+adresses.STRAATNM+", "+adresses.POSTCODE+", "+adresses.GEMEENTE
    adresses['adresses'] = adresses['adresses'].str.lower()
    adresses['CaPaKey'] = adresses.geometry.apply(lambda x: capakey_collector(x, cadastre))
    adresses = adresses[['adresses', 'CaPaKey', 'geometry']]
    if not os.path.exists(f'{dir_path}/{city_name}'):
        os.mkdir(f'{dir_path}/{city_name}')
    with open(f'{dir_path}/{city_name}/adresses.pickle', "wb") as file_adresses:
            pickle.dump(adresses, file_adresses)
    print('capakey collected')

def shapefile_collector(shapefile_name, city):
    if os.path.exists(f'{dir_path}/{city}_L72_2020/{shapefile_name}.shp'):
        return gpd.read_file(f'{dir_path}/{city}_L72_2020/{shapefile_name}.shp')
    else:
        return []

def cadikey_collector(point, cadi):
    for index, row in cadi.iterrows():
        polygon = row.geometry
        if polygon.contains(point):
            return row.CaDiKey
    return ''

def capakey_collector(point, cadastre):
    for index, row in cadastre.iterrows():
        polygon = row.geometry
        if polygon.contains(point):
            return row.CaPaKey
    return ''


def district_filer(city, adresses_city, cadastre, cadi, cabu, rebu, dsm, dtm):
    left, right = np.array(dtm.x).min(), np.array(dtm.x).max() 
    up, down = np.array(dtm.y).min(), np.array(dtm.y).max() 
    dtm_boundaries = Polygon([(left, down), (right, down), (right, up), (left, up), (left,down)])
    for index, row  in adresses_city.iterrows():
        zip_path = f"{dir_path}/{city}/{str(row.CaPaKey).replace('/', '_')}"
        main_house = collect_main_house(row.geometry, cabu, rebu)
        if not main_house:
            main_house = collect_main_house(row.geometry, cadastre, [])
        if not main_house:
            continue
        cadikey = cadikey_collector(row.geometry, cadi)
        poly_cadastre = collect_cadastre(main_house, cadastre[cadastre.CaPaKey.str.contains(cadikey)])
        poly_houses = collect_houses(poly_cadastre, cabu, rebu)
        with open(f"cadastre.pickle", "wb") as file_cadastre:
            pickle.dump([poly_cadastre, poly_houses], file_cadastre)
        save_clipped_tif(poly_cadastre, dsm, 'dsm.tif')
        save_clipped_tif(poly_cadastre, dtm, 'dtm.tif')
        with ZipFile(f'{zip_path}.zip', 'w') as zip:
            zip.write('cadastre.pickle')
            zip.write('dsm.tif')
            zip.write('dtm.tif')
        os.remove(f'cadastre.pickle')
        os.remove(f'dsm.tif')
        os.remove(f'dtm.tif')

        

def collect_main_house(point, cabu, rebu):
    for building in cabu.geometry:
        if building.contains(point):
            return building
    if len(rebu)>0:
        for building in rebu.geometry:
            if building.contains(point):
                return building

def collect_houses(cadastre, cabu, rebu):
    houses = []
    for building in cabu.geometry:
        if cadastre.contains(building):
            houses.append(building)
    if len(rebu)>0:
        for building in rebu.geometry:
            if cadastre.contains(building):
                houses.append(building)
    return houses

def save_clipped_tif(poly, tif, file_name):
    coords = list(poly.buffer(5).exterior.coords)
    min_x, max_x = coords[0][0], coords[0][0]
    min_y, max_y = coords[0][1],coords[0][1]
    for x, y in coords:
            min_x, max_x = min(min_x, x), max(max_x, x)
            min_y, max_y = min(min_y, y), max(max_y, y)
    geometries = [
    {
        'type': 'Polygon',
        'coordinates': [[
            [min_x, min_y], [min_x, max_y], [max_x, max_y], [max_x, min_y], [min_x, min_y]
        ]]
    }
    ]
    try:
        clipped = tif.rio.clip(geometries, from_disk=True)
        clipped.rio.to_raster(f"{file_name}", dtype="float64")
    except:
        geometries = [
            {
                'type': 'Polygon',
                'coordinates': [[
                    [coord[0], coord[1]] for coord in poly.exterior.coords
                ]]
            }
        ]
        clipped = tif.rio.clip(geometries, from_disk=True)
        clipped.rio.to_raster(f'{file_name}', dtype="float64")




def  collect_cadastre(house, cadastre):
    cad = cadastre[cadastre.geometry.contains(house)]
    if len(cad)>0:
        return cad.geometry.iloc[0]
    #cad = cadastre[cadastre.geometry.intersection(house).area>0]
    #if len(cad)>0:
    #    return cad.geometry.iloc[0]
    return house
    



if __name__=='__main__':
    #addresses =  "CRAB_Adressenlijst_Shapefile/Shapefile/CrabAdr.shp"
    #addresses = gpd.read_file(addresses)
    #addresses = addresses[(addresses.GEMEENTE=='Oostkamp')]
    #with open(f"test_address.pickle", "wb") as file_adresses:
    #    pickle.dump(addresses, file_adresses)

    #print(addresses)

    #with open(f"test_address.pickle", "rb") as file_adresses:
    #    addresses = pickle.load(file_adresses)
    with open('OOSTKAMP/adresses.pickle', 'rb') as file:
        addresses = pickle.load(file)
    print(addresses.shape)
    print(addresses.head())
    #print(addresses[addresses.HUISNR=='106'])
    #city_folder_creator(['OOSTKAMP'],addresses) 

