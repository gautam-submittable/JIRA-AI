import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import IntakeForm from './IntakeForm';
import { ScholarshipOption } from '../types/form';

describe('IntakeForm', () => {
  const mockOnSubmit = jest.fn();
  const scholarshipOptions: ScholarshipOption[] = [
    { id: '1', name: 'Scholarship A' },
    { id: '2', name: 'Scholarship B' },
  ];

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  it('renders all form fields correctly', () => {
    render(
      <IntakeForm onSubmit={mockOnSubmit} scholarshipOptions={scholarshipOptions} />
    );

    expect(screen.getByLabelText(/Location Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Market DFA Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Operator/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Region/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Store Number/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Scholarship Name/i)).toBeInTheDocument();
  });

  it('shows required validation errors when fields are empty', async () => {
    render(
      <IntakeForm onSubmit={mockOnSubmit} scholarshipOptions={scholarshipOptions} />
    );

    const submitButton = screen.getByRole('button', { name: /Submit/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Location Name is required')).toBeInTheDocument();
      expect(screen.getByText('Market DFA Name is required')).toBeInTheDocument();
      expect(screen.getByText('Operator is required')).toBeInTheDocument();
      expect(screen.getByText('Region is required')).toBeInTheDocument();
      expect(screen.getByText('Store Number is required')).toBeInTheDocument();
      expect(screen.getByText('Scholarship Name is required')).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('validates store number as numeric', async () => {
    render(
      <IntakeForm onSubmit={mockOnSubmit} scholarshipOptions={scholarshipOptions} />
    );

    const storeNumberField = screen.getByLabelText(/Store Number/i);
    fireEvent.change(storeNumberField, { target: { value: 'abc' } });

    const submitButton = screen.getByRole('button', { name: /Submit/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Store Number must be a number')).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('submits form with valid data', async () => {
    render(
      <IntakeForm onSubmit={mockOnSubmit} scholarshipOptions={scholarshipOptions} />
    );

    await userEvent.type(screen.getByLabelText(/Location Name/i), 'Test Location');
    await userEvent.type(screen.getByLabelText(/Market DFA Name/i), 'Test Market');
    await userEvent.type(screen.getByLabelText(/Operator/i), 'Test Operator');
    await userEvent.type(screen.getByLabelText(/Region/i), 'Test Region');
    await userEvent.type(screen.getByLabelText(/Store Number/i), '12345');
    await userEvent.selectOptions(screen.getByLabelText(/Scholarship Name/i), '1');

    const submitButton = screen.getByRole('button', { name: /Submit/i });
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        LOCATION_NAME: 'Test Location',
        MARKET_DFA_NAME: 'Test Market',
        OPERATOR: 'Test Operator',
        REGION: 'Test Region',
        STORE_NUMBER: '12345',
        SCHOLARSHIP_NAME: '1',
      });
    });
  });

  it('resets form when reset button is clicked', async () => {
    render(
      <IntakeForm onSubmit={mockOnSubmit} scholarshipOptions={scholarshipOptions} />
    );

    const locationField = screen.getByLabelText(/Location Name/i);
    await userEvent.type(locationField, 'Some Value');

    const resetButton = screen.getByRole('button', { name: /Reset/i });
    await userEvent.click(resetButton);

    expect(locationField).toHaveValue('');
  });

  it('renders with default values when provided', () => {
    const defaultValues = {
      LOCATION_NAME: 'Default Location',
      MARKET_DFA_NAME: 'Default Market',
      OPERATOR: 'Default Operator',
      REGION: 'Default Region',
      STORE_NUMBER: '99999',
      SCHOLARSHIP_NAME: '2',
    };

    render(
      <IntakeForm
        onSubmit={mockOnSubmit}
        scholarshipOptions={scholarshipOptions}
        defaultValues={defaultValues}
      />
    );

    expect(screen.getByLabelText(/Location Name/i)).toHaveValue('Default Location');
    expect(screen.getByLabelText(/Market DFA Name/i)).toHaveValue('Default Market');
    expect(screen.getByLabelText(/Operator/i)).toHaveValue('Default Operator');
    expect(screen.getByLabelText(/Region/i)).toHaveValue('Default Region');
    expect(screen.getByLabelText(/Store Number/i)).toHaveValue('99999');
    expect(screen.getByLabelText(/Scholarship Name/i)).toHaveValue('2');
  });
});
