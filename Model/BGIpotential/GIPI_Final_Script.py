# -*- coding: utf-8 -*-
"""
Thesis Tool: GIPI Component Average Calculator
Computes zonal mean averages for the three component variables:
  Hydrological Risk, Heat Severity, Air Quality
Formulation:
  Normalised (_Norm) tabular inputs:
    Abs_P_Norm, Abs_CSO_Norm, Abs_PLA_Norm, Abs_AugT_Norm
Output fields written to CityData:
  HydroRiskAvg  |  HeatRiskAvg |  AQAvg
"""
import arcpy, os
from arcpy.sa import *
from datetime import datetime
def run_component_averages():
    # =========================================================================
    # 1. INPUTS
    # =========================================================================
    CityName   = arcpy.GetParameterAsText(0)
    rImp       = arcpy.Raster(arcpy.GetParameterAsText(1))  # Impervious surface (%)
    rHeat      = arcpy.Raster(arcpy.GetParameterAsText(2))  # Spatial heat (1-5 scale)
    AQ_Polygon = arcpy.GetParameterAsText(3)                # Air quality polygons
    City_Bound = arcpy.GetParameterAsText(4)                # City boundary polygon
    # =========================================================================
    # 2. PATHS
    # =========================================================================
    GDB      = r"C:\Users\npm2054\Documents\ArcGIS\Projects\Thesis1\Thesis1.gdb"
    CityData = os.path.join(GDB, "GIPI_Collec_Table_Apr8")
    # =========================================================================
    # 3. COORDINATE SYSTEM & ENVIRONMENT SETTINGS
    # =========================================================================
    nad83_albers = arcpy.SpatialReference(102003)
    arcpy.env.overwriteOutput        = True
    arcpy.env.outputCoordinateSystem = nad83_albers  # All outputs use this CRS
    arcpy.CheckOutExtension("spatial")
    # Reproject city boundary so it is used consistently for extent/mask/zonal stats
    city_bound_proj = os.path.join(GDB, "CityBound_{}_Albers".format(CityName))
    arcpy.management.Project(City_Bound, city_bound_proj, nad83_albers)
    arcpy.AddMessage("City boundary reprojected to NAD 1983 Albers.")
    arcpy.env.snapRaster = rImp
    arcpy.env.cellSize   = rImp
    arcpy.env.extent     = city_bound_proj
    arcpy.env.mask       = city_bound_proj
    zone_field = arcpy.Describe(city_bound_proj).OIDFieldName
    arcpy.AddMessage("Using zone field: {}".format(zone_field))
    where = "City = '{}'".format(CityName)
    # =========================================================================
    # 4. FETCH NORMALISED CITY STATS FROM MASTER TABLE
    # =========================================================================
    fields = ["Abs_P_Norm", "Abs_CSO_Norm", "PLA_perarea_Abs_norm", "Abs_AugT_Norm"]
    with arcpy.da.SearchCursor(CityData, fields, where) as cur:
        row = next(cur, None)
    if not row:
        arcpy.AddError("City '{}' not found in master table.".format(CityName))
        return
    Precip_Norm, CSO_Norm, Prkng_Norm, Aug_T_Norm = [float(v) for v in row]
    # =========================================================================
    # 5. BUILD AIR QUALITY RASTER (from polygons)
    #    -999 or any negative value is converted to NoData.
    #    ZonalStatisticsAsTable ignores NoData, so the mean reflects valid cells only.
    # =========================================================================
    date_str = datetime.now().strftime("%Y_%m_%d")
    aq_path  = os.path.join(GDB, "AQ_{}_{}".format(CityName, date_str))
    if arcpy.Exists(aq_path):
        try:
            m = arcpy.mp.ArcGISProject("CURRENT").activeMap
            for lyr in m.listLayers(os.path.basename(aq_path)):
                m.removeLayer(lyr)
        except Exception:
            pass
        arcpy.management.ClearWorkspaceCache()
        arcpy.management.Delete(aq_path)
    arcpy.conversion.PolygonToRaster(AQ_Polygon, "RPL_EBM_DOM1", aq_path, cellsize=rImp)
    rAir = arcpy.sa.SetNull(arcpy.Raster(aq_path) < 0, arcpy.Raster(aq_path))
    # =========================================================================
    # 6. COMPUTE COMPONENT RASTERS
    # =========================================================================
    # Normalised sub-component layers (stored for zonal-mean extraction below)
    rImp_Norm  = rImp  / 100
    rHeat_Norm = rHeat / 5
    HydroRisk = (0.7 * SquareRoot(rImp_Norm * Precip_Norm)) + (0.1 * CSO_Norm) + (0.2 * Prkng_Norm)
    HeatRisk  = (0.5 * rHeat_Norm) + (0.5 * Aug_T_Norm)
    # rAir used directly as the AQ component
    # =========================================================================
    # 7. HELPER: COMPUTE ZONAL MEAN AND WRITE TO MASTER TABLE
    # =========================================================================
    def zonal_mean_to_table(val_raster, field_name, label):
        mem_tbl = r"memory\Zonal_{}".format(label)
        if arcpy.Exists(mem_tbl):
            arcpy.management.Delete(mem_tbl)
        ZonalStatisticsAsTable(city_bound_proj, zone_field, val_raster, mem_tbl, "DATA", "MEAN")
        with arcpy.da.SearchCursor(mem_tbl, ["MEAN"]) as cur:
            row = next(cur, None)
        mean_val = row[0] if row else 0
        arcpy.management.Delete(mem_tbl)
        with arcpy.da.UpdateCursor(CityData, [field_name], where) as cur:
            for r in cur:
                r[0] = mean_val
                cur.updateRow(r)
        arcpy.AddMessage("{} mean ({:.4f}) written to field '{}'.".format(label, mean_val, field_name))
    # =========================================================================
    # 8. COMPUTE AND WRITE COMPONENT AVERAGES
    # =========================================================================
    arcpy.AddMessage("\n-- Component averages --")
    zonal_mean_to_table(HydroRisk, "HydroRiskAvg", "HydroRisk")
    zonal_mean_to_table(HeatRisk,  "HeatRiskAvg",   "HeatRisk")
    zonal_mean_to_table(rAir,      "AQAvg",        "AQ")
    # Sub-component layer means (normalised inputs that feed into the components)
    arcpy.AddMessage("\n-- Sub-component layer averages --")
    zonal_mean_to_table(rImp_Norm,  "ImpervAvg",   "Imperv")
    zonal_mean_to_table(rHeat_Norm, "HeatGeoAvg",  "HeatGeo")
# Calculate GIPI Tabularly
    arcpy.management.CalculateField(CityData, "Tbl_GIPI", "(0.6 * float(!HydroRiskAvg!)) + (0.3 * float(!HeatRiskAvg!)) + (0.1 * float(!AQAvg!))", "PYTHON3")
    arcpy.AddMessage("Calculated Tbl_GIPI using tabular component averages.")
    # =========================================================================
    # 9. CLASSIC GIPI COMPOSITE INDEX
    # =========================================================================
    gipi_path = os.path.join(GDB, "ClGIPI_{}_{}".format(CityName, date_str))
    
    # ArcGIS calculates everything here because aq_path still exists!
    ClassicGIPI = Float((0.6 * HydroRisk) + (0.3 * HeatRisk) + (0.1 * rAir))
    ClassicGIPI.save(gipi_path)
    # Add to map
    arcpy.mp.ArcGISProject("CURRENT").activeMap.addDataFromPath(gipi_path)
    arcpy.AddMessage("ClassicGIPI added to map.")
    arcpy.AddMessage("ClassicGIPI saved -> {}".format(gipi_path))
    # =========================================================================
    # 10. CLEANUP
    # =========================================================================
    arcpy.management.Delete(aq_path)
    arcpy.AddMessage("\nComponent average calculation and cleanup complete.")
if __name__ == '__main__':
    run_component_averages()
