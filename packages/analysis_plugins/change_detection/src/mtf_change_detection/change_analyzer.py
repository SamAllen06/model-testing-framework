import numpy as np

from mtf.analysis import SampleGroupAnalyzer
from mtf.output.file_utils import FileSystemTree
from mtf.sampling import SampleGroup
from mtf.testing import ModelData

from mtf_change_detection import output


class ChangeAnalyzer(SampleGroupAnalyzer):
    def analyze_sample_data(
        self,
        sample_group: SampleGroup,
        reference_data: ModelData,
        sample_data: list[ModelData],
    ) -> tuple[str, FileSystemTree]:
        used_constants = self._get_used_constants(sample_group)
        changed_outputs = self._get_changed_outputs(reference_data, sample_data)

        return output.make_output(used_constants, changed_outputs)


    def _get_used_constants(self, sample_group: SampleGroup) -> set[str]:
        constants = set()

        for sample in sample_group:
            for constant in sample:
                constants.add(constant)

        return constants

    def _get_changed_outputs(
        self,
        reference_data: ModelData,
        sample_data: list[ModelData]
    ) -> set[str]:
        outputs = set()

        with reference_data:
            for individual_sample_data in sample_data:
                with individual_sample_data:
                    for output, data in individual_sample_data.items():
                        ref_data = reference_data[output]
                        if not np.array_equal(ref_data, data):
                            # Indicates the binary failed to run, these are excluded to
                            # prevent this from flagging all outputs as changed.
                            if hasattr(data, "mask") and np.all(data.mask):
                                continue
                            outputs.add(output)

        return outputs
