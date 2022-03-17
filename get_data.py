"""
Section AC
Topic: Final Project
Group Members: Kairui Huang, Runbo Wang, Danhiel Vu
Date: 03/13/2020

Gets all the respective Jersey City, CitiBike datas and
organizes/reformats it the data for it to compatible
when used from other classes.
"""
import os
import sys
import zipfile
from urllib.request import urlretrieve
import shutil

import pandas as pd


def get_data(start_year, end_year, start_month):
    """
    Returns the data from the specified starting year and month
    to the ending year. The data is about Jersey City, Citi Bike
    trips.

    @param start_year  | starting year
    @param end_year    | ending year
    @param start_month | starting month
    """
    urls = get_urls(start_year, end_year, start_month)

    csv_file_path, zip_file_path = get_file_path()
    extract_files(urls, zip_file_path, csv_file_path)
    csv_file_path, zip_file_path = get_file_path()

    return get_combined_csv_files(csv_file_path)


def get_urls(start_year, end_year, start_month):
    """
    Generates all the urls from the inputted date to the end,
    returning an array of all the urls created.

    @param start_year  | starting year
    @param end_year    | ending year
    @param start_month | starting month
    """
    base_url = 'https://s3.amazonaws.com/tripdata/JC-'
    end_url = '-citibike-tripdata.csv.zip'
    urls = []
    for year in range(start_year, end_year + 1):
        for month in range(start_month, 13):
            if year == 2017 and month == 8:
                url = base_url + '201708%20citibike-tripdata.csv.zip'
                urls.append(url)
            elif month < 10:
                url = base_url + str(year) + "0" + str(month) + end_url
                urls.append(url)
            elif month >= 10:
                url = base_url + str(year) + str(month) + end_url
                urls.append(url)
        start_month = 1
    return urls


def get_file_path():
    """
    Get the file paths of the csv and zip files and
    returns it as a tuple.
    """
    csv_file_path = sys.path[0] + "/JCfiles"
    zip_file_path = sys.path[0] + "/ZIPfiles"
    if not os.path.exists(csv_file_path):
        os.makedirs(csv_file_path)
    if not os.path.exists(zip_file_path):
        os.makedirs(zip_file_path)
    return (csv_file_path, zip_file_path)


def extract_files(urls, zip_file_path, csv_file_path):
    """
    Extract files from zip and csv file and deletes
    all temporary zip files.

    @param urls          | list containing all url links.
    @param zip_file_path | the zip file path name
    @param csv_file_path | the csv file path name
    """
    for i in range(len(urls)):
        print("downloading " + urls[i])
        zip_filename = zip_file_path + "/" + str(i + 1) + ".zip"
        urlretrieve(urls[i], zip_filename)
        print("extracting " + urls[i] + "\n")
        extracting = zipfile.ZipFile(zip_filename)
        extracting.extractall(csv_file_path)

    print("download & extract complete")
    print("deleting all temporary zip files")
    extracting.close()
    shutil.rmtree(zip_file_path)
    print("complete")


def get_combined_csv_files(csv_file_path):
    """
    Combines all the csv file and returns it.

    @param csv_file_path | the csv file path name
    """
    trip_file_list = []
    all_trip_file = pd.DataFrame()
    print("Combining CSV Files: Started")
    for file_name in os.listdir(csv_file_path):
        trip_file_list.append(file_name)

    for i in range(len(trip_file_list)):
        df = pd.read_csv(csv_file_path + "/" + trip_file_list[i])
        df.columns = map(str.lower, df.columns)
        df.columns = df.columns.str.replace(' ', '')
        all_trip_file = all_trip_file.append(df, ignore_index=True)

    all_trip_file.to_csv(sys.path[0] + '/bike_data.csv',
                         index=None, header=True)
    print("Combining CSV Files: Complete")
    return all_trip_file


def data_cleaning(bike_data):
    """
    Cleans the data by removing age outliers, null values,
    and adds new columns of periods, peaks, seasons, and
    age.

    @param bike_data | Tripdata from Jersey City Citi Bikes.
    """
    print('Cleaning Data: Starting')

    # Drop NaN
    df = bike_data
    df = df.dropna()

    # Remove the data that destinations are in New York City
    jersey = set(df['startstationname'])
    df = df.loc[df['endstationname'].isin(jersey)]

    add_column_periods(df)
    add_column_peaks(df)
    add_column_seasons(df)
    add_column_age(df)

    df.to_csv('fliterd_data.csv', index=None, header=True)
    print('Cleaning Data: Completed')


def add_column_periods(df):
    """
    Add new column to the dataframe representing
    morning/afternoon/evening/midnight

    @param df | the dataframe to be modified.
    """
    df.loc[:, 'Hour'] = pd.to_datetime(df['starttime']).dt.hour
    df.loc[df['Hour'] < 5, 'Period'] = 'Midnight'
    df.loc[(df['Hour'] >= 5) & (df['Hour'] < 12), 'Period'] = 'Morning'
    df.loc[(df['Hour'] >= 12) & (df['Hour'] < 17), 'Period'] = 'Afternoon'
    df.loc[df['Hour'] >= 17, 'Period'] = 'Evening'


def add_column_peaks(df):
    """
    Add new column to the dataframe representing peak/off-peak

    @param df | the dataframe to be modified.
    """
    df.loc[((df['Hour'] >= 6) & (df['Hour'] < 10)) | ((df['Hour'] >= 16) &
           (df['Hour'] < 20)), 'Peak'] = 'Peak'
    df.loc[df['Peak'] != 'Peak', 'Peak'] = 'Off Peak'


def add_column_seasons(df):
    """
    Add a new column to the dataframe representing the
    different seasons: Winter, Spring, Summer, and Autumn.

    @param df | the dataframe to be modified.
    """
    df.loc[:, 'month'] = pd.to_datetime(df['starttime']).dt.month
    df.loc[(df['month'] == 12) | (df['month'] == 1) |
           (df['month'] == 2), 'Season'] = 'Winter'
    df.loc[(df['month'] == 3) | (df['month'] == 4) |
           (df['month'] == 5), 'Season'] = 'Spring'
    df.loc[(df['month'] == 6) | (df['month'] == 7) |
           (df['month'] == 8), 'Season'] = 'Summer'
    df.loc[(df['month'] == 9) | (df['month'] == 10) |
           (df['month'] == 11), 'Season'] = 'Autumn'


def add_column_age(df):
    """
    Changes the dataframes' birth year to age and filters outliers

    @param df | the dataframe to be modified.
    """
    df.loc[:, 'year'] = pd.to_datetime(df['starttime']).dt.year
    df.loc[:, 'age'] = df['year'] - df['birthyear']
    df = df.loc[df['age'] < 90, :]


def main():
    """
    Saves the trip datas from CitiBike and cleans it.
    """
    data_cleaning(get_data(2015, 2019, 9))


if __name__ == '__main__':
    main()
