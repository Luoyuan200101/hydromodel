"""
Author: Wenyu Ouyang
Date: 2023-06-02 09:30:36
LastEditTime: 2023-06-03 10:42:33
LastEditors: Wenyu Ouyang
Description: 
FilePath: /hydro-model-xaj/test/test_hymod.py
Copyright (c) 2023-2024 Wenyu Ouyang. All rights reserved.
"""
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
import spotpy

import definitions
from hydromodel.trainers.calibrate_sceua import calibrate_by_sceua, SpotSetup
from hydromodel.models.hymod import hymod
from hydromodel.trainers.plots import show_calibrate_result


@pytest.fixture()
def basin_area():
    # # the area of basin 01013500 is 2252.7; unit km2
    # the area of a basin from hymod example, unit km2
    return 1.783


@pytest.fixture()
def the_data():
    root_dir = definitions.ROOT_DIR
    return pd.read_csv(
        os.path.join(root_dir, "hydromodel", "example", "hymod_input.csv"), sep=";"
    )
    # return pd.read_csv(os.path.join(root_dir, "hydromodel","example", '01013500_lump_p_pe_q.txt'))


@pytest.fixture()
def qobs(the_data, basin_area):
    # 1 ft3 = 0.02831685 m3
    ft3tom3 = 2.831685e-2
    # 1 km2 = 10^6 m2
    km2tom2 = 1e6
    # 1 m = 1000 mm
    mtomm = 1000
    # 1 day = 24 * 3600 s
    daytos = 24 * 3600
    # qobs_ = np.expand_dims(test_data[['streamflow(ft3/s)']].values, axis=1)
    # trans ft3/s to mm/day
    # return qobs_ * ft3tom3 / (basin_area * km2tom2) * mtomm * daytos

    qobs_ = np.expand_dims(the_data[["Discharge[ls-1]"]].values, axis=1)
    # trans l/s to mm/day
    return qobs_ * 1e-3 / (basin_area * km2tom2) * mtomm * daytos


@pytest.fixture()
def p_and_e(the_data):
    p_and_e_df = the_data[["rainfall[mm]", "TURC [mm d-1]"]]
    # p_and_e_df = test_data[['prcp(mm/day)', 'petfao56(mm/day)']]
    # three dims: batch (basin), sequence (time), feature (variable)
    return np.expand_dims(p_and_e_df.values, axis=1)


@pytest.fixture()
def params():
    return np.array([0.39359, 0.01005, 0.20831, 0.75010, 0.48652]).reshape(1, 5)


def test_hymod(p_and_e, params):
    qsim = hymod(p_and_e, params, warmup_length=10)
    np.testing.assert_almost_equal(
        qsim[:5, 0, 0], [0.0003, 0.0003, 0.0002, 0.0002, 0.0002], decimal=4
    )
