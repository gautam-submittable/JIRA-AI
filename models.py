from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional


class ApplicantStatus(str, Enum):
    """Valid status values for applicants in the grant lifecycle.

    These statuses represent the stages an applicant can be in:
    - submitted: Application has been submitted
    - reviewed: Application has been reviewed
    - selected: Applicant has been selected
    - rejected: Application has been rejected
    - withdrawn: Applicant has withdrawn their application
    """

    SUBMITTED = "submitted"
    REVIEWED = "reviewed"
    SELECTED = "selected"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


# Define valid status transitions as a mapping
VALID_STATUS_TRANSITIONS: dict[str, set[str]] = {
    ApplicantStatus.SUBMITTED.value: {ApplicantStatus.REVIEWED.value, ApplicantStatus.REJECTED.value, ApplicantStatus.WITHDRAWN.value},
    ApplicantStatus.REVIEWED.value: {ApplicantStatus.SELECTED.value, ApplicantStatus.REJECTED.value, ApplicantStatus.WITHDRAWN.value},
    ApplicantStatus.SELECTED.value: {ApplicantStatus.WITHDRAWN.value},
    ApplicantStatus.REJECTED.value: {ApplicantStatus.WITHDRAWN.value},
    ApplicantStatus.WITHDRAWN.value: set(),
}


@dataclass
class Applicant:
    """Represents an applicant in the grant lifecycle.

    Attributes:
        id: Unique identifier for the applicant.
        name: Name of the applicant.
        email: Email address of the applicant.
        status: Current status of the applicant in the grant lifecycle.
        cycle_id: The cycle this applicant belongs to.
        organization_id: The organization associated with the applicant.
        program_id: The program associated with the applicant.
    """

    id: str
    name: str
    email: str
    status: str = ""
    cycle_id: str = ""
    organization_id: str = ""
    program_id: str = ""


@dataclass
class UpdateApplicantsStatusInput:
    """Input for the updateApplicantsStatus mutation.

    Attributes:
        applicant_ids: List of applicant IDs to update.
        status: Target status to set for all applicants.
        cycle_id: The cycle ID context for the update.
        organization_id: The organization ID context for the update.
        program_id: The program ID context for the update.
    """

    applicant_ids: List[str]
    status: str
    cycle_id: str
    organization_id: str
    program_id: str


@dataclass
class UpdateApplicantsStatusPayload:
    """Payload returned by the updateApplicantsStatus mutation.

    Attributes:
        applicants: List of applicants whose statuses were updated.
    """

    applicants: List[Applicant] = field(default_factory=list)
