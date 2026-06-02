from io import BytesIO
from pathlib import Path
from typing import Type

import numpy as np

# Any line in the input file with this character is treated as a variable definition.
VARIABLE_IDENTIFIER = b'%'
VARIABLE_ENCODING = "utf-8"
VARIABLE_FILL_VALUES = {
    np.float64: np.float64(1E36),
    np.int32: np.int32(2147483647),
}


# Tells the TextDataset where each variable's data is located in the file.
class DatasetMeta:
    """
    Finds where each variable's data is located in the file. 
    """

    def __init__(self, from_file: BytesIO):
        # { var_name: (data_start, data_end, datatype) }
        self._var_meta = {}

        # Every two integers is the start and end of the corresponding variable in
        # variables.
        positions = []
        # Variable names.
        variables = []
        # Numpy data types for each variable.
        types = []

        before_line = from_file.tell()
        while (line := from_file.readline()):
            after_line = from_file.tell()

            if VARIABLE_IDENTIFIER in line:
                var_name = line.strip().decode(VARIABLE_ENCODING)
                variables.append(var_name)

                positions.append(before_line - 1)
                positions.append(after_line)

                # We assume each variable has at least one line of data.
                next_line = from_file.readline()
                if b"." in next_line or b"NaN" in next_line:
                    types.append(np.float64)
                else:
                    types.append(np.int32)

            before_line = from_file.tell()

        # Close the last variable where the file ends.
        positions.append(after_line)

        # Remove the false end from the first variable being identified.
        positions.pop(0)

        for index, variable in enumerate(variables):
            self._var_meta[variable] = (
                positions[index * 2],
                positions[index * 2 + 1],
                types[index],
            )

    def get_range_for_var(self, variable: str) -> tuple[int, int]:
        """
        Gets the location of a variable from the file. 
        
        :param variable: Name of a variable
        :type variable: str
        :return: Tuple containing the start and end position of the variable
        :rtype: tuple[int, int]
        """

        meta = self._var_meta[variable]
        return (meta[0], meta[1])

    def get_type_for_var(self, variable: str) -> Type[np.generic]:
        """
        Gets the type of a variable. 
        
        :param variable: Name of a variable
        :type variable: str
        :return: The generic NumPy type of the variable
        :rtype: type[generic[Any]]
        """

        meta = self._var_meta[variable]
        return meta[2]

    def get_variables(self) -> list[str]:
        """
        Gets all of the names of the variables from the file. 
        
        :return: List of all the names of the variables from the file
        :rtype: list[str]
        """

        return list(self._var_meta.keys())


class TextDataset:
    """
    Docstring for TextDataset
    """

    def __init__(self, filepath: Path):
        self._filepath = filepath
        self._file = open(filepath, "rb")
        self._meta = DatasetMeta(self._file)

    def get_variable(self, variable: str) -> np.ma.MaskedArray:
        """
        Reads a single variable from the file.
        
        :param variable: Name of the variable
        :type variable: str
        :return: The values that the variable contains
        :rtype: MaskedArray[_AnyShape, dtype[Any]]
        """

        self._assert_file_is_open()

        start, end = self._meta.get_range_for_var(variable)
        dtype = self._meta.get_type_for_var(variable)
        mask = VARIABLE_FILL_VALUES[dtype]

        self._file.seek(start)
        raw = self._file.read(end - start)
        data_text = raw.decode(VARIABLE_ENCODING)

        array = np.fromstring(data_text, sep=" ", dtype=dtype)
        return np.ma.masked_equal(array, mask)

    def get_variables(self) -> list[str]:
        """
        Gets all of the names of the variables from the file. 
        
        :return: List of all the names of the variables from the file
        :rtype: list[str]
        """

        return self._meta.get_variables()
       
    def reopen(self) -> None:
        """
        Opens the file for reading in binary mode. 
        """

        self._file = open(self._filepath, "rb")

    def close(self) -> None:
        """
        Closes the file.
        """

        self._file.close()
        self._file = None

    def is_open(self) -> bool:
        """
        Checks if the file is open.
        
        :return: Whether the file is open
        :rtype: bool
        """

        return self._file is not None

    def _assert_file_is_open(self) -> None:
        if self._file is None:
            raise OSError("Cannot lazy load from text file, file was closed")
