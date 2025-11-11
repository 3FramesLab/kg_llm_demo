# Unified Environment Configuration Guide

## 🎯 **Problem Solved**

Previously, the DQ-POC project had **multiple scattered environment files**:
- Root `.env` (171 lines) - Main backend configuration
- `web-app/.env` (2 lines) - Frontend API URL
- `config/airflow.env` (53 lines) - Airflow settings
- Docker Compose environment variables

This created **configuration drift** and made deployment complex.

## ✅ **Solution: Unified Environment System**

Created a **single source of truth** for all environment configuration:

### **📁 New Structure**
```
config/
├── unified.env                    # 🎯 Master configuration file
└── (other config files...)

scripts/
└── setup-environment.py          # 🔧 Environment management script
```

## 🔧 **How to Use**

### **1. Setup Environment**

```bash
# Development environment (local development)
python scripts/setup-environment.py development

# Docker environment (containerized deployment)
python scripts/setup-environment.py docker

# Production environment (production deployment)
python scripts/setup-environment.py production
```

### **2. Validate Configuration**

```bash
# Check if environment is properly configured
python scripts/setup-environment.py --validate
```

## 📋 **What the Script Does**

### **Automatic Configuration**
1. **📋 Copies** `config/unified.env` → root `.env`
2. **🌐 Creates** `web-app/.env` with appropriate API URL
3. **🔧 Applies** environment-specific overrides
4. **✅ Validates** configuration completeness

### **Environment-Specific Overrides**

#### **🏠 Development Environment**
- Uses `localhost` for all services
- Enables debug features
- Local file paths

#### **🐳 Docker Environment**
- Uses container hostnames (`falkordb`, `mongodb`)
- Container file paths (`/app/jdbc_drivers`)
- Host machine database access (`host.docker.internal`)

#### **🏭 Production Environment**
- Disables debug features
- Warning-level logging
- Production-ready settings

## 🎯 **Unified Configuration Sections**

### **🔧 Core Application**
- API host, port, logging
- Frontend API URL

### **🗄️ Database Connections**
- FalkorDB (graph database)
- MongoDB (results storage)
- Source/Target databases
- KPI Analytics database
- Landing database

### **🤖 AI/LLM Configuration**
- OpenAI API settings
- LLM feature flags

### **📊 Airflow Integration**
- Scheduler settings
- Email notifications
- Performance tuning

### **🔗 JDBC Configuration**
- Driver paths
- Connection settings

## 📝 **Customization Guide**

### **1. Database Credentials**
```env
# Update these with your actual database details
SOURCE_DB_HOST=your-database-server
SOURCE_DB_USERNAME=your-username
SOURCE_DB_PASSWORD=your-secure-password
```

### **2. OpenAI API Key**
```env
# Add your actual OpenAI API key
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### **3. Email Notifications**
```env
# Configure SMTP for Airflow notifications
SMTP_SERVER=your-smtp-server.com
SMTP_USERNAME=notifications@yourcompany.com
SMTP_PASSWORD=your-email-password
```

### **4. Production URLs**
```env
# Update for your production environment
REACT_APP_API_URL=https://api.yourcompany.com/v1
```

## 🔒 **Security Best Practices**

1. **🚫 Never commit `.env`** - Already in `.gitignore`
2. **🔐 Use strong passwords** - 12+ characters, mixed case, symbols
3. **🔄 Rotate credentials** - Every 90 days
4. **👤 Use read-only users** - For data source connections
5. **🏢 Environment separation** - Different credentials per environment

## 🚀 **Migration from Old System**

### **Before (Multiple Files)**
```bash
# Had to manage multiple files
.env                    # Backend config
web-app/.env           # Frontend config  
config/airflow.env     # Airflow config
docker-compose.yml     # Container overrides
```

### **After (Unified System)**
```bash
# Single command setup
python scripts/setup-environment.py development

# Everything configured automatically:
# ✅ .env (root)
# ✅ web-app/.env  
# ✅ Environment-specific overrides applied
```

## 🧪 **Testing the Setup**

### **1. Validate Configuration**
```bash
python scripts/setup-environment.py --validate
```

### **2. Test Backend**
```bash
# Start backend and check health
python run_server.py
curl http://localhost:8000/health
```

### **3. Test Frontend**
```bash
# Start frontend
cd web-app
npm start
# Should connect to backend API
```

### **4. Test Docker**
```bash
# Setup for Docker and run
python scripts/setup-environment.py docker
docker-compose up -d
```

## 🎉 **Benefits**

1. **🎯 Single Source of Truth** - All configuration in one place
2. **🔧 Environment-Aware** - Automatic environment-specific settings
3. **🚀 Easy Deployment** - One command setup
4. **✅ Validation** - Built-in configuration checking
5. **📚 Documentation** - Clear configuration guide
6. **🔒 Security** - Best practices built-in

---

**Created**: November 9, 2025  
**Status**: ✅ Ready for use  
**Migration**: Backward compatible with existing setup
