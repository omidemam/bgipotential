# BGIpotential

Blue-Green Infrastructure Potential. This repository contains the computational workflow used to estimate, analyze, classify, and visualize citywide blue-green infrastructure (BGI) potential across major U.S. cities. It accompanies the manuscript *Ranking the aggregate potential for blue-green infrastructure in U.S. cities*.

[![Made with Jupyter](https://img.shields.io/badge/Made%20with-Jupyter-F37626.svg)](https://jupyter.org)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![ArcGIS](https://img.shields.io/badge/ArcGIS-ArcPy-2C7AC3.svg)](https://pro.arcgis.com/en/pro-app/latest/arcpy/get-started/what-is-arcpy-.htm)
[![License](https://img.shields.io/badge/License-CC0-green.svg)](#license)

## Overview

The Green Infrastructure Potential Index (GIPI) is a city-scale screening index for comparing the potential of blue-green infrastructure to mitigate three urban stressors:

- Hydrological risk
- Heat severity
- Air-quality burden

The workflow combines ArcGIS-based raster and polygon processing with Python analysis scripts. ArcGIS is used to compute component-level city averages; downstream Python scripts use the processed results table to rank cities, test sensitivity to component weights, classify cities, and generate publication figures.

The classic GIPI score is calculated as:

```text
GIPI = 0.60 * HydroRiskAvg + 0.30 * HeatRiskAvg + 0.10 * AQAvg
```

## Website

Project website and visual materials:

[https://bgipotential.github.io/](https://bgipotential.github.io/)

## Repository Structure

```text
bgipotential/
|-- Data/
|   |-- City_boundaries.rar
|   `-- Datasets.txt
|-- Model/
|   |-- BGIpotential/
|   |   `-- GIPI_Final_Script.py
|   |-- Clustring/
|   |   `-- BGIPI_classification.ipynb
|   `-- Sensitivity analysis/
|       |-- GIPI_SensAnalys_AllCities_Dist.py
|       `-- GIPI_SensAnalys_plot_diag_combined.py
|-- Results/
|   `-- GIPI_Results.xls
|-- Visualization/
|   |-- Figure1_Stressors_Rank.ipynb
|   |-- Figure2_SD_Rank.ipynb
|   |-- GIPI_RankedBarFigure.py
|   |-- GIPI_StaticMap.py
|   |-- Figures and maps/
|   `-- NYC maps/
|       `-- NYC maps.ipynb
|-- environment.yml
|-- LICENSE
`-- README.md
```

## Workflow

The intended data flow is:

```text
Raw spatial datasets
    -> ArcGIS component calculations
    -> ArcGIS geodatabase table
    -> exported Results/GIPI_Results.xls
    -> sensitivity analysis, classification, and visualization
```

The ArcGIS script updates a geodatabase table named `GIPI_Collec_Table_Apr8`. The processed Excel file in `Results/GIPI_Results.xls` is the downstream input used by the notebooks and visualization scripts.

## Data and Inputs

The repository includes:

- `Data/City_boundaries.rar`: city boundary polygons
- `Data/Datasets.txt`: source descriptions for public datasets
- `Results/GIPI_Results.xls`: processed city-level component scores and GIPI results

Most raw spatial inputs are not bundled in this repository and must be downloaded from the public sources listed in `Data/Datasets.txt`.

The main downstream analyses expect `Results/GIPI_Results.xls` to include at least:

```text
City
HydroRiskAvg
HeatRiskAvg
AQAvg
Tbl_GIPI
```

## Setup

Create the project environment:

```bash
conda env create -f environment.yml
conda activate bgipotential
```

The conda environment supports the main pandas, matplotlib, scikit-learn, scikit-fuzzy, and notebook workflows. ArcPy is not installed by `environment.yml`; `Model/BGIpotential/GIPI_Final_Script.py` must be run from an ArcGIS Pro Python environment with the Spatial Analyst extension available.

Some optional geospatial notebook work, especially `Visualization/NYC maps/NYC maps.ipynb`, uses additional packages and local spatial paths, including `geopandas`, `contextily`, and `rasterio`.

## Running the Workflows

### 1. ArcGIS Component Calculation

Run this script inside ArcGIS Pro or as an ArcGIS script tool:

```text
Model/BGIpotential/GIPI_Final_Script.py
```

Script-tool inputs:

- City name
- Impervious surface raster
- Heat severity raster
- Air-quality polygon layer
- City boundary polygon

Important: the script currently contains a local geodatabase path and writes to `GIPI_Collec_Table_Apr8`. Update the geodatabase path before running on a new machine.

After running the ArcGIS workflow, export the updated city-level table to:

```text
Results/GIPI_Results.xls
```

### 2. Classification

Open and run:

```text
Model/Clustring/BGIPI_classification.ipynb
```

The notebook performs K-means and fuzzy C-means classification using `HydroRiskAvg`, `HeatRiskAvg`, and `AQAvg`. It includes silhouette-based K-means exploration, fuzzy partition coefficient output, Xie-Beni index evaluation, membership probabilities, and 3D classification plots.

### 3. Sensitivity Analysis

Run from the repository root:

```bash
python "Model/Sensitivity analysis/GIPI_SensAnalys_AllCities_Dist.py"
python "Model/Sensitivity analysis/GIPI_SensAnalys_plot_diag_combined.py"
```

These scripts sample 5,000 component-weight combinations using `Dirichlet(1,1,1)` with random seed `35`. They compare alternative city rankings against the classic weights `(0.60, 0.30, 0.10)` using rank correlation, R2, mean absolute rank shift, and rank-distribution summaries.

Generated outputs are written to:

```text
Visualization/Figures and maps/GIPI_RankStability_AllCities_6_6.xlsx
Visualization/Figures and maps/GIPI_RankDistributions_AllCities_6_6.png
Visualization/Figures and maps/GIPI_simplex_combined2.png
Visualization/Figures and maps/GIPI_RankStability_5_5.xlsx
Visualization/Figures and maps/GIPI_RankDistributions_5_5.png
```

### 4. Figures and Maps

Run these scripts from the repository root:

```bash
python Visualization/GIPI_RankedBarFigure.py
python Visualization/GIPI_StaticMap.py
```

Outputs:

```text
Visualization/Figures and maps/GIPI_RankedBar6_6.png
Visualization/Figures and maps/GIPI_ClassicMap_6_6.png
```

`GIPI_StaticMap.py` downloads U.S. state boundary GeoJSON from GitHub at runtime, so it requires internet access.

Additional figure notebooks:

```text
Visualization/Figure1_Stressors_Rank.ipynb
Visualization/Figure2_SD_Rank.ipynb
Visualization/NYC maps/NYC maps.ipynb
```

`NYC maps.ipynb` is a local data-visualization notebook with machine-specific input paths. It is useful as a record of the NYC input-map workflow, but it is not fully portable without updating paths and installing the extra geospatial packages noted above.

## Reproducibility Notes

- The processed results table `Results/GIPI_Results.xls` is the central input for downstream analysis.
- Scripts in `Model/Sensitivity analysis/` and `Visualization/` use repository-relative paths.
- ArcGIS execution requires local spatial datasets and an ArcGIS Pro environment.
- Some notebooks assume they are launched from specific working directories.
- On case-sensitive systems, use `Results/` rather than `results/`.
- Generated figures and Excel summaries are stored in `Visualization/Figures and maps/`.

## Manuscript

This repository accompanies:

*Ranking the aggregate potential for blue-green infrastructure in U.S. cities*

Nate Mestre, Berina Mina Kilicarslan, Mason Majszak, Omid Emamjomehzadeh, Shalini Seenu Pillai, Yang Yang, Seyedamirhossein Zarei, Runzi Wang, Kun Zhang, Caroline Evans, and Omar Wani.

## Contact

For questions, feedback, or collaboration opportunities, please contact:

[npm2054@nyu.edu](mailto:npm2054@nyu.edu),
[berina.k@nyu.edu](mailto:berina.k@nyu.edu),
[omarwani@nyu.edu](mailto:omarwani@nyu.edu),
[omid.emamjomehzadeh@nyu.edu](mailto:omid.emamjomehzadeh@nyu.edu)

## Citation

If you use this repository in your research or projects, please cite the accompanying manuscript and repository.

```bibtex
@misc{Mestre2026BGIpotential,
  author       = {Mestre, Nate and Kilicarslan, Berina Mina and Majszak, Mason and Emamjomehzadeh, Omid and Pillai, Shalini Seenu and Yang, Yang and Zarei, Seyedamirhossein and Wang, Runzi and Zhang, Kun and Evans, Caroline and Wani, Omar},
  title        = {BGIpotential: Ranking the aggregate potential for blue-green infrastructure in U.S. cities},
  year         = {2026},
  note         = {GitHub repository accompanying the manuscript ``Ranking the aggregate potential for blue-green infrastructure in U.S. cities''},
  howpublished = {\url{https://github.com/omidemam/bgipotential.git}},
}
```

## License

This repository is released under the CC0 1.0 Universal license. See [LICENSE](LICENSE) for details.
