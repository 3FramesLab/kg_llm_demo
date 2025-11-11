/**
 * SQL Viewer Component
 * Always shows generated SQL with enhancement indicators and copy functionality
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Tooltip,
  Chip,
  Card,
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert
} from '@mui/material';
import {
  Code as CodeIcon,
  ContentCopy as ContentCopyIcon,
  CheckCircle as CheckCircleIcon,
  ExpandMore as ExpandMoreIcon,
  Visibility as VisibilityIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import { hasOpsPlanner, involvesHanaMaster, involvesMaterialTables, getEnhancementStatus } from '../services/kpiAnalyticsApi';

const SQLViewer = ({ 
  originalSql, 
  enhancedSql, 
  title = "Generated SQL",
  showAlwaysVisible = true,
  defaultExpanded = true,
  showEnhancementInfo = true,
  compact = false,
  error = null
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopySQL = async (sql) => {
    try {
      await navigator.clipboard.writeText(sql);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy SQL:', err);
    }
  };

  const renderSQLContent = (sql, label, isEnhanced = false) => {
    if (!sql) return null;

    return (
      <Box sx={{ mb: isEnhanced ? 0 : 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="subtitle2" fontWeight="600">
              {label}
            </Typography>
            {isEnhanced && showEnhancementInfo && (
              <Box sx={{ display: 'flex', gap: 0.5 }}>
                {involvesHanaMaster(sql) && (
                  <Chip label="material_master" color="info" size="small" />
                )}
                {hasOpsPlanner(sql) && (
                  <Chip label="ops_planner" color="success" size="small" />
                )}
                {involvesMaterialTables(originalSql) && !involvesHanaMaster(sql) && (
                  <Chip label="enhancement_needed" color="warning" size="small" />
                )}
              </Box>
            )}
          </Box>
          <Tooltip title={copied ? "Copied!" : "Copy SQL"}>
            <IconButton onClick={() => handleCopySQL(sql)} size="small">
              {copied ? <CheckCircleIcon color="success" /> : <ContentCopyIcon />}
            </IconButton>
          </Tooltip>
        </Box>
        
        <Box sx={{
          fontFamily: 'monospace',
          fontSize: compact ? '0.75rem' : '0.875rem',
          bgcolor: 'grey.50',
          p: compact ? 1.5 : 2,
          borderRadius: 1,
          border: '1px solid',
          borderColor: 'grey.200',
          maxHeight: compact ? 200 : 300,
          overflow: 'auto',
          whiteSpace: 'pre-wrap'
        }}>
          {sql}
        </Box>
      </Box>
    );
  };

  // If no SQL provided
  if (!originalSql && !enhancedSql) {
    return (
      <Alert severity="info" sx={{ mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CodeIcon />
          <Typography variant="subtitle2">No SQL Generated</Typography>
        </Box>
        <Typography variant="body2">
          SQL will be displayed here once generated.
        </Typography>
      </Alert>
    );
  }

  // Error state
  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <ErrorIcon />
          <Typography variant="subtitle2">SQL Generation Error</Typography>
        </Box>
        <Typography variant="body2" sx={{ mb: 1 }}>
          {error}
        </Typography>
        {originalSql && (
          <Box>
            <Typography variant="body2" sx={{ mb: 1 }}>
              Partial SQL (if available):
            </Typography>
            {renderSQLContent(originalSql, "Generated SQL")}
          </Box>
        )}
      </Alert>
    );
  }

  // Compact view
  if (compact) {
    const sqlToShow = enhancedSql || originalSql;
    return (
      <Card sx={{ mb: 1 }}>
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <CodeIcon color="primary" fontSize="small" />
            <Typography variant="subtitle2">{title}</Typography>
            {showAlwaysVisible && (
              <Chip label="Always Visible" color="success" size="small" variant="outlined" />
            )}
            {showEnhancementInfo && enhancedSql && enhancedSql !== originalSql && (
              <Chip label="Enhanced" color="info" size="small" />
            )}
          </Box>
          {renderSQLContent(sqlToShow, "", enhancedSql && enhancedSql !== originalSql)}
        </CardContent>
      </Card>
    );
  }

  // Full accordion view
  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Accordion defaultExpanded={defaultExpanded}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
              <VisibilityIcon color="primary" />
              <Typography variant="h6">{title}</Typography>
              {showAlwaysVisible && (
                <Chip 
                  label="Always Visible" 
                  color="success" 
                  size="small" 
                  variant="outlined"
                />
              )}
              <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto' }}>
                SQL shown regardless of results
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            {/* Original SQL */}
            {originalSql && renderSQLContent(originalSql, "Original Generated SQL")}
            
            {/* Enhanced SQL */}
            {enhancedSql && enhancedSql !== originalSql && renderSQLContent(
              enhancedSql, 
              "Enhanced SQL (with ops_planner)", 
              true
            )}
            
            {/* Enhancement Status Info */}
            {showEnhancementInfo && (
              (() => {
                const enhancementStatus = getEnhancementStatus(originalSql, enhancedSql);

                if (enhancementStatus.wasEnhanced) {
                  return (
                    <Alert severity="success" sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" fontWeight="600">SQL Enhancement Applied ✅</Typography>
                      <Typography variant="body2">
                        {enhancementStatus.hasMaterialMaster && 'Added hana_material_master join. '}
                        {enhancementStatus.hasOpsPlanner && 'Added ops_planner column. '}
                        This provides enhanced material analysis capabilities.
                      </Typography>
                    </Alert>
                  );
                } else if (enhancementStatus.shouldBeEnhanced && !enhancementStatus.enhancementWorking) {
                  return (
                    <Alert severity="warning" sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" fontWeight="600">Enhancement Expected But Not Applied ⚠️</Typography>
                      <Typography variant="body2">
                        This query involves material tables but doesn't include hana_material_master or ops_planner.
                        The enhancement may not be working correctly.
                      </Typography>
                    </Alert>
                  );
                } else if (!enhancementStatus.shouldBeEnhanced) {
                  return (
                    <Alert severity="info" sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" fontWeight="600">No Enhancement Needed</Typography>
                      <Typography variant="body2">
                        This query doesn't involve material tables, so no material master enhancement is needed.
                      </Typography>
                    </Alert>
                  );
                } else {
                  return (
                    <Alert severity="info" sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" fontWeight="600">Enhancement Already Present</Typography>
                      <Typography variant="body2">
                        This query already includes hana_material_master and ops_planner.
                      </Typography>
                    </Alert>
                  );
                }
              })()
            )}
          </AccordionDetails>
        </Accordion>
      </CardContent>
    </Card>
  );
};

export default SQLViewer;
