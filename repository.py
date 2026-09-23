from typing import List, Optional
from models import Applicant, ApplicantStatus, VALID_STATUS_TRANSITIONS, UpdateApplicantsStatusInput, UpdateApplicantsStatusPayload


class CycleNotFoundError(Exception):
    """Raised when a cycle is not found."""
    pass


class InvalidStatusTransitionError(Exception):
    """Raised when an invalid status transition is attempted."""
    pass


class ApplicantNotFoundError(Exception):
    """Raised when an applicant is not found."""
    pass


class CyclesRepository:
    """Repository for managing cycles and their associated applicants.

    This repository provides bulk applicant operations including
    status transitions across multiple applicants at once.

    In a production environment, this would connect to a database.
    For demonstration and testing purposes, it uses an in-memory store.
    """

    def __init__(self):
        """Initialize the CyclesRepository with an in-memory store."""
        self._applicants: dict[str, Applicant] = {}
        self._cycles: dict[str, dict] = {}

    def add_applicant(self, applicant: Applicant) -> None:
        """Add an applicant to the repository.

        Args:
            applicant: The applicant to add.
        """
        self._applicants[applicant.id] = applicant

    def get_applicant(self, applicant_id: str) -> Optional[Applicant]:
        """Retrieve an applicant by ID.

        Args:
            applicant_id: The ID of the applicant to retrieve.

        Returns:
            The applicant if found, None otherwise.
        """
        return self._applicants.get(applicant_id)

    def get_all_applicants(self) -> List[Applicant]:
        """Retrieve all applicants.

        Returns:
            A list of all applicants in the repository.
        """
        return list(self._applicants.values())

    def update_applicants_status(
        self,
        applicant_ids: List[str],
        status: str,
        cycle_id: str,
        organization_id: str,
        program_id: str,
    ) -> List[Applicant]:
        """Update the status of multiple applicants in bulk.

        This mutation allows admins to change the status of multiple applicants
        at once. It is essential for managing cohorts effectively.

        The method is idempotent: if an applicant already has the target status,
        it is included in the results without error.

        Args:
            applicant_ids: List of applicant IDs to update.
            status: The target status to set. Must be a valid ApplicantStatus value.
            cycle_id: The cycle ID context for the update.
            organization_id: The organization ID context for the update.
            program_id: The program ID context for the update.

        Returns:
            A list of Applicant objects whose statuses were updated.

        Raises:
            InvalidStatusTransitionError: If the target status is not a valid
                ApplicantStatus value or if the transition from the current
                status to the target status is not allowed.
            ApplicantNotFoundError: If any of the provided applicant IDs
                does not exist in the repository.
            ValueError: If applicant_ids is empty.

        Example:
            >>> repo = CyclesRepository()
            >>> repo.add_applicant(Applicant(id="ap_123", name="John", email="john@example.com", status="submitted"))
            >>> applicants = repo.update_applicants_status(
            ...     applicant_ids=["ap_123"],
            ...     status="reviewed",
            ...     cycle_id="cyc_789",
            ...     organization_id="org_1",
            ...     program_id="prog_1"
            ... )
            >>> applicants[0].status
            'reviewed'
        """
        if not applicant_ids:
            raise ValueError("applicant_ids must not be empty")

        # Validate that the target status is a valid ApplicantStatus value
        valid_status_values = {s.value for s in ApplicantStatus}
        if status not in valid_status_values:
            raise InvalidStatusTransitionError(
                f"Invalid status '{status}'. Valid status values are: {sorted(valid_status_values)}"
            )

        updated_applicants: List[Applicant] = []

        for applicant_id in applicant_ids:
            applicant = self._applicants.get(applicant_id)
            if applicant is None:
                raise ApplicantNotFoundError(
                    f"Applicant with ID '{applicant_id}' not found"
                )

            current_status = applicant.status

            # Idempotency: if applicant already has the target status, skip transition validation
            if current_status == status:
                updated_applicants.append(applicant)
                continue

            # Validate status transition
            allowed_transitions = VALID_STATUS_TRANSITIONS.get(current_status, set())
            if status not in allowed_transitions:
                raise InvalidStatusTransitionError(
                    f"Invalid status transition from '{current_status}' to '{status}'. "
                    f"Allowed transitions from '{current_status}': {sorted(allowed_transitions)}"
                )

            # Update the applicant's status
            applicant.status = status
            self._applicants[applicant_id] = applicant
            updated_applicants.append(applicant)

        return updated_applicants

    def update_applicants_status_mutation(
        self,
        input_data: UpdateApplicantsStatusInput,
    ) -> UpdateApplicantsStatusPayload:
        """Execute the updateApplicantsStatus mutation.

        Args:
            input_data: The input containing applicant_ids, status, cycle_id,
                organization_id, and program_id.

        Returns:
            UpdateApplicantsStatusPayload containing the list of updated applicants.
        """
        applicants = self.update_applicants_status(
            applicant_ids=input_data.applicant_ids,
            status=input_data.status,
            cycle_id=input_data.cycle_id,
            organization_id=input_data.organization_id,
            program_id=input_data.program_id,
        )
        return UpdateApplicantsStatusPayload(applicants=applicants)

    def bulk_get_applicants_by_cycle(self, cycle_id: str) -> List[Applicant]:
        """Retrieve all applicants for a given cycle.

        Args:
            cycle_id: The cycle ID to filter by.

        Returns:
            A list of applicants in the specified cycle.
        """
        return [a for a in self._applicants.values() if a.cycle_id == cycle_id]

    def bulk_update_applicants_cycle_status(
        self, cycle_id: str, status: str
    ) -> List[Applicant]:
        """Update all applicants in a cycle to a given status.

        Args:
            cycle_id: The cycle ID to filter by.
            status: The target status.

        Returns:
            A list of updated applicants.
        """
        applicants_in_cycle = self.bulk_get_applicants_by_cycle(cycle_id)
        applicant_ids = [a.id for a in applicants_in_cycle]
        return self.update_applicants_status(
            applicant_ids=applicant_ids,
            status=status,
            cycle_id=cycle_id,
            organization_id="",
            program_id="",
        )
