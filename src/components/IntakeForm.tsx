import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import {
  Box,
  Button,
  TextField,
  Grid,
  Typography,
} from '@mui/material';
import { IntakeFormData, ScholarshipOption } from '../types/form';

interface IntakeFormProps {
  onSubmit: (data: IntakeFormData) => void;
  scholarshipOptions?: ScholarshipOption[];
  defaultValues?: Partial<IntakeFormData>;
}

const IntakeForm: React.FC<IntakeFormProps> = ({
  onSubmit,
  scholarshipOptions = [],
  defaultValues = {},
}) => {
  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<IntakeFormData>({
    defaultValues,
  });

  const handleReset = () => {
    reset();
  };

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
      <Typography variant="h4" component="h2" gutterBottom>
        Intake Form
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6}>
          <Controller
            name="LOCATION_NAME"
            control={control}
            rules={{ required: 'Location Name is required' }}
            render={({ field: { onChange, onBlur, value, name }, fieldState: { error } }) => (
              <TextField
                {...field}
                label="Location Name"
                variant="outlined"
                fullWidth
                onBlur={onBlur}
                onChange={onChange}
                value={value || ''}
                error={!!error}
                helperText={error?.message}
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="MARKET_DFA_NAME"
            control={control}
            rules={{ required: 'Market DFA Name is required' }}
            render={({ field: { onChange, onBlur, value, name }, fieldState: { error } }) => (
              <TextField
                {...field}
                label="Market DFA Name"
                variant="outlined"
                fullWidth
                onBlur={onBlur}
                onChange={onChange}
                value={value || ''}
                error={!!error}
                helperText={error?.message}
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="OPERATOR"
            control={control}
            rules={{ required: 'Operator is required' }}
            render={({ field: { onChange, onBlur, value, name }, fieldState: { error } }) => (
              <TextField
                {...field}
                label="Operator"
                variant="outlined"
                fullWidth
                onBlur={onBlur}
                onChange={onChange}
                value={value || ''}
                error={!!error}
                helperText={error?.message}
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="REGION"
            control={control}
            rules={{ required: 'Region is required' }}
            render={({ field: { onChange, onBlur, value, name }, fieldState: { error } }) => (
              <TextField
                {...field}
                label="Region"
                variant="outlined"
                fullWidth
                onBlur={onBlur}
                onChange={onChange}
                value={value || ''}
                error={!!error}
                helperText={error?.message}
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="STORE_NUMBER"
            control={control}
            rules={{
              required: 'Store Number is required',
              pattern: {
                value: /^[0-9]+$/,
                message: 'Store Number must be a number',
              },
            }}
            render={({ field: { onChange, onBlur, value, name }, fieldState: { error } }) => (
              <TextField
                {...field}
                label="Store Number"
                variant="outlined"
                fullWidth
                onBlur={onBlur}
                onChange={onChange}
                value={value || ''}
                error={!!error}
                helperText={error?.message}
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="SCHOLARSHIP_NAME"
            control={control}
            rules={{ required: 'Scholarship Name is required' }}
            render={({ field: { onChange, onBlur, value, name }, fieldState: { error } }) => (
              <TextField
                {...field}
                select
                label="Scholarship Name"
                variant="outlined"
                fullWidth
                onBlur={onBlur}
                onChange={onChange}
                value={value || ''}
                error={!!error}
                helperText={error?.message}
                SelectProps={{
                  native: true,
                }}
              >
                <option value="">Select a scholarship</option>
                {scholarshipOptions.map((option) => (
                  <option key={option.id} value={option.id}>
                    {option.name}
                  </option>
                ))}
              </TextField>
            )}
          />
        </Grid>
      </Grid>

      <Box mt={3} display="flex" gap={2}>
        <Button type="submit" variant="contained" color="primary">
          Submit
        </Button>
        <Button type="button" variant="outlined" onClick={handleReset}>
          Reset
        </Button>
      </Box>
    </Box>
  );
};

export default IntakeForm;
