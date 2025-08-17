#!/usr/bin/env python3
"""
Create sample data files for the SEP QP Pack Generator
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon
import numpy as np

# Create sample parcel data
def create_sample_parcels():
    """Create sample parcel polygons"""
    # Create some simple rectangular parcels
    parcels_data = []
    
    # Sample parcel geometries (simple rectangles)
    geometries = [
        Polygon([(0, 0), (100, 0), (100, 100), (0, 100)]),
        Polygon([(200, 0), (300, 0), (300, 150), (200, 150)]),
        Polygon([(0, 200), (120, 200), (120, 320), (0, 320)]),
        Polygon([(250, 250), (400, 250), (400, 400), (250, 400)]),
        Polygon([(500, 100), (700, 100), (700, 300), (500, 300)])
    ]
    
    for i, geom in enumerate(geometries):
        parcels_data.append({
            'APN': f'PARCEL_{i+1:03d}',  # Required field
            'COUNTY': 'MCLEAN',  # Required field
            'STATE': 'IL',  # Required field
            'parcel_id': f'PARCEL_{i+1:03d}',
            'acres': np.random.uniform(50, 200),  # Random acreage
            'geometry': geom
        })
    
    gdf = gpd.GeoDataFrame(parcels_data, crs='EPSG:5070')
    return gdf

def create_sample_soils():
    """Create sample soils data"""
    soils_data = []
    
    # Sample soil mapunit polygons (overlapping with parcels)
    geometries = [
        Polygon([(-50, -50), (150, -50), (150, 150), (-50, 150)]),
        Polygon([(150, -50), (350, -50), (350, 200), (150, 200)]),
        Polygon([(-50, 150), (170, 150), (170, 370), (-50, 370)]),
        Polygon([(200, 200), (450, 200), (450, 450), (200, 450)]),
        Polygon([(450, 50), (750, 50), (750, 350), (450, 350)])
    ]
    
    soil_types = ['Alfisols', 'Mollisols', 'Entisols', 'Inceptisols', 'Spodosols']
    
    for i, geom in enumerate(geometries):
        soils_data.append({
            'mukey': f'MU{i+1:05d}',
            'muname': f'Sample Soil {i+1}',
            'taxorder': soil_types[i % len(soil_types)],
            'slope_r': np.random.uniform(2, 8),  # Random slope percentage
            'geometry': geom
        })
    
    gdf = gpd.GeoDataFrame(soils_data, crs='EPSG:5070')
    return gdf

def create_sample_roads():
    """Create sample road network"""
    roads_data = []
    
    # Sample road line geometries
    geometries = [
        # Horizontal roads
        Polygon([(-100, 50), (800, 50), (800, 60), (-100, 60)]),
        Polygon([(-100, 250), (800, 250), (800, 260), (-100, 260)]),
        # Vertical roads
        Polygon([(100, -100), (110, -100), (110, 500), (100, 500)]),
        Polygon([(400, -100), (410, -100), (410, 500), (400, 500)]),
        Polygon([(600, -100), (610, -100), (610, 500), (600, 500)])
    ]
    
    road_types = ['primary', 'secondary', 'tertiary', 'residential', 'service']
    
    for i, geom in enumerate(geometries):
        roads_data.append({
            'road_id': f'ROAD_{i+1:03d}',
            'road_type': road_types[i % len(road_types)],
            'geometry': geom
        })
    
    gdf = gpd.GeoDataFrame(roads_data, crs='EPSG:5070')
    return gdf

def create_sample_nlcd():
    """Create sample NLCD raster data"""
    # Create a simple raster with land cover classes
    # This is a simplified version - in practice you'd use real NLCD data
    print("Note: NLCD raster creation requires rasterio and would create a large file.")
    print("For now, we'll create a placeholder file.")
    
    # Create a simple CSV with land cover info for demonstration
    nlcd_data = pd.DataFrame({
        'parcel_id': [f'PARCEL_{i+1:03d}' for i in range(5)],
        'nlcd_class': np.random.choice(['Cropland', 'Grassland', 'Forest', 'Wetland'], 5),
        'nlcd_percent': np.random.uniform(60, 95, 5)
    })
    
    return nlcd_data

def create_sample_negative_list():
    """Create sample negative list data"""
    negative_list_data = pd.DataFrame({
        'state': ['IL', 'IL', 'IL', 'IL', 'IL'],
        'county': ['MCLEAN', 'CHAMPAIGN', 'TAZEWELL', 'WOODFORD', 'LIVINGSTON'],
        'practice_type': ['cover_crops', 'cover_crops', 'cover_crops', 'cover_crops', 'cover_crops'],
        'status': ['INELIGIBLE', 'ELIGIBLE', 'INELIGIBLE', 'ELIGIBLE', 'INELIGIBLE']
    })
    
    return negative_list_data

def main():
    """Create all sample data files"""
    print("Creating sample data files...")
    
    # Create parcels
    print("Creating sample parcels...")
    parcels = create_sample_parcels()
    parcels.to_file('data/parcels.gpkg', driver='GPKG')
    
    # Create soils
    print("Creating sample soils...")
    soils = create_sample_soils()
    soils.to_file('data/ssurgo.gpkg', driver='GPKG')
    
    # Create roads
    print("Creating sample roads...")
    roads = create_sample_roads()
    roads.to_file('data/roads.gpkg', driver='GPKG')
    
    # Create NLCD data
    print("Creating sample NLCD data...")
    nlcd = create_sample_nlcd()
    nlcd.to_csv('data/nlcd_2021.csv', index=False)
    
    # Create negative list
    print("Creating sample negative list...")
    negative_list = create_sample_negative_list()
    negative_list.to_csv('data/sep_negative_list.csv', index=False)
    
    print("✅ Sample data files created successfully!")
    print("Files created:")
    print("  - data/parcels.gpkg")
    print("  - data/ssurgo.gpkg") 
    print("  - data/roads.gpkg")
    print("  - data/nlcd_2021.csv")
    print("  - data/sep_negative_list.csv")
    print("\nYou can now run: python qpland.py")

if __name__ == "__main__":
    main() 