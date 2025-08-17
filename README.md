# 🌱 SEP QP Pack Generator

**Comprehensive SEP (Soil and Environmental Practices) QP Pack Generator with Real Data Integration**

A powerful, configurable system for generating SEP program qualification packs with real parcel data, address information, and USDA soil data integration.

## 🚀 Features

### ✅ **Real Data Integration**
- **County Assessor APIs** - Connect to real parcel data sources
- **USDA SSURGO Soils** - Live soil data from USDA databases
- **Address & APN Information** - Complete parcel identification
- **Enhanced Sample Data** - Realistic data for testing and development

### ✅ **Configurable Programs**
- **JSON-based Configuration** - Easy program requirement management
- **Multiple SEP Programs** - Cover Crops, Conservation Tillage, Nutrient Management
- **Customizable Criteria** - Min/max acres, slope, soil types, road access
- **County Restrictions** - Program-specific eligibility by county
- **Scoring Systems** - Configurable weighting for parcel evaluation

### ✅ **Comprehensive Outputs**
- **GeoPackage Files** - Spatial data for GIS analysis
- **CSV Reports** - Tabular data for analysis
- **Individual PDF Reports** - Per-parcel detailed reports
- **Summary Reports** - Program-wide statistics and overview

### ✅ **Advanced Features**
- **Data Validation** - Automatic data quality checks
- **Error Handling** - Robust API failure management
- **Logging System** - Detailed operation tracking
- **Modular Architecture** - Easy to extend and customize

## 📋 Available Programs

### 1. **Cover Crops Program**
- **Min Acres**: 10 | **Max Acres**: 1,000
- **Max Slope**: 15% | **Road Access**: 1.0 miles
- **Soils**: Alfisols, Mollisols, Entisols, Inceptisols, Spodosols
- **Excluded**: Histosols, Vertisols

### 2. **Conservation Tillage Program**
- **Min Acres**: 20 | **Max Acres**: 2,000
- **Max Slope**: 12% | **Road Access**: 0.75 miles
- **Soils**: Alfisols, Mollisols, Entisols, Inceptisols
- **Excluded**: Histosols

### 3. **Nutrient Management Program**
- **Min Acres**: 15 | **Max Acres**: 1,500
- **Max Slope**: 8% | **Road Access**: 0.5 miles
- **Soils**: Alfisols, Mollisols, Entisols
- **Excluded**: Histosols, Spodosols

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Git

### Quick Start
```bash
# Clone the repository
git clone https://github.com/yourusername/sep-qp-generator.git
cd sep-qp-generator

# Install dependencies
pip install -r requirements.txt

# Run the generator
python sep_qp_generator.py
```

### Manual Installation
```bash
# Install required packages
pip install pandas geopandas numpy rasterio shapely reportlab tqdm fiona pyproj requests osmnx
```

## 📖 Usage

### 1. **Basic Usage**
```bash
# Run with default cover crops program
python sep_qp_generator.py
```

### 2. **Program Configuration Editor**
```bash
# Edit program requirements interactively
python program_editor.py
```

### 3. **Data Integration Testing**
```bash
# Test real data connections
python data_integration.py
```

### 4. **Custom Program Creation**
```bash
# Use the interactive editor to create new programs
python program_editor.py
# Select option 4: Create new program
```

## 📁 Project Structure

```
sep-qp-generator/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── sep_config.json          # Program configurations
├── sep_qp_generator.py      # Main generator script
├── program_editor.py        # Interactive configuration editor
├── data_integration.py      # Real data integration tools
├── create_sample_data.py    # Sample data creation
├── qpland.py               # Original OSM-based script
├── qpland_simple.py        # Simplified version
├── output/                 # Generated outputs
│   ├── cover_crops_qp_pack.gpkg
│   ├── cover_crops_qp_pack.csv
│   ├── cover_crops_summary_report.pdf
│   └── parcel_*.pdf
└── data/                   # Data files (if using local data)
```

## 🔧 Configuration

### Program Configuration (`sep_config.json`)
```json
{
  "programs": {
    "your_program": {
      "name": "Your Program Name",
      "description": "Program description",
      "requirements": {
        "min_acres": 10,
        "max_acres": 1000,
        "max_slope_pct": 15,
        "allowed_soil_orders": ["Alfisols", "Mollisols"],
        "county_restrictions": {
          "MCLEAN": "ELIGIBLE"
        }
      },
      "scoring": {
        "acres": 25,
        "soil_health": 25,
        "erosion_risk": 25,
        "access": 25
      }
    }
  }
}
```

### Data Sources Configuration
```json
{
  "data_sources": {
    "county_assessors": {
      "mclean": {
        "name": "McLean County Assessor",
        "api_url": "https://mcleancountyil.gov/assessor/",
        "data_format": "shapefile"
      }
    },
    "usda_sources": {
      "ssurgo": {
        "name": "SSURGO Soils Database",
        "api_url": "https://sdmdataaccess.nrcs.usda.gov/"
      }
    }
  }
}
```

## 📊 Output Files

### 1. **GeoPackage (.gpkg)**
- Spatial data with parcel geometries
- All parcel attributes and scores
- Compatible with QGIS, ArcGIS, and other GIS software

### 2. **CSV Report (.csv)**
- Tabular data for analysis
- Includes all parcel information and scores
- Easy to import into Excel, R, or Python

### 3. **Individual PDF Reports**
- Detailed per-parcel reports
- Complete parcel information
- Technical data and eligibility status
- Professional formatting

### 4. **Summary Report**
- Program-wide statistics
- Total eligible parcels and acres
- Average scores and distributions
- Summary table of all parcels

## 🔗 Data Integration

### County Assessor Integration
The system is designed to integrate with county assessor APIs:

```python
# Example: McLean County Integration
county_integrator = CountyDataIntegrator()
parcels = county_integrator.fetch_mclean_county_data()
```

### USDA SSURGO Integration
Real-time soil data from USDA:

```python
# Example: Soil Data Retrieval
usda_integrator = USDADataIntegrator()
soil_data = usda_integrator.get_soil_data(wkt_geometry)
```

## 🎯 Example Results

### Sample Output Data
```
APN: 14-21-32-123-456
Address: 1234 E 1000 North Road, Bloomington, IL 61701
Owner: Smith Family Farm LLC
Acres: 85.2
Soil Order: Alfisols
Slope: 4.2%
Organic Matter: 2.1%
Erodibility: 0.28
Distance to Road: 0.15 miles
Fit Score: 85/100
Status: ELIGIBLE
```

## 🚀 Advanced Usage

### Creating Custom Programs
1. Run `python program_editor.py`
2. Select option 4: Create new program
3. Enter program details and requirements
4. Save configuration

### Modifying Existing Programs
1. Run `python program_editor.py`
2. Select option 3: Edit program requirement
3. Enter program key and requirement
4. Enter new value

### Batch Processing
```python
from sep_qp_generator import SEPQPGenerator

generator = SEPQPGenerator()
programs = ["cover_crops", "conservation_tillage", "nutrient_management"]

for program in programs:
    generator.set_program(program)
    parcels = generator.fetch_real_parcels("McLean", "IL")
    eligible = generator.apply_program_screening(parcels)
    generator.generate_outputs(eligible)
```

## 🔍 Troubleshooting

### Common Issues

1. **No eligible parcels found**
   - Check county restrictions in configuration
   - Verify acreage and slope requirements
   - Review soil type restrictions

2. **API connection errors**
   - Check internet connection
   - Verify API endpoints in configuration
   - Review API rate limits

3. **Missing dependencies**
   - Run `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is the exclusive property of **Lanward**. All Rights Reserved.

No part of this software may be reproduced, distributed, or transmitted without the prior written permission of Lanward.

For licensing inquiries, please contact Lanward.

---

**🌱 Built for sustainable agriculture and environmental stewardship**

**© 2024 Lanward. All Rights Reserved.** 