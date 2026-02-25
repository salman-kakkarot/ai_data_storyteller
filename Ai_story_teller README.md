# 📊 AI Data Teller Dashboard

An interactive **Streamlit-based dashboard** for automated **data storytelling, exploratory data analysis (EDA), AI-generated insights, interactive visualizations, and PDF report generation**.  

---

## 🚀 Approach Overview
1. **Data Upload & Preprocessing**
   - Supports `.csv` and `.xlsx` files.
   - Automatically loads and validates datasets.
   - Detects missing values, duplicates, and data types.

2. **Comprehensive Analysis**
   - Summarizes dataset shape, data types, missing values, duplicates.
   - Generates numeric and categorical statistics.
   - Computes correlations between numeric variables.

3. **AI Insights**
   - Automatically produces data-driven insights:
     - Dataset overview
     - Data quality checks
     - Numeric and categorical summaries
     - Correlation findings
     - Duplicate detection

4. **Interactive Visualizations**
   - Correlation heatmap
   - Distribution plots
   - Scatter matrix
   - Categorical analysis (box plots)
   - Time-series visualization (if date columns exist)

5. **Report Generation**
   - Creates a professional **PDF Report** with:
     - Executive summary
     - Dataset overview
     - Numeric & categorical analysis
     - Recommendations & conclusions
     - Data quality assessment
   - Supports **A4 formatting** for business-ready documentation.

---

## 📚 Libraries Used
The following Python libraries are required:

- **Streamlit** – UI framework for interactive dashboards  
- **Pandas** – Data manipulation and preprocessing  
- **NumPy** – Numerical computations  
- **Matplotlib & Seaborn** – Basic visualizations (backend support)  
- **Plotly** – Interactive charts (heatmaps, scatter matrix, etc.)  
- **FPDF** – Automated PDF report generation  
- **Datetime, OS, Tempfile, Pathlib** – File handling and utilities  
- **Regex (re), Traceback** – Text cleaning and error handling  

---

## 🛠️ Steps to Run the Dashboard

### 1. Clone or Download the Repository
```bash
git clone <your-repo-link>
cd <repo-folder>
```

### 2. Install Required Dependencies
Make sure you have Python 3.8+ installed. Then run:
```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available, install manually:
```bash
pip install streamlit pandas numpy matplotlib seaborn plotly fpdf
```

### 3. Run the Streamlit App
```bash
streamlit run Ai_story_teller.py
```

### 4. Upload Your Dataset
- Upload a **CSV or Excel file** from the sidebar.  
- Explore **dataset overview, AI insights, and visualizations**.  
- Optionally, **generate a PDF report** of your analysis.  

---

## 🎯 Key Features
- One-click **AI-powered analysis**  
- **Interactive and customizable visualizations**  
- **Automated PDF reporting** (executive summary, insights, recommendations)  
- Multi-theme and multi-language support  
- Works with **custom datasets or sample data**  
