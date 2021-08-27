import urllib.request
import zipfile38 as zipfile
import os
import shutil
import geopandas as gpd
import rasterio
from rasterio.plot import show
import numpy as np
from shapely.geometry import Polygon
import rioxarray
from rioxarray.merge import merge_arrays


dirpath = '../database'

def tiff_loader(city, auto_finder=True , tiff_numbers=[]):
    if auto_finder:
        tiff_numbers  = collect_tiff_number(city)
        for i in tiff_numbers:
            filename = f'DHMVIIDSMRAS1m_k{0 if (i<10) else ""}{i}'
            url = f'https://downloadagiv.blob.core.windows.net/dhm-vlaanderen-ii-dsm-raster-1m/{filename}.zip'
            download(url, filename)
    else:
        for i in tiff_numbers:
            filename = f'DHMVIIDTMRAS1m_k{0 if (i<10) else ""}{i}'
            url = f'https://downloadagiv.blob.core.windows.net/dhm-vlaanderen-ii-dtm-raster-1m/{filename}.zip'
            download(url, filename)
            filename = f'DHMVIIDSMRAS1m_k{0 if (i<10) else ""}{i}'
            url = f'https://downloadagiv.blob.core.windows.net/dhm-vlaanderen-ii-dsm-raster-1m/{filename}.zip'
            download(url, filename)
    tiff_merger(tiff_numbers, city)
    cleaner(tiff_numbers, city)


def tiff_merger(tiff_numbers, city):
    clips_dsm = []
    clips_dtm = []
    for i in tiff_numbers:
        filename = f'DHMVIIDTMRAS1m_k{i}'
        clips_dtm+=cut_city(filename, city)
        filename = f'DHMVIIDSMRAS1m_k{i}'
        clips_dsm+=cut_city(filename, city)
    dtm = merge_arrays(clips_dtm)
    dtm.rio.to_raster(f'{dirpath}/dtm_{city}.tiff', dtype="float64")
    dsm = merge_arrays(clips_dsm)
    dsm.rio.to_raster(f'{dirpath}/dsm_{city}.tiff', dtype="float64")

def cleaner(tiff_numbers, city):
    for i in tiff_numbers:
        filename = f'{dirpath}/DHMVIIDTMRAS1m_k{0 if (i<10) else ""}{i}'
        shutil.rmtree(filename)
        filename = f'{dirpath}/DHMVIIDSMRAS1m_k{0 if (i<10) else ""}{i}'
        shutil.rmtree(filename)

            

def cut_city(filename, city):
    fp = f'{dirpath}/{city.upper()}_L72_2020/Apn_CaDi.shp'
    data = gpd.read_file(fp)
    clips = []
    DTM_path = f'{dirpath}/{filename}/GeoTIFF/{filename}.tif'
    DTM = rasterio.open(DTM_path)
    dsm_poly = Polygon([[DTM.bounds.left, DTM.bounds.bottom], [DTM.bounds.left, DTM.bounds.top], 
                [DTM.bounds.right, DTM.bounds.top], [DTM.bounds.right, DTM.bounds.bottom],
                [DTM.bounds.left, DTM.bounds.bottom]])
    for poly in data.geometry:
        if not dsm_poly.intersects(poly):
            continue
        geometries = [
            {
                'type': 'Polygon',
                'coordinates': [[
                    [coord[0], coord[1]] for coord in poly.exterior.coords
                ]]
            }
        ]
        clipped = rioxarray.open_rasterio(
            DTM_path,
            masked=True,
        ).rio.clip(geometries, from_disk=True)
        
        clips.append(clipped)
    return clips



def collect_tiff_number(city):
    required_tiff = []
    fp = f'{dirpath}/{city.upper()}_L72_2020/Apn_CaDi.shp'
    data = gpd.read_file(fp)

    for i in range(1, 44):
        filename = f'DHMVIIDTMRAS1m_k{0 if (i<10) else ""}{i}'
        url = f'https://downloadagiv.blob.core.windows.net/dhm-vlaanderen-ii-dtm-raster-1m/{filename}.zip'
        download(url, filename)
        DTM_path = f'{dirpath}/{filename}/GeoTIFF/{filename}.tif'
        DTM = rasterio.open(DTM_path)
        dsm_poly = Polygon([[DTM.bounds.left, DTM.bounds.bottom], [DTM.bounds.left, DTM.bounds.top], 
                    [DTM.bounds.right, DTM.bounds.top], [DTM.bounds.right, DTM.bounds.bottom],
                    [DTM.bounds.left, DTM.bounds.bottom]])
        if any([dsm_poly.intersects(poly) for poly in data.geometry]):
            print(filename)
            required_tiff.append(i)
        else:
            shutil.rmtree(filename)



def download(url, filename):
    print(url)
    zip_name = f'{dirpath}/{filename}.zip'
    urllib.request.urlretrieve(url, zip_name)
    with zipfile.ZipFile(zip_name, 'r') as zip: 
        zip.extract(f'GeoTIFF/{filename}.tif', f'{dirpath}/'+filename)
    os.remove(zip_name)

	
    
