# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 15:43:20 2019

@author: afrazier
"""

import pandas as pd
import numpy as np

def set_retire_years(nems):

# =============================================================================
# Technology naming convention
# =============================================================================

    nems['tech'].replace('csp','csp-ns',inplace=True)
    
    upv = (nems['tech'] == 'pv') & (nems['SUMMER_CAP'] >= 5)
    dupv = (nems['tech'] == 'pv') & (nems['SUMMER_CAP'] < 5)
    
    nems.loc[upv,'tech'] = 'UPV'
    nems.loc[dupv,'tech'] = 'DUPV'
    
    # =============================================================================
    # Retire years
    # =============================================================================
    
    no_retires = nems['RETIRE_YR'] == 9999
    
    nems.loc[no_retires,'RetireYearGiven'] = False
    nems.loc[~no_retires,'RetireYearGiven'] = True
    
    lifetimes = pd.read_csv('lifetimes.csv')
    lifetimes.set_index('tech',inplace=True)
    
    for i in range(0,len(nems),1):
        if nems.loc[i,'RETIRE_YR'] == 9999:
            tech = nems.loc[i,'tech']
            size = nems.loc[i,'SUMMER_CAP']
            if size >= 100:
                lifetime = lifetimes.loc[tech,'lifetime_big']
            elif size < 100:
                lifetime = lifetimes.loc[tech,'lifetime_small']
            nems.loc[i,'RETIRE_YR'] = nems.loc[i,'REFURB_YR'] + lifetime
        elif nems.loc[i,'RETIRE_YR'] != 9999:
            pass
            
    nems['Nuke60RetireYear'] = nems['RETIRE_YR']
    nems['Nuke80RetireYear'] = nems['RETIRE_YR']
    nems['NukeRefRetireYear'] = nems['RETIRE_YR']
    nems['NukeEarlyRetireYear'] = nems['RETIRE_YR']
    
    nukes = (nems['tech'] == 'nuclear') & (nems['RetireYearGiven'] == False)
    
    nems.loc[nukes,'Nuke80RetireYear'] += 20
    
    nukes1 = (nems['RetireYearGiven'] == False) & (nems['NukeRetireBin'] == 1)
    nukes2 = (nems['RetireYearGiven'] == False) & (nems['NukeRetireBin'] == 2)
    
    nems.loc[nukes2,'NukeRefRetireYear'] += 20
    nems.loc[nukes1,'NukeEarlyRetireYear'] -= 10
    
    check = nems[['tech','PLANT_NAME','SUMMER_CAP','NukeRetireBin','RETIRE_YR','Nuke60RetireYear','Nuke80RetireYear','NukeRefRetireYear','NukeEarlyRetireYear','RetireYearGiven']]
    
    nems_cats = list(nems)
    
    exist = nems['RETIRE_YR'] > 2010
    not_exist = nems['RETIRE_YR'] <= 2010
    nems.loc[exist,'IsExistUnit'] = True
    nems.loc[not_exist,'IsExistUnit'] = False
    
    # =============================================================================
    # Formatting
    # =============================================================================
    
    nems.loc[:,'Plant.NAICS.Description'] = 'Utilities'
    
    nems_cats_ordered = ['tech','PCA','DEMREG','SUMMER_CAP','RETIRE_YR','NukeRefRetireYear','Nuke60RetireYear','Nuke80RetireYear','NukeEarlyRetireYear','START_YR',
                         'IsExistUnit','HEATRATE','Plant.NAICS.Description']
    
    for cat in nems_cats:
        if cat not in nems_cats_ordered:
            nems_cats_ordered.append(cat)
            
    nems_ordered = nems[nems_cats_ordered]
    
    nems_ordered.rename(columns={'PCA':'pca','SUMMER_CAP':'cap','RETIRE_YR':'RetireYear','START_YR':'Commercial.Online.Year.Quarter','HEATRATE':'Fully.Loaded.Tested.Heat.Rate.Btu.kWh...Modeled'},inplace=True)
    
    nems_ordered.loc[:,'Commercial.Online.Year.Quarter'] = nems_ordered.loc[:,'Commercial.Online.Year.Quarter'].astype(str) + '-1'
    
    nems = nems_ordered.copy()
    
    techs = nems['tech'].drop_duplicates().tolist()
    
    no_hr = ['hydro','pumped-hydro','wind-ons','wind-ofs','csp-ns','DUPV','UPV','battery']
    
    nems.loc[nems['tech'].isin(no_hr),'Fully.Loaded.Tested.Heat.Rate.Btu.kWh...Modeled'] = np.nan
    
    # =============================================================================
    # Siting plants with no lat/long coordinates
    # =============================================================================
    
    for i in range(0,len(nems),1):
        nems.loc[i,'Commercial.Online.Year.Quarter'] = pd.to_numeric(nems.loc[i,'Commercial.Online.Year.Quarter'][:4])
        
    hierarchy = pd.read_csv('hierarchy.csv')
    hierarchy.rename(columns={'Dim1':'resource_region_replace','Dim2':'pca_replace','Dim7':'STATE'},inplace=True)
    hierarchy = hierarchy[['resource_region_replace','pca_replace','STATE']]
    hierarchy = hierarchy.drop_duplicates().reset_index(drop=True)
    hierarchy = hierarchy[hierarchy['resource_region_replace']<=356].reset_index(drop=True)
    hierarchy = hierarchy.drop_duplicates(keep='first', subset='STATE').reset_index(drop=True)
    
    nems_no_ba = nems[nems['LONG']==0]
    nems_no_ba = pd.merge(left=hierarchy, right=nems_no_ba, on='STATE', how='right')
    
    cols = [col for col in list(nems)]
    
    nems = pd.merge(left=nems_no_ba, right=nems, on=cols, how='right')
    
    nems['DEMREG'].update(nems['resource_region_replace'])
    nems['pca'].update(nems['pca_replace'])
    
    nems.drop(['resource_region_replace','pca_replace'],1,inplace=True)
    
    return nems


