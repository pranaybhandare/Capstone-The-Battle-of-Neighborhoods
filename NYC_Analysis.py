#Import libraries
import pandas as pd
from geopy.geocoders import Nominatim
import matplotlib.cm as cm
import matplotlib.colors as colors
from sklearn.cluster import KMeans
import folium
import requests
from pandas.io.json import json_normalize
import numpy as np

#### AIRBNB DATA  ####
airbnb_df = pd.read_csv('Airbnb_Data.csv')
#df shape
airbnb_df.shape
#columns
airbnb_df.columns
#Initial drop of columns
airbnb_df.drop(['id', 'host_id', 'host_name', 'latitude', 'longitude', 'last_review'], axis = 1, inplace = True)
#Change column name
airbnb_df.rename(columns = {'calculated_host_listings_count': 'Total_Listings', 'availability_365': 'Yearly_Availability'}, inplace = True)

## EDA ##

# number of unique neighborhood_groups
airbnb_df['neighbourhood_group'].unique()
# number of unique neighborhoods
airbnb_df['neighbourhood'].unique()

#Only interested in BK and Manhattan neighborhood groups
neighbourhood_grps = ['Brooklyn', 'Manhattan']
airbnb_df = airbnb_df[airbnb_df.neighbourhood_group.isin(neighbourhood_grps)]

#Average price of Brooklyn & Manhattan listings 
airbnb_df.groupby('neighbourhood_group')['price'].mean().round(2)

#count of each room type of listings in BK & Manhattan
airbnb_df.groupby('neighbourhood_group')['room_type'].value_counts()[0]

#pie graph for type of rooms in BK and Manhattan
import matplotlib.pyplot as plt
BK_roomtype_chart  = [airbnb_df.groupby('neighbourhood_group')['room_type'].value_counts()[0], airbnb_df.groupby('neighbourhood_group')['room_type'].value_counts()[1], airbnb_df.groupby('neighbourhood_group')['room_type'].value_counts()[2]]
BK_labels = 'Private Room', 'Entire home/apt', 'Shared room'
plt.pie(BK_roomtype_chart, labels = BK_labels, autopct = '%1.1f%%')
plt.title('BK Room Types')
plt.axis('equal')
plt.show()

Manhattan_roomtype_chart = [airbnb_df.groupby('neighbourhood_group')['room_type'].value_counts()[3], airbnb_df.groupby('neighbourhood_group')['room_type'].value_counts()[4], airbnb_df.groupby('neighbourhood_group')['room_type'].value_counts()[5]]
Manhattan_labels = 'Private Room', 'Entire home/apt', 'Shared room'
plt.pie(Manhattan_roomtype_chart, labels = Manhattan_labels, autopct = '%1.1f%%')
plt.title('Manhattan Room Types')
plt.axis('equal')
plt.show()

#NYC neighborhood data
import urllib
import json
import pathlib

url = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DS0701EN-SkillsNetwork/labs/newyork_data.json'
r = requests.get(url)
pathlib.Path('data.json').write_bytes(r.content)

with open('data.json') as json_data:
    newyork_data = json.load(json_data)

neighborhoods_data = newyork_data['features']
neighborhoods_data[0]

#define the df columns
column_names = ['Borough', 'Neighborhood', 'Latitude', 'Longitude']
neighborhoods = pd.DataFrame(columns = column_names)

#Loop through json and fill the df row at a time - n
for data in neighborhoods_data:
    borough = neighborhood_name = data['properties']['borough']
    neighborhood_name = data['properties']['name']

    neighborhood_latlon = data['geometry']['coordinates']
    neighborhood_lat = neighborhood_latlon[1]
    neighborhood_lon = neighborhood_latlon[0]
    
    neighborhoods = neighborhoods.append({'Borough': borough,
                                          'Neighborhood': neighborhood_name,
                                          'Latitude': neighborhood_lat,
                                          'Longitude': neighborhood_lon}, ignore_index=True)

#NY lat and long values
address = 'New York City, NY'

geolocator = Nominatim(user_agent="ny_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of New York City are {}, {}.'.format(latitude, longitude))

#Create a map of NY with neighborhoods superimposed on top
map_newyork = folium.Map(location=[latitude, longitude], zoom_start=10)

# add markers to map
for lat, lng, borough, neighborhood in zip(neighborhoods['Latitude'], neighborhoods['Longitude'], neighborhoods['Borough'], neighborhoods['Neighborhood']):
    label = '{}, {}'.format(neighborhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_newyork)  
    
map_newyork

#Slice for only BK and manhattan boroughs
NYC_data = neighborhoods[neighborhoods.Borough.isin(neighbourhood_grps)].reset_index(drop = True)

#Create map of only BK/Manhattan neighborhoods
map_BK_Manhattan = folium.Map(location=[latitude, longitude], zoom_start=10)
for lat, lng, borough, neighborhood in zip(NYC_data['Latitude'], NYC_data['Longitude'], NYC_data['Borough'], NYC_data['Neighborhood']):
    label = '{}, {}'.format(neighborhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_BK_Manhattan)  
    
map_BK_Manhattan

#Define 4square credentials
CLIENT_ID = 'HPZZ3EGEUVTHDDQSTKFKNA205RJNFXN0Z4J0QUZWHHVYYJF3' # your Foursquare ID
CLIENT_SECRET = 'NIWQYH3UIY0XUP3WYK4I34U5JGAHZR3TB4AUPLWOA452XEZA' # your Foursquare Secret
VERSION = '20180605' # Foursquare API version
LIMIT = 100 # A default Foursquare API limit value

print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)

#Manhattan neighborhoods - contains only the borough  of Manhattan
Manhattan_data = NYC_data[NYC_data['Borough'] == 'Manhattan'].reset_index(drop = True)
#BK neighborhoods - contains only the borough  of BK
BK_data = NYC_data[NYC_data['Borough'] == 'Brooklyn'].reset_index(drop = True)

#Function to extract all the neighborhoods in Manhattan
def getNearbyVenues(names, latitudes, longitudes, radius=500):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)

#manhattan venues
manhattan_venues  = getNearbyVenues(names = Manhattan_data['Neighborhood'], latitudes = Manhattan_data['Latitude'], longitudes = Manhattan_data['Longitude'])
#print(manhattan_venues.shape)
manhattan_venues.shape

#BK venues
BK_venues  = getNearbyVenues(names = BK_data['Neighborhood'], latitudes = BK_data['Latitude'], longitudes = BK_data['Longitude'])
print(BK_venues.shape)
BK_venues.head()

#Manhattan neighborhoods analysis
manhattan_venues.groupby('Neighborhood').count()
print('There are {} uniques categories.'.format(len(manhattan_venues['Venue Category'].unique())))

BK_venues.groupby('Neighborhood').count()
print('There are {} uniques categories.'.format(len(BK_venues['Venue Category'].unique())))

# one hot encoding
manhattan_onehot = pd.get_dummies(manhattan_venues[['Venue Category']], prefix="", prefix_sep="")
BK_onehot = pd.get_dummies(BK_venues[['Venue Category']], prefix="", prefix_sep="")


# add neighborhood column back to dataframe
manhattan_onehot['Neighborhood'] = manhattan_venues['Neighborhood'] 
BK_onehot['Neighborhood'] = BK_venues['Neighborhood'] 

# move neighborhood column to the first column
fixed_columns = [manhattan_onehot.columns[-1]] + list(manhattan_onehot.columns[:-1])
manhattan_onehot = manhattan_onehot[fixed_columns]
manhattan_onehot.head()

BK_fixed_columns = [BK_onehot.columns[-1]] + list(BK_onehot.columns[:-1])
BK_onehot = BK_onehot[BK_fixed_columns]
BK_onehot.head()

#lets group by neighborhood and take the mean of the frequence of occurence of each category
manhattan_grouped = manhattan_onehot.groupby('Neighborhood').mean().reset_index()
manhattan_grouped

BK_grouped = BK_onehot.groupby('Neighborhood').mean().reset_index()
BK_grouped

#top 10 venues by neighborhood
num_top_venues = 10

for hood in manhattan_grouped['Neighborhood']:
    print("----"+hood+"----")
    temp = manhattan_grouped[manhattan_grouped['Neighborhood'] == hood].T.reset_index()
    temp.columns = ['venue','freq']
    temp = temp.iloc[1:]
    temp['freq'] = temp['freq'].astype(float)
    temp = temp.round({'freq': 2})
    print(temp.sort_values('freq', ascending=False).reset_index(drop=True).head(num_top_venues))
    print('\n')

for hood in BK_grouped['Neighborhood']:
    print("----"+hood+"----")
    temp = BK_grouped[BK_grouped['Neighborhood'] == hood].T.reset_index()
    temp.columns = ['venue','freq']
    temp = temp.iloc[1:]
    temp['freq'] = temp['freq'].astype(float)
    temp = temp.round({'freq': 2})
    print(temp.sort_values('freq', ascending=False).reset_index(drop=True).head(num_top_venues))
    print('\n')

#Function to sort the venues in descending order for each neighborhood
def return_most_common_venues(row, num_top_venues):
    row_categories = row.iloc[1:]
    row_categories_sorted = row_categories.sort_values(ascending=False)
    
    return row_categories_sorted.index.values[0:num_top_venues]

#Lets  create a dataframe and display the 10 ten venues for each  neighborhood
indicators = ['st', 'nd', 'rd']

# create columns according to number of top venues
columns = ['Neighborhood']
for ind in np.arange(num_top_venues):
    try:
        columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
    except:
        columns.append('{}th Most Common Venue'.format(ind+1))

# create a new dataframe
neighborhoods_venues_sorted = pd.DataFrame(columns=columns)
neighborhoods_venues_sorted['Neighborhood'] = manhattan_grouped['Neighborhood']

for ind in np.arange(manhattan_grouped.shape[0]):
    neighborhoods_venues_sorted.iloc[ind, 1:] = return_most_common_venues(manhattan_grouped.iloc[ind, :], num_top_venues)

#df for Manhattan venues
neighborhoods_venues_sorted.head()

BK_neighborhoods_venues_sorted = pd.DataFrame(columns=columns)
BK_neighborhoods_venues_sorted['Neighborhood'] = BK_grouped['Neighborhood']

for ind in np.arange(BK_grouped.shape[0]):
    BK_neighborhoods_venues_sorted.iloc[ind, 1:] = return_most_common_venues(BK_grouped.iloc[ind, :], num_top_venues)
#df for BK venues 
BK_neighborhoods_venues_sorted.head()

#Cluster Analysis for Manhattan 
# set number of clusters
kclusters = 3

manhattan_grouped_clustering = manhattan_grouped.drop('Neighborhood', 1)

# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(manhattan_grouped_clustering)

# check cluster labels generated for each row in the dataframe
kmeans.labels_ 

#MANHATTAN VENUES
# add clustering labels
neighborhoods_venues_sorted.insert(0, 'Cluster Labels', kmeans.labels_)

manhattan_merged = manhattan_venues

# merge manhattan_grouped with manhattan_data to add latitude/longitude for each neighborhood
manhattan_merged = manhattan_merged.join(neighborhoods_venues_sorted.set_index('Neighborhood'), on='Neighborhood')

manhattan_merged.head() # check the last columns!

##BK Cluster
BK_kclusters = 3
BK_grouped_clustering = BK_grouped.drop('Neighborhood', 1)
BK_kmeans = KMeans(n_clusters=BK_kclusters, random_state=0).fit(BK_grouped_clustering)
BK_kmeans.labels_
BK_neighborhoods_venues_sorted.insert(0, 'Cluster Labels', BK_kmeans.labels_)
BK_merged = BK_venues
BK_merged = BK_merged.join(BK_neighborhoods_venues_sorted.set_index('Neighborhood'), on = 'Neighborhood')
BK_merged.head()

#Visualize Manhattan Clusters
# create map
Manhattan_map_clusters = folium.Map(location=[latitude, longitude], zoom_start=11)

# set color scheme for the clusters
x = np.arange(kclusters)
ys = [i + x + (i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, poi, cluster in zip(manhattan_merged['Neighborhood Latitude'], manhattan_merged['Neighborhood Longitude'], manhattan_merged['Neighborhood'], manhattan_merged['Cluster Labels']):
    label = folium.Popup(str(poi) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(Manhattan_map_clusters)
       
Manhattan_map_clusters

#Visualize BK clusters
BK_map_clusters = folium.Map(location=[latitude, longitude], zoom_start=11)

# set color scheme for the clusters
x = np.arange(BK_kclusters)
ys = [i + x + (i*x)**2 for i in range(BK_kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, poi, cluster in zip(BK_merged['Neighborhood Latitude'], BK_merged['Neighborhood Longitude'], BK_merged['Neighborhood'], BK_merged['Cluster Labels']):
    label = folium.Popup(str(poi) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(BK_map_clusters)
       
BK_map_clusters


