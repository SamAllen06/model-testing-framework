from pathlib import Path
import testing

import netCDF4


DEFAULTS_PATH = Path("../../netcdf_lake_temp_testing/model/spel-constant-defaults0001.nc")
PARAMS_PATH = Path("../../netcdf_lake_temp_testing/model/spel-constants0001.nc")
REF_PATH = Path("../../netcdf_lake_temp_testing/model/spel-outputs0001.nc")
TEST_PATH = Path("../../netcdf_lake_temp_testing/model/fut-outputs0001.nc")


def main() -> None:
    output_file_reader = testing.make_output_file_reader(REF_PATH, TEST_PATH)

    print(output_file_reader.get_reference_data())




if __name__ == "__main__":
    main()
