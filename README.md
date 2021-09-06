# Belgian Houses 3D visualization and Price prediction

This application allows to vizualise and predict the price of any building in Belgium.
The price prediction is based on a [XGBoost model](https://github.com/Nathanael-Mariaule/Belgium-immo-price-prediction). The [web app](http://nathanael-mrl.be) was build using Flask.

Currently the 3D visualization is limited to the city of Oostkamp due to server limitations and
non-optimized database construction.

To use the app type the followings commands:

1. docker-compose build  #build docker environment
2. docker-compose run flask\_app python database_initializer.py   #build database
3. docker-compose up #launch app

Remark: if one want to increase the database for cities other than Oostkamp, one need to edit the file database/cities as described in database/database_creator.py


#### This project was designed as part of the [Becode](https://becode.org/) AI's formation.


## App Structure:
The application is divided into 3 tasks:
- **Database builder**: LIDAR datas and belgian houses adresses and cadastral plan are collected from public databases. These datas are then split, cut and transformed to speed up further use in the app. This part is contained in the _database_ folder.
- **3D modeling**: The algorithm receives tiff-files with LIDAR datas from a cadastral area and build using [Open3D](http://www.open3d.org/)  a modelization of the data. It stores the 3D models as PLY file to be displayed by the web app. This part is contained in the _flask\_app/python\_scripts_
- **Web app**: The user interact with the [web application](http://nathanael-mrl.be). He enter as input the adress of a house and its caracteristics. The app retrieves then the 3D model and price prediction and display it in a [Three.js](https://threejs.org/) canvas.  See _flask\_app_ folder
<p align="center">
    <img src="https://github.com/Nathanael-Mariaule/Belgium_3D_immo/blob/main/Doc/program_structure.svg">
</p>

## Data collection and pre-processing
This application use 3 datasets:
- **Adresse location catalogus** : This [public dataset](https://download.vlaanderen.be/Producten/Detail?id=447&title=CRAB_Adressenlijst#) contains the adress and geographic coordinates of each property in Vlanderen. This dataset is used to get the precise geographic coordinate and not rely less precise geographic API.

- **Cadastre Plan**: We use the dataset of the [belgian fiscal service](https://eservices.minfin.fgov.be/myminfin-web/pages/cadastral-plans) to get the belgian cadastral plans. This contains the geographic coordinates of every cadastral area and every building in Belgium.

- **LIDAR datas**: The LIDAR datas were collected by the belgian service public [1](https://download.vlaanderen.be/Producten/Detail?id=939&title=Digitaal_Hoogtemodel_Vlaanderen_II_DTM_raster_1_m), [2](https://download.vlaanderen.be/Producten/Detail?id=939&title=Digitaal_Hoogtemodel_Vlaanderen_II_DSM_raster_1_m) It consists of LIDAR data collected using drone i.e. spatial coordinates of the belgian territory. The DTM contains informations at the level of the ground while the DSM contains building, trees,... informations.

### Problem: each DSM/DTM has size 1Go+
It is difficult to store all these datas. Also, this make 3D rendering very slow as we have to manipulate these big file to extract the 3D meshes.

**Solution**: We split the file into small pieces

Using the cadastral plans, we cut the area corresponding to an adress in the DSM and DTM file and store them in a compressed folder. This allows faster loading of the LIDAR data and reduced storage space.

When a user enter an adresse, the API use the adresse catalogus to determine the CaPaKey of the adress (i.e. a unique ID). Then, it collect the following compressed folder:
```
 capakey_of_adress
 |- cadastre.pickle
 |- dsm.tiff
 |- dtm.tiff
```
The dsm.tiff and dtm.tiff contains the LIDAR data on the parcel and cadastre.pickle contains the geographic data of the buildings.



__Remark:__ We use datasets for the region of Vlanderen. The same data exits for the region of Wallonia.


## 3D modelization
The 3D representation is done using Open3D. 
<p align="center">
    <img src="https://github.com/Nathanael-Mariaule/Belgium_3D_immo/blob/main/Doc/3d_house.png">
</p>
When the user input an adress, the algorithm collect the LIDAR points in the cadastral area of the adress and compute the following 3D meshes:

#### 1. The ground area:
A ball pivoting algorithm [BM99] implemented in open3d is applied on the LIDAR point from the DTM-file to generate a good resolution modeling of the land.

#### 2. The house:
The house is build using many meshes. First, we use the cadastral data to get the coordinates of the boundaries of the house. We compute a likely hight for the walls using the LIDAR points and create a rectangle mesh for each wall. Then we use a convex hull to generate a mesh for the roof.

<p align="center">
    <img src="https://github.com/Nathanael-Mariaule/Belgium_3D_immo/blob/main/Doc/convex_hull.png">
</p>

**Problem:**  it could happens that the convex hull is to big and contains points outside the house.

So we first split the house area into smaller pieces so that in each piece the convex hull stays inside the house area.

<p align="center">
    <img src="https://github.com/Nathanael-Mariaule/Belgium_3D_immo/blob/main/Doc/convex_pieces.png">
</p>
 
#### 3. Everything else: 
We have no information about what could be these points (it is very likely that it is vegetation). So we leave the points cloud as it is. Though for clarity, we remove the points that are too close from the house.

## Web App
The web app is developped with [Flask](https://flask.palletsprojects.com/en/2.0.x/). A Flask form is used to collect inputs from the user that are fed to the API. It uses [Three.js](https://threejs.org/) a powerfull javascript library to display the 3D objects in the browser.




## Further Possible improvements:
- **Database:** At the moment the database is poorly designed and can be improved in many ways. First, we can reduce the memory space by storing the LIDAR data in arrays instead of tiff-file and by using a better compression format. Second, we should use ad-hoc system to store the database.

- **Optimization of the App:** Currently, the app does not support many simultaneous request (mostly due to the database building). Many steps in the process can be speed up (generation of the 3D-meshes using multithreading, creation of a "cache" to avoid mutiple creation of the same model,...)

- **3D visualization:** Machine learning algorithm can be used to improve the rendering (e.g. to get better result for the walls). Also, it remains some bugs during the generation of the roof.

- **Price prediction:** The model for price prediction can be improved as discussed in [the following repo](https://github.com/Nathanael-Mariaule/Belgium-immo-price-prediction).




## References:
[BM99] F. Bernardini and J. Mittleman and HRushmeier and C. Silva and G. Taubin: The ball-pivoting algorithm for surface reconstruction, IEEE transactions on visualization and computer graphics, 5(4), 349-359, 1999



