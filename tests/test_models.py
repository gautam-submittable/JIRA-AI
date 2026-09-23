import pytest
from models import (
    Applicant,
    ApplicantStatus,
    UpdateApplicantsStatusInput,
    UpdateApplicantsStatusPayload,
    VALID_STATUS_TRANSITIONS,
)


class TestApplicantStatus:
    """Tests for the ApplicantStatus enum."""

    def test_valid_status_values(self):
        """Test that all expected status values exist."""
        expected_values = {"submitted", "reviewed", "selected", "rejected", "withdrawn"}
        actual_values = {s.value for s in ApplicantStatus}
        assert actual_values == expected_values

    def test_applicant_status_is_str_enum(self):
        """Test that ApplicantStatus is a string enum."""
        assert issubclass(ApplicantStatus, str)
        assert ApplicantStatus.SUBMITTED.value == "submitted"
        assert ApplicantStatus.REVIEWED.value == "reviewed"
        assert ApplicantStatus.SELECTED.value == "selected"
        assert ApplicantStatus.REJECTED.value == "rejected"
        assert ApplicantStatus.WITHDRAWN.value == "withdrawn"


class TestValidStatusTransitions:
    """Tests for valid status transition definitions."""

    def test_submitted_transitions(self):
        """Test transitions from submitted status."""
        assert ApplicantStatus.REVIEWED.value in VALID_STATUS_TRANSITIONS[ApplicantStatus.SUBMITTED.value]
        assert ApplicantStatus.REJECTED.value in VALID_STATUS_TRANSITIONS[ApplicantStatus.SUBMITTED.value]
        assert ApplicantStatus.WITHDRAWN.value in VALID_STATUS_TRANSITIONS[ApplicantStatus.SUBMITTED.value]
        assert ApplicantStatus.SELECTED.value not in VALID_STATUS_TRANSITIONS[ApplicantStatus.SUBMITTED.value]

    def test_reviewed_transitions(self):
        """Test transitions from reviewed status."""
        assert ApplicantStatus.SELECTED.value in VALID_STATUS_TRANSITIONS[ApplicantStatus.REVIEWED.value]
        assert ApplicantStatus.REJECTED.value in VALID_STATUS_TRANSITIONS[ApplicantStatus.REVIEWED.value]
        assert ApplicantStatus.WITHDRAWN.value in VALID_STATUS_TRANSITIONS[ApplicantStatus.REVIEWED.value]

    def test_selected_transitions(self):
        """Test transitions from selected status."""
        assert ApplicantStatus.WITHDRAWN.value in VALID_STATUS_TRANSITIONS[ApplicantStatus.SELECTED.value]
        assert len(VALID_STATUS_TRANSITIONS[ApplicantStatus.SELECTED.value]) == 1

    def test_rejected_transitions(self):
        """Test transitions from rejected status."""
        assert ApplicantStatus.WITHDRAWN.value in VALID_STATUS_TRANSITIONS[ApplicantStatus.REJECTED.value]
        assert len(VALID_STATUS_TRANSITIONS[ApplicantStatus.REJECTED.value]) == 1

    def test_withdrawn_has_no_transitions(self):
        """Test that withdrawn status has no valid transitions."""
        assert len(VALID_STATUS_TRANSITIONS[ApplicantStatus.WITHDRAWN.value]) == 0


class TestApplicant:
    """Tests for the Applicant model."""

    def test_applicant_without_status(self):
        """Test creating an applicant without a status."""
        applicant = Applicant(id="ap_1", name="Alice", email="alice@example.com")
        assert applicant.status == ""
        assert applicant.id == "ap_1"
        assert applicant.name == "Alice"
        assert applicant.email == "alice@example.com"

    def test_applicant_with_status(self):
        """Test creating an applicant with a status."""
        applicant = Applicant(
            id="ap_2", name="Bob", email="bob@example.com", status="submitted"
        )
        assert applicant.status == "submitted"

    def test_applicant_full_fields(self):
        """Test creating an applicant with all fields."""
        applicant = Applicant(
            id="ap_3",
            name="Charlie",
            email="charlie@example.com",
            status="reviewed",
            cycle_id="cyc_1",
            organization_id="org_1",
            program_id="prog_1",
        )
        assert applicant.id == "ap_3"
        assert applicant.cycle_id == "cyc_1"
        assert applicant.organization_id == "org_1"
        assert applicant.program_id == "prog_1"

    def test_applicant_status_field_is_str(self):
        """Test that Applicant has a status field of type str."""
        applicant = Applicant(id="ap_4", name="Dana", email="dana@example.com", status="selected")
        assert isinstance(applicant.status, str)


class TestUpdateApplicantsStatusInput:
    """Tests for UpdateApplicantsStatusInput."""

    def test_input_creation(self):
        """Test creating an input object."""
        input_data = UpdateApplicantsStatusInput(
            applicant_ids=["ap_1", "ap_2"],
            status="selected",
            cycle_id="cyc_1",
            organization_id="org_1",
            program_id="prog_1",
        )
        assert input_data.applicant_ids == ["ap_1", "ap_2"]
        assert input_data.status == "selected"
        assert input_data.cycle_id == "cyc_1"
        assert input_data.organization_id == "org_1"
        assert input_data.program_id == "prog_1"


class TestUpdateApplicantsStatusPayload:
    """Tests for UpdateApplicantsStatusPayload."""

    def test_payload_with_applicants(self):
        """Test creating a payload with applicants."""
        applicants = [Applicant(id="ap_1", name="A", email="a@a.com", status="selected")]
        payload = UpdateApplicantsStatusPayload(applicants=applicants)
        assert len(payload.applicants) == 1
        assert payload.applicants[0].status == "selected"

    def test_payload_empty_applicants(self):
        """Test creating a payload with no applicants."""
        payload = UpdateApplicantsStatusPayload()
        assert payload.applicants == []
