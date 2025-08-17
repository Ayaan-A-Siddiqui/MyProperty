#!/usr/bin/env python3
"""
All-in-one SEP QP Pack generator (no manual downloads):
- Fetches polygons ("parcels") & roads from OpenStreetMap for a county/state.
- Calls USDA Soil Data Access (SDA) Tabular API to get soil taxorder + slope_r
  for each parcel's geometry (WKT in WGS84), robust to API failures/timeouts.
- Applies SEP-style screening (min acres, slope, soil exclusion, road access).
- (Optional) Negative-List flag via a tiny inline CSV you can replace later.
- Outputs: GPKG + CSV + per-parcel one-pager PDFs.

NOTE: OSM "parcels" are landuse polygons (ag/grass/etc.), not legal assessor parcels.
Use this to prototype end-to-end; swap OSM with assessor data when ready.
"""

import os, json, time, math, warnings
import requests
import pandas as pd
import geopandas as gpd
import numpy as np
import osmnx as ox
import rasterio, rasterio.mask
from shapely.geometry import mapping
from shapely.ops import nearest_points
from shapely.geometry import Polygon, MultiPolygon
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from tqdm import tqdm

warnings.filterwarnings("ignore")

# ---------------- USER SETTINGS ----------------
CFG = {
    # Area of interest
    "state":  "Illinois",
    "county": "Chicago",  # Changed to Chicago for better OSM recognition

    # CRS for processing (US Albers Equal Area, meters)
    "crs": "EPSG:5070",

    # Output folder
    "out_dir": "output",

    # Program-ish filters (SEP-style, pragmatic)
    "min_acres": 40,          # min size
    "max_slope_pct": 10,      # slope guardrail (set None to skip)
    "allowed_landuse": {"farmland","farmyard","meadow","grass","orchard","vineyard"},  # OSM landuse tags to keep
    "max_dist_to_road_miles": 0.5,    # practical MRV/access

    # USDA SDA API
    "sda_url": "https://sdmdataaccess.nrcs.usda.gov/Tabular/post.rest",
    "sda_timeout_sec": 30,

    # Negative-List inline (replace with your real file later)
    # Keys must be UPPERCASE
    "negative_list_rows": [
        {"state":"IL", "county":"CHAMPAIGN", "practice_type":"cover_crops", "status":"ELIGIBLE"},
        {"state":"IL", "county":"MCLEAN",    "practice_type":"cover_crops", "status":"INELIGIBLE"}
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

def to_wkt_wgs84(geom_5070):
    """Transform parcel geometry (EPSG:5070) -> WGS84 and get WKT."""
    g = gpd.GeoSeries([geom_5070], crs=CFG["crs"]).to_crs("EPSG:4326").iloc[0]
    # simplify a bit to keep payload small
    g_simpl = g.simplify(0.0001, preserve_topology=True)
    return g_simpl.wkt

def call_sda_for_parcel(geom_5070):
    """Query USDA SDA to get soil 'taxorder' and 'slope_r' for the parcel geometry.
       Returns dict: {"taxorder": <str or None>, "slope_r": <float or None>}
    """
    wkt = to_wkt_wgs84(geom_5070)

    # Use SDA_Get_Mukey_from_intersection_with_WktWgs84 to find intersecting mapunits,
    # then join to component (majcompflag='Yes') to get dominant taxorder & slope_r.
    sql = f"""
    SELECT TOP 1
        c.taxorder   AS taxorder,
        c.slope_r    AS slope_r
    FROM SDA_Get_Mukey_from_intersection_with_WktWgs84('{wkt}') AS a
    INNER JOIN mapunit mu ON mu.mukey = a.mukey
    INNER JOIN component c ON c.mukey = mu.mukey AND c.majcompflag = 'Yes'
    ORDER BY a.area_acres DESC
    """

    payload = {"query": sql}
    try:
        r = requests.post(CFG["sda_url"], data=json.dumps(payload),
                          headers={"Content-Type":"application/json"},
                          timeout=CFG["sda_timeout_sec"])
        r.raise_for_status()
        data = r.json()
        # SDA returns a structure with "Table" key
        rows = data.get("Table", [])
        if not rows:
            return {"taxorder": None, "slope_r": None}
        row = rows[0]
        return {
            "taxorder": row.get("taxorder"),
            "slope_r":  float(row["slope_r"]) if row.get("slope_r") not in (None,"") else None
        }
    except Exception:
        return {"taxorder": None, "slope_r": None}

def dist_to_roads_m(geom, roads_union):
    try:
        centroid = geom.centroid
        nearest = nearest_points(centroid, roads_union)[1]
        return centroid.distance(nearest)
    except Exception:
        return np.nan

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
        story.append(Paragraph(f"Soil order (SDA taxorder): {r.get('soil_order','Unknown')}", styles["Normal"]))
        story.append(Paragraph(f"Slope % (SDA slope_r): {r.get('slope_pct', 'Unknown')}", styles["Normal"]))
        story.append(Paragraph(f"OSM landuse: {r.get('landuse','')}", styles["Normal"]))
        story.append(Paragraph(f"Distance to Road (mi): {r.get('dist_road_mi',np.nan):.2f}", styles["Normal"]))
        story.append(Paragraph(f"Negative-List County: {r.get('negative_list','No')}", styles["Normal"]))
        story.append(Paragraph(f"Stack Required (if single-practice): {r.get('stack_required','No')}", styles["Normal"]))
        story.append(Paragraph(f"Program Fit Score: {r['fit_score']}", styles["Normal"]))
        doc.build(story)

# --------------- MAIN ----------------
def main():
    ensure_dir(CFG["out_dir"])
    place = f"{CFG['county']}, {CFG['state']}, USA"
    print(f"▶ Fetching OSM polygons and roads for: {place}")

    # 1) OSM "parcels": use landuse polygons as a stand-in
    tags = {"landuse": True}
    poly = ox.geometries_from_place(place, tags)
    poly = poly.to_crs(CFG["crs"])
    # keep only polygons
    poly = poly[poly.geom_type.isin(["Polygon","MultiPolygon"])].copy()

    # assign IDs & area
    poly["parcel_id"] = poly.index.astype(str)
    poly["county"]    = CFG["county"]
    poly["state"]     = CFG["state"]

    # choose a representative landuse string (some rows have multiple)
    landuse_col = "landuse"
    if landuse_col not in poly.columns:
        poly[landuse_col] = None
    # normalize landuse (if list-like, pick first)
    poly[landuse_col] = poly[landuse_col].astype(str).str.lower().str.replace(r"[\[\]']", "", regex=True).str.split(",").str[0].str.strip()

    # area in acres
    poly["acres"] = poly.geometry.area.apply(acres_from_m2)

    # 2) Roads (for distance)
    G = ox.graph_from_place(place, network_type="drive")
    roads = ox.graph_to_gdfs(G, nodes=False, edges=True)
    roads = roads.to_crs(CFG["crs"])
    roads_union = roads.unary_union

    # 3) Filter to ag-like landuse upfront
    poly["landuse_ok"] = np.where(poly[landuse_col].isin(CFG["allowed_landuse"]), "Yes", "No")
    # Keep only those that look ag-like AND above min acres (fast prefilter)
    pre = poly[(poly["landuse_ok"]=="Yes") & (poly["acres"] >= CFG["min_acres"])].copy()
    pre = pre.reset_index(drop=True)

    # 4) USDA SDA soils per parcel (taxorder + slope_r)
    print("▶ Querying USDA SDA for soils (taxorder, slope_r)…")
    soil_order_list, slope_list = [], []
    for _, row in tqdm(pre.iterrows(), total=len(pre)):
        res = call_sda_for_parcel(row.geometry)
        soil_order_list.append(res.get("taxorder"))
        slope_list.append(res.get("slope_r"))
        # be polite to API
        time.sleep(0.2)
    pre["soil_order"] = soil_order_list
    pre["slope_pct"]  = slope_list

    # 5) Distance to nearest road (mi)
    print("▶ Computing distance to nearest road…")
    dists_m = []
    for _, row in tqdm(pre.iterrows(), total=len(pre)):
        d = nearest_points(row.geometry.centroid, roads_union)[1]
        dists_m.append(row.geometry.centroid.distance(d))
    pre["dist_road_mi"] = pd.Series(dists_m).apply(miles_from_m)

    # 6) Negative-List flag (inline)
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

    # 7) Apply program filters (slope, soils, access)
    # slope
    if CFG["max_slope_pct"] is not None:
        pre = pre[(pre["slope_pct"].isna()) | (pre["slope_pct"] <= CFG["max_slope_pct"])]

    # exclude Histosols (peat)
    pre = pre[~pre["soil_order"].astype(str).str.contains("HISTOSOL", case=False, na=False)]

    # access (road distance)
    pre = pre[(pre["dist_road_mi"].isna()) | (pre["dist_road_mi"] <= CFG["max_dist_to_road_miles"])]

    # 8) Score
    pre["fit_score"] = pre.apply(score_row, axis=1)

    # 9) Export
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

    print("✅ Done. See 'output/' for GPKG, CSV, and PDFs.")

if __name__ == "__main__":
    main()
