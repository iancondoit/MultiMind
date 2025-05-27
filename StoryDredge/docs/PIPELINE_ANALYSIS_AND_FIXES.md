# StoryDredge Pipeline Analysis & Critical Fixes

## 🔍 **Complete Pipeline Analysis**

After thorough examination of the StoryDredge codebase, here's the current pipeline flow and critical issues that need fixing:

### **Current Pipeline Flow**
```
Raw Files (cache/) → OCR Cleaner → Article Splitter → Article Classifier → HSA Formatter → PostgreSQL Database
```

### **🚨 Critical Issues Identified**

#### 1. **Import Path Issues**
- **Problem**: Mixed import paths (`src.utils` vs `src.src.utils`)
- **Impact**: Pipeline components may fail to import properly
- **Fix**: Standardize all imports to use `src.src.` prefix

#### 2. **Missing Dependencies**
- **Problem**: Ollama not installed/configured for classification
- **Impact**: Article classification will fail
- **Fix**: Install Ollama or enable skip_classification mode

#### 3. **Database Connection Issues**
- **Problem**: PostgreSQL may not be running on expected port (5433)
- **Impact**: Final database import will fail
- **Fix**: Start PostgreSQL container or update connection settings

#### 4. **Output Directory Structure**
- **Problem**: Pipeline expects specific directory structure that may not exist
- **Impact**: File operations may fail
- **Fix**: Ensure all output directories are created

#### 5. **Configuration Files Missing**
- **Problem**: Pipeline expects config files in `config/` directory
- **Impact**: Components may use default settings or fail
- **Fix**: Create necessary configuration files

### **🛠️ Fixes to Implement**

#### Fix 1: Standardize Import Paths
All pipeline components need consistent import paths.

#### Fix 2: Create Missing Configuration
The pipeline needs proper configuration files for all components.

#### Fix 3: Setup PostgreSQL Database
Ensure database is running and accessible.

#### Fix 4: Install/Configure Ollama (or skip classification)
Either install Ollama for classification or enable skip mode.

#### Fix 5: Create Output Directory Structure
Ensure all necessary directories exist.

### **📋 Test Plan for 100 Articles**

1. **Pre-flight Checks**
   - Verify all imports work
   - Check database connectivity
   - Validate configuration files
   - Test with single article first

2. **Batch Processing**
   - Process 100 articles through complete pipeline
   - Monitor for errors at each stage
   - Verify database insertion

3. **Output Validation**
   - Check article count in database
   - Verify data quality and structure
   - Confirm HSA-ready format

### **🎯 Expected Output Structure**

```
output/
├── hsa-ready/
│   └── atlanta-constitution/
│       └── [year]/
│           └── [month]/
│               └── [day]/
│                   ├── article_001.json
│                   ├── article_002.json
│                   └── ...
└── processing_reports/
    └── batch_report.json
```

### **📊 Success Metrics**

- **Processing Rate**: >90% of articles successfully processed
- **Database Insertion**: All processed articles in PostgreSQL
- **Data Quality**: Articles have proper metadata and content
- **Performance**: Complete processing in <30 minutes for 100 articles

### **🔧 Implementation Priority**

1. **HIGH**: Fix import paths (blocks everything)
2. **HIGH**: Create configuration files (required for components)
3. **MEDIUM**: Setup database (needed for final output)
4. **MEDIUM**: Configure Ollama or skip classification
5. **LOW**: Optimize performance settings

This analysis provides the roadmap for successfully running 100 test articles through the complete StoryDredge pipeline. 