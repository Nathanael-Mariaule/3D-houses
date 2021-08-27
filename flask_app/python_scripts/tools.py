from fuzzywuzzy import process
import pandas as pd
import numpy as np
import pickle
from typing import Tuple

path_to_static = '../flask_app/static' 

def get_city_info(post_code: str, city: str)->Tuple[str, str]:
    """
        Return correct name of the city and province corresponding to a belgian city postal code.
        If the postal code does not correspond to a city, it returns 'city' and 'Brussels'
        :param post_code str: postal code of the city
        :param city str: presumed name of the city
        :return Tuple[str, str]: name and province of the city
    """
    provinces = { 'Anvers' : 'Antwerp', 
                'Brabant Wallon' : 'Brabant Wallon', 
                'Bruxelles (19 communes)': 'Brussels', 
                'Hainaut' : 'Hainaut', 
                'Limbourg' : 'Limburg', 
                'Liège': 'Liège', 
                'Luxembourg': 'Luxembourg', 
                'Namur' : 'Namur', 
                'Flandre-Occidentale' : 'Oost-Vlanderen', 
                'Brabant Flamand' : 'Vlaams-Brabant', 
                'Flandre-Orientale'  : 'West-Vlanderen',
                np.nan :'Brussels' 
                }    
    post = pd.read_csv(f'{path_to_static}/post_codes.csv', sep=';')
    postal_codes = post[post['Code postal']==post_code]
    postal_codes['Province'] = postal_codes['Province'].map(provinces)
    if len(postal_codes)==0:
        return 'city', 'Brussels' 
    elif len(postal_codes)==1:
        return postal_codes.iloc[0,1],  postal_codes.iloc[0,4]
    adress_index = process.extractOne(city, postal_codes['Localité'])[2]
    return postal_codes.loc[adress_index,'Localité'], postal_codes.loc[adress_index,'Province']



def get_capakey(adress: str, city:str)->Tuple[str, str]:
    """ Take an adress formatted as '{house_number}, {street_name}, {postal_code}, {city_name}' and a city name
        and return the CaPaKey of the adress and the correct street name 
    """
    with open(f"{path_to_static}/{city.upper()}/adresses.pickle", "rb") as file_adresses:
            df_adresses = pickle.load(file_adresses)
    adress_index = process.extractOne(adress.lower(), df_adresses.adresses)[2]
    capakey = df_adresses.CaPaKey.loc[adress_index]
    correct_adress = df_adresses.adresses.loc[adress_index].split(', ')[1].strip()
    return capakey.replace('/', '_'), correct_adress




