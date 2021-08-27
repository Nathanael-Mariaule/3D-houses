from flask import render_template, redirect
from flask import Flask
from traitlets.traitlets import default
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, SelectField, RadioField
from wtforms.validators import DataRequired
from python_scripts.price_prediction import predict
from python_scripts.tools import get_city_info, get_capakey
from python_scripts.draw_house import draw_houses
import shutil
import os




path_to_static = '../flask_app/static'
city_available = ['oostkamp']
class Config(object):
    SECRET_KEY = 'you-will-never-guess'

class HouseForm(FlaskForm):
    number = StringField('Number', validators=[DataRequired()])
    street_name = StringField('Street Name', validators=[DataRequired()])
    postal_code = StringField('Postal Code', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    province = SelectField('Province', choices=[ 'Antwerp', 'Brabant Wallon', 'Brussels', 
                                    'Hainaut', 'Limburg', 'Liège', 'Luxembourg', 
                                    'Namur', 'Oost-Vlanderen', 'Vlaams-Brabant', 'West-Vlanderen'], default='Brussels') 
    type_house =  SelectField('Type', choices= ['House', 'Apartment'])
    state = SelectField('State of the Builing', choices= ['good', 'new', 'to renovate'])
    number_room = StringField('Number of Rooms')
    number_facade = StringField('Number of Facades')
    area = StringField('Area')
    area_of_land = StringField('Area of the Land')
    garden = BooleanField('Garden')
    garden_area = StringField('Area of the Garden')
    terrace = BooleanField('Terrace')
    terrace_area = StringField('Area of the Terrace')
    equipped = BooleanField('Fully equipped kitchen')
    furnished = BooleanField('Furnished')
    fire = BooleanField('Open Fire')
    pool = BooleanField('Pool')
    submit = SubmitField('Estimate Price')

server = Flask(__name__)
server.config.from_object(Config)
server.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
@server.route('/', methods=['GET', 'POST'])
@server.route('/index', methods=['GET', 'POST'])
def index():
    form = HouseForm()
    shutil.rmtree(f'{path_to_static}/3d-models')
    os.mkdir(f'{path_to_static}/3d-models')
    if form.validate_on_submit():
        building = {'median_price': [], 
            'locality': [int(form.postal_code.data)],
            'number_of_rooms': [form.number_room.data],
            'area': [form.area.data],
            'fully_equipped_kitchen':[int(form.equipped.data)],
            'furnished': [int(form.furnished.data)],
            'open_fire':[int(form.fire.data)],
            "terrace": [int(form.terrace.data)],
            'terrace_area':[form.terrace_area.data],
            'garden':[int(form.garden.data)],
            'garden_area':[form.garden_area.data],
            'surface_of_the_land': [form.area_of_land.data],
            "number_of_facades": [form.number_facade.data],
            'swimming_pool': [int(form.pool.data)],
            'state_of_the_building': [form.state.data],
            'province': [form.province.data],
            'region': [],
            'type_of_property': [form.type_house.data.lower()]}
        form.city.data, form.province.data = get_city_info(int(form.postal_code.data), form.city.data)
        form.city.data = form.city.data.capitalize()
        building['locality'] = [int(form.postal_code.data)]
        price = str(predict(building))+'€'
        if not form.city.data.lower() in city_available:
            form=form
            price=price 
            nmesh=0
            plot='not available'
            return redirect('/')
        else:
            adress = form.number.data+", "+form.street_name.data+', '+form.postal_code.data+', '+form.postal_code.data+', '+form.city.data
            capakey, adress = get_capakey(adress, form.city.data)
            form.street_name.data = adress
            nmesh = draw_houses(capakey, form.city.data)
            return render_template('index.html', title='Price Estimation for housing in Belgium', form=form , price=price, nmesh=nmesh, plot='done')
        
    return render_template('index.html', title='Price Estimation for housing in Belgium',form=form, nmesh=0, plot='')



    #(size=32, class_='country_dropdown custom-select') }}
if __name__=='__main__':
    server.run(host='0.0.0.0', port=8000)
