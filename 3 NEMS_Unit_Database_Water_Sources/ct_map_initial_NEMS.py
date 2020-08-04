# -*- coding: utf-8 -*-
"""
Spyder Editor

Script to automate cooling technology type (ct, finally called ctt) and water source type (wst) mapping to NEMS unit dataset! 
@author: skhanal
"""
import numpy as np
import pandas as pd
import time
import os

if not os.path.exists("outputs"): os.mkdir("outputs")
output_intermediates=True # True to see intermediate files in the outputs/ folder
print_time=True # True if printing of time duration is preferred
troubleshoot_on=False # True to customize columns to see in the intermediate outputs, customize in the slicing of abb dataframe, in "if troubleshoot_on: abb=abb[['Plant.Name',...]]" 
if print_time: start_time = time.time()

# Blocks below read in NEMS unit database, EIA unit cooling dataset, another EIA dataset with the nameplate capacity to append to the cooling dataset, tech codes and default cooling tech
ucs=pd.read_excel('inputs/UCS-EW3-Energy-Water-Database.xlsx',sheet_name='MAIN DATA', skiprows=4) # Classic UCS dataset containing ct and wst
eia_orig=pd.read_excel('inputs/cooling_detail_2018.xlsx', skiprows=2) # fresh EIA dataset
eia_orig.columns = eia_orig.columns.str.strip()
eia=eia_orig.groupby(['Plant Code','Generator ID'], as_index=False).first()
eia['Plant-Generator Code']=eia['Plant Code'].astype(str) + '-' + eia['Generator ID'].astype(str) # column to help map UCS dataset to EIA dataset
eia['tech code_eia']=eia['Generator Primary Energy Source Code']+'-'+eia['Generator Prime Mover Code']
eia['Plant Code']=eia['Plant Code'].astype(str)

# Assign the tech to the eia dataset based on tech codes
tech_codes_orig=pd.read_excel('inputs/tech_codes_new.xlsx', index_col=0)
tech_codes_eia=pd.read_excel('inputs/eia_tech_codes_to_tech_mapper.xlsx', skiprows=0)
tech_codes_eia=pd.merge(tech_codes_eia, tech_codes_orig[['tech code', 'tech']], on='tech code', how='left')
tech_codes_eia.loc[tech_codes_eia['tech code']=='NUC-ST','tech']='nuclear' # to handle a weird tech codes; it NUC-ST is generalized in EIA than codes like URA-CD;URA-NB;URA-ND;URA-NG;URA-NH;URA-NL;URA-NP;URA-NQ in ABB
tech_codes_eia=tech_codes_eia[['tech code_eia', 'tech code', 'tech']].copy()
if output_intermediates: tech_codes_eia.to_csv('outputs/tech_codes_eia.csv')

# Update eia dataset with compatible ABB tech codes and techs
eia=pd.merge(eia, tech_codes_eia, on='tech code_eia', how='left')
#=================================================================================================
Plant_Y2018=pd.read_excel('inputs/2___Plant_Y2018.xlsx', skiprows=1)
# Nameplate capacity mapper to update EIA cooling dataset
Generator_Y2018_OP=pd.read_excel('inputs/3_1_Generator_Y2018.xlsx', sheet_name='Operable', skiprows=1)
Generator_Y2018_OP_req=Generator_Y2018_OP[['Plant Code', 'Plant Name', 'Generator ID', 'Nameplate Capacity (MW)']]
Generator_Y2018_RE_CN=pd.read_excel('inputs/3_1_Generator_Y2018.xlsx', sheet_name='Retired and Canceled', skiprows=1)
Generator_Y2018_RE_CN['Nameplate Capacity (MW)']=pd.to_numeric(Generator_Y2018_RE_CN['Nameplate Capacity (MW)'], errors='coerce')
Generator_Y2018_RE_CN_req=Generator_Y2018_RE_CN[['Plant Code', 'Plant Name', 'Generator ID', 'Nameplate Capacity (MW)']]
Generator_Y2018=pd.concat([Generator_Y2018_OP_req,Generator_Y2018_RE_CN_req])
Generator_Y2018['Plant Code']=Generator_Y2018['Plant Code'].astype(str).str.rstrip('0').str.strip('.')
Generator_Y2018['Plant-Generator Code']=Generator_Y2018['Plant Code'].astype(str)+'-'+Generator_Y2018['Generator ID'].astype(str)
Plant_Y2018['Plant Code']=Plant_Y2018['Plant Code'].astype(str)
eia_withMW=pd.merge(eia,Generator_Y2018[['Nameplate Capacity (MW)','Plant-Generator Code']], on='Plant-Generator Code', how='left')

#update missing nameplate capacity from UCS dataset
eia_withMW=pd.merge(eia_withMW, ucs[['Plant-Generator Code', 'Nameplate Capacity (MW)']], on='Plant-Generator Code', how='left')
eia_withMW.loc[(eia_withMW['Nameplate Capacity (MW)_x'].isna() & ~eia_withMW['Nameplate Capacity (MW)_y'].isna()),'Nameplate Capacity (MW)_x']=eia_withMW['Nameplate Capacity (MW)_y']
eia_withMW.rename(columns={'Nameplate Capacity (MW)_x':'Nameplate Capacity (MW)'}, inplace=True)
eia_withMW.drop(['Nameplate Capacity (MW)_y'], axis=1, inplace=True)

if output_intermediates: eia_withMW.to_csv('outputs/eia_withMW.csv')
# eia_withMW data as eia onward
eia=eia_withMW.copy() # This is not good, .copy() should be used, but carefully to avoid warning when working on copied data! 
eia_unique=eia.drop_duplicates(subset=['Plant Code', 'Generator ID'], keep = 'first')

#%% ct and wst mapping with ReEDS technologies within EIA dataset 
#==========================================================#
# cooling tech assignements to a newly created 'ct' column #
#==========================================================#
if troubleshoot_on: eia['Type 1 Cooling']=eia['860 Cooling Type 1'] # Just to make columns near to the newly assigned ct 
if troubleshoot_on: eia['Type 2 Cooling']=eia['860 Cooling Type 2']
if troubleshoot_on: eia['Type 3 Cooling']=eia['923 Cooling Type']

# This portion could be mapped making a mapper file, however, the problems occurs at blank entries! But, it should be tried! 
# Assign ct based on the the Type 1, Type 2, and Type 3 Cooling data available, it creates a new columns 'ct' in "eia" dataframe
eia.loc[((eia['860 Cooling Type 1'] == '(ON) Once through No Cool Pond') |
        (eia['923 Cooling Type']=='ON')), 'ct']= 'once'
eia.loc[((eia['860 Cooling Type 1'] == '(RI) Recirculate: Induced Draft') |
        (eia['860 Cooling Type 1'] == '(RN) Recirculate: Natural Draft') | 
        (eia['860 Cooling Type 1'] == '(RF) Recirculate: Forced Draft')), 'ct'] = 'recirc'      
eia.loc[((eia['860 Cooling Type 1'] == '(RC) Recirculate: Cooling Pond') | 
       (eia['860 Cooling Type 1'] == '(OC) Once through with Cool Pond') |
       (eia['923 Cooling Type']=='RC')), 'ct'] = 'pond'
eia.loc[eia['860 Cooling Type 1'] == '(DC) Dry Cooling', 'ct']='dry'
eia.loc[eia['860 Cooling Type 1'] == '(HRI) Hybrid: Dry / Induced Draft', 'ct']='dry' # follow workflow doc, as most of them claims to conserve water more than 30% 
eia.loc[((eia['860 Cooling Type 1'] == '(OT) Other') &
        (eia['860 Cooling Type 2'] == 'RI')), 'ct']='recirc' # follow workflow doc 
eia.loc[((eia['860 Cooling Type 1'] == '(OT) Other') &
        (eia['923 Cooling Type'] == 'OT')), 'ct']='???map_to_manual_csv_or_ucs'        
eia.loc[((eia['860 Cooling Type 1'].isnull()) &
        (eia['860 Cooling Type 2'].isnull()) &
        (eia['923 Cooling Type']=='RI')), 'ct'] = 'recirc'
eia.loc[((eia['860 Cooling Type 1'].isnull()) &
        (eia['860 Cooling Type 2'].isnull()) &
        (eia['923 Cooling Type']=='HRF')), 'ct'] = 'recirc' # check the fraction of hybrid nature
eia.loc[((eia['860 Cooling Type 1'].isnull()) &
        (eia['860 Cooling Type 2'].isnull()) &
        (eia['923 Cooling Type']=='OC')), 'ct'] = 'pond'
eia.loc[((eia['860 Cooling Type 1'].isnull()) &
        (eia['860 Cooling Type 2'].isnull()) &
        (eia['923 Cooling Type'].isnull())), 'ct']='???ct'
if output_intermediates: eia.to_csv('outputs/eia.csv')

# append ct and wst columns to later supplement the unassigned ones: 
ucs=ucs.copy()
ucs[['Plant Code','Generator ID']] = ucs['Plant-Generator Code'].str.split("-", n=1, expand=True)
if output_intermediates: ucs.to_csv('outputs/ucs.csv')

dict_UCS_ct_mapper={'Once-Through': 'once', 'none': 'none', 'Dry Cooled':'dry', 'Cooling Pond':'pond', 'Recirculating': 'recirc'}
ucs['ct']=ucs['Cooling Technology'].map(dict_UCS_ct_mapper)

dict_UCS_wst_mapper={'Surface Water':'fsa', 'Municipal':'Municipal', 'Groundwater':'fg', 'Unknown Freshwater': 'fsa', 
                     'Ocean':'ss', 'Waste Water':'ww', 'Unknown':'???wst', 'GW/Waste Water':'ww', 'GW/Surface Water':'fsa', 
                     'GW/Municipal':'fg', 'Unknown Ocean':'ss'}
ucs['wst']=ucs['Reported Water Source (Type)'].map(dict_UCS_wst_mapper)
ucs['wst_name_ucs']=ucs['Reported Water Source (Type)']
eia_ucs_merged=pd.merge(eia, ucs[['Plant-Generator Code','ct', 'wst', 'wst_name_ucs']], on='Plant-Generator Code', how='left')
eia_ucs_merged['isUCS_EIA_equal']=np.where(eia_ucs_merged['ct_x']!=eia_ucs_merged['ct_y'], 'False', 'True')
eia_ucs_merged.rename(columns={'ct_x': 'ct', 'ct_y':'ct_ucs', 'wst':'wst_ucs'}, inplace=True)

# water source type assignements to a new 'wst' column:
eia_ucs_merged['Water Type.Water Source']=eia_ucs_merged['Water Type'].astype(str) + '.' + eia_ucs_merged['Water Source'].astype(str)
eia_ucs_merged['wst_name']=eia_ucs_merged['Water Source Name']
#eia_ucs_merged['wst']='' # optional
eia_ucs_merged.loc[(eia_ucs_merged['Water Type']== 'Fresh') & (eia_ucs_merged['Water Source']=='Surface'),'wst']='fsa'
eia_ucs_merged.loc[(eia_ucs_merged['Water Type']== 'Reclaimed') & (eia_ucs_merged['Water Source']=='Discharge'),'wst']='ww'
eia_ucs_merged.loc[(eia_ucs_merged['Water Type']== 'Fresh') & (eia_ucs_merged['Water Source']=='Ground'),'wst']='fg'
eia_ucs_merged.loc[(eia_ucs_merged['Water Type'].isnull()) & (eia_ucs_merged['Water Source'].isnull()),'wst']='.' # .
eia_ucs_merged.loc[(eia_ucs_merged['Water Type']== 'Saline') & (eia_ucs_merged['Water Source']=='Surface'),'wst']='ss'
eia_ucs_merged.loc[(eia_ucs_merged['Water Type']== 'Brackish') & (eia_ucs_merged['Water Source']=='Surface'),'wst']='ss'
eia_ucs_merged.loc[(eia_ucs_merged['Water Type']== 'Saline') & (eia_ucs_merged['Water Source']=='Other'),'wst']='ss'
eia_ucs_merged.loc[(eia_ucs_merged['Water Type']== 'Other') & (eia_ucs_merged['Water Source']=='Ground'),'wst']='fg'
eia_ucs_merged.loc[(eia_ucs_merged['Water Type']== 'Other') & (eia_ucs_merged['Water Source']=='Other'),'wst']='Other.Other'#Other.Other
eia_ucs_merged.loc[(eia_ucs_merged['Water Type']== 'Fresh') & (eia_ucs_merged['Water Source']=='Other'),'wst']='fsa'
eia_ucs_merged.loc[(eia_ucs_merged['Water Type']== 'Brackish') & (eia_ucs_merged['Water Source']=='Ground'),'wst']='sg'
eia_ucs_merged.loc[(eia_ucs_merged['Water Type'].isnull()) & (eia_ucs_merged['Water Source']=='Other'),'wst']='.Other'# .Other
eia_ucs_merged.loc[(eia_ucs_merged['Water Type']== 'Saline') & (eia_ucs_merged['Water Source']=='Ground'),'wst']='sg'
eia_ucs_merged.loc[(eia_ucs_merged['Water Type']=='Other') & (eia_ucs_merged['Water Source'].isnull()),'wst']='Other.' #Other.
eia_ucs_merged.loc[((eia_ucs_merged['wst']=='.') | 
                   (eia_ucs_merged['wst']=='Other.Other') | 
                   (eia_ucs_merged['wst']=='Other.') | 
                   (eia_ucs_merged['wst']=='.Other')),'wst']='???wst' 

# mapping water source from "2___Plant_Y2018.xlsx", which has rich entries of wst:
eia_ucs_merged=pd.merge(eia_ucs_merged,Plant_Y2018[['Plant Code','Name of Water Source']], on='Plant Code', how='left')
eia_ucs_merged.loc[((eia_ucs_merged['wst']=='???wst') & ~(eia_ucs_merged['Name of Water Source'].isnull())),'Water Source Name']=eia_ucs_merged['Name of Water Source']
eia_ucs_merged.loc[((eia_ucs_merged['wst']=='???wst') & (eia_ucs_merged['Water Source Name'].str.contains('chemical|treatment|waste|wtp|sewage', case=False, regex=True))), 'wst']='ww' #Some wst with Sewage is not working! 
eia_ucs_merged.loc[((eia_ucs_merged['wst']=='???wst') & (eia_ucs_merged['Water Source Name'].str.contains('munici|munci|city', case=False, regex=True))), 'wst']='Municipal' # attn: there are some municipality/well

# eia_ucs_merged.loc[((eia_ucs_merged['wst']=='???wst') & (eia_ucs_merged['Water Source Name'].str.contains('river', case=False, regex=True))), 'wst']= 'fsa'
# eia_ucs_merged.loc[((eia_ucs_merged['wst']=='???wst') & (eia_ucs_merged['Water Source Name'].str.contains('lake|reservoir|pool', case=False, regex=True))), 'wst']= 'fsl'
# comment this [line below] out if you want new water source type type 'fsl' for this category # verify if pool falls in this category and fresh water maps to this
eia_ucs_merged.loc[((eia_ucs_merged['wst']=='???wst') & (eia_ucs_merged['Water Source Name'].str.contains('river|lake|reservoir|pool', case=False, regex=True))), 'wst']= 'fsa' 

eia_ucs_merged.loc[((eia_ucs_merged['wst']=='???wst') & (eia_ucs_merged['Water Source Name'].str.contains('ocean|sound|bay', case=False, regex=True))), 'wst']='ss'
#eia_ucs_merged.loc[(eia_ucs_merged['wst']=='???wst') & (eia_ucs_merged['Water Source Name'].str.contains('munici|munci|well|city', case=False, regex=True)), 'wst']='fg' # attn: there are some municipality/well
eia_ucs_merged.loc[((eia_ucs_merged['wst']=='???wst') & (eia_ucs_merged['Water Source Name'].str.contains('well', case=False, regex=True))), 'wst']='fg' # attn: there are some municipality/well
eia_ucs_merged.loc[((eia_ucs_merged['wst']=='???wst') & (~eia_ucs_merged['wst_ucs'].isna())),'wst']=eia_ucs_merged['wst_ucs']

# Update the missing ct and wst dataset by merged UCS dataset columns
eia_ucs_merged.loc[eia_ucs_merged['ct']=='???ct', 'ct']=eia_ucs_merged['ct_ucs']
eia_ucs_merged.loc[eia_ucs_merged['ct'].isna() & ~eia_ucs_merged['wst_ucs'].isna(), 'wst']=eia_ucs_merged['wst_ucs'].isna()
eia_ucs_merged['map_ID']=eia_ucs_merged.index # map_ID later helps to track the status of mapping
if output_intermediates: eia_ucs_merged.to_csv('outputs/eia_ucs_merged.csv')

#%% mapping ct and wst to NEMS dataset
nems = pd.read_csv('inputs/2020nems_needs_ct.csv', index_col=None, low_memory=False) # input processed NEMS database
nems_orig=nems.copy() # df = df.copy() # to avoid warning # for pontential future use of full abb dataframe!
nems=nems.drop_duplicates(subset=['index'], keep='first')
nems=nems.copy()  # Check if required!
nems['PLANT_NAME']=nems['PLANT_NAME'].str.rstrip(' ').str.lstrip(' ')
nems['PLANT_ID']=nems['PLANT_ID'].astype(str)
nems['UNIT_ID']=nems['UNIT_ID'].str.rstrip(' ').str.lstrip(' ')

# # function below converts any lat and lon to FIPS code
# def lat_long2FIPS(lat=0, lon=0):
#    import requests
#    import urllib
#    #lat = 40
#    lon = -lon
#    params = urllib.parse.urlencode({'latitude': lat, 'longitude':lon, 'format':'json'}) #Encode parameters 
#    url = 'https://geo.fcc.gov/api/census/block/find?' + params #Contruct request URL
#    response = requests.get(url) #Get response from API
#    data = response.json() # Parse json in response
#    return(data['County']['FIPS']) # Print FIPS code

# nems['FIPS']=nems.apply(lambda row: lat_long2FIPS(row['LAT'],row['LONG']), axis=1)
# NEMS_index_FIPS = nems[['index', 'FIPS']].copy()
# NEMS_index_FIPS.to_csv('inputs/NEMS_index_FIPS.csv')

NEMS_index_FIPS=pd.read_csv('inputs/NEMS_index_FIPS.csv', index_col=None)

# append FIPS codes from Lattitude and Longitude; not all lat and long are in the NEMS datasets, so further merge from ABB datasets is used to complement the gap
nems=pd.merge(nems,NEMS_index_FIPS, on='index', how='left', validate='one_to_one')
abb = pd.read_csv('inputs/VentyxUnitData - Full.csv',sep=',', index_col=0, encoding='ISO-8859-1', low_memory=False) # ABB/Ventyx Unit Database
abb.drop_duplicates(subset=['Plant.Name', 'Plant.County.FIPS'], keep='first', inplace=True)
abb['Plant.County.FIPS']=abb['Plant.County.FIPS'].fillna(0).astype(np.int64)
abb['Plant Code']=abb['Plant.Government.ID'].str.split(';', expand=True)[0].astype(str).str.lstrip('0')
abb_sliced=abb[['Plant Code','Plant.County.FIPS']].copy()
abb_sliced.rename(columns={'Plant.County.FIPS':'FIPS'}, inplace=True)
nems.rename(columns={'PLANT_ID':'Plant Code'}, inplace=True)
abb_sliced.drop_duplicates(subset=['Plant Code'], keep='first', inplace=True)
nems_abb=pd.merge(nems, abb_sliced, on='Plant Code', how='left', validate='many_to_one')
nems_abb.loc[(nems_abb['FIPS_x'].isna() & ~nems_abb['FIPS_y'].isna()),'FIPS_x']=nems_abb['FIPS_y']
nems_abb.rename(columns={'FIPS_x':'FIPS', 'Plant Code':'PLANT_ID'}, inplace=True)
del nems_abb['FIPS_y']
nems=nems_abb.copy()
if output_intermediates: nems_abb.to_csv('outputs/nems_abb.csv')

if troubleshoot_on:
    nems=nems[['PLANT_NAME', 'PLANT_ID', 'UNIT_ID', 'index', 'RetireYear', 'tech', 'resource_region', 'pca', 'NAME_PLATE', 'NEMS_TYPE', 'REFURB_YR', 'LONG', 'LAT', 'FIPS']].copy() # needs update
    #'Commercial.Online.Year': 'REFURB_YR', 'Net.Summer.Capacity.MW':'WC_SUM'
    nems.rename(columns={'PLANT_NAME':'Plant Name', 'PLANT_ID':'Plant Code', 'UNIT_ID':'Generator ID', 'NAME_PLATE':'Nameplate Capacity (MW)'}, inplace=True)
else:
    nems=nems[['PLANT_NAME', 'PLANT_ID', 'UNIT_ID', 'index', 'RetireYear', 'tech', 'resource_region', 'pca', 'NAME_PLATE', 'NEMS_TYPE', 'LONG', 'LAT', 'FIPS']].copy() # needs update
    #'Commercial.Online.Year': 'REFURB_YR', 'Net.Summer.Capacity.MW':'WC_SUM'
    nems.rename(columns={'PLANT_NAME':'Plant Name', 'PLANT_ID':'Plant Code', 'UNIT_ID':'Generator ID','NAME_PLATE':'Nameplate Capacity (MW)'}, inplace=True)

# EIA cooling datasets to NEMS mapping
nems_eia_ucs_supplemented=pd.merge(nems,eia_ucs_merged[['Plant Code', 'Generator ID', 'ct', 'wst', 'map_ID']], on=['Plant Code', 'Generator ID'], how='left')
if output_intermediates: nems_eia_ucs_supplemented.to_csv('outputs/nems_eia_ucs_supplemented.csv')

def column2column_ct_wst_updater(row):
    row.loc[(row['ct_x'].isna() & ~row['ct_y'].isna()),'ct_x']=row['ct_y']
    row.loc[(row['wst_x'].isna() & ~row['wst_y'].isna()),'wst_x']=row['wst_y']
    row.rename(columns={'ct_x':'ct', 'wst_x':'wst'}, inplace=True)
    row.drop(columns=['ct_y', 'wst_y'], inplace=True)

# UCS supplemental update to the EIA mapped NEMS dataset
nems_eia_ucs_supplemented_ucs=pd.merge(nems_eia_ucs_supplemented, ucs[['Plant Code', 'Generator ID', 'ct', 'wst']], on=['Plant Code', 'Generator ID'], how='left')
if output_intermediates: nems_eia_ucs_supplemented_ucs.to_csv('outputs/nems_eia_ucs_supplemented_ucs.csv')
column2column_ct_wst_updater(nems_eia_ucs_supplemented_ucs)
if output_intermediates: nems_eia_ucs_supplemented_ucs.to_csv('outputs/nems_eia_ucs_supplemented_ucs_updated.csv')

#=============#
# Default cts #
#=============#
# first assign the same cts and wst to the units in the same plants whose 'NEMS_TYPE' are same
nems_eia_ucs_supplemented_ucs_dict=nems_eia_ucs_supplemented_ucs[['Plant Name', 'NEMS_TYPE', 'ct', 'wst']].drop_duplicates(subset=['Plant Name', 'NEMS_TYPE', 'ct'], keep='first') # This has some bugs!
nems_eia_ucs_supplemented_ucs_dict.dropna(axis=0, subset=['ct'], inplace=True)
nems_eia_ucs_supplemented_ucs_dict_nodups=nems_eia_ucs_supplemented_ucs_dict.drop_duplicates(subset=['Plant Name', 'NEMS_TYPE'], keep=False)
nems_eia_ucs_supplemented_ucs_flooded=pd.merge(nems_eia_ucs_supplemented_ucs, nems_eia_ucs_supplemented_ucs_dict_nodups, on=['Plant Name', 'NEMS_TYPE'], how='left')
column2column_ct_wst_updater(nems_eia_ucs_supplemented_ucs_flooded)
if output_intermediates: nems_eia_ucs_supplemented_ucs_flooded.to_csv('outputs/nems_eia_ucs_supplemented_ucs_flooded.csv')

#=========================================================================#
# Defaulting ct according to EFD Code (equivalent tech code) to ct mapper #
#=========================================================================#
tech_codes_orig=pd.read_excel('inputs/NEMS to ReEDS Tech Mapping_default cts.xlsx', skiprows=0)
tech_codes_orig_sliced=tech_codes_orig[['EFD Code', 'ReEDS Tech', 'default ct']].copy()
tech_codes_orig_sliced.rename(columns={'EFD Code': 'NEMS_TYPE', 'ReEDS Tech':'tech'}, inplace=True)

nems_ucs_defaulted=pd.merge(nems_eia_ucs_supplemented_ucs_flooded, tech_codes_orig_sliced[['NEMS_TYPE', 'default ct']], on='NEMS_TYPE', how='left')
nems_ucs_defaulted.loc[(nems_ucs_defaulted['ct'].isna() & ~nems_ucs_defaulted['default ct'].isna()),'ct']=nems_ucs_defaulted['default ct']
if output_intermediates: nems_ucs_defaulted.to_csv('outputs/nems_ucs_defaulted.csv')

#======================================#
# Check if it falls under allowable ct #
#======================================#
allowable_ct_mapper=pd.read_csv('inputs/allowable_ct_mapper.csv', index_col=0)
def validate_ct (row_orig): # function targeted for EIA dataset (eia)
    row=row_orig.copy()
    return allowable_ct_mapper.loc[row['tech'], row['ct']]

nems_ucs_defaulted['is_ct_allowed']=nems_ucs_defaulted.apply(validate_ct, axis='columns')
if output_intermediates: nems_ucs_defaulted.to_csv('outputs/nems_ucs_defaulted_validated.csv')
nems_ucs_defaulted.loc[~(nems_ucs_defaulted['is_ct_allowed']=='yes'), 'ct']=nems_ucs_defaulted['default ct']
nems_ucs_defaulted.loc[~(nems_ucs_defaulted['is_ct_allowed']=='yes'), 'wst']='???wst'
del nems_ucs_defaulted['is_ct_allowed']
nems_ucs_defaulted['is_ct_allowed']=nems_ucs_defaulted.apply(validate_ct, axis='columns')
if output_intermediates: nems_ucs_defaulted.to_csv('outputs/nems_ucs_defaulted_validated_corrected.csv')

# Default wst
#========================================#
# Verification of wst from USGS database #
#========================================#
# Extract useful columns like maximum water usage water source type for municipal, once-power, and recric-power plants with FIPS code from USGS data
usgs=pd.read_excel('inputs/usco2015v2.0.xlsx', sheet_name='usco2015v2.0', skiprows=1)
#usgs['FIPS']=usgs['FIPS'].astype(str)
county_munitype={'PS-WGWFr':'fg', 'PS-WGWSa':'sg', 'PS-WSWFr':'fsa', 'PS-WSWSa': 'ss'}
usgs['county_munitype_max']=usgs[['PS-WGWFr', 'PS-WGWSa', 'PS-WSWFr','PS-WSWSa']].idxmax(axis=1, skipna=True).map(county_munitype)

county_oncepower={'PO-WSWFr':'fsa', 'PO-WSWSa':'ss', 'PO-WGWFr':'fg', 'PO-WGWSa':'sg', 'PO-RecWW':'ww'}
usgs['PO-RecWW']=usgs['PO-RecWW'].str.strip('-').fillna(0).replace('',np.nan).astype('float64').fillna(0)
usgs['county_oncepower_max']=usgs[['PO-WSWFr', 'PO-WSWSa', 'PO-WGWFr', 'PO-WGWSa', 'PO-RecWW']].idxmax(axis=1, skipna=True).map(county_oncepower)

county_recircpower={'PC-WSWFr':'fsa', 'PC-WSWSa':'ss', 'PC-WGWFr':'fg', 'PC-WGWSa':'sg', 'PC-RecWW':'ww'}
usgs['PC-RecWW']=usgs['PC-RecWW'].str.strip('-').fillna(0).replace('',np.nan).astype('float64').fillna(0)
usgs['county_recircpower_max']=usgs[['PC-WSWFr', 'PC-WSWSa', 'PC-WGWFr', 'PC-WGWSa', 'PC-RecWW']].idxmax(axis=1, skipna=True).map(county_recircpower)

usgs_mapper=usgs[['FIPS','county_munitype_max', 'county_oncepower_max', 'county_recircpower_max']]
if output_intermediates: usgs_mapper.to_csv('outputs/usgs_mapper.csv')

usgs_sliced_dict=usgs_mapper[['FIPS', 'county_munitype_max']].set_index('FIPS')['county_munitype_max'].to_dict()

# Fill "Municipal" water category to ReEDS category with max water type from USGS datatypes for municipal water source:
nems_ucs_defaulted_temp=nems_ucs_defaulted.copy()
nems_ucs_defaulted_temp['usgs_municipal_water_type']=nems_ucs_defaulted_temp['FIPS'].map(usgs_sliced_dict)
if output_intermediates: nems_ucs_defaulted_temp.to_csv('outputs/nems_ucs_defaulted_temp.csv')
nems_ucs_defaulted_temp.loc[((nems_ucs_defaulted_temp['wst']=='Municipal') & (~nems_ucs_defaulted_temp['usgs_municipal_water_type'].isna())), 'wst']=nems_ucs_defaulted_temp['usgs_municipal_water_type']
if output_intermediates: nems_ucs_defaulted_temp.to_csv('outputs/nems_ucs_defaulted_temp_updated_wst.csv')

#================================================================================#
# Assign wst based on ct and available wst withtin the county from USGS database #
#================================================================================#
usgs_sliced_dict_once=usgs_mapper[['FIPS', 'county_oncepower_max']].set_index('FIPS')['county_oncepower_max'].to_dict()
nems_ucs_defaulted_temp['usgs_sliced_dict_once_water_type']=nems_ucs_defaulted_temp['FIPS'].map(usgs_sliced_dict_once)
usgs_sliced_dict_recirc=usgs_mapper[['FIPS', 'county_recircpower_max']].set_index('FIPS')['county_recircpower_max'].to_dict()
nems_ucs_defaulted_temp['usgs_sliced_dict_recirc_water_type']=nems_ucs_defaulted_temp['FIPS'].map(usgs_sliced_dict_recirc)
if output_intermediates: nems_ucs_defaulted_temp.to_csv('outputs/nems_ucs_defaulted_temp_updated_wst_once_recirc.csv')

#==================================================#
# Final mapped file (mapping with resource_region) #
#==================================================#
# Update unknown water source type data, denoted as '???wst', from USGS database for max water type for once and recirc power plants
ct_wst_pca_region_code_map=nems_ucs_defaulted_temp.copy()
ct_wst_pca_region_code_map.loc[ct_wst_pca_region_code_map['wst'].isna(), 'wst']='???wst'
#ct_wst_pca_region_code_map.loc[((ct_wst_pca_region_code_map['wst']=='???wst') & ((ct_wst_pca_region_code_map['ct']=='dry') | (ct_wst_pca_region_code_map['ct']=='n'))), 'wst']='n'
ct_wst_pca_region_code_map.loc[((ct_wst_pca_region_code_map['wst']=='???wst') & ((ct_wst_pca_region_code_map['ct']=='dry') | (ct_wst_pca_region_code_map['ct']=='n'))), 'wst']=ct_wst_pca_region_code_map['usgs_municipal_water_type']
ct_wst_pca_region_code_map.loc[((ct_wst_pca_region_code_map['wst']=='???wst') & (ct_wst_pca_region_code_map['ct']=='once') & (~ct_wst_pca_region_code_map['usgs_sliced_dict_once_water_type'].isna())), 'wst']=ct_wst_pca_region_code_map['usgs_sliced_dict_once_water_type']
ct_wst_pca_region_code_map.loc[((ct_wst_pca_region_code_map['wst']=='???wst') & (ct_wst_pca_region_code_map['ct']=='recirc') & (~ct_wst_pca_region_code_map['usgs_sliced_dict_recirc_water_type'].isna())), 'wst']=ct_wst_pca_region_code_map['usgs_sliced_dict_recirc_water_type']
ct_wst_pca_region_code_map.loc[(ct_wst_pca_region_code_map['wst']=='???wst'), 'wst']='fsa'
#ct_wst_pca_region_code_map.loc[(ct_wst_pca_region_code_map['wst']=='Municipal'), 'wst']='fg' # confirm this with Stuart
if output_intermediates: ct_wst_pca_region_code_map.to_csv('outputs/ct_wst_pca_region_code_map_prefinal.csv')
ct_wst_pca_region_code_map=ct_wst_pca_region_code_map[['index', 'pca', 'resource_region', 'ct', 'wst']].copy()

ct_encoder_dict={'once':'o', 'dry':'d', 'recirc':'r', 'pond':'p', 'none':'n'}
# wst_encoder={'None':'n', 'Unappropriated': 'fsa', 'Potable Groundwater':'fg', 'Saline Surface': 'ss', 'Wastewater':'ww', 'Brackish Groundwater':'sg'}
ct_wst_pca_region_code_map['ct']=ct_wst_pca_region_code_map['ct'].map(ct_encoder_dict)
ct_wst_pca_region_code_map.rename(columns = {'ct': 'ctt'}, inplace = True)
ct_wst_pca_region_code_map.to_csv('ct_wst_pca_region_code_map_NEMS.csv')

# [End of Code]

if print_time:  print("--- %s seconds ---" % (time.time() - start_time))