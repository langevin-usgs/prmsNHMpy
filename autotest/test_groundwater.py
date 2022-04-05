from datetime import datetime, timedelta

import numpy as np
import pandas as pd

import pynhm.preprocess
from pynhm.atmosphere.NHMBoundaryLayer import NHMBoundaryLayer
from pynhm.boundary_conditions.boundaryConditions import BoundaryConditions
from pynhm.groundwater.PRMSGroundwater import PRMSGroundwater
from pynhm.preprocess.csv_utils import CsvFile
from pynhm.utils import ControlVariables
from pynhm.utils.parameters import PrmsParameters


class TestPRMSGroundwaterDomain:
    def test_init(self, domain):
        prms_params = PrmsParameters.load(domain["param_file"])

        # Set information from the control file
        control_file = domain["control_file"]
        control = ControlVariables.load(control_file)
        start_time = control.control.start_time
        end_time = control.control.end_time
        initial_deltat = control.control.initial_deltat

        atm_information_dict = {
            "start_time": start_time,
            "end_time": end_time,
            "time_step": initial_deltat,
            "verbosity": 3,
            "height_m": 5,
        }
        print(domain["cbh_nc"])
        atm = NHMBoundaryLayer.load_netcdf(
            domain["cbh_nc"], prms_params, **atm_information_dict
        )
        atm.calculate_sw_rad_degree_day()
        atm.calculate_potential_et_jh()

        # load csv files into dataframes
        output_files = domain["prms_outputs"]
        input_data = ("soil_to_gw", "ssr_to_gw", "dprst_seep")
        input_recarrays = {}
        for key in input_data:
            fpth = output_files[key]
            input_recarrays[key] = CsvFile(fpth).data

        bcs = BoundaryConditions()
        for key, recarr in input_recarrays.items():
            bcs.add_boundary_recarray(key, recarr)

        gw = PRMSGroundwater(prms_params, atm)

        for istep in range(atm.n_time):
            if istep > 0:
                atm.advance()

            # print(f"Running canopy for step {istep} and day: {atm.current_time}")
            gw.advance(0)

            # set pointers to attributes in the groundwater component
            bcs.advance(itime_step=istep)
            bcs.set_pointers(gw)

            gw.calculate(1.0)

        # # create data frame of prms interception storage (from nhru_hru_intcpstor.csv)
        # output_files = domain["prms_outputs"]
        # fname = output_files["intcpstor"]
        # print(f"loading {fname}")
        # intcpstor_prms = pynhm.preprocess.CsvFile(fname)
        # intcpstor_prms = intcpstor_prms.to_dataframe()
        #
        # # create data frame of pynhm interception storage
        # intcpstor_pynhm = pd.DataFrame(
        #     self.cnp.output_data, columns=self.cnp.output_column_names
        # )
        # intcpstor_pynhm.set_index("date", inplace=True)
        #
        # print("intcp_stor  min  max")
        # a1 = intcpstor_prms.to_numpy()
        # a2 = intcpstor_pynhm.to_numpy()
        # print(f"prms  {a1.min()}    {a1.max()}")
        # print(f"pynhm  {a2.min()}    {a2.max()}")
        #
        # makeplot = False
        # if makeplot:
        #     import matplotlib.pyplot as plt
        #
        #     f = plt.figure()
        #     ax = plt.subplot(1, 1, 1, aspect="equal")
        #     xmin = 1e30
        #     xmax = -1e30
        #     for colname in intcpstor_prms.columns:
        #         x1 = intcpstor_prms.loc[:, colname].values
        #         x2 = intcpstor_pynhm.loc[:, colname].values
        #         ax.scatter(
        #             x1, x2, facecolors="none", edgecolors="k", linewidth=0.25
        #         )
        #         xmin = min(xmin, x1.min(), x2.min())
        #         xmax = max(xmax, x1.max(), x2.max())
        #     ax.set_title("Interception Storage")
        #     ax.set_xlabel("PRMS Interception Storage, in inches")
        #     ax.set_ylabel("PYNHM Interception Storage, in inches")
        #     ax.set_xlim(xmin, xmax)
        #     ax.set_ylim(xmin, xmax)
        #     pname = domain["domain_name"] + "_1-1.png"
        #     print(f"Creating plot {pname}")
        #     plt.savefig(pname, dpi=300)
        #
        #     f = plt.figure()
        #     ax = plt.subplot(1, 1, 1)
        #     pc = plt.imshow(a1 - a2, cmap="jet")
        #     plt.colorbar(pc, shrink=0.5)
        #     ax.set_title("Difference Between PRMS and PYNHM")
        #     ax.set_xlabel("HRU number")
        #     ax.set_ylabel("Time step")
        #     pname = domain["domain_name"] + "_2d.png"
        #     print(f"Creating plot {pname}")
        #     plt.savefig(pname, dpi=300)

        return