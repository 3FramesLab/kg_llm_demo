/**
 * Standardized Input Field Styles
 * 
 * This file contains consistent styling for all input components (TextField, Select, Autocomplete)
 * across the application to ensure visual consistency.
 * 
 * Design System Standards:
 * - Primary Color: #5B6FE5
 * - Border Color: #E5E7EB
 * - Text Primary: #1F2937
 * - Text Secondary: #6B7280
 * - Background: #F9FAFB
 * - Border Radius: 1 (8px)
 * - Input Height: 40px (with size="small")
 */

/**
 * Standard TextField/Input styling
 * Use this for all TextField components
 */
export const standardInputStyles = {
  '& .MuiInputLabel-root': {
    fontSize: '0.875rem',
    color: '#6B7280',
    '&.Mui-focused': {
      color: '#5B6FE5',
    },
  },
  '& .MuiOutlinedInput-root': {
    fontSize: '0.875rem',
    bgcolor: '#FFFFFF',
    '& fieldset': {
      borderColor: '#E5E7EB',
    },
    '&:hover fieldset': {
      borderColor: '#D1D5DB',
    },
    '&.Mui-focused fieldset': {
      borderColor: '#5B6FE5',
      borderWidth: '1px',
    },
    '& input': {
      padding: '8.5px 14px', // Consistent vertical padding (40px total height with border)
      color: '#1F2937',
    },
    '& textarea': {
      padding: '8.5px 14px',
      color: '#1F2937',
    },
  },
  '& .MuiFormHelperText-root': {
    fontSize: '0.75rem',
    color: '#6B7280',
    marginLeft: '2px',
    marginTop: '4px',
  },
  '& .MuiInputBase-input::placeholder': {
    color: '#9CA3AF',
    opacity: 1,
  },
};

/**
 * Search input styling (lighter background)
 * Use this for search fields
 */
export const searchInputStyles = {
  '& .MuiInputLabel-root': {
    fontSize: '0.875rem',
    color: '#6B7280',
    '&.Mui-focused': {
      color: '#5B6FE5',
    },
  },
  '& .MuiOutlinedInput-root': {
    fontSize: '0.875rem',
    bgcolor: '#F9FAFB',
    '& fieldset': {
      borderColor: '#E5E7EB',
    },
    '&:hover fieldset': {
      borderColor: '#D1D5DB',
    },
    '&.Mui-focused fieldset': {
      borderColor: '#5B6FE5',
      borderWidth: '1px',
    },
    '& input': {
      padding: '8.5px 14px',
      color: '#1F2937',
    },
  },
  '& .MuiInputBase-input::placeholder': {
    color: '#9CA3AF',
    opacity: 1,
  },
};

/**
 * Standard Select/Autocomplete styling
 * Use this for Select and Autocomplete components
 */
export const standardSelectStyles = {
  '& .MuiOutlinedInput-root': {
    fontSize: '0.875rem',
    bgcolor: '#FFFFFF',
    '& fieldset': {
      borderColor: '#E5E7EB',
    },
    '&:hover fieldset': {
      borderColor: '#D1D5DB',
    },
    '&.Mui-focused fieldset': {
      borderColor: '#5B6FE5',
      borderWidth: '1px',
    },
  },
  '& .MuiInputLabel-root': {
    fontSize: '0.875rem',
    color: '#6B7280',
    '&.Mui-focused': {
      color: '#5B6FE5',
    },
  },
  '& .MuiSelect-select': {
    padding: '8.5px 14px',
    color: '#1F2937',
  },
  '& .MuiFormHelperText-root': {
    fontSize: '0.75rem',
    color: '#6B7280',
    marginLeft: '2px',
    marginTop: '4px',
  },
};

/**
 * Standard FormControl styling for Select components
 * Use this for FormControl wrapping Select
 */
export const standardFormControlStyles = {
  '& .MuiInputLabel-root': {
    fontSize: '0.875rem',
    color: '#6B7280',
    '&.Mui-focused': {
      color: '#5B6FE5',
    },
  },
};

/**
 * Standard props for all input components
 * Spread these props on TextField, Select, Autocomplete
 */
export const standardInputProps = {
  size: 'small',
  fullWidth: true,
};

/**
 * Multiline TextField specific adjustments
 * Merge with standardInputStyles for multiline fields
 */
export const multilineInputStyles = {
  '& .MuiOutlinedInput-root': {
    padding: 0, // Remove default padding for multiline
    '& textarea': {
      padding: '8.5px 14px',
    },
  },
};

