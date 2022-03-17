'''
Section AC
Topic: Final Project
Group Members: Kairui Huang, Runbo Wang, Danhiel Vu
Date: 03/13/2020

This Program test the code of spatial analysis part,
whether it runs successfully and correctly.
'''

from assert_equal import assert_equals
import question1

import pandas as pd
import geopandas as gpd


def test_spatial_analysis():
    """
    Tests the function spatial_analysis
    """
    print('Testing spatial_analysis')

    # To test the spatiao analysis function, we first need to
    # genereate the three documents, which will be taken into parameters.
    # The frist document needs to be bike trip data with longitude, latatidue,
    # start station id, and tripduration.

    # need to change the path
    df = pd.read_csv('filtered_bike_data.csv')
    doc1 = df.sample(1000)

    # The second document is the transit station data,
    # must have geometry, transit type, and station name.
    doc2 = gpd.read_file('jersey-city-public-transit.geojson')

    # This is just the base map of Jersey City
    doc3 = gpd.read_file('jersey-city-parcels.geojson')

    result = question1.spatial_analysis(doc1, doc2, doc3)
    assert_equals(float(len(doc1)), result['trip_allocate'].sum())
    assert_equals(1.0, result['% trip'].sum())
    assert_equals(1.0, result['% tripduration'].sum())

    print('Test spatial_analysis: Success')


def main():
    test_spatial_analysis()


if __name__ == '__main__':
    main()
