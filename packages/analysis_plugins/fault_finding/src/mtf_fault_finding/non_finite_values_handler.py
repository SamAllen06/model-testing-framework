import numpy as np
import numpy.typing as npt

class NonFiniteValuesHandler:    
    def is_all_not_finite(*vars: npt.NDArray) -> bool:
        for var in vars:
            if np.all(~np.isfinite(var)):
                return True
        return False

    def mask_non_finite_values(*vars:npt.NDArray
                               ) -> npt.NDArray | tuple[npt.NDArray, ...]:
        masked_vars = []
        for var in vars:
            if np.any(~np.isfinite(var)):
                masked_var = np.ma.masked_invalid(var)
                masked_vars.append(masked_var)
            else:
                masked_vars.append(var)
        if len(masked_vars) == 1:
            return masked_vars[0]
        return tuple(masked_vars)