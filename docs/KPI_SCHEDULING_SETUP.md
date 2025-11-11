# KPI Scheduling System - Setup Guide

## 🚀 Overview

The KPI Scheduling System provides automated execution of KPI calculations using Apache Airflow. This system allows you to:

- **Schedule KPI executions** with flexible timing (daily, weekly, monthly, cron)
- **Monitor execution history** and performance metrics
- **Receive email notifications** on failures or successes
- **Manage schedules** through a user-friendly web interface
- **Track execution statistics** and system health

## 📋 Prerequisites

- **Python 3.11+**
- **SQL Server** (for KPI definitions and execution history)
- **Apache Airflow 2.7+** (optional but recommended for production)
- **SMTP Server** (for email notifications)
- **Docker & Docker Compose** (for containerized deployment)

## 🛠️ Installation Steps

### 1. Database Setup

First, run the database migration to create the required tables:

```sql
-- Run the SQL scripts in order:
-- 1. kg_builder/migrations/001_create_kpi_schedules.sql
-- 2. kg_builder/migrations/002_create_schedule_executions.sql  
-- 3. kg_builder/migrations/003_create_schedule_notifications.sql
```

### 2. Environment Configuration

Copy and configure the environment files:

```bash
# Main application environment
cp .env.example .env

# Airflow environment (if using Airflow)
cp config/airflow.env .env.airflow
```

Update the following key settings in `.env`:

```env
# Database Connection
MSSQL_CONNECTION_STRING=your_connection_string

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
NOTIFICATION_FROM_EMAIL=kpi-scheduler@yourcompany.com

# Airflow Integration
AIRFLOW_DAGS_FOLDER=/opt/airflow/dags
```

### 3. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd web-app
npm install
cd ..
```

### 4. Start the Application

```bash
# Start the backend API
uvicorn kg_builder.main:app --host 0.0.0.0 --port 8000 --reload

# Start the frontend (in another terminal)
cd web-app
npm start
```

### 5. Airflow Setup (Optional but Recommended)

For production deployments, set up Airflow:

```bash
# Using Docker Compose
docker-compose -f docker/docker-compose.airflow.yml up -d

# Or install Airflow manually
pip install apache-airflow[postgres,celery]==2.7.3
airflow db init
airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
```

## 🎯 Usage Guide

### Creating a Schedule

1. **Navigate to KPI Management** in the web interface
2. **Click "Manage Schedule"** for any KPI
3. **Fill in the schedule details**:
   - **Schedule Name**: Descriptive name
   - **Schedule Type**: Daily, Weekly, Monthly, or Cron
   - **Start Date**: When to begin execution
   - **Timezone**: Execution timezone
   - **Retry Settings**: Number of retries and delay
   - **Email Notifications**: Recipients for alerts

### Schedule Types

- **Daily**: Executes every day at a specified time
- **Weekly**: Executes weekly on a specified day
- **Monthly**: Executes monthly on a specified date
- **Cron**: Custom cron expression for complex schedules

### Monitoring Schedules

1. **Schedule Monitor Dashboard**: View system-wide execution statistics
2. **Execution History**: Detailed history for each schedule
3. **Manual Triggers**: Trigger schedules manually for testing
4. **Airflow Integration**: View DAGs in Airflow UI (if enabled)

## 🔧 Configuration Options

### Schedule Configuration

```json
{
  "retry_count": 3,
  "retry_delay": 300,
  "timeout": 3600,
  "email_notifications": ["admin@company.com"],
  "notification_settings": {
    "on_failure": true,
    "on_success": false,
    "on_retry": true
  }
}
```

### Email Notification Settings

Configure SMTP settings in your environment:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
NOTIFICATION_FROM_EMAIL=kpi-scheduler@company.com
```

## 📊 API Endpoints

### Schedule Management
- `POST /v1/kpi-schedules/` - Create schedule
- `GET /v1/kpi-schedules/{id}` - Get schedule details
- `PUT /v1/kpi-schedules/{id}` - Update schedule
- `DELETE /v1/kpi-schedules/{id}` - Delete schedule
- `POST /v1/kpi-schedules/{id}/toggle` - Enable/disable schedule

### Execution Tracking
- `POST /v1/kpi-schedule-executions/` - Create execution record
- `PUT /v1/kpi-schedule-executions/{id}` - Update execution status
- `GET /v1/kpi-schedules/{id}/executions` - Get execution history
- `GET /v1/kpi-schedules/{id}/statistics` - Get execution statistics

### Monitoring
- `GET /v1/kpi-schedules/dashboard-overview` - Dashboard data
- `POST /v1/kpi-schedules/sync-all-to-airflow` - Sync to Airflow
- `GET /v1/kpi-schedules/{id}/airflow-status` - Airflow DAG status

## 🚨 Troubleshooting

### Common Issues

1. **Schedules not executing**
   - Check Airflow is running and DAGs are synced
   - Verify schedule is active (`is_active = true`)
   - Check Airflow logs for errors

2. **Email notifications not working**
   - Verify SMTP configuration
   - Check email credentials and permissions
   - Test SMTP connection manually

3. **Database connection errors**
   - Verify connection string format
   - Check database server accessibility
   - Ensure required tables exist

### Logs and Debugging

- **Application logs**: Check console output or log files
- **Airflow logs**: Available in Airflow UI under each DAG run
- **Database logs**: Check SQL Server logs for connection issues

## 🔒 Security Considerations

- **Database Access**: Use dedicated service account with minimal permissions
- **Email Credentials**: Store in environment variables, not code
- **API Security**: Implement authentication for production deployments
- **Airflow Security**: Enable authentication and use HTTPS

## 📈 Performance Optimization

- **Database Indexing**: Ensure proper indexes on schedule and execution tables
- **Airflow Configuration**: Tune parallelism and concurrency settings
- **Cleanup Jobs**: Implement retention policies for old execution records
- **Monitoring**: Set up alerts for failed executions and system health
