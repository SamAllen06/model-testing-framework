import numpy as np

from analysis import SampleGroupAnalyzer
from output.file_utils import FileSystemTree
from sampling import SampleGroup
from testing import ModelData

from . import output


class ChangeAnalyzer(SampleGroupAnalyzer):
    def analyze_sample_data(
        self,
        sample_group: SampleGroup,
        reference_data: ModelData,
        sample_data: list[ModelData],
    ) -> tuple[str, FileSystemTree]:
        used_inputs = self._get_used_inputs(sample_group)
        changed_outputs = self._get_changed_outputs(reference_data, sample_data)

        return output.make_output(used_inputs, changed_outputs)


    def _get_used_inputs(self, sample_group: SampleGroup) -> set[str]:
        inputs = set()

        for sample in sample_group:
            for input in sample:
                inputs.add(input)

        return inputs

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
