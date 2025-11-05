import DashboardTrendsWidget from '../components/DashboardTrendsWidget';

/**
 * DashboardTrends Page
 *
 * This page component renders the self-contained KPI dashboard with three-column layout.
 * The DashboardTrendsWidget now includes:
 * - Left sidebar (15%): Reserved space for future features
 * - Center area (70%): Main KPI dashboard with metrics and visualizations
 * - Right sidebar (15%): Planner filter for filtering KPIs by owner
 */
const DashboardTrend = () => {
  return <DashboardTrendsWidget />;
};

export default DashboardTrend;

