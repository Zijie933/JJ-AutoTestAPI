import json
from typing import Optional, List

from autotest.schemas.api_test_schemas import StepInput
from common.models.step import Step


def convert_step_input_to_step(step_input: StepInput) -> Step:
    try:
        extract_dict = json.loads(step_input.extract) if step_input.extract else {}
    except (TypeError, json.JSONDecodeError):
        extract_dict = {}

    return Step(
        name=step_input.name,
        case=step_input.case,
        asserts=step_input.asserts or [],
        extract=extract_dict
    )

def convert_step_inputs_to_steps(step_inputs: Optional[List[StepInput]] = None) -> List[Step]:
    if not step_inputs:
        return []
    return [convert_step_input_to_step(step_input) for step_input in step_inputs]