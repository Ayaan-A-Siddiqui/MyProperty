#!/usr/bin/env python3
"""
Simplified SEP QP Pack generator for testing:
- Uses sample data instead of OSM/USDA APIs
- Demonstrates the core SEP screening logic
- Outputs: GPKG + CSV + per-parcel one-pager PDFs.
"""

import os, json, time, math, warnings
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from tqdm import tqdm

warnings.filterwarnings("ignore")

# ---------------- USER SETTINGS ----------------
CFG = {
    # Area of interest
    "state":  "Illinois",
    "county": "McLean",

    # CRS for processing (US Albers Equal Area, meters)
    "crs": "EPSG:5070",

    # Output folder
    "out_dir": "output",

    # Program-ish filters (SEP-style, pragmatic)
    "min_acres": 40,          # min size
    "max_slope_pct": 10,      # slope guardrail (set None to skip)
    "max_dist_to_road_miles": 0.5,    # practical MRV/access

    # Negative-List inline (replace with your real file later)
    "negative_list_rows": [
        {"state":"IL", "county":"MCLEAN",    "practice_type":"cover_crops", "status":"INELIGIBLE"},
        {"state":"IL", "county":"CHAMPAIGN", "practice_type":"cover_crops", "status":"ELIGIBLE"}
    ],

    # Scoring weights (sum ~= 100)
    "score_w": {
        "acres": 25,
        "slope": 25,
        "landuse": 25,
        "access": 25
    }
}

# --------------- HELPERS ----------------
def ensure_dir(p): os.makedirs(p, exist_ok=True)
def acres_from_m2(a): return a / 4046.86
def miles_from_m(m):  return m * 0.000621371

def norm_up(s):
    return str(s).strip().upper() if s is not None else ""

def score_row(r):
    s = 0
    if r["acres"] >= CFG["min_acres"]:
        s += CFG["score_w"]["acres"]
    if CFG["max_slope_pct"] is None or (pd.notna(r["slope_pct"]) and r["slope_pct"] <= CFG["max_slope_pct"]):
        s += CFG["score_w"]["slope"]
    if r["landuse_ok"] == "Yes":
        s += CFG["score_w"]["landuse"]
    if pd.notna(r["dist_road_mi"]) and r["dist_road_mi"] <= CFG["max_dist_to_road_miles"]:
        s += CFG["score_w"]["access"]
    return s

def make_pdf_onepagers(gdf):
    styles = getSampleStyleSheet()
    for _, r in gdf.iterrows():
        apn = r["parcel_id"]
        fn  = os.path.join(CFG["out_dir"], f"parcel_{apn}.pdf")
        doc = SimpleDocTemplate(fn, pagesize=A4)
        story = []
        story.append(Paragraph("SEP QP Candidate – One Pager", styles["Title"]))
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"County/State: {r['county']}, {r['state']}", styles["Normal"]))
        story.append(Paragraph(f"Parcel ID: {apn}", styles["Normal"]))
        story.append(Paragraph(f"Acreage (calc): {r['acres']:.2f}", styles["Normal"]))
        story.append(Paragraph(f"Soil order: {r.get('soil_order','Unknown')}", styles["Normal"]))
        story.append(Paragraph(f"Slope %: {r.get('slope_pct', 'Unknown')}", styles["Normal"]))
        story.append(Paragraph(f"Landuse: {r.get('landuse','')}", styles["Normal"]))
        story.append(Paragraph(f"Distance to Road (mi): {r.get('dist_road_mi',np.nan):.2f}", styles["Normal"]))
        story.append(Paragraph(f"Negative-List County: {r.get('negative_list','No')}", styles["Normal"]))
        story.append(Paragraph(f"Stack Required: {r.get('stack_required','No')}", styles["Normal"]))
        story.append(Paragraph(f"Program Fit Score: {r['fit_score']}", styles["Normal"]))
        doc.build(story)

def create_sample_data():
    """Create sample parcel data for testing"""
    parcels_data = []
    
    # Create sample parcel geometries (simple rectangles)
    geometries = [
        Polygon([(0, 0), (1000, 0), (1000, 1000), (0, 1000)]),
        Polygon([(2000, 0), (3000, 0), (3000, 1500), (2000, 1500)]),
        Polygon([(0, 2000), (1200, 2000), (1200, 3200), (0, 3200)]),
        Polygon([(2500, 2500), (4000, 2500), (4000, 4000), (2500, 4000)]),
        Polygon([(5000, 1000), (7000, 1000), (7000, 3000), (5000, 3000)])
    ]
    
    # Sample data
    sample_data = [
        {"acres": 60, "soil_order": "Alfisols", "slope_pct": 5, "landuse": "farmland", "dist_road_mi": 0.2},
        {"acres": 120, "soil_order": "Mollisols", "slope_pct": 3, "landuse": "farmland", "dist_road_mi": 0.1},
        {"acres": 80, "soil_order": "Entisols", "slope_pct": 8, "landuse": "meadow", "dist_road_mi": 0.3},
        {"acres": 200, "soil_order": "Inceptisols", "slope_pct": 12, "landuse": "farmland", "dist_road_mi": 0.4},
        {"acres": 150, "soil_order": "Spodosols", "slope_pct": 6, "landuse": "grass", "dist_road_mi": 0.6}
    ]
    
    for i, (geom, data) in enumerate(zip(geometries, sample_data)):
        parcels_data.append({
            'parcel_id': f'PARCEL_{i+1:03d}',
            'county': CFG["county"],
            'state': CFG["state"],
            'acres': data["acres"],
            'soil_order': data["soil_order"],
            'slope_pct': data["slope_pct"],
            'landuse': data["landuse"],
            'dist_road_mi': data["dist_road_mi"],
            'geometry': geom
        })
    
    gdf = gpd.GeoDataFrame(parcels_data, crs=CFG["crs"])
    return gdf

# --------------- MAIN ----------------
def main():
    ensure_dir(CFG["out_dir"])
    print(f"▶ Creating sample data for: {CFG['county']}, {CFG['state']}")

    # 1) Create sample parcel data
    poly = create_sample_data()
    
    # 2) Apply landuse filter
    poly["landuse_ok"] = np.where(poly["landuse"].isin(["farmland","farmyard","meadow","grass","orchard","vineyard"]), "Yes", "No")
    
    # 3) Keep only those that look ag-like AND above min acres
    pre = poly[(poly["landuse_ok"]=="Yes") & (poly["acres"] >= CFG["min_acres"])].copy()
    pre = pre.reset_index(drop=True)

    # 4) Negative-List flag (inline)
    neg = pd.DataFrame(CFG["negative_list_rows"])
    neg["_STATE"]  = neg["state"].apply(norm_up)
    neg["_COUNTY"] = neg["county"].apply(norm_up)
    pre["_STATE"]  = pre["state"].apply(norm_up)
    pre["_COUNTY"] = pre["county"].apply(norm_up)
    pre = pre.merge(
        neg[["_STATE","_COUNTY","status"]].rename(columns={"status":"negative_list"}),
        on=["_STATE","_COUNTY"], how="left"
    )
    pre["negative_list"] = pre["negative_list"].fillna("No")
    pre["negative_list"] = pre["negative_list"].replace({"INELIGIBLE":"Yes","ELIGIBLE":"No"})

    # Stack required if Negative-List county
    pre["stack_required"] = np.where(pre["negative_list"]=="Yes", "Yes", "No")

    # 5) Apply program filters (slope, soils, access)
    # slope
    if CFG["max_slope_pct"] is not None:
        pre = pre[(pre["slope_pct"].isna()) | (pre["slope_pct"] <= CFG["max_slope_pct"])]

    # exclude Histosols (peat)
    pre = pre[~pre["soil_order"].astype(str).str.contains("HISTOSOL", case=False, na=False)]

    # access (road distance)
    pre = pre[(pre["dist_road_mi"].isna()) | (pre["dist_road_mi"] <= CFG["max_dist_to_road_miles"])]

    # 6) Score
    pre["fit_score"] = pre.apply(score_row, axis=1)

    # 7) Export
    ensure_dir(CFG["out_dir"])
    out_gpkg = os.path.join(CFG["out_dir"], "sep_qp_pack.gpkg")
    out_csv  = os.path.join(CFG["out_dir"], "sep_qp_pack.csv")

    keep_cols = ["parcel_id","county","state","acres","landuse","landuse_ok",
                 "soil_order","slope_pct","dist_road_mi","negative_list","stack_required","fit_score","geometry"]
    out = pre[keep_cols].copy()

    print(f"▶ Writing {out_gpkg}")
    out.to_file(out_gpkg, driver="GPKG")

    print(f"▶ Writing {out_csv}")
    out.drop(columns="geometry").to_csv(out_csv, index=False)

    print("▶ Generating PDF one-pagers…")
    make_pdf_onepagers(out)

    print(f"✅ Done. Found {len(out)} eligible parcels.")
    print("See 'output/' for GPKG, CSV, and PDFs.")

if __name__ == "__main__":
    main() 