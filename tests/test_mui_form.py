import pytest
from mui_form import MUIForm

@pytest.fixture
def valid_scholarship():
    return 'Scholarship A'

@pytest.fixture
def invalid_scholarship():
    return 'Invalid Scholarship'

def test_form_initialization():
    form = MUIForm('Loc1', 'Mkt1', 'Op1', 'Reg1', '123', 'Scholarship A')
    assert form.location_name == 'Loc1'
    assert form.scholarship_name == 'Scholarship A'

def test_invalid_scholarship_raises_error(invalid_scholarship):
    with pytest.raises(ValueError):
        MUIForm('Loc1', 'Mkt1', 'Op1', 'Reg1', '123', invalid_scholarship)

def test_short_answer_fields():
    form = MUIForm('Loc1', 'Mkt1', 'Op1', 'Reg1', '123', 'Scholarship A')
    assert form.market_dfa_name == 'Mkt1'
    assert form.operator == 'Op1'

def test_empty_short_answer():  # Assuming empty strings are allowed unless specified
    form = MUIForm('', 'Mkt1', 'Op1', 'Reg1', '123', 'Scholarship A')
    assert form.location_name == ''