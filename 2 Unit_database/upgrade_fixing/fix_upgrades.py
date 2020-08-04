# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 16:33:51 2019

@author: afrazier
"""

import pandas as pd

def fix_upgrades(nems):
    
    subset = nems[['tech','pca','DEMREG','cap','RetireYear','Commercial.Online.Year.Quarter','IsExistUnit','Fully.Loaded.Tested.Heat.Rate.Btu.kWh...Modeled','PLANT_ID','VINTAGE','REFURB_YR','UID']]
    
    retires = (subset['VINTAGE'] == 6) & (subset['RetireYear'] >= 2009)
    refurbs = (subset['VINTAGE'] == 7) & (subset['Commercial.Online.Year.Quarter']>=2010)
    
    rets = subset[retires].reset_index(drop=True)
    refs = subset[refurbs].reset_index(drop=True)
    
    upgrades = pd.concat([refs,rets], sort=False).reset_index(drop=True)
    upgrades = upgrades.sort_values('UID').reset_index(drop=True)
#    wrong = upgrades[upgrades['Commercial.Online.Year.Quarter']>upgrades['RetireYear']].reset_index(drop=True)
    upgrades = upgrades[upgrades['Commercial.Online.Year.Quarter']<=upgrades['RetireYear']].reset_index(drop=True)
    upgrades_by_id = upgrades.set_index('UID')
    
    plant_refurbs = pd.DataFrame(columns=['UID_retire','UID_refurb'])
    plant_upgrades = pd.DataFrame(columns=['UID_retire','UID_refurb'])
    plant_downgrades = pd.DataFrame(columns=['UID_retire','UID_refurb'])
    intermediate_ids = []
    no_match_ids = []
    
    start = -1
    i = 0
    while i in range(0,len(upgrades),1):
        
        if start == -1 and upgrades.loc[i,'VINTAGE'] == 6:
            start = i
            id_ret = upgrades.loc[i,'UID']
        elif start != -1 and upgrades.loc[i,'VINTAGE'] == 6:
            id_intermediate = upgrades.loc[i,'UID']
            if upgrades_by_id.loc[id_ret,'REFURB_YR'] == upgrades_by_id.loc[id_intermediate,'REFURB_YR']:
                intermediate_ids.append(id_intermediate)
        elif start != -1 and upgrades.loc[i,'VINTAGE'] == 7:
            id_refurb = upgrades.loc[i,'UID']
            if upgrades_by_id.loc[id_ret,'REFURB_YR'] == upgrades_by_id.loc[id_refurb,'REFURB_YR']:
                if upgrades_by_id.loc[id_refurb,'cap'] == upgrades_by_id.loc[id_ret,'cap']:
                    plant_refurb = pd.DataFrame(columns=['UID_retire','UID_refurb'], data=[[id_ret,id_refurb]])
                    plant_refurbs = pd.concat([plant_refurbs,plant_refurb], sort=False).reset_index(drop=True)
                elif upgrades_by_id.loc[id_refurb,'cap'] > upgrades_by_id.loc[id_ret,'cap']:
                    plant_upgrade = pd.DataFrame(columns=['UID_retire','UID_refurb'], data=[[id_ret,id_refurb]])
                    plant_upgrades = pd.concat([plant_upgrades,plant_upgrade], sort=False).reset_index(drop=True)
                elif upgrades_by_id.loc[id_refurb,'cap'] < upgrades_by_id.loc[id_ret,'cap']:
                    plant_downgrade = pd.DataFrame(columns=['UID_retire','UID_refurb'], data=[[id_ret,id_refurb]])
                    plant_downgrades = pd.concat([plant_downgrades,plant_downgrade], sort=False).reset_index(drop=True)
            else:
                no_match_ids.append(id_ret)
                i -= 2
            start = -1
        elif start == -1 and upgrades.loc[i,'VINTAGE'] == 7:
            pass
        i += 1
        
    nems.loc[:,'index'] = nems.loc[:,'UID']
    nems = nems.set_index('index')
    
    for refurb in range(0,len(plant_refurbs),1):
        nems.loc[plant_refurbs.loc[refurb,'UID_refurb'],'Commercial.Online.Year.Quarter'] = nems.loc[plant_refurbs.loc[refurb,'UID_retire'],'Commercial.Online.Year.Quarter']
    
    ret_cols = ['RetireYear','NukeRefRetireYear','NukeEarlyRetireYear','Nuke60RetireYear','Nuke80RetireYear']
    
    for upgrade in range(0,len(plant_upgrades),1):
        for ret_col in ret_cols:
            nems.loc[plant_upgrades.loc[upgrade,'UID_retire'],ret_col] = nems.loc[plant_upgrades.loc[upgrade,'UID_refurb'],ret_col]
        cap_dif = nems.loc[plant_upgrades.loc[upgrade,'UID_refurb'],'cap'] - nems.loc[plant_upgrades.loc[upgrade,'UID_retire'],'cap']
        nems.loc[plant_upgrades.loc[upgrade,'UID_refurb'],'cap'] = cap_dif
        
    remove_plants = plant_refurbs['UID_retire'].tolist() + intermediate_ids
    
    nems = nems[~nems['UID'].isin(remove_plants)]
    
    index_new_coal = (nems['tech'].isin(['CoalOldUns','CoalOldScr'])) & (nems['Commercial.Online.Year.Quarter'] > 1994)
    nems.loc[index_new_coal,'tech'] = 'coal-new'
    
    index_battery_CA = (nems['tech'] == 'battery') & (nems['STATE'] == 'CA')
    index_battery_notCA = (nems['tech'] == 'battery') & (nems['STATE'] != 'CA')
    nems.loc[index_battery_notCA,'tech'] = 'battery_2'
    nems.loc[index_battery_CA,'tech'] = 'battery_4'
        
    return nems
