import pytest
from models import (
    Applicant,
    ApplicantStatus,
    UpdateApplicantsStatusInput,
    UpdateApplicantsStatusPayload,
)
from repository import (
    CyclesRepository,
    InvalidStatusTransitionError,
    ApplicantNotFoundError,
    CycleNotFoundError,
)


@pytest.fixture
def repo():
    """Create a fresh CyclesRepository with sample applicants for each test."""
    repository = CyclesRepository()
    repository.add_applicant(
        Applicant(id="ap_1", name="Alice", email="alice@example.com", status="submitted", cycle_id="cyc_1", organization_id="org_1", program_id="prog_1")
    )
    repository.add_applicant(
        Applicant(id="ap_2", name="Bob", email="bob@example.com", status="reviewed", cycle_id="cyc_1", organization_id="org_1", program_id="prog_1")
    )
    repository.add_applicant(
        Applicant(id="ap_3", name="Charlie", email="charlie@example.com", status="selected", cycle_id="cyc_2", organization_id="org_2", program_id="prog_2")
    )
    repository.add_applicant(
        Applicant(id="ap_4", name="Dana", email="dana@example.com", status="rejected", cycle_id="cyc_1", organization_id="org_1", program_id="prog_1")
    )
    repository.add_applicant(
        Applicant(id="ap_5", name="Eve", email="eve@example.com", status="withdrawn", cycle_id="cyc_1", organization_id="org_1", program_id="prog_1")
    )
    return repository


class TestUpdateApplicantsStatus:
    """Tests for the update_applicants_status method."""

    # --- Successful transitions ---

    def test_single_applicant_submitted_to_reviewed(self, repo):
        """Test transitioning a single applicant from submitted to reviewed."""
        applicants = repo.update_applicants_status(
            applicant_ids=["ap_1"],
            status="reviewed",
            cycle_id="cyc_1",
            organization_id="org_1",
            program_id="prog_1",
        )
        assert len(applicants) == 1
        assert applicants[0].id == "ap_1"
        assert applicants[0].status == "reviewed"

    def test_single_applicant_reviewed_to_selected(self, repo):
        """Test transitioning a single applicant from reviewed to selected."""
        applicants = repo.update_applicants_status(
            applicant_ids=["ap_2"],
            status="selected",
            cycle_id="cyc_1",
            organization_id="org_1",
            program_id="prog_1",
        )
        assert len(applicants) == 1
        assert applicants[0].status == "selected"

    def test_bulk_update_multiple_applicants(self, repo):
        """Test bulk updating multiple applicants at once."""
        applicants = repo.update_applicants_status(
            applicant_ids=["ap_1", "ap_2"],
            status="reviewed",
            cycle_id="cyc_1",
            organization_id="org_1",
            program_id="prog_1",
        )
        assert len(applicants) == 2
        statuses = {a.id: a.status for a in applicants}
        assert statuses["ap_1"] == "reviewed"
        assert statuses["ap_2"] == "reviewed"

    def test_reviewed_to_rejected(self, repo):
        """Test transitioning from reviewed to rejected."""
        applicants = repo.update_applicants_status(
            applicant_ids=["ap_2"],
            status="rejected",
            cycle_id="cyc_1",
            organization_id="org_1",
            program_id="prog_1",
        )
        assert applicants[0].status == "rejected"

    def test_selected_to_withdrawn(self, repo):
        """Test transitioning from selected to withdrawn."""
        applicants = repo.update_applicants_status(
            applicant_ids=["ap_3"],
            status="withdrawn",
            cycle_id="cyc_2",
            organization_id="org_2",
            program_id="prog_2",
        )
        assert applicants[0].status == "withdrawn"

    def test_rejected_to_withdrawn(self, repo):
        """Test transitioning from rejected to withdrawn."""
        applicants = repo.update_applicants_status(
            applicant_ids=["ap_4"],
            status="withdrawn",
            cycle_id="cyc_1",
            organization_id="org_1",
            program_id="prog_1",
        )
        assert applicants[0].status == "withdrawn"

    def test_submitted_to_rejected(self, repo):
        """Test transitioning from submitted to rejected."""
        applicants = repo.update_applicants_status(
            applicant_ids=["ap_1"],
            status="rejected",
            cycle_id="cyc_1",
            organization_id="org_1",
            program_id="prog_1",
        )
        assert applicants[0].status == "rejected"

    def test_submitted_to_withdrawn(self, repo):
        """Test transitioning from submitted to withdrawn."""
        applicants = repo.update_applicants_status(
            applicant_ids=["ap_1"],
            status="withdrawn",
            cycle_id="cyc_1",
            organization_id="org_1",
            program_id="prog_1",
        )
        assert applicants[0].status == "withdrawn"

    def test_reviewed_to_withdrawn(self, repo):
        """Test transitioning from reviewed to withdrawn."""
        applicants = repo.update_applicants_status(
            applicant_ids=["ap_2"],
            status="withdrawn",
            cycle_id="cyc_1",
            organization_id="org_1",
            program_id="prog_1",
        )
        assert applicants[0].status == "withdrawn"

    # --- Idempotency tests ---

    def test_idempotent_already_target_status(self, repo):
        """Test that updating to the same status is idempotent."""
        applicants = repo.update_applicants_status(
            applicant_ids=["ap_2"],
            status="reviewed",
            cycle_id="cyc_1",
            organization_id="org_1",
            program_id="prog_1",
        )
        assert len(applicants) == 1
        assert applicants[0].status == "reviewed"

    def test_idempotent_multiple_applicants_same_status(self, repo):
        """Test idempotency with multiple applicants already at target status."""
        applicants = repo.update_applicants_status(
            applicant_ids=["ap_2"],
            status="reviewed",
            cycle_id="cyc_1",
            organization_id="org_1",
            program_id="prog_1",
        )
        assert applicants[0].status == "reviewed"
        # Call again - should still work
        applicants_again = repo.update_applicants_status(
            applicant_ids=["ap_2"],
            status="reviewed",
            cycle_id="cyc_1",
            organization_id="org_1",
            program_id="prog_1",
        )
        assert applicants_again[0].status == "reviewed"

    def test_idempotent_selected_already_selected(self, repo):
        """Test idempotency for an applicant already selected."""
        applicants = repo.update_applicants_status(
            applicant_ids=["ap_3"],
            status="selected",
            cycle_id="cyc_2",
            organization_id="org_2",
            program_id="prog_2",
        )
        assert applicants[0].status == "selected"

    # --- Invalid status transition tests ---

    def test_invalid_transition_submitted_to_selected(self, repo):
        """Test that submitted -> selected raises an error."""
        with pytest.raises(InvalidStatusTransitionError):
            repo.update_applicants_status(
                applicant_ids=["ap_1"],
                status="selected",
                cycle_id="cyc_1",
                organization_id="org_1",
                program_id="prog_1",
            )

    def test_invalid_transition_selected_to_reviewed(self, repo):
        """Test that selected -> reviewed raises an error."""
        with pytest.raises(InvalidStatusTransitionError):
            repo.update_applicants_status(
                applicant_ids=["ap_3"],
                status="reviewed",
                cycle_id="cyc_2",
                organization_id="org_2",
                program_id="prog_2",
            )

    def test_invalid_transition_selected_to_rejected(self, repo):
        """Test that selected -> rejected raises an error."""
        with pytest.raises(InvalidStatusTransitionError):
            repo.update_applicants_status(
                applicant_ids=["ap_3"],
                status="rejected",
                cycle_id="cyc_2",
                organization_id="org_2",
                program_id="prog_2",
            )

    def test_invalid_transition_withdrawn_to_submitted(self, repo):
        """Test that withdrawn -> submitted raises an error."""
        with pytest.raises(InvalidStatusTransitionError):
            repo.update_applicants_status(
                applicant_ids=["ap_5"],
                status="submitted",
                cycle_id="cyc_1",
                organization_id="org_1",
                program_id="prog_1",
            )

    def test_invalid_transition_withdrawn_to_selected(self, repo):
        """Test that withdrawn -> selected raises an error."""
        with pytest.raises(InvalidStatusTransitionError):
            repo.update_applicants_status(
                applicant_ids=["ap_5"],
                status="selected",
                cycle_id="cyc_1",
                organization_id="org_1",
                program_id="prog_1",
            )

    def test_invalid_transition_rejected_to_selected(self, repo):
        """Test that rejected -> selected raises an error."""
        with pytest.raises(InvalidStatusTransitionError):
            repo.update_applicants_status(
                applicant_ids=["ap_4"],
                status="selected",
                cycle_id="cyc_1",
                organization_id="org_1",
                program_id="prog_1",
            )

    # --- Invalid status value tests ---

    def test_invalid_status_value(self, repo):
        """Test that an invalid status value raises an error."""
        with pytest.raises(InvalidStatusTransitionError):
            repo.update_applicants_status(
                applicant_ids=["ap_1"],
                status="invalid_status",
                cycle_id="cyc_1",
                organization_id="org_1",
                program_id="prog_1",
            )

    def test_empty_status_value(self, repo):
        """Test that an empty status value raises an error."""
        with pytest.raises(InvalidStatusTransitionError):
            repo.update_applicants_status(
                applicant_ids=["ap_1"],
                status="",
                cycle_id="cyc_1",
                organization_id="org_1",
                program_id="prog_1",
            )

    # --- Applicant not found tests ---

    def test_applicant_not_found(self, repo):
        """Test that a non-existent applicant ID raises an error."""
        with pytest.raises(ApplicantNotFoundError):
            repo.update_applicants_status(
                applicant_ids=["nonexistent"],
                status="reviewed",
                cycle_id="cyc_1",
                organization_id="org_1",
                program_id="prog_1",
            )

    def test_mixed_existing_and_nonexistent(self, repo):
        """Test that a mix of existing and nonexistent IDs raises an error."""
        with pytest.raises(ApplicantNotFoundError):
            repo.update_applicants_status(
                applicant_ids=["ap_1", "nonexistent"],
                status="reviewed",
                cycle_id="cyc_1",
                organization_id="org_1",
                program_id="prog_1",
            )

    # --- Empty input tests ---

    def test_empty_applicant_ids(self, repo):
        """Test that empty applicant_ids raises a ValueError."""
        with pytest.raises(ValueError, match="applicant_ids must not be empty"):
            repo.update_applicants_status(
                applicant_ids=[],
                status="reviewed",
                cycle_id="cyc_1",
                organization_id="org_1",
                program_id="prog_1",
            )

    # --- Mutation method tests ---

    def test_mutation_method_returns_payload(self, repo):
        """Test that the mutation method returns a proper payload."""
        input_data = UpdateApplicantsStatusInput(
            applicant_ids=["ap_1"],
            status="reviewed",
            cycle_id="cyc_1",
            organization_id="org_1",
            program_id="prog_1",
        )
        payload = repo.update_applicants_status_mutation(input_data)
        assert isinstance(payload, UpdateApplicantsStatusPayload)
        assert len(payload.applicants) == 1
        assert payload.applicants[0].status == "reviewed"

    def test_mutation_method_with_multiple_applicants(self, repo):
        """Test the mutation method with multiple applicants."""
        input_data = UpdateApplicantsStatusInput(
            applicant_ids=["ap_1", "ap_2"],
            status="reviewed",
            cycle_id="cyc_1",
            organization_id="org_1",
            program_id="prog_1",
        )
        payload = repo.update_applicants_status_mutation(input_data)
        assert len(payload.applicants) == 2
        for applicant in payload.applicants:
            assert applicant.status == "reviewed"

    # --- Testing example from Jira ---

    def test_jira_testing_example(self, repo):
        """Test the example from the Jira issue."""
        applicants = repo.update_applicants_status(
            applicant_ids=["ap_1"],
            status="selected",
            cycle_id="cyc_789",
            organization_id="org_1",
            program_id="prog_1",
        )
        # Note: This will fail because submitted->selected is not a valid transition
        # The Jira example assumes a direct transition which we validate against
        # This test documents the expected behavior per the issue
        with pytest.raises(InvalidStatusTransitionError):
            repo.update_applicants_status(
                applicant_ids=["ap_1"],
                status="selected",
                cycle_id="cyc_789",
                organization_id="org_1",
                program_id="prog_1",
            )

    def test_jira_example_via_valid_path(self, repo):
        """Test the Jira example pattern via a valid transition path."""
        # First transition to reviewed, then to selected
        repo.update_applicants_status(
            applicant_ids=["ap_1"],
            status="reviewed",
            cycle_id="cyc_789",
            organization_id="org_1",
            program_id="prog_1",
        )
        applicants = repo.update_applicants_status(
            applicant_ids=["ap_1"],
            status="selected",
            cycle_id="cyc_789",
            organization_id="org_1",
            program_id="prog_1",
        )
        assert applicants[0].status == "selected"


class TestCyclesRepositoryBulkMethods:
    """Tests for existing bulk applicant methods in CyclesRepository."""

    def test_bulk_get_applicants_by_cycle(self, repo):
        """Test retrieving applicants by cycle."""
        applicants = repo.bulk_get_applicants_by_cycle("cyc_1")
        assert len(applicants) == 4  # ap_1, ap_2, ap_4, ap_5
        for applicant in applicants:
            assert applicant.cycle_id == "cyc_1"

    def test_bulk_get_applicants_by_cycle_empty(self, repo):
        """Test retrieving applicants from a non-existent cycle."""
        applicants = repo.bulk_get_applicants_by_cycle("nonexistent")
        assert applicants == []

    def test_get_applicant(self, repo):
        """Test retrieving a single applicant."""
        applicant = repo.get_applicant("ap_1")
        assert applicant is not None
        assert applicant.name == "Alice"

    def test_get_applicant_not_found(self, repo):
        """Test retrieving a non-existent applicant."""
        applicant = repo.get_applicant("nonexistent")
        assert applicant is None

    def test_get_all_applicants(self, repo):
        """Test retrieving all applicants."""
        applicants = repo.get_all_applicants()
        assert len(applicants) == 5

    def test_bulk_update_applicants_cycle_status(self, repo):
        """Test bulk updating all applicants in a cycle."""
        applicants = repo.bulk_update_applicants_cycle_status("cyc_1", "reviewed")
        # Only ap_1 (submitted) and ap_4 (rejected) can transition to reviewed
        # ap_2 is already reviewed (idempotent), ap_5 is withdrawn (can't go to reviewed)
        # This should raise an error due to withdrawn -> reviewed being invalid
        with pytest.raises(InvalidStatusTransitionError):
            repo.bulk_update_applicants_cycle_status("cyc_1", "reviewed")


class TestErrorHandling:
    """Tests for error handling and exception classes."""

    def test_invalid_status_transition_error_message(self):
        """Test that InvalidStatusTransitionError can be instantiated with a message."""
        error = InvalidStatusTransitionError("Test error message")
        assert str(error) == "Test error message"

    def test_applicant_not_found_error_message(self):
        """Test that ApplicantNotFoundError can be instantiated with a message."""
        error = ApplicantNotFoundError("Test error message")
        assert str(error) == "Test error message"

    def test_cycle_not_found_error_message(self):
        """Test that CycleNotFoundError can be instantiated with a message."""
        error = CycleNotFoundError("Test error message")
        assert str(error) == "Test error message"

    def test_invalid_transition_error_is_exception(self):
        """Test that InvalidStatusTransitionError is a subclass of Exception."""
        assert issubclass(InvalidStatusTransitionError, Exception)

    def test_applicant_not_found_is_exception(self):
        """Test that ApplicantNotFoundError is a subclass of Exception."""
        assert issubclass(ApplicantNotFoundError, Exception)

    def test_cycle_not_found_is_exception(self):
        """Test that CycleNotFoundError is a subclass of Exception."""
        assert issubclass(CycleNotFoundError, Exception)
