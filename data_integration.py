#!/usr/bin/env python3
"""
Data Integration Script for SEP QP Generator:
- County Assessor API connections
- USDA SSURGO soils data
- Open data sources
- Data validation and cleaning
"""

import requests
import pandas as pd
import geopandas as gpd
import json
import logging
from typing import Optional, Dict, List
import time

logger = logging.getLogger(__name__)

class CountyDataIntegrator:
    """Integrate with county assessor data sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SEP-QP-Generator/1.0 (Educational Use)'
        })
        
    def fetch_mclean_county_data(self) -> Optional[gpd.GeoDataFrame]:
        """Fetch McLean County, IL parcel data"""
        logger.info("Attempting to fetch McLean County data")
        
        # McLean County Open Data Portal
        # https://mcleancountyil.gov/assessor/
        
        # Try multiple data sources
        sources = [
            self._try_mclean_open_data,
            self._try_illinois_gis_data,
            self._try_usda_farm_data
        ]
        
        for source_func in sources:
            try:
                data = source_func()
                if data is not None and len(data) > 0:
                    logger.info(f"Successfully fetched data from {source_func.__name__}")
                    return data
            except Exception as e:
                logger.warning(f"Failed to fetch from {source_func.__name__}: {e}")
                continue
                
        logger.warning("All data sources failed, returning None")
        return None
        
    def _try_mclean_open_data(self) -> Optional[gpd.GeoDataFrame]:
        """Try McLean County Open Data Portal"""
        try:
            # McLean County doesn't have a public API, but we can try to find open data
            # This would be implemented when the county provides open data access
            
            # For now, return None to indicate no data available
            return None
            
        except Exception as e:
            logger.error(f"Error accessing McLean open data: {e}")
            return None
            
    def _try_illinois_gis_data(self) -> Optional[gpd.GeoDataFrame]:
        """Try Illinois State GIS Data"""
        try:
            # Illinois State GIS Data Portal
            # https://clearinghouse.isgs.illinois.edu/
            
            # This would be implemented to fetch state-level parcel data
            return None
            
        except Exception as e:
            logger.error(f"Error accessing Illinois GIS data: {e}")
            return None
            
    def _try_usda_farm_data(self) -> Optional[gpd.GeoDataFrame]:
        """Try USDA Farm Data"""
        try:
            # USDA Farm Service Agency data
            # This would be implemented to fetch agricultural parcel data
            return None
            
        except Exception as e:
            logger.error(f"Error accessing USDA farm data: {e}")
            return None

class USDADataIntegrator:
    """Integrate with USDA data sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.sda_url = "https://sdmdataaccess.nrcs.usda.gov/Tabular/post.rest"
        
    def get_soil_data(self, wkt_geometry: str) -> Dict:
        """Get soil data for a parcel using USDA SDA API"""
        try:
            # SQL query to get soil properties
            sql = f"""
            SELECT TOP 1
                c.taxorder AS taxorder,
                c.slope_r AS slope_r,
                c.om_r AS organic_matter,
                c.kwfact AS erodibility,
                mu.muname AS soil_name
            FROM SDA_Get_Mukey_from_intersection_with_WktWgs84('{wkt_geometry}') AS a
            INNER JOIN mapunit mu ON mu.mukey = a.mukey
            INNER JOIN component c ON c.mukey = mu.mukey AND c.majcompflag = 'Yes'
            ORDER BY a.area_acres DESC
            """
            
            payload = {"query": sql}
            response = self.session.post(
                self.sda_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            rows = data.get("Table", [])
            
            if rows:
                row = rows[0]
                return {
                    "taxorder": row.get("taxorder"),
                    "slope_r": float(row["slope_r"]) if row.get("slope_r") not in (None, "") else None,
                    "organic_matter": float(row["om_r"]) if row.get("om_r") not in (None, "") else None,
                    "erodibility": float(row["kwfact"]) if row.get("kwfact") not in (None, "") else None,
                    "soil_name": row.get("muname")
                }
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching USDA soil data: {e}")
            return {}
            
    def get_nlcd_data(self, parcel_centroid: tuple) -> Dict:
        """Get National Land Cover Database data for a parcel"""
        try:
            # This would integrate with NLCD API or raster data
            # For now, return sample data
            return {
                "landcover_class": "Cropland",
                "percent_cover": 85.0
            }
        except Exception as e:
            logger.error(f"Error fetching NLCD data: {e}")
            return {}

class DataValidator:
    """Validate and clean parcel data"""
    
    @staticmethod
    def validate_parcel_data(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Validate and clean parcel data"""
        logger.info("Validating parcel data")
        
        # Remove rows with missing critical data
        critical_fields = ["apn", "acres", "geometry"]
        for field in critical_fields:
            if field in gdf.columns:
                gdf = gdf.dropna(subset=[field])
                
        # Validate acreage
        if "acres" in gdf.columns:
            gdf = gdf[gdf["acres"] > 0]
            
        # Validate geometries
        gdf = gdf[gdf.geometry.is_valid]
        
        # Remove duplicate APNs
        if "apn" in gdf.columns:
            gdf = gdf.drop_duplicates(subset=["apn"])
            
        logger.info(f"Validation complete: {len(gdf)} valid parcels remain")
        return gdf
        
    @staticmethod
    def enrich_parcel_data(gdf: gpd.GeoDataFrame, usda_integrator: USDADataIntegrator) -> gpd.GeoDataFrame:
        """Enrich parcel data with USDA information"""
        logger.info("Enriching parcel data with USDA information")
        
        # Add soil data columns
        gdf["soil_order"] = None
        gdf["slope_pct"] = None
        gdf["organic_matter"] = None
        gdf["erodibility"] = None
        gdf["soil_name"] = None
        
        # Process each parcel
        for idx, row in gdf.iterrows():
            try:
                # Convert geometry to WKT for USDA API
                wkt = row.geometry.wkt
                
                # Get soil data
                soil_data = usda_integrator.get_soil_data(wkt)
                
                # Update parcel data
                if soil_data:
                    gdf.at[idx, "soil_order"] = soil_data.get("taxorder")
                    gdf.at[idx, "slope_pct"] = soil_data.get("slope_r")
                    gdf.at[idx, "organic_matter"] = soil_data.get("organic_matter")
                    gdf.at[idx, "erodibility"] = soil_data.get("erodibility")
                    gdf.at[idx, "soil_name"] = soil_data.get("soil_name")
                    
                # Be polite to the API
                time.sleep(0.2)
                
            except Exception as e:
                logger.warning(f"Error enriching parcel {idx}: {e}")
                continue
                
        logger.info("Data enrichment complete")
        return gdf

def main():
    """Main function to test data integration"""
    print("🔗 Testing Data Integration for SEP QP Generator")
    print("=" * 60)
    
    # Initialize integrators
    county_integrator = CountyDataIntegrator()
    usda_integrator = USDADataIntegrator()
    validator = DataValidator()
    
    # Try to fetch real county data
    print("\n📊 Attempting to fetch real county data...")
    parcels = county_integrator.fetch_mclean_county_data()
    
    if parcels is not None:
        print(f"✅ Successfully fetched {len(parcels)} parcels from county data")
        
        # Validate data
        parcels = validator.validate_parcel_data(parcels)
        
        # Enrich with USDA data
        parcels = validator.enrich_parcel_data(parcels, usda_integrator)
        
        print(f"✅ Data processing complete: {len(parcels)} valid parcels")
        
        # Show sample data
        print("\n📋 Sample parcel data:")
        print(parcels.head())
        
    else:
        print("⚠️  No real county data available")
        print("💡 The system will use enhanced sample data instead")
        
    print("\n🔗 Data integration test complete!")

if __name__ == "__main__":
    main() 