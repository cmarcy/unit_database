# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 16:34:09 2019

@author: afrazier
"""

import pandas as pd
import os
import numpy as np

os.chdir('C:/Users/SKHANAL/Desktop/WaterClimate/AEO 2020 Update/Unit_database_cooling_water/upgrade_fixing')

# =============================================================================
# Generating input files for ReEDS
# =============================================================================

nems = pd.read_csv('ReEDS_generator_database_final_EIA-NEMS_input.csv', low_memory=False)

nems.rename(columns={' T_PCA':'pca'}, inplace=True)

nems['tech'].replace('battery','battery_4',inplace=True)

techs = nems['tech'].drop_duplicates().tolist()

no_hr = ['hydro','pumped-hydro','wind-ons','wind-ofs','csp-ns','DUPV','UPV','battery_4']

qctn = [tech for tech in techs if tech not in no_hr]
qctn.append('coal-new')

nems.rename(columns={'Commercial.Online.Year.Quarter':'Commercial.Online.Year'}, inplace=True)

coal_new_ind = (nems['tech'].isin(['CoalOldScr','CoalOldUns'])) & (nems['Commercial.Online.Year']>=1995)
nems.loc[coal_new_ind,'tech'] = 'coal-new'

# Existing capacity


CONVOLDqctn = nems[['tech','coolingwatertech','pca','ctt','wst','cap','IsExistUnit','Commercial.Online.Year']].copy()
coal_new_ind = (CONVOLDqctn['tech'].isin(['CoalOldScr','CoalOldUns'])) & (CONVOLDqctn['Commercial.Online.Year']>=1995)
CONVOLDqctn.loc[coal_new_ind,'tech'] = 'coal-new'
includers = (CONVOLDqctn['tech'].isin(qctn)) & (CONVOLDqctn['IsExistUnit'] == True) & (CONVOLDqctn['Commercial.Online.Year']<2010)
CONVOLDqctn = CONVOLDqctn[includers].reset_index(drop=True)
CONVOLDqctn = CONVOLDqctn[['tech','coolingwatertech','pca','ctt','wst','cap']].groupby(by=['tech','coolingwatertech','pca', 'ctt', 'wst'], as_index=False).sum().reset_index(drop=True)

import_store_power_cap_at_grid = nems[nems['tech'].isin(['pumped-hydro','battery_4', 'battery_2'])][['tech','coolingwatertech','pca','cap','IsExistUnit','Commercial.Online.Year']].reset_index(drop=True)
includers = (import_store_power_cap_at_grid['IsExistUnit']==True) & (import_store_power_cap_at_grid['Commercial.Online.Year']<2010)
import_store_power_cap_at_grid = import_store_power_cap_at_grid[includers].reset_index(drop=True)
import_store_power_cap_at_grid = import_store_power_cap_at_grid[['tech','coolingwatertech','pca','cap']].groupby(by=['coolingwatertech','pca'], as_index=False).sum().reset_index(drop=True)

tmpCSPOct = nems[nems['tech']=='csp-ns'][['tech','pca','resource_region','ctt','wst','cap','IsExistUnit','Commercial.Online.Year']].reset_index(drop=True)
includers = (tmpCSPOct['IsExistUnit']==True) & (tmpCSPOct['Commercial.Online.Year']<2010)
tmpCSPOct = tmpCSPOct[includers].reset_index(drop=True)
tmpCSPOct = tmpCSPOct[['resource_region','ctt','wst','cap']].groupby(by=['resource_region','ctt','wst'], as_index=False).sum()

tmpDUPVOn = nems[nems['tech']=='DUPV'][['tech','pca','ctt','wst','cap','IsExistUnit','Commercial.Online.Year']].reset_index(drop=True)
includers = (tmpDUPVOn['IsExistUnit']==True) & (tmpDUPVOn['Commercial.Online.Year']<2010)
tmpDUPVOn = tmpDUPVOn[includers].reset_index(drop=True)
tmpDUPVOn = tmpDUPVOn[['pca','cap']].groupby(by='pca', as_index=False).sum()
tmpDUPVOn.loc[:,'cap'] *= 1.3

tmpUPVOn = nems[nems['tech']=='UPV'][['tech','pca','ctt','cap','IsExistUnit','Commercial.Online.Year']].reset_index(drop=True)
includers = (tmpUPVOn['IsExistUnit']==True) & (tmpUPVOn['Commercial.Online.Year']<2010)
tmpUPVOn = tmpUPVOn[includers].reset_index(drop=True)
tmpUPVOn = tmpUPVOn[['pca','cap']].groupby(by='pca', as_index=False).sum()
tmpUPVOn.loc[:,'cap'] *= 1.3

tmpWTOi = nems[nems['tech'].isin(['wind-ons','wind-ofs'])][['tech','pca','resource_region','ctt','cap','IsExistUnit','Commercial.Online.Year']].reset_index(drop=True)
includers = (tmpWTOi['IsExistUnit']==True) & (tmpWTOi['Commercial.Online.Year']<2010)
tmpWTOi = tmpWTOi[includers].reset_index(drop=True)
tmpWTOi = tmpWTOi[['resource_region','cap']].groupby(by=['resource_region'], as_index=False).sum()

# Prescribed builds

PrescriptiveBuildsNonQn = nems[nems['tech'].isin(['DUPV','UPV','csp-ns'])].copy()
PrescriptiveBuildsNonQn = PrescriptiveBuildsNonQn[PrescriptiveBuildsNonQn['Commercial.Online.Year']>=2010]
PrescriptiveBuildsNonQn = PrescriptiveBuildsNonQn[['Commercial.Online.Year','pca','tech','cap']].groupby(by=['Commercial.Online.Year','pca','tech'], as_index=False).sum()
PrescriptiveBuildsNonQn.loc[:,'cap'] *= 1.3

qctn.append('hydro')
PrescriptiveBuildsnqct = nems[nems['tech'].isin(qctn)].copy()
coal_new_ind = (PrescriptiveBuildsnqct['tech'].isin(['CoalOldScr','CoalOldUns'])) & (PrescriptiveBuildsnqct['Commercial.Online.Year']>=1995)
PrescriptiveBuildsnqct.loc[coal_new_ind,'tech'] = 'coal-new'
PrescriptiveBuildsnqct = PrescriptiveBuildsnqct[PrescriptiveBuildsnqct['Commercial.Online.Year']>=2010]
PrescriptiveBuildsnqct = PrescriptiveBuildsnqct[['Commercial.Online.Year','pca','tech','coolingwatertech','ctt','wst','cap']].groupby(by=['Commercial.Online.Year','pca','tech','coolingwatertech','ctt','wst'], as_index=False).sum()

PrescriptiveBuildsStorage = nems[nems['tech'].isin(['pumped-hydro','battery_4', 'battery_2'])].copy()
PrescriptiveBuildsStorage = PrescriptiveBuildsStorage[PrescriptiveBuildsStorage['Commercial.Online.Year']>=2010]
PrescriptiveBuildsStorage = PrescriptiveBuildsStorage[['Commercial.Online.Year','pca','tech','cap']].groupby(by=['Commercial.Online.Year','pca','tech'], as_index=False).sum()

PrescriptiveBuildsWind = nems[nems['tech'].isin(['wind-ofs','wind-ons'])].copy()
PrescriptiveBuildsWind = PrescriptiveBuildsWind[PrescriptiveBuildsWind['Commercial.Online.Year']>=2010]
PrescriptiveBuildsWind = PrescriptiveBuildsWind[['Commercial.Online.Year','resource_region','tech','cap']].groupby(by=['Commercial.Online.Year','resource_region','tech'], as_index=False).sum()

# Prescribed Retirements

qctn.remove('geothermal')
qctn.append('pumped-hydro')
Nuke60RetireYear = nems[nems['IsExistUnit']==True].copy()
coal_new_ind = (Nuke60RetireYear['tech'].isin(['CoalOldScr','CoalOldUns'])) & (Nuke60RetireYear['Commercial.Online.Year']>=1995)
Nuke60RetireYear.loc[coal_new_ind,'tech'] = 'coal-new'
Nuke60RetireYear = Nuke60RetireYear[Nuke60RetireYear['tech'].isin(qctn)].reset_index(drop=True)
Nuke60RetireYear = Nuke60RetireYear[['Nuke60RetireYear','pca','tech','coolingwatertech', 'ctt','wst','cap']].groupby(by=['Nuke60RetireYear','pca','tech','coolingwatertech', 'ctt','wst'], as_index=False).sum()

Nuke80RetireYear = nems[nems['IsExistUnit']==True].copy()
coal_new_ind = (Nuke80RetireYear['tech'].isin(['CoalOldScr','CoalOldUns'])) & (Nuke80RetireYear['Commercial.Online.Year']>=1995)
Nuke80RetireYear.loc[coal_new_ind,'tech'] = 'coal-new'
Nuke80RetireYear = Nuke80RetireYear[Nuke80RetireYear['tech'].isin(qctn)].reset_index(drop=True)
Nuke80RetireYear = Nuke80RetireYear[['Nuke80RetireYear','pca','tech','coolingwatertech','ctt','wst','cap']].groupby(by=['Nuke80RetireYear','pca','tech','coolingwatertech','ctt','wst'], as_index=False).sum()

NukeRefRetireYear = nems[nems['IsExistUnit']==True].copy()
coal_new_ind = (NukeRefRetireYear['tech'].isin(['CoalOldScr','CoalOldUns'])) & (NukeRefRetireYear['Commercial.Online.Year']>=1995)
NukeRefRetireYear.loc[coal_new_ind,'tech'] = 'coal-new'
NukeRefRetireYear = NukeRefRetireYear[NukeRefRetireYear['tech'].isin(qctn)].reset_index(drop=True)
NukeRefRetireYear = NukeRefRetireYear[['NukeRefRetireYear','pca','tech','coolingwatertech','ctt','wst','cap']].groupby(by=['NukeRefRetireYear','pca', 'tech','coolingwatertech','ctt','wst'], as_index=False).sum()

NukeEarlyRetireYear = nems[nems['IsExistUnit']==True].copy()
coal_new_ind = (NukeEarlyRetireYear['tech'].isin(['CoalOldScr','CoalOldUns'])) & (NukeEarlyRetireYear['Commercial.Online.Year']>=1995)
NukeEarlyRetireYear.loc[coal_new_ind,'tech'] = 'coal-new'
NukeEarlyRetireYear = NukeEarlyRetireYear[NukeEarlyRetireYear['tech'].isin(qctn)].reset_index(drop=True)
NukeEarlyRetireYear = NukeEarlyRetireYear[['NukeEarlyRetireYear','pca','tech', 'coolingwatertech','ctt','wst','cap']].groupby(by=['NukeEarlyRetireYear','pca','tech', 'coolingwatertech','ctt','wst'], as_index=False).sum()

PrescriptiveRet = nems[nems['IsExistUnit']==True].copy()
coal_new_ind = (PrescriptiveRet['tech'].isin(['CoalOldScr','CoalOldUns'])) & (PrescriptiveRet['Commercial.Online.Year']>=1995)
PrescriptiveRet.loc[coal_new_ind,'tech'] = 'coal-new'
PrescriptiveRet = PrescriptiveRet[PrescriptiveRet['tech'].isin(qctn)].reset_index(drop=True)
PrescriptiveRet = PrescriptiveRet[['RetireYear','pca','tech','coolingwatertech','ctt','wst','cap']].groupby(by=['RetireYear','pca','tech','coolingwatertech','ctt','wst'], as_index=False).sum()

WindRetireExisting = nems[nems['IsExistUnit']==True].copy()
WindRetireExisting = WindRetireExisting[WindRetireExisting['tech'].isin(['wind-ons','wind-ofs'])].reset_index(drop=True)
WindRetireExisting = WindRetireExisting[WindRetireExisting['RetireYear']<2040].reset_index(drop=True)
WindRetireExisting = WindRetireExisting[['resource_region','tech','RetireYear','cap']].groupby(by=['resource_region','tech','RetireYear'], as_index=False).sum()

WindRetirePrescribed = nems[nems['IsExistUnit']==True].copy()
WindRetirePrescribed = WindRetirePrescribed[WindRetirePrescribed['tech'].isin(['wind-ons','wind-ofs'])].reset_index(drop=True)
WindRetirePrescribed = WindRetirePrescribed[WindRetirePrescribed['RetireYear']>=2040].reset_index(drop=True)
WindRetirePrescribed = WindRetirePrescribed[['resource_region','tech','RetireYear','cap']].groupby(by=['resource_region','tech','RetireYear'], as_index=False).sum()

if not os.path.exists(os.path.join('post_ct_mapping','post_wst_implementation')):
    os.mkdir(os.path.join('C:/Users/SKHANAL/Desktop/WaterClimate/AEO 2020 Update/Unit_database_cooling_water/upgrade_fixing','post_ct_mapping'))
    os.mkdir(os.path.join('C:/Users/SKHANAL/Desktop/WaterClimate/AEO 2020 Update/Unit_database_cooling_water/upgrade_fixing','post_ct_mapping','post_wst_implementation'))
CONVOLDqctn.to_csv(os.path.join('post_ct_mapping','post_wst_implementation','CONVOLDqctn.csv'),index=False)
import_store_power_cap_at_grid.to_csv(os.path.join('post_ct_mapping','post_wst_implementation','import_store_power_cap_at_grid.csv'),index=False)
tmpCSPOct.to_csv(os.path.join('post_ct_mapping','post_wst_implementation','tmpCSPOct.csv'),index=False)
tmpDUPVOn.to_csv(os.path.join('post_ct_mapping','post_wst_implementation','tmpDUPVOn.csv'),index=False)
tmpUPVOn.to_csv(os.path.join('post_ct_mapping','post_wst_implementation','tmpUPVOn.csv'),index=False)
tmpWTOi.to_csv(os.path.join('post_ct_mapping','post_wst_implementation','tmpWTOi.csv'),index=False)
PrescriptiveBuildsNonQn.to_csv(os.path.join('post_ct_mapping','post_wst_implementation','PrescriptiveBuildsNonQn.csv'),index=False)
PrescriptiveBuildsnqct.to_csv(os.path.join('post_ct_mapping','post_wst_implementation','PrescriptiveBuildsnqct.csv'),index=False)
PrescriptiveBuildsStorage.to_csv(os.path.join('post_ct_mapping','post_wst_implementation','PrescriptiveBuildsStorage.csv'),index=False)
PrescriptiveBuildsWind.to_csv(os.path.join('post_ct_mapping','post_wst_implementation','PrescriptiveBuildsWind.csv'),index=False)
Nuke60RetireYear.to_csv(os.path.join('post_ct_mapping','post_wst_implementation','Nuke60RetireYear.csv'),index=False)
Nuke80RetireYear.to_csv(os.path.join('post_ct_mapping','post_wst_implementation','Nuke80RetireYear.csv'),index=False)
NukeRefRetireYear.to_csv(os.path.join('post_ct_mapping','post_wst_implementation','NukeRefRetireYear.csv'),index=False)
NukeEarlyRetireYear.to_csv(os.path.join('post_ct_mapping','post_wst_implementation','NukeEarlyRetireYear.csv'),index=False)
PrescriptiveRet.to_csv(os.path.join('post_ct_mapping','post_wst_implementation','PrescriptiveRet.csv'),index=False)
WindRetireExisting.to_csv(os.path.join('post_ct_mapping','post_wst_implementation','WindRetireExisting.csv'),index=False)
WindRetirePrescribed.to_csv(os.path.join('post_ct_mapping','post_wst_implementation','WindRetirePrescribed.csv'),index=False)

# =============================================================================
# Finalizing units file
# =============================================================================

nems.loc[:,'Commercial.Online.Year.Quarter'] = nems.loc[:,'Commercial.Online.Year'].astype(str) + '-1'

leading_cols = ["tech","pca","resource_region","cap","Nuke60RetireYear","Nuke80RetireYear","NukeEarlyRetireYear","NukeRefRetireYear","RetireYear","Commercial.Online.Year.Quarter","IsExistUnit","Fully.Loaded.Tested.Heat.Rate.Btu.kWh...Modeled","Plant.NAICS.Description"]

other_cols = [col for col in list(nems) if col not in leading_cols]

col_order = leading_cols + other_cols

nems = nems[col_order]

nems.loc[nems['tech'].isin(no_hr),'Fully.Loaded.Tested.Heat.Rate.Btu.kWh...Modeled'] = np.nan

nems.rename(columns = {"VAR_OM":"W_VOM", "FIX_OM":"W_FOM", "CAPADD":"W_CAPAD", "COMBf":"WCOMB_F", "COMBv":"WCOMB_V", "SNCRf":"WSNCR_F", "SNCRv":"WSNCR_V", "SCRf":"WSCR_F", "SCRv":"WSCR_V", "DSIF":"W_DSIF", "DSIV":"W_DSIV", "FFF":"W_FFF", "FFV":"W_FFV"}, inplace='True')

nems.to_csv('ReEDS_generator_database_final_EIA-NEMS.csv',index=False)

