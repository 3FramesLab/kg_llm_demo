import {
  Box,
  Container,
  Fade,
  useTheme,
  alpha,
} from '@mui/material';
import SchemaWizard from '../components/SchemaWizard';

/**
 * Schemas Page Component
 * Main page for creating knowledge graphs from database sources
 */
function Schemas() {
  const theme = useTheme();

  return (
    <Box sx={{ p: 2 }}>
      <Container maxWidth="auto" disableGutters>
        {/* Knowledge Graph Wizard with Enhanced Animation */}
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
            <SchemaWizard />
          </Box>
        </Fade>
      </Container>
    </Box>
  );
}

export default Schemas;