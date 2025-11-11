import DashboardTrendsWidget from '../components/DashboardTrendsWidget';

/**
 * DashboardTrends Page
 *
 * This page component renders the self-contained KPI dashboard with two-column layout.
 * The DashboardTrendsWidget now includes:
 * - Main content area: KPI dashboard with metrics and visualizations
 * - Right sidebar: Planner filter for filtering KPIs by owner
 */
const DashboardTrend = () => {
  return <DashboardTrendsWidget />;
};

export default DashboardTrend;

