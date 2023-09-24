from pathlib import Path
from filelock import FileLock

import pytest

from prms_convert_to_netcdf import convert_csv_to_nc, convert_soltab_to_nc
from prms_diagnostic_variables import (
    diagnose_simple_vars_to_nc,
    diagnose_final_vars_to_nc,
)


@pytest.fixture
def netcdf_file(csv_file) -> Path:
    """Convert CSV files from model output to NetCDF"""

    var_name = csv_file.stem
    data_dir = csv_file.parent
    convert_csv_to_nc(var_name, data_dir)

    diagnose_simple_vars_to_nc(var_name, data_dir)

    return


def make_netcdf_files(netcdf_file):
    print(f"Created NetCDF from CSV: {netcdf_file}")


@pytest.fixture(scope="session")
def soltab_netcdf_file(tmp_path_factory, soltab_file) -> Path:
    """Convert soltab files to NetCDF, one file for each variable"""
    domain_dir = soltab_file.parent
    output_dir = domain_dir / "output"
    convert_soltab_to_nc(soltab_file, output_dir, domain_dir)


def make_soltab_netcdf_files(soltab_netcdf_file):
    print(f"Creating NetCDF files for soltab file {soltab_netcdf_file}")


@pytest.fixture(scope="session")
def final_netcdf_file(tmp_path_factory, simulation) -> Path:
    """Create the final NetCDF file (through_rain.nc) from other NetCDFs"""

    # Currently there is only a single final variable
    var_name = "through_rain"
    data_dir = Path(simulation["ws"]) / "output"

    root_tmpdir = tmp_path_factory.getbasetemp().parent
    with FileLock(root_tmpdir / "final_nc.lock"):
        yield  # do this in session cleanup

        diagnose_final_vars_to_nc(var_name, data_dir)


def make_final_netcdf_files(final_netcdf_file):
    print(f"Creating final NetCDF file {final_netcdf_file}")