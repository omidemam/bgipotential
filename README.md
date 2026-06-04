# BGIpotential

> Blue-Green Infrastructure Potential. This repository contains the computational workflow used to estimate, uncertainty analyze, classify, and visualize citywide blue-green infrastructure (BGI) potential across major U.S. cities. It accompanies the manuscript *Ranking the aggregate potential for blue-green infrastructure in U.S. cities*.

[![Made with Jupyter](https://img.shields.io/badge/Made%20with-Jupyter-F37626.svg)](https://jupyter.org)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![ArcGIS](https://img.shields.io/badge/ArcGIS-ArcPy-2C7AC3.svg)](https://pro.arcgis.com/en/pro-app/latest/arcpy/get-started/what-is-arcpy-.htm)
[![License](https://img.shields.io/badge/License-CC0-green.svg)](#-license)

---

## Overview

Blue-green infrastructure is central to urban sustainability and resilience, but citywide screening metrics are still limited. This repository implements a simple and scalable **Green Infrastructure Potential Index (GIPI)** workflow that spatially aggregates the potential to alleviate:

- hydrological component,
- heat-related component,
- air-quality-related component.

The workflow combines spatial raster and polygon inputs in ArcGIS, computes component-level city averages, produces a composite GIPI score, analyzes uncertainty, and classifies cities according to their aggregate BGI potential. The results indicate that **NYC, Houston, and Chicago** rank highest among the evaluated U.S. cities.

---

## Website

Explore the project website and visual materials here:

[https://natem5384.github.io/gipi.github.io/](https://natem5384.github.io/gipi.github.io/)

---

## Repository Structure

```
bgipotential/
|-- Model/
|   |-- BGIpotential/
|   |   `-- GIPI_Final_Script.py
|   |-- Clustring/
|   |   `-- BGIPI_classification.ipynb
|   `-- Uncertainty analysis/
|-- Results/
|   `-- GIPI_Results.xls
|-- Visualization/
|-- environment.yml
|-- LICENSE
`-- README.md
```

---

## Methodology

- Spatial preprocessing: Project city boundaries to NAD 1983 Albers and align rasters using the impervious surface raster as the snap raster and cell size reference.

- Component computation: Compute hydrological, heat severity, and air-quality components from normalized tabular variables and spatial layers.

- Zonal aggregation: Use city boundaries to calculate zonal mean component values and write them to the master city table.

- Composite index: Calculate the tabular classic GIPI score as:

  ```text
  GIPI = 0.6 * HydroRiskAvg + 0.3 * HeatRiskAvg + 0.1 * AQAvg
  ```
- Uncertainty analyses: Try different weight combinations for different components of the index and their effect on the city rankings.
- Classification: Use fuzzy C-means clustering to classify cities based on hydrological, heat, and air-quality component averages.

- Visualization: Visualizes results.

---

## Data and Inputs

The ArcGIS workflow expects local spatial datasets supplied through the script tool interface:

- city name,
- impervious surface raster,
- heat severity raster,
- air-quality polygon layer,
- city boundary polygon.

The script also uses a master geodatabase table named `GIPI_Collec_Table_Apr8`, which contains normalized city-level attributes such as precipitation, CSO outfalls, parking-lot area, and August nighttime low temperature.

The repository includes the processed output table used by the classification notebook:

```text
Results/GIPI_Results.xls
```

---

## Getting Started

1. Clone the repository:

   ```bash
   git clone https://github.com/omidemam/bgipotential.git
   cd bgipotential
   ```

2. Create the conda environment:

   ```bash
   conda env create -f environment.yml
   conda activate bgipotential
   ```

3. Run the ArcGIS computation workflow:

   ```text
   Model/BGIpotential/GIPI_Final_Script.py
   ```

   This script is intended to run inside ArcGIS Pro or an ArcGIS script tool with the required Spatial Analyst extension.

4. Run the city classification notebook:

   ```text
   Model/Clustring/BGIPI_classification.ipynb
   ```

---

## Manuscript

This repository accompanies:

*Ranking the aggregate potential for blue-green infrastructure in U.S. cities*

Nate Mestre, Berina Mina Kilicarslan, Mason Majszak, Omid Emamjomehzadeh, Shalini Seenu Pillai, Yang Yang, Seyedamirhossein Zarei, Runzi Wang, Kun Zhang, Caroline Evans, and Omar Wani.

---

## Keywords

blue-green infrastructure, green infrastructure potential index, stormwater, urban heat, air quality, urban resilience, spatial analysis

---

## Contact

For questions, feedback, or collaboration opportunities, please contact:
[omarwani@nyu.edu](mailto:omarwani@nyu.edu)
[npm2054@nyu.edu](mailto:npm2054@nyu.edu)
[berina.k@nyu.edu](mailto:berina.k@nyu.edu)
[omid.emamjomehzadeh@nyu.edu](mailto:omid.emamjomehzadeh@nyu.edu)

---

## Citation

If you use this repository in your research or projects, please cite the accompanying manuscript and repository.

BibTeX format:

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
