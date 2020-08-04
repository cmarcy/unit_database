parameters       CONVOLDqctn, import_store_power_cap_at_grid, PrescriptiveBuildsNonQn, PrescriptiveBuildsnqct,
                 PrescriptiveBuildsStorage, PrescriptiveBuildsWind, NukeRefRetireYear, Nuke60RetireYear,
                 Nuke80RetireYear, NukeRefRetireYear, NukeEarlyRetireYear, PrescriptiveRet,
                 tmpCSPOct, tmpDUPVOn, tmpUPVOn, tmpWTOi, WindRetireExisting, WindRetirePrescribed;

$call csv2gdx CONVOLDqctn.csv id=d index=1..5 values=lastCol useHeader=y trace=0
$gdxin CONVOLDqctn.gdx
$load CONVOLDqctn=d

$call csv2gdx import_store_power_cap_at_grid.csv id=d index=1..2 values=lastCol useHeader=y trace=0
$gdxin import_store_power_cap_at_grid.gdx
$load import_store_power_cap_at_grid=d

$call csv2gdx PrescriptiveBuildsNonQn.csv id=d index=1..3 values=lastCol useHeader=y trace=0
$gdxin PrescriptiveBuildsNonQn.gdx
$load PrescriptiveBuildsNonQn=d

$call csv2gdx PrescriptiveBuildsnqct.csv id=d index=1..6 values=lastCol useHeader=y trace=0
$gdxin PrescriptiveBuildsnqct.gdx
$load PrescriptiveBuildsnqct=d

$call csv2gdx PrescriptiveBuildsStorage.csv id=d index=1..3 values=lastCol useHeader=y trace=0
$gdxin PrescriptiveBuildsStorage.gdx
$load PrescriptiveBuildsStorage=d

$call csv2gdx PrescriptiveBuildsWind.csv id=d index=1..3 values=lastCol useHeader=y trace=0
$gdxin PrescriptiveBuildsWind.gdx
$load PrescriptiveBuildsWind=d

$call csv2gdx Nuke60RetireYear.csv id=d index=1..6 values=lastCol useHeader=y trace=0
$gdxin Nuke60RetireYear.gdx
$load Nuke60RetireYear=d

$call csv2gdx Nuke80RetireYear.csv id=d index=1..6 values=lastCol useHeader=y trace=0
$gdxin Nuke80RetireYear.gdx
$load Nuke80RetireYear=d

$call csv2gdx NukeRefRetireYear.csv id=d index=1..6 values=lastCol useHeader=y trace=0
$gdxin NukeRefRetireYear.gdx
$load NukeRefRetireYear=d

$call csv2gdx NukeEarlyRetireYear.csv id=d index=1..6 values=lastCol useHeader=y trace=0
$gdxin NukeEarlyRetireYear.gdx
$load NukeEarlyRetireYear=d

$call csv2gdx PrescriptiveRet.csv id=d index=1..6 values=lastCol useHeader=y trace=0
$gdxin PrescriptiveRet.gdx
$load PrescriptiveRet=d

$call csv2gdx WindRetireExisting.csv id=d index=1..3 values=lastCol useHeader=y trace=0
$gdxin WindRetireExisting.gdx
$load WindRetireExisting=d

$call csv2gdx WindRetirePrescribed.csv id=d index=1..3 values=lastCol useHeader=y trace=0
$gdxin WindRetirePrescribed.gdx
$load WindRetirePrescribed=d

$call csv2gdx tmpCSPOct.csv id=d index=1..3 values=lastCol useHeader=y trace=0
$gdxin tmpCSPOct.gdx
$load tmpCSPOct=d

$call csv2gdx tmpDUPVOn.csv id=d index=1 values=lastCol useHeader=y trace=0
$gdxin tmpDUPVOn.gdx
$load tmpDUPVOn=d

$call csv2gdx tmpUPVOn.csv id=d index=1 values=lastCol useHeader=y trace=0
$gdxin tmpUPVOn.gdx
$load tmpUPVOn=d

$call csv2gdx tmpWTOi.csv id=d index=1 values=lastCol useHeader=y trace=0
$gdxin tmpWTOi.gdx
$load tmpWTOi=d

execute_unload 'ExistingUnits_EIA-NEMS.gdx' tmpCSPOct, tmpDUPVOn, tmpUPVOn, tmpWTOi, CONVOLDqctn, import_store_power_cap_at_grid ;

execute_unload 'PrescriptiveBuilds_EIA-NEMS.gdx' PrescriptiveBuildsStorage, PrescriptiveBuildsnqct, PrescriptiveBuildsNonQn, PrescriptiveBuildsWind ;

execute_unload 'PrescriptiveRetirements_EIA-NEMS.gdx' Nuke60RetireYear, Nuke80RetireYear, NukeRefRetireYear, NukeEarlyRetireYear, PrescriptiveRet, WindRetireExisting, WindRetirePrescribed ;
