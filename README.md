# ReEDS unit database update workflow

This document provides the standard, high level steps to finalize the unit database update. Like this one, please make a copy of all directories and rename a project like `AEO 2021 Update` when updating database for `2021` and same true for coming years. All suites of scripts from bullet **1-5** needs to be updated sequentially every year. After all updates are done, please keep a copy in `\\nrelqnap02\ReEDS\_ReEDS Documentation` like past years' updates. Short descriptions of the each module are given below, in an order that the execution should be done:

 1. `NEMS Plant File/`: raw plant file data from AEO, which will be updated every year
    - point of contact: Wesley Cole \<Wesley.Cole@nrel.gov\>

 2. `Unit_database/`: prepossessing scripts to create almost-ready unit database files (These don't contain cooling/water data). Follow `workflow.docx`
    - output file: `2020nems_needs_ct.csv`
    - point of contact: Will Frazier \<Will.Frazier@nrel.gov\>

 3. `NEMS_Unit_Database_Water_Sources/`: scripts to that add cooling/water data to the `2020nems_needs_ct.csv`, specifically appends cooling technology type as `ctt` column, water source type as `wst` column, cooling water tech as `coolingwatertech` column. `coolingwatertech` column will have entries like `CoalOldUns_r_fg` where `CoalOldUns` is a standard numeraire tech, `r` is ctt referring to recirculating cooling type, and `fg` is a `wst` referring to fresh ground water type. When switch `Sw_WaterMain` is ON while running ReEDS 2.0, `coolingwatertech` will replace `tech`
    - output file: `ReEDS_generator_database_final_EIA-NEMS_input.csv`
    - needs annual update by updating in `\inputs\` files like `2020nems_needs_ct.csv` created by **Step 2** and [thermoelectric cooling water data](https://www.eia.gov/electricity/data/water/) like `cooling_summary_2018.xlsx`, among others. Please follow README.md in `NEMS_Unit_Database_Water_Sources/` and update all the possible inputs while updating, might require some updates in codes depending on how column names of processed AEO Plant File created by **Step 2** (like `2020nems_needs_ct.csv`) look like
    - point of contact: Saroj Khanal \<Saroj.Khanal@nrel.gov or sarojpkhanal@gmail.com\>

 4. `Unit_database_cooling_water/`: creates data files (three unit gdx files and one unit csv file) ready for ReEDS 2.0.
    - output files: `ReEDS_generator_database_final_EIA-NEMS.csv`, `ExistingUnits_EIA-NEMS.gdx`, `PrescriptiveBuilds_EIA-NEMS.gdx`, and `PrescriptiveRetirements_EIA-NEMS.gdx`, to be placed in `ReEDS-2.0/inputs/capacitydata/`
    - point of contact: Saroj Khanal \<Saroj.Khanal@nrel.gov or sarojpkhanal@gmail.com\>

 5. `Unit_database_cooling_water_wst_fixed/`: These final scripts fix some of insufficient water supply data through one standard ReEDS 2.0 sequential reference run using previous unit gdx files and csv files (`outputs/` of `Unit_database_cooling_water/`) and follows some manual steps to update `ReEDS_generator_database_final_EIA-NEMS_input.csv` file. Details are provided in README.md of individual folders that has suites of scripts to perform particular operations.
     - output file: `ReEDS_generator_database_final_EIA-NEMS.csv`, `ExistingUnits_EIA-NEMS.gdx`, `PrescriptiveBuilds_EIA-NEMS.gdx`, and `PrescriptiveRetirements_EIA-NEMS.gdx`, to be placed in `ReEDS-2.0/inputs/capacitydata/`
    - point of contact: Saroj Khanal \<Saroj.Khanal@nrel.gov or sarojpkhanal@gmail.com\>

By: Saroj Khanal \<Saroj.Khanal@nrel.gov or sarojpkhanal@gmail.com\> on 6/11/2020 

P.S. Please click `Ctrl + Shift + V` to view this file in a well formatted markdown in Visual Studio Code.