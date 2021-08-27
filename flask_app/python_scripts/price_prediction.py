import pickle
import pandas as pd
import numpy as np
from xgboost import XGBRegressor

path_to_static = '../flask_app/static' 

def predict(house:dict)->int:
    """
        Take a dictionary containing the informations about a house and predict its price
        :param dict house: dictionnary containing the datas of house.
        :return int: price of the house
    """
    house['median_price'].append(get_median_price(house['locality'][0]))
    house['region'].append(get_region(house['province'][0]))
    data = pd.DataFrame.from_dict(house)
    data = preprocessing(data)
    pipe = pickle.load(open(f'{path_to_static}/preprocessor.pkl', 'rb'))
    X = pipe.transform(data)
    model_xgb = XGBRegressor()
    model_xgb.load_model(f"{path_to_static}/model.json")
    return int(np.exp(model_xgb.predict(X)[0]))


def preprocessing(data:pd.DataFrame)->pd.DataFrame:
    """
        preprocessing of the dataframe
        :param pd.DataFrame data: the pandas DataFrame
        :return pd.DataFrame: the preprocessed DataFrame
    """
    if not data.loc[0,'garden']:
        data.loc[0,'garden_area'] = 0
    elif data.loc[0,'garden_area']== "":
        data.loc[0,'garden_area'] = np.nan
    else:
        data.loc[0,'garden_area'] = float(data.loc[0,'garden_area'])
    if not data.loc[0,'terrace']:
        data.loc[0,'terrace_area'] =0
    elif data.loc[0,'terrace_area']== "":
        data.loc[0,'terrace_area'] = np.nan
    else:
        data.loc[0,'terrace_area'] = float(data.loc[0,'terrace_area'])
    if data.loc[0,'surface_of_the_land'] == "":
        data.loc[0,'surface_of_the_land'] = np.nan
    else:
        data.loc[0,'surface_of_the_land'] = float(data.loc[0,'surface_of_the_land'])
    if data.loc[0,'number_of_rooms'] == "":
        data.loc[0,'number_of_rooms'] = np.nan
    else:
        data.loc[0,'number_of_rooms'] = int(data.loc[0,'number_of_rooms'])
    if data.loc[0,'number_of_facades'] == "":
        data.loc[0,'number_of_facades'] = np.nan
    else:
        data.loc[0,'number_of_facades'] = int(data.loc[0,'number_of_facades'])
    if data.loc[0,'area'] == "":
        data.loc[0,'area'] = np.nan
    else:
        data.loc[0,'area'] = float(data.loc[0,'area'])
    if data.loc[0,'surface_of_the_land'] == "":
        data.loc[0,'surface_of_the_land'] = np.nan
    else:
        data.loc[0,'surface_of_the_land'] = float(data.loc[0,'surface_of_the_land'])
    return data



def get_median_price(post_code:str)->str:
    """ 
        return the median price of housing in the city with postal code post_code
        :param str post_code: postal code of a belgian city
        :return float: median price of housing in the city
    """
    median = pd.read_csv(f'{path_to_static}/median.csv')
    post = pd.read_csv(f'{path_to_static}/post_codes.csv', sep=';')
    median['Gemeente'] = median['Gemeente'].str.lower()
    post['Commune Principale'] = post['Commune principale'].str.lower()
    median_with_post = median.merge(post[['Code postal', 'Commune Principale']], how='left', left_on='Gemeente', right_on='Commune Principale')
    median_with_post = median_with_post.groupby('Gemeente').median()
    median_with_post['Mediaanprijs 2020'].fillna(median_with_post['Mediaanprijs 2019'], inplace=True)
    median_with_post['Mediaanprijs 2020'].fillna(median_with_post['Mediaanprijs 2018'], inplace=True)
    post_with_median = post[['Code postal','Commune principale']].merge(median_with_post[['Code postal', 'Mediaanprijs 2020']], how='left', left_on='Code postal', right_on='Code postal')
    post_with_median.sort_values(by='Code postal', inplace=True)
    post_with_median.fillna(method='bfill', inplace=True)
    post_with_median.fillna(method='ffill', inplace=True)
    post_with_median.drop_duplicates(inplace=True)
    post_with_median.set_index('Code postal', drop=True, inplace=True)
    post_with_median.pop('Commune principale')
    try:
        post_code = int(post_code)
        print(post_with_median.loc[post_code, 'Mediaanprijs 2020'])
        return post_with_median.loc[post_code, 'Mediaanprijs 2020']
    except:
        return post_with_median.mean()['Mediaanprijs 2020']


def get_region(prov:str)->str:
    """
        return belgian region of a belgian province
        :param str prov: a belgian province
        :return str: the corresponding belgian region (or '' if prov is not a belgian province)
    """
    provinces_flandres = ['Antwerp', 'West-Vlanderen', 'Oost-Vlanderen', 'Vlaams-Brabant', 'Limburg']
    provinces_wallonie = ['Hainaut', 'Liège', 'Namur', 'Luxembourg', 'Brabant Wallon']
    if prov in provinces_wallonie:
        return 'Wallonie'
    elif prov in provinces_flandres:
        return 'Vlaams'
    elif prov == 'Brussels':
        return 'Brussels Capital'
    else:
        return ''
