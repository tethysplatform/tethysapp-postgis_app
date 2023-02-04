import json
from django.shortcuts import render
from tethys_sdk.gizmos import *
from tethys_sdk.routing import controller
from .model import AddressPoint, FloodExtent

from tethysapp.postgis_app.app import PostgisApp as app


@controller
def home(request):
    """
    Controller for the app home page.
    """
    # Create a session in preparation for working with the database
    Session = app.get_persistent_store_database('flooded_addresses', as_sessionmaker=True)
    session = Session()

    # Query the database for all the address points
    # Convert to GeoJSON format on the fly
    address_points = session.query(AddressPoint.geometry.ST_AsGeoJSON()).all()

    # Create a feature collection of GeoJSON features
    features = []

    for address_point in address_points:
        address_point_feature = {
            'type': 'Feature',
            'geometry': json.loads(address_point[0])
        }

        features.append(address_point_feature)

    geojson_address_points = {
        'type': 'FeatureCollection',
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        },
        'features': features
    }

    # Create a Map View Layer with from the GeoJSON
    address_points_layer = MVLayer(
        source='GeoJSON',
        options=geojson_address_points,
        legend_title='Address Points',
        legend_extent=[-111.74, 40.20, -111.61, 40.33],
    )

    # Define the initial view of the map
    initial_view = MVView(
        projection='EPSG:4326',
        center=[-111.6608, 40.2444],
        zoom=12
    )

    # Define the map
    map_options = MapView(
        height='100%',
        width='100%',
        controls=[{'MousePosition': {'projection': 'EPSG:4326'}}],
        layers=[address_points_layer],
        basemap=['OpenStreetMap'],
        view=initial_view,
        legend=True
    )

    context = {'map_options': map_options}

    # Close the session to prevent problems with the database
    session.close()

    return render(request, 'postgis_app/home.html', context)


@controller
def flood(request):
    """
    Controller for flood page
    """
    # Create a session in preparation for working with the database
    Session = app.get_persistent_store_database('flooded_addresses', as_sessionmaker=True)
    session = Session()

    # Query for all the flood extents
    # Convert to GeoJSON on the fly
    flood_extents = session.query(FloodExtent.geometry.ST_AsGeoJSON(), FloodExtent.map_id).all()

    # Create a Map View Layer from each flood extent GeoJSON
    layers = []

    for flood_extent in flood_extents:
        flood_extent_feature = {
            'type': 'Feature',
            'geometry': json.loads(flood_extent[0])
        }

        geojson_flood_extent = {
            'type': 'FeatureCollection',
            'crs': {
                'type': 'name',
                'properties': {
                    'name': 'EPSG:4326'
                }
            },
            'features': [flood_extent_feature]
        }

        flood_extent_layer = MVLayer(
            source='GeoJSON',
            options=geojson_flood_extent,
            legend_title='FloodExtent {0}'.format(flood_extent.map_id),
            legend_extent=[-111.74, 40.21, -111.61, 40.27],
        )

        layers.append(flood_extent_layer)

    # Define the initial view of the map
    initial_view = MVView(
        projection='EPSG:4326',
        center=[-111.6608, 40.2444],
        zoom=12
    )

    # Define the map
    map_options = MapView(
        height='100%',
        width='100%',
        controls=[{'MousePosition': {'projection': 'EPSG:4326'}}],
        layers=layers,
        basemap=['OpenStreetMap'],
        view=initial_view,
        legend=True
    )

    context = {'map_options': map_options}

    # Close the session to prevent problems with the database
    session.close()

    return render(request, 'postgis_app/flood.html', context)


@controller(url='flooded-addresses/{url_id}')
def flooded_addresses(request, url_id):
    """
    Controller for flooded address page
    """
    # Create a session in preparation for working with the database
    Session = app.get_persistent_store_database('flooded_addresses', as_sessionmaker=True)
    session = Session()

    # Query for a single Flood Extent by id
    # Convert to GeoJSON on the fly
    flood_extent = session.query(FloodExtent.geometry.ST_AsGeoJSON(), FloodExtent.map_id). \
        filter(FloodExtent.id == int(url_id)). \
        one()

    # Create a GeoJSON feature collection for the flood extent
    flood_extent_feature = {
        'type': 'Feature',
        'geometry': json.loads(flood_extent[0])
    }

    geojson_flood_extent = {
        'type': 'FeatureCollection',
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        },
        'features': [flood_extent_feature]
    }

    # Create a Map View Layer from the GeoJSON feature collection
    flood_extent_layer = MVLayer(
        source='GeoJSON',
        options=geojson_flood_extent,
        legend_title='FloodExtent {0}'.format(flood_extent.map_id),
        legend_extent=[-111.74, 40.21, -111.61, 40.27],
    )

    # Query for address points that fall within (intersect) the flood extent
    flood_extent_as_wkt = session.query(FloodExtent.geometry.ST_AsText()). \
        filter(FloodExtent.id == int(url_id)). \
        one()

    wkt = 'SRID=4326;{0}'.format(flood_extent_as_wkt[0])

    flooded_addresses_query = session.query(AddressPoint.geometry.ST_AsGeoJSON()). \
        filter(AddressPoint.geometry.ST_Intersects(wkt)). \
        all()

    # Create a GeoJSON feature collection of the address points
    features = []

    for address_point in flooded_addresses_query:
        address_point_feature = {
            'type': 'Feature',
            'geometry': json.loads(address_point[0])
        }

        features.append(address_point_feature)

    geojson_address_points = {
        'type': 'FeatureCollection',
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        },
        'features': features
    }

    # Create a Map View Layer from the GeoJSON
    flooded_addresses_layer = MVLayer(
        source='GeoJSON',
        options=geojson_address_points,
        legend_title='Flooded Addresses',
        legend_extent=[-111.74, 40.20, -111.61, 40.33],
    )

    # Define the initial view of the map
    initial_view = MVView(
        projection='EPSG:4326',
        center=[-111.6608, 40.2444],
        zoom=12
    )

    # Define the map
    map_options = MapView(
        height='100%',
        width='100%',
        layers=[flooded_addresses_layer, flood_extent_layer],
        basemap=['OpenStreetMap'],
        view=initial_view,
        legend=True
    )

    context = {
        'map_options': map_options,
        'id': url_id
    }
    
    # Close the session to prevent problems with the database          
    session.close()

    return render(request, 'postgis_app/flood.html', context)


@controller(name='list', url='flooded-addresses/{url_id}/list')
def list_flooded_addresses(request, url_id):
    """
    Controller for listing flooded Addresses
    """
    # Create a session in preparation for working with the database
    Session = app.get_persistent_store_database('flooded_addresses', as_sessionmaker=True)
    session = Session()

    # Query the database for address points that fall within the flood extent
    flood_extent_as_wkt = session.query(FloodExtent.geometry.ST_AsText()). \
        filter(FloodExtent.id == int(url_id)). \
        one()

    wkt = 'SRID=4326;{0}'.format(flood_extent_as_wkt[0])

    flooded_addresses_query = session.query(AddressPoint). \
        filter(AddressPoint.geometry.ST_Intersects(wkt)). \
        all()

    context = {
        'flooded_addresses': flooded_addresses_query,
        'id': url_id
    }

    # Close the session to prevent problems with the database
    session.close()

    return render(request, 'postgis_app/list.html', context)
