# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 14:34:22 2019

@author: skhanal
This script generates new technologies set `i_new.csv`, linking set `i_new_linkage.csv`, and `append2tech_map.csv` for bokeh

"""
import pandas as pd
tech_ctt_wst=pd.read_csv("tech_ctt_wst_map.csv", sep = ',', skiprows = [0], index_col=0)
myfile = open('i_coolingtech_watersource_link.csv', 'w')

def expand_index(index2expand):
    _expanded_index = list()
    i=index2expand
    if '*' in i:
        _start = int(i.split('*')[0].split('_')[-1])
        _end = int(i.split('*')[1].split('_')[-1])
        _base = i.split('_'+ i.split('*')[0].split('_')[-1])[0]
        for i in range(_start, _end+1):
            _expanded_index.append(f'{_base}_{i}')
    return _expanded_index

def name_tech(row):
    myfile.write('*i,ii,ctt,wst\n')
    i_n_n_ctt = list(row.loc[row.loc[: ,'none_n'] == 'YES'].index.unique())
    for i in row.index:
        for ctt in ['once_o', 'recirc_r', 'pond_p', 'dry_d', 'none_n'] if i in i_n_n_ctt else ['once_o', 'recirc_r', 'pond_p', 'dry_d']:
            for wst in ['fsu', 'fsa', 'fsl', 'fg', 'sg', 'ss', 'ww']:
                if row.loc[i, ctt] == "YES":
                    ctt_temp = ctt.split('_')[1]
                    if '*' in i:
                        _j=expand_index(i)
                        for j in _j:
                            myfile.write(f'{j}_{ctt_temp}_{wst},{j},{ctt_temp},{wst}\n')
                    else:
                        myfile.write(f'{i}_{ctt_temp}_{wst},{i},{ctt_temp},{wst}\n')
    myfile.close()

def main():
    name_tech(tech_ctt_wst)
    i_new=pd.read_csv('i_coolingtech_watersource_link.csv', sep = ',')
    i_new.rename(columns={"*i": "tech"}).to_csv("tech_ctt_wst.csv", index = False, sep = ',', columns = ['tech', 'ctt', 'wst'])
    i_new.to_csv('i_coolingtech_watersource.csv', index = False, sep = ',', columns = ['*i'])
    append2tech_map = pd.DataFrame( columns = ['raw', 'display'])
    append2tech_map['raw'], append2tech_map['display'] = i_new['*i'].str.lower(), i_new['ii'].str.lower()
    append2tech_map.loc[append2tech_map['raw'].str.contains('csp', case=False, regex=True), 'display'] = 'csp'
    # append2tech_map.loc[append2tech_map['raw'].str.contains('deep-egs_pbinary|geohydro_pbinary|NF-EGS_pbinary|undisc_pbinary|deep-egs_pflash|geohydro_pflash|NF-EGS_pflash|undisc_pflash', case=False, regex=True), 'display'] = 'geothermal'
    # append2tech_map.loc[append2tech_map['raw'].str.contains('hydD|hydND|hydSD|hydSND|hydUD|hydUND|hydNPD|hydNPND|hydED|hydEND', case=False, regex=True), 'display'] = 'hydro'
    
    append2tech_map.to_csv('append2tech_map.csv', index = False, sep = ',')

if __name__== '__main__' : main()
