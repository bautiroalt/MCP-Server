# 🧠 META-MINDS Quick Start Guide

## 🎯 What is META-MINDS?

META-MINDS is an **AI-powered data analytics platform** integrated into your MCP Server that generates **SMART analytical questions** with **97%+ quality scores**.

**Repository**: [https://github.com/Jatin23K/META-MINDS](https://github.com/Jatin23K/META-MINDS)

## ⚡ 3-Minute Quick Start

### Step 1: Start Your Servers

```bash
# Terminal 1: Start Backend (if not already running)
cd "C:\Users\Jatin\Documents\APP\MCP_Server\NEW MCP\backend"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Interface
cd "C:\Users\Jatin\Documents\APP\MCP_Server\NEW MCP"
python -m http.server 3001
```

### Step 2: Open Interface

Navigate to: **http://localhost:3001/mcp-interface.html**

### Step 3: Run Your First Analysis

1. Click the **🧠 Analytics** tab
2. Upload a dataset (CSV, XLSX, JSON, TXT) or select an uploaded file
3. Choose your configuration:
   - **Business Context**: Financial Analysis
   - **Analysis Focus**: Performance evaluation
   - **Target Audience**: Executives
   - **Questions**: 15
4. Click **"🧠 Run META-MINDS Analysis"**
5. View your results!

## 📊 Example Analysis

### Input
```
Dataset: sales_data.csv
Business Context: Sales Analytics
Analysis Focus: Performance evaluation
Target Audience: Executives
Questions: 15
```

### Output
```
✅ Quality Assessment:
   📈 Average SMART Score: 97.0%
   ✅ High Quality Questions: 15/15
   🌟 Status: Excellent - Ready for Executive Review

🔍 Generated Questions (Sample):
   
📊 DATA QUALITY & COMPLETENESS
Q1. What percentage of missing values exists in sales_data.csv...
Q2. How does data completeness vary across different time periods...
Q3. What outliers or anomalies are present in sales analytics metrics...

📈 PATTERN DISCOVERY  
Q4. What are the top 3 patterns emerging from sales analytics metrics...
Q5. Which variables show the strongest correlation in sales_data.csv...
Q6. How do different segments compare in terms of performance evaluation...

... (9 more questions across 3 categories)
```

## 🎨 Interface Features

### Analytics Tab Components

1. **📊 Dataset Selection**
   - Upload new datasets
   - Select from uploaded files
   - Supports: CSV, XLSX, JSON, TXT

2. **⚙️ Analysis Configuration**
   - 7 business contexts
   - 5 analysis focus areas
   - 4 target audiences
   - Customizable question count

3. **✅ Quality Assessment**
   - Real-time SMART score calculation
   - High-quality question count
   - Quality status indicator

4. **🔍 Generated Questions**
   - Categorized by analytical dimension
   - Individual SMART scores
   - Relevance and complexity indicators

5. **📤 Export Options**
   - Export as JSON
   - Export as TXT report
   - Copy to clipboard

## 🏢 Business Context Templates

Choose from 7+ templates:

1. **💰 Financial Analysis** - Performance evaluation, risk assessment
2. **📈 Sales Analytics** - Sales performance, pipeline analysis
3. **📣 Marketing Analytics** - Campaign effectiveness, ROI
4. **⚙️ Operations** - Efficiency optimization, cost reduction
5. **👥 HR Analytics** - Performance, retention studies
6. **🎯 Customer Analytics** - Behavior, satisfaction analysis
7. **📦 Product Analytics** - Usage, feature adoption

## 🔧 Advanced Usage

### Via MCP Tools Tab

1. Go to **🔧 MCP Tools** tab
2. Click **meta_minds_analysis**
3. Fill in parameters:
   ```
   dataset_path: data/sales.csv
   business_context: Sales Analytics
   analysis_focus: Trend analysis
   target_audience: Managers
   num_questions: 20
   ```
4. Click **Execute Tool**

### Via API (for automation)

```bash
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "meta_minds_analysis",
    "arguments": {
      "dataset_path": "data/financial_report.csv",
      "business_context": "Financial Analysis",
      "analysis_focus": "Risk assessment",
      "target_audience": "Executives",
      "num_questions": 15
    }
  }'
```

### Batch Analysis

```bash
curl -X POST http://localhost:8000/mcp/api/v1/analytics/batch-analyze \
  -H "Content-Type": application/json" \
  -d '{
    "dataset_paths": ["sales_q1.csv", "sales_q2.csv", "sales_q3.csv"],
    "business_context": "Sales Analytics",
    "num_questions": 15
  }'
```

## 💡 Best Practices

### 1. Dataset Preparation
- ✅ Clean, structured data (CSV, XLSX)
- ✅ Clear column headers
- ✅ Consistent formatting
- ✅ Reasonable file size (<50MB recommended)

### 2. Context Selection
- ✅ Match business context to your data type
- ✅ Choose focus based on your analysis goals
- ✅ Select audience appropriate for output

### 3. Question Count
- **5-10**: Quick insights
- **10-15**: Standard analysis (recommended)
- **15-20**: Comprehensive review
- **20-30**: Deep dive analysis

### 4. Quality Expectations
- **97%+**: Executive-ready
- **95-97%**: Very good quality
- **90-95%**: Good, may need review
- **<90%**: Refine parameters

## 📈 Real-World Use Cases

### Use Case 1: Quarterly Financial Review
```
1. Upload Q4_financials.xlsx
2. Context: Financial Analysis
3. Focus: Performance evaluation
4. Audience: Executives
5. Result: 15 executive-level questions for board meeting
```

### Use Case 2: Sales Pipeline Analysis
```
1. Upload sales_pipeline.csv
2. Context: Sales Analytics
3. Focus: Trend analysis
4. Audience: Managers
5. Result: Sales insights and forecasting questions
```

### Use Case 3: Marketing Campaign ROI
```
1. Upload campaign_data.csv
2. Context: Marketing Analytics
3. Focus: Optimization
4. Audience: Stakeholders
5. Result: ROI analysis and optimization recommendations
```

## 🎓 Understanding SMART Questions

### What Makes a Question SMART?

- **S**pecific: "What percentage of customers..." vs "How are customers..."
- **M**easurable: "What is the year-over-year growth rate..." with quantifiable metrics
- **A**chievable: Based on available data columns
- **R**elevant: Aligned with business context and goals
- **T**ime-bound: "How has X changed over the past year..."

### Question Categories

Each analysis generates questions across 5 dimensions:

1. **📊 Data Quality** - Completeness, accuracy, outliers
2. **📈 Patterns** - Trends, correlations, segments
3. **⏰ Temporal** - Time-based trends, forecasting
4. **🎯 Business Impact** - Revenue, cost, risk, strategy
5. **🔗 Relationships** - Causation, dependencies, interactions

## 🔄 Workflow Automation

### Automated Pipeline

```
1. Upload Dataset → 2. Run Analysis → 3. Store in Context → 
4. Generate Report → 5. Export Results → 6. Share with Team
```

### Features:
- ✅ Auto-save to context
- ✅ Professional report generation
- ✅ Batch processing support
- ✅ Cross-dataset comparison
- ✅ Quality validation
- ✅ Export automation

## 📊 Output Formats

### 1. JSON Export
- Complete analysis data
- Structured for API integration
- Machine-readable

### 2. TXT Report
- Professional formatting
- Executive-ready
- Print-ready

### 3. Clipboard Copy
- Quick sharing
- Email integration
- Documentation

## 🆘 Troubleshooting

### "Failed to load tools"
- ✅ Check backend is running on port 8000
- ✅ Refresh the interface
- ✅ Check browser console for CORS errors

### "Dataset not found"
- ✅ Verify file path is correct
- ✅ Upload file via Files tab first
- ✅ Use relative paths from MCP root

### "Analysis takes too long"
- ✅ Reduce number of questions
- ✅ Check dataset size (<50MB recommended)
- ✅ Monitor backend logs for errors

## 📞 Need Help?

- **Integration Docs**: See `docs/META_MINDS_INTEGRATION.md`
- **API Docs**: http://localhost:8000/mcp/docs
- **META-MINDS Repo**: https://github.com/Jatin23K/META-MINDS
- **MCP Interface**: Click the ❓ Help tab

---

**Ready to transform your data into actionable insights!** 🧠✨

**Time to first analysis: < 3 minutes** ⚡

