'''
Section AC
Topic: Final Project
Group Members: Kairui Huang, Runbo Wang, Danhiel Vu
Date: 03/13/2020

This Program address the spatial analysis question in final project
'''
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns


def get_bike_stations(df_trip):
    '''
    Return grouped bike station data

    Transfrom the bike dataframe to geodataframe
    Add extra column "count" for following dissolve
    Set coordinate reference system, same as bike dataframe.
    '''
    gdf_trip = gpd.GeoDataFrame(
        df_trip, geometry=gpd.points_from_xy(
            df_trip['startstationlongitude'], df_trip['startstationlatitude']))
    gdf_trip.loc[:, 'trip count'] = 1

    bike_stations = gdf_trip[
        ['tripduration', 'startstationid', 'geometry', 'trip count']]
    bike_stations = bike_stations.dissolve(by='startstationid', aggfunc='sum')
    bike_stations.crs = {'init': 'epsg:4326'}

    return bike_stations


def filter_transit(gdf_transit):
    '''
    Return filtered transit station data

    Filter stations that are not light rail stations
    '''
    # Filter transit type to only light rail
    filtered_gdf_transit = gdf_transit.loc[
        gdf_transit['public_transit_type'] == 'Light Rail', :]
    return filtered_gdf_transit


def create_transit_buffer(filtered_gdf_transit):
    '''
    Return a transit buffer dataframe with polygon geometry

    Create buffer for transit station.
    When New Jersey Coordinate: 40.0583° N, 74.4057° W,
    it means, 1 decimal degree change indicates about 80 km change.
    So a 0.5 mile = 0.8 km buffer is about 0.01.
    Set coordinate reference system, same as bike dataframe
    '''
    transit_buffer = filtered_gdf_transit[['station_name', 'geometry']]
    transit_buffer.loc[:, 'geometry'] = transit_buffer.loc[
        :, 'geometry'].buffer(0.01)
    transit_buffer.crs = {'init': 'epsg:4326'}

    return transit_buffer


def filter_transit_buffer(transit_buffer, bike_stations):
    '''
    Return a modified transit buffer dataframe

    Filter transit stations that do not cover any bike stations
    '''
    mod_transit_buffer = gpd.sjoin(
        transit_buffer,
        bike_stations,
        how='inner',
        op='intersects')

    return mod_transit_buffer


def filter_bike_stations(transit_buffer, bike_stations):
    '''
    Return a modified transit buffer dataframe

    Filter bikes stations that are not within any transit station
    '''
    bike_within_transit = gpd.sjoin(
        bike_stations,
        transit_buffer,
        how='inner',
        op='within')

    return bike_within_transit


def merge_bike_and_transit(bike_within_transit, filtered_gdf_transit):
    '''
    Return a dataframe that merge bike and transit station dataframes

    The merged dataframes are the two proccessed dataframe, only included
    neccessary links (bike station to transit station)
    '''
    bike_copy = bike_within_transit.reset_index()
    transit_copy = filtered_gdf_transit[['station_name', 'geometry']]
    bike_transit = transit_copy.merge(
        bike_copy,
        left_on='station_name',
        right_on='station_name',
        how='right')

    return bike_transit


def bike_to_transit_distance(bike_transit):
    '''
    Return a dataframe with distance calculated

    Create two dataframes for targeted bike stations'
    and transit stations' locationsC
    Calculate distance from bike station
    to transit station for each line
    '''
    bike_location = bike_transit[['index', 'geometry_x']]
    bike_location = gpd.GeoDataFrame(bike_location, geometry='geometry_x')
    transit_location = bike_transit[['station_name', 'geometry_y']]
    transit_location = gpd.GeoDataFrame(
        transit_location, geometry='geometry_y')
    bike_transit.loc[:, 'distance'] = bike_location.distance(transit_location)

    return bike_transit


def distribute_trips(bike_transit):
    '''
    Return a dataframe with distributed trip and trip duration

    Calculate the proportion of the distance and acorrding this
    ratio to distribute total trip counts and total trip duration.
    '''
    # Calculate the proportion of the distance
    # and acorrding this ratio to distribute trip counts.
    # So we sum the distance by bike station,
    # which includes all distance to all accessible transit stations
    # Distance ratio indicate the trip counts allocation
    total_dist = bike_transit.groupby('index')['distance'].sum()
    total_dist = total_dist.reset_index()

    distribute = bike_transit.merge(
        total_dist, left_on='index', right_on='index', how='left')
    distribute = distribute.drop(['index_right'], axis=1)
    distribute.loc[:, 'distance_ratio'] = \
        distribute['distance_x'] / distribute['distance_y']
    distribute.loc[:, 'trip_allocate'] = \
        distribute['trip count'] * distribute['distance_ratio']
    distribute.loc[:, 'tripduration_allocate'] = \
        distribute['tripduration'] * distribute['distance_ratio']

    trip_allocate = distribute.groupby(
        'station_name')['trip_allocate'].sum()
    tripduration_allocate = distribute.groupby(
        'station_name')['tripduration_allocate'].sum()
    bike_trip_conclusion = pd.concat(
        [trip_allocate, tripduration_allocate], axis=1).reset_index()

    return bike_trip_conclusion


def bike_outside_transit(bike_stations, bike_within_transit):
    '''
    Return a Seires with information about the bike stations
    that are not near any transit station

    Store all station id not within transit buffer in a set.
    Locate all the data with these id and sum their trip information.
    Transform these values: name, trip count, trip duration to a series.
    '''
    bike_outside_transit = set()
    for station in set(bike_stations.reset_index()['startstationid']):
        if station not in set(bike_within_transit.reset_index()['index']):
            bike_outside_transit.add(station)
    other = bike_stations.reset_index()
    other = other.loc[other['startstationid'].isin(bike_outside_transit), :]
    other_trip = other['trip count'].sum()
    other_tripduration = other['tripduration'].sum()
    other_row = pd.Series(
        {'station_name': 'Not within any station',
            'trip_allocate': other_trip,
            'tripduration_allocate': other_tripduration})

    return other_row


def conclude_data(bike_trip_conclusion, other_row):
    '''
    Return a dataframe that consist all results
    and correspond transit station name.

    Append the Series from parameter to conclusion dataframe,
    calculate the % of trip and trip duration.
    Then sort value by descending.
    '''
    bike_trip_conclusion = bike_trip_conclusion.append(
        other_row, ignore_index=True)
    bike_trip_conclusion.loc[:, '% trip'] = \
        bike_trip_conclusion['trip_allocate'] / \
        bike_trip_conclusion['trip_allocate'].sum()
    bike_trip_conclusion.loc[:, '% tripduration'] = \
        bike_trip_conclusion['tripduration_allocate'] / \
        bike_trip_conclusion['tripduration_allocate'].sum()
    bike_trip_conclusion = bike_trip_conclusion.sort_values(
        by=['% trip', '% tripduration'], ascending=False)

    return bike_trip_conclusion


def sptial_plot(
        mod_transit_buffer,
        gdf_jersey, bike_stations,
        bike_within_transit,
        bike_trip_conclusion):
    '''
    Save a figure that represent the spatial distribution of bikes
    and frequency of bike usage near transit stations.

    Add % trip information to the transit buffer geodataframe.
    Jersey city parcel is the bottom layer.
    Transit station buffer is second layer with transparancy.
    All bike stations is third layer.
    Bike station within transit station is top layer.
    '''
    conlusion_transit = mod_transit_buffer.drop_duplicates('station_name')
    conclusion_buffer = conlusion_transit.merge(
        bike_trip_conclusion,
        left_on='station_name',
        right_on='station_name',
        how='inner')
    with sns.plotting_context(rc={"legend.fontsize": 15}):
        fig, ax = plt.subplots(1, figsize=(20, 15))
        gdf_jersey.plot(ax=ax, color='#AAAAAA')
        conclusion_buffer.plot(
            ax=ax, column='% trip', legend=True, alpha=0.3, edgecolor='black')
        bike_stations.plot(ax=ax, markersize=40)
        bike_within_transit.plot(ax=ax, color='#FF9923', markersize=40)
        fig.suptitle('station distribution plot', fontsize=30)
        plt.xlabel('Longitude', fontsize=25)
        plt.ylabel('Latitude', fontsize=25)
        ax.xaxis.label.set_size(20)
        ax.yaxis.label.set_size(20)

        # may need to change the path
        plt.savefig('station distribution plot.png')


def pie_chart(bike_trip_conclusion):
    '''
    Save a figure that plot the % of bike counts for each transit station
    (over total bike counts from 2015 - 2019)

    Filter the least representative data as other stations,
    sum the trip information for these station and append it back.
    Draw the pie chart based on the calculated % bike trip distribution
    among the transit stations.
    '''
    other_stations = bike_trip_conclusion.loc[
        bike_trip_conclusion['% trip'] < 0.01, :]
    pie_chart_conclusion = bike_trip_conclusion.loc[
        bike_trip_conclusion['% trip'] >= 0.01, :]
    if len(other_stations) > 0:
        pie_chart_conclusion = pie_chart_conclusion.append({
            'station_name': 'Other Stations',
            'trip_allocate': other_stations['trip_allocate'].sum(),
            'tripduration_allocate': other_stations[
                'tripduration_allocate'].sum(),
            '% trip': other_stations['% trip'].sum(),
            '% tripduration': other_stations['% tripduration'].sum()
            }, ignore_index=True)
    sns.set_style('darkgrid', {"xtick.major.size": 10, "ytick.major.size": 10})
    with sns.plotting_context(rc={"legend.fontsize": 15}):
        fig, ax = plt.subplots(figsize=(30, 30))
        labels = pie_chart_conclusion['station_name']
        fracs = pie_chart_conclusion['% trip']
        ax.pie(
            fracs, labels=labels,
            autopct='%1.1f%%',
            textprops={'fontsize': 40})
        plt.title('Trip Counts in % By Transit Stations', fontsize=60)

    # may need to change the path
    plt.savefig('pie_chart.png')


def main():
    '''
    This function first reads all the files needed
    and run the above functions step by step.
    Then, plot the graphs with concluded table.
    '''
    df_trip = pd.read_csv('filtered_bike_data.csv')
    gdf_transit = gpd.read_file('jersey-city-public-transit.geojson')
    gdf_jersey = gpd.read_file('jersey-city-parcels.geojson')

    bike_stations = get_bike_stations(df_trip)
    filtered_gdf_transit = filter_transit(gdf_transit)
    transit_buffer = create_transit_buffer(filtered_gdf_transit)
    mod_transit_buffer = filter_transit_buffer(transit_buffer, bike_stations)
    bike_within_transit = filter_bike_stations(transit_buffer, bike_stations)
    bike_transit = merge_bike_and_transit(
        bike_within_transit, filtered_gdf_transit)
    bike_transit = bike_to_transit_distance(bike_transit)
    bike_trip_conclusion = distribute_trips(bike_transit)
    other_row = bike_outside_transit(bike_stations, bike_within_transit)
    bike_trip_conclusion = conclude_data(bike_trip_conclusion, other_row)

    sptial_plot(
        mod_transit_buffer,
        gdf_jersey,
        bike_stations,
        bike_within_transit,
        bike_trip_conclusion)

    pie_chart(bike_trip_conclusion)


if __name__ == '__main__':
    main()
