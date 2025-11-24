import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Stepper,
  Step,
  StepLabel,
  Typography,
  Paper,
  Button,
  Alert,
  Divider,
  Fade,
  useTheme,
  alpha,
} from '@mui/material';
import { ArrowForward, AutoAwesome } from '@mui/icons-material';
import SchemaConfigurationDisplay from '../components/relationshipAndkgGeneration-components/SchemaConfigurationDisplay';
import RelationshipEditor from '../components/relationshipAndkgGeneration-components/RelationshipEditor';
import KGGenerationPanel from '../components/relationshipAndkgGeneration-components/KGGenerationPanel';

const steps = ['Schema Configuration', 'Relationships', 'Generate Knowledge Graph'];

export default function RelationshipAndKGGeneration() {
  const theme = useTheme();
  const [activeStep, setActiveStep] = useState(0);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [schemaConfig, setSchemaConfig] = useState(null);
  const [relationships, setRelationships] = useState([]);

  useEffect(() => {
    // Clear messages after 5 seconds
    if (success || error) {
      const timer = setTimeout(() => {
        setSuccess(null);
        setError(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [success, error]);

  const handleNext = () => {
    // Only allow moving to next step if a schema is selected (when on step 0)
    if (activeStep === 0 && !schemaConfig) {
      setError('Please select a schema configuration to continue');
      return;
    }
    if (activeStep < steps.length - 1) {
      setActiveStep(activeStep + 1);
    }
  };

  const handleBack = () => {
    if (activeStep > 0) {
      setActiveStep(activeStep - 1);
    }
  };

  const handleSchemaLoaded = (config) => {
    setSchemaConfig(config);
    if (config) {
      setSuccess('Schema configuration loaded successfully');
    }
  };

  const handleRelationshipsUpdated = (updatedRelationships) => {
    setRelationships(updatedRelationships);
  };

  const handleKGGenerated = () => {
    setSuccess('Knowledge graph generated successfully!');
    setActiveStep(0); // Reset to first step
  };

  return (
    <Box sx={{ p: 1 }}>
      <Container maxWidth="auto" disableGutters>
        <Fade in timeout={600}>
          <Box
            sx={{
              position: 'relative',
              '&::before': {
                content: '""',
                position: 'absolute',
                top: -8,
                left: -8,
                right: -8,
                bottom: -8,
                borderRadius: '16px',
                background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.05)} 0%, ${alpha(theme.palette.secondary.main, 0.05)} 100%)`,
                opacity: 0,
                transition: 'opacity 0.3s ease-in-out',
                pointerEvents: 'none',
                zIndex: -1,
              },
              '&:hover::before': {
                opacity: 1,
              },
            }}
          >
            <Paper
              elevation={0}
              sx={{
                height: '100%',
                minHeight: 'calc(100vh - 64px)',
                p: 1.25,
                bgcolor: '#FFFFFF',
                border: '1px solid #E5E7EB',
                borderRadius: 4,
                display: 'flex',
                flexDirection: 'column',
              }}
            >
              {/* Header Section */}
              <Box sx={{ mb: 1 }}>
                <Typography
                  variant="h5"
                  sx={{
                    mb: 0.25,
                    fontWeight: 600,
                    fontSize: '1.25rem',
                    color: '#5B6FE5',
                    lineHeight: 1.3,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                  }}
                >
                  <AutoAwesome sx={{ fontSize: '1.5rem' }} />
                  Relationship and Knowledge Graph Generation
                </Typography>

                <Typography
                  variant="body2"
                  sx={{
                    color: '#6B7280',
                    fontSize: '0.875rem',
                    lineHeight: 1.4,
                  }}
                >
                  Configure schemas, manage relationships, and generate knowledge graphs to unlock deeper insights from your data.
                </Typography>
              </Box>
              <Divider sx={{ mb: 1.5 }} />

              {/* Alerts */}
              {error && (
                <Alert severity="error" sx={{ mb: 1 }}>
                  {error}
                </Alert>
              )}
              {success && (
                <Alert severity="success" sx={{ mb: 1 }}>
                  {success}
                </Alert>
              )}

              {/* Stepper */}
              <Stepper
                activeStep={activeStep}
                sx={{
                  mb: 1.25,
                  '& .MuiStepLabel-label': { fontSize: '0.875rem' },
                  '& .MuiStepIcon-root': { width: 28, height: 28 },
                  '& .MuiStep-root': { padding: '8px 0' },
                }}
              >
                {steps.map((label) => (
                  <Step key={label}>
                    <StepLabel>{label}</StepLabel>
                  </Step>
                ))}
              </Stepper>

              {/* Content Area */}
              <Box
                sx={{
                  flex: 1,
                  bgcolor: '#F9FAFB',
                  p: 1,
                  borderRadius: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  minHeight: 300,
                }}
              >
                {activeStep === 0 && (
                  <SchemaConfigurationDisplay onSchemaLoaded={handleSchemaLoaded} />
                )}
                {activeStep === 1 && (
                  <RelationshipEditor
                    schemaConfig={schemaConfig}
                    onRelationshipsUpdated={handleRelationshipsUpdated}
                  />
                )}
                {activeStep === 2 && (
                  <KGGenerationPanel
                    schemaConfig={schemaConfig}
                    relationships={relationships}
                    onKGGenerated={handleKGGenerated}
                  />
                )}
              </Box>

              {/* Action Buttons */}
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  mt: 1,
                  pt: 0.75,
                }}
              >
                <Button
                  disabled={activeStep === 0}
                  onClick={handleBack}
                  variant="outlined"
                  size="small"
                  sx={{
                    px: 1.5,
                    py: 0.5,
                    minWidth: 'auto',
                    color: '#64748B',
                    borderColor: '#CBD5E1',
                    fontSize: '0.8125rem',
                    textTransform: 'none',
                    borderRadius: '8px',
                    '&:hover': {
                      bgcolor: '#F8FAFC',
                      borderColor: '#94A3B8',
                      color: '#475569',
                    },
                    '&:disabled': {
                      color: '#D1D5DB',
                      borderColor: '#E5E7EB',
                    },
                  }}
                >
                  ← Back
                </Button>
                <Button
                  onClick={handleNext}
                  variant="contained"
                  disabled={
                    activeStep === steps.length - 1 ||
                    (activeStep === 0 && !schemaConfig) ||
                    (activeStep === 1 && relationships.length === 0)
                  }
                  size="small"
                  endIcon={<ArrowForward />}
                  sx={{
                    px: 2,
                    py: 0.5,
                    minHeight: 'auto',
                    bgcolor: '#5B6FE5',
                    color: '#FFFFFF',
                    fontSize: '0.8125rem',
                    fontWeight: 500,
                    textTransform: 'none',
                    borderRadius: '8px',
                    boxShadow: '0 1px 3px 0 rgba(91, 111, 229, 0.2)',
                    '&:hover': {
                      bgcolor: '#4C5FD5',
                      boxShadow: '0 2px 6px 0 rgba(91, 111, 229, 0.3)',
                    },
                    '&:disabled': {
                      bgcolor: '#E5E7EB',
                      color: '#9CA3AF',
                      boxShadow: 'none',
                    },
                  }}
                  title={
                    activeStep === 0 && !schemaConfig
                      ? 'Please select a schema configuration first'
                      : activeStep === 1 && relationships.length === 0
                      ? 'Please add at least one relationship to continue'
                      : ''
                  }
                >
                  Next
                </Button>
              </Box>
            </Paper>
          </Box>
        </Fade>
      </Container>
    </Box>
  );
}

