import React, { useState, useEffect, useRef } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Typography,
  CircularProgress,
  LinearProgress,
  Alert,
  Button,
  Stepper,
  Step,
  StepLabel,
  Paper,
} from '@mui/material';
import {
  CheckCircle,
  Error as ErrorIcon,
  HourglassEmpty,
  PlayArrow,
} from '@mui/icons-material';
import { getKPIExecutionResult } from '../../services/api';

const KPIExecutionStatusModal = ({ open, executionId, kpiName, onComplete, onError, onClose }) => {
  const [status, setStatus] = useState('pending'); // pending, running, success, failed
  const [execution, setExecution] = useState(null);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('Initializing execution...');
  const [elapsedTime, setElapsedTime] = useState(0);
  const pollingInterval = useRef(null);
  const startTime = useRef(Date.now());

  const statusSteps = [
    { label: 'Queued', status: 'pending' },
    { label: 'Executing Query', status: 'running' },
    { label: 'Completed', status: 'success' },
  ];

  useEffect(() => {
    if (open && executionId) {
      startTime.current = Date.now();
      pollExecutionStatus();

      // Poll every 1 second
      pollingInterval.current = setInterval(() => {
        pollExecutionStatus();
      }, 1000);

      // Update elapsed time every 100ms
      const timeInterval = setInterval(() => {
        setElapsedTime(Date.now() - startTime.current);
      }, 100);

      return () => {
        clearInterval(pollingInterval.current);
        clearInterval(timeInterval);
      };
    }
  }, [open, executionId]);

  const pollExecutionStatus = async () => {
    try {
      const response = await getKPIExecutionResult(executionId);
      const exec = response.data.execution;
      setExecution(exec);

      const execStatus = exec.execution_status;
      setStatus(execStatus);

      // Update status message
      if (execStatus === 'pending') {
        setStatusMessage('Waiting in queue...');
        setProgress(10);
      } else if (execStatus === 'running') {
        setStatusMessage(`Executing SQL query... (${(elapsedTime / 1000).toFixed(1)}s)`);
        setProgress(50);
      } else if (execStatus === 'success') {
        setStatusMessage(`Completed successfully! Found ${exec.number_of_records || 0} records`);
        setProgress(100);
        clearInterval(pollingInterval.current);
        setTimeout(() => {
          onComplete && onComplete(exec);
        }, 1500); // Give user time to see success
      } else if (execStatus === 'failed') {
        setStatusMessage('Execution failed');
        setProgress(100);
        clearInterval(pollingInterval.current);
        setTimeout(() => {
          onError && onError(exec.error_message || 'Unknown error');
        }, 2000); // Give user time to see error
      }
    } catch (error) {
      console.error('Error polling execution status:', error);
      setStatus('failed');
      setStatusMessage('Failed to check execution status');
      clearInterval(pollingInterval.current);
    }
  };

  const getActiveStep = () => {
    if (status === 'pending') return 0;
    if (status === 'running') return 1;
    if (status === 'success' || status === 'failed') return 2;
    return 0;
  };

  const getStepIcon = (stepStatus) => {
    if (stepStatus === status) {
      if (status === 'success') return <CheckCircle color="success" />;
      if (status === 'failed') return <ErrorIcon color="error" />;
      if (status === 'running') return <CircularProgress size={24} />;
      if (status === 'pending') return <HourglassEmpty color="action" />;
    }
    return null;
  };

  const formatTime = (ms) => {
    const seconds = (ms / 1000).toFixed(1);
    return `${seconds}s`;
  };

  return (
    <Dialog
      open={open}
      maxWidth="sm"
      fullWidth
      disableEscapeKeyDown
      onClose={(event, reason) => {
        // Prevent closing by clicking backdrop or escape key
        if (reason === 'backdropClick' || reason === 'escapeKeyDown') {
          return;
        }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {status === 'running' && <CircularProgress size={24} />}
          {status === 'success' && <CheckCircle color="success" />}
          {status === 'failed' && <ErrorIcon color="error" />}
          <Typography variant="h6" component="div">
            Executing: {kpiName}
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Box sx={{ py: 2 }}>
          {/* Progress Bar */}
          <Box sx={{ mb: 3 }}>
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{
                height: 8,
                borderRadius: 4,
                backgroundColor: '#e0e0e0',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 4,
                  background:
                    status === 'success'
                      ? 'linear-gradient(90deg, #43e97b 0%, #38f9d7 100%)'
                      : status === 'failed'
                      ? 'linear-gradient(90deg, #f85032 0%, #e73827 100%)'
                      : 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                },
              }}
            />
            <Typography
              variant="body2"
              sx={{ mt: 1, textAlign: 'center', color: 'text.secondary' }}
            >
              {statusMessage}
            </Typography>
          </Box>

          {/* Execution Steps */}
          <Stepper activeStep={getActiveStep()} sx={{ mb: 3 }}>
            {statusSteps.map((step, index) => (
              <Step key={step.label}>
                <StepLabel
                  StepIconComponent={() => getStepIcon(step.status) || <div>{index + 1}</div>}
                >
                  {step.label}
                </StepLabel>
              </Step>
            ))}
          </Stepper>

          {/* Status Details */}
          <Paper
            elevation={0}
            sx={{
              p: 2,
              bgcolor: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: 2,
            }}
          >
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Execution ID:</strong> {executionId}
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Status:</strong>{' '}
              <Box
                component="span"
                sx={{
                  px: 1,
                  py: 0.5,
                  borderRadius: 1,
                  bgcolor:
                    status === 'success'
                      ? '#d4edda'
                      : status === 'failed'
                      ? '#f8d7da'
                      : status === 'running'
                      ? '#d1ecf1'
                      : '#e2e3e5',
                  color:
                    status === 'success'
                      ? '#155724'
                      : status === 'failed'
                      ? '#721c24'
                      : status === 'running'
                      ? '#0c5460'
                      : '#383d41',
                  textTransform: 'uppercase',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                }}
              >
                {status}
              </Box>
            </Typography>
            <Typography variant="body2">
              <strong>Elapsed Time:</strong> {formatTime(elapsedTime)}
            </Typography>
            {execution && execution.number_of_records !== undefined && (
              <Typography variant="body2" sx={{ mt: 1 }}>
                <strong>Records Found:</strong> {execution.number_of_records.toLocaleString()}
              </Typography>
            )}
          </Paper>

          {/* Error Message */}
          {status === 'failed' && execution && execution.error_message && (
            <Alert severity="error" sx={{ mt: 2 }}>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                Error:
              </Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                {execution.error_message}
              </Typography>
            </Alert>
          )}

          {/* Success Message */}
          {status === 'success' && execution && (
            <Alert severity="success" sx={{ mt: 2 }}>
              <Typography variant="body2">
                Query executed successfully in {execution.execution_time_ms?.toFixed(2) || 0}ms
              </Typography>
            </Alert>
          )}
        </Box>
      </DialogContent>

      {/* Close button for error states */}
      {status === 'failed' && (
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button
            onClick={onClose}
            variant="contained"
            color="primary"
            fullWidth
            size="small"
          >
            Close
          </Button>
        </DialogActions>
      )}
    </Dialog>
  );
};

export default KPIExecutionStatusModal;
