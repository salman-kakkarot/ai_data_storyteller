import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from fpdf import FPDF
import tempfile
import os
from datetime import datetime
import io
import re
import traceback
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Data teller",
    page_icon="☠️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for red, gray & white theme with black text
# Custom CSS for tabs

st.markdown("""
<style>
    body, .stApp {
        background-color: white !important;
        color: black !important;
    }
    .main-header {
        font-size: 2.5rem;
        color: ; /* deep red */
        text-align: center;
        margin-bottom: 1rem;
    }
    .tab-container {
        background-color: #de0202; /* very light red */
        padding: 20px;
        border-radius: 10px;
        margin-top: 1rem;
        border: 1px solid #080707;
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(179,0,0,0.2);
        margin: 5px;
        color: Black;
    }
    .insight-box {
        background-color: #ffe6e6; /* pale red */
        padding: 15px;
        border-left: 4px solid #b30000;
        border-radius: 5px;
        margin: 10px 0;
        color: black;
    }
    .checkbox-container {
        display: flex;
        align-items: flex-start;
        margin: 10px 0;
    }
    .checkbox-col {
        width: 40px;
        padding-top: 15px
        color: red;
    }
    .insight-col {
        flex: 1;
    }
    /* Streamlit buttons */
    .stButton button {
        background-color: #5c5b5b !important;
        color: White !important;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #800000 !important;
    }
</style>
""", unsafe_allow_html=True)

class DataAnalyzer:
    def __init__(self):
        self.df = None
        self.analysis_results = {}
        
    def load_data(self, uploaded_file):
        """Load data """
        try:
            if uploaded_file.name.endswith('.csv'):
                self.df = pd.read_csv(uploaded_file)
            else:
                self.df = pd.read_excel(uploaded_file)
            return True, "loaded successfully✅!"
        except Exception as e:
            return False, f"Error loading data: {str(e)}"
    
    def perform_comprehensive_analysis(self):
        """Perform comprehensive EDA"""
        if self.df is None:
            return {}
        
        results = {}
        
        # Basic statistics
        results['shape'] = self.df.shape
        results['columns'] = list(self.df.columns)
        results['data_types'] = self.df.dtypes.to_dict()
        results['missing_values'] = self.df.isnull().sum().to_dict()
        results['missing_percentage'] = (self.df.isnull().sum() / len(self.df) * 100).to_dict()
        results['duplicates'] = int(self.df.duplicated().sum())
        
        # Numeric columns analysis
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        results['numeric_columns'] = list(numeric_cols)
        results['numeric_stats'] = self.df[numeric_cols].describe().to_dict() if len(numeric_cols) > 0 else {}
        
        # Categorical columns analysis
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns
        results['categorical_columns'] = list(categorical_cols)
        results['categorical_stats'] = {}
        for col in categorical_cols:
            results['categorical_stats'][col] = {
                'unique_count': int(self.df[col].nunique()),
                'top_categories': self.df[col].value_counts().head(5).to_dict()
            }
        
        # Correlation analysis
        if len(numeric_cols) > 1:
            results['correlation_matrix'] = self.df[numeric_cols].corr()
        
        return results
    
    def generate_ai_insights(self, analysis_results):
        """Generate AI-like insights based on data analysis"""
        insights = []
        if not analysis_results:
            return insights
        
        # Dataset overview insights
        rows, cols = analysis_results.get('shape', (0,0))
        insights.append(f"📚 <b>Data Overview</b>: The dataset contains {rows:,} rows and {cols} columns.")
        
        # Missing values insights
        total_missing = sum(analysis_results.get('missing_values', {}).values())
        if total_missing > 0:
            insights.append(f"🕵🏼‍♂️ <b>Data Quality</b>: {total_missing:,} missing values detected across the dataset.")
        
        # Numeric columns insights
        numeric_cols = analysis_results.get('numeric_columns', [])
        if numeric_cols:
            numeric_insight = f"🔢 <b>Numeric Analysis</b>: {len(numeric_cols)} numeric columns found."
            col = numeric_cols[0]
            stats = analysis_results.get('numeric_stats', {}).get(col, {})
            if isinstance(stats, dict) and 'mean' in stats:
                try:
                    numeric_insight += f" {col} has mean {stats['mean']:.2f} and std {stats['std']:.2f}."
                except Exception:
                    numeric_insight += f" {col} stats available."
            insights.append(numeric_insight)
        
        # Categorical insights
        categorical_cols = analysis_results.get('categorical_columns', [])
        if categorical_cols:
            cat_insight = f"🗂️ <b>Categorical Analysis<b/>: {len(categorical_cols)} categorical columns identified."
            insights.append(cat_insight)
        
        # Correlation insights
        if 'correlation_matrix' in analysis_results and analysis_results.get('correlation_matrix') is not None:
            corr_matrix = analysis_results['correlation_matrix']
            high_corr_pairs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    if abs(corr_matrix.iloc[i, j]) > 0.7:
                        high_corr_pairs.append(
                            f"{corr_matrix.columns[i]} & {corr_matrix.columns[j]} ({corr_matrix.iloc[i, j]:.2f})"
                        )
            if high_corr_pairs:
                insights.append(f"👨‍👩‍👧‍👦 <b>Strong Correlations</b>: Found between {', '.join(high_corr_pairs[:3])}")
        
        # Data quality insights
        if analysis_results.get('duplicates', 0) > 0:
            insights.append(f"🔍 <b>Data Quality</b>: {analysis_results['duplicates']} duplicate rows found.")
        
        return insights

class InteractiveVisualizations:
    def __init__(self, df):
        self.df = df
    
    def create_correlation_heatmap(self):
        """Create interactive correlation heatmap"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            return None
        
        corr_matrix = self.df[numeric_cols].corr()
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='RdBu_r',
            title="Correlation Heatmap"
        )
        fig.update_layout(height=600)
        return fig
    
    def create_distribution_plots(self):
        """Create interactive distribution plots"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return None
        
        # Create subplots
        cols = min(2, len(numeric_cols))
        rows = (len(numeric_cols) + cols - 1) // cols
        
        fig = make_subplots(
            rows=rows, 
            cols=cols,
            subplot_titles=[f"Distribution of {col}" for col in numeric_cols]
        )
        
        for i, col in enumerate(numeric_cols):
            row = (i // cols) + 1
            col_num = (i % cols) + 1
            
            fig.add_trace(
                go.Histogram(x=self.df[col], name=col, nbinsx=30),
                row=row, col=col_num
            )
        
        fig.update_layout(height=300*rows, title_text="Distribution Analysis", showlegend=False)
        return fig
    
    def create_scatter_matrix(self):
        """Create interactive scatter matrix"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            return None
        
        # Take first 4 numeric columns for scatter matrix
        selected_cols = numeric_cols[:4] if len(numeric_cols) > 4 else numeric_cols
        fig = px.scatter_matrix(
            self.df[selected_cols],
            title="Scatter Matrix",
            height=800
        )
        return fig
    
    def create_time_series_plot(self):
        """Create time series plot if date column exists"""
        date_columns = self.df.select_dtypes(include=['datetime64']).columns
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        if len(date_columns) > 0 and len(numeric_cols) > 0:
            date_col = date_columns[0]
            numeric_col = numeric_cols[0]
            
            fig = px.line(
                self.df, 
                x=date_col, 
                y=numeric_col,
                title=f"{numeric_col} over Time",
                height=400
            )
            return fig
        return None
    
    def create_categorical_analysis(self):
        """Create categorical data visualizations"""
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            
            # Box plot
            fig = px.box(
                self.df, 
                x=cat_col, 
                y=num_col,
                title=f"{num_col} by {cat_col}",
                height=500
            )
            return fig
        return None

class ReportGenerator:
    def __init__(self):
        # A4 dimensions in mm (210 x 297)
        self.a4_width = 210
        self.a4_height = 297
        self.left_margin = 15
        self.right_margin = 15
        self.top_margin = 15
        self.bottom_margin = 20
        self.content_width = self.a4_width - self.left_margin - self.right_margin

    def clean_text(self, text):
        """Sanitize text so it's safe for fpdf (latin-1). Removes or replaces problematic unicode."""
        if text is None:
            return ""
        s = str(text)
        # replace bullets/emojis/dashes with ascii equivalents
        s = s.replace('•', '- ')
        s = s.replace('–', '-')
        s = s.replace('—', '-')
        # remove other emoji ranges and non-ascii characters
        s = re.sub(r'[\u2600-\u26FF\u2700-\u27BF]', '', s)  # miscellaneous symbols
        s = re.sub(r'[^\x00-\x7F]+', '', s)  # remove any remaining non-ascii
        return s

    def generate_pdf_report(self, analysis_results, insights, output_file=None):
        """
        Generate a PDF report with proper A4 formatting and margins
        """
        try:
            analysis_results = analysis_results or {}
            insights = insights or []

            if output_file is None:
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                output_path = tmp.name
                tmp.close()
            else:
                output_path = str(output_file)
                parent = Path(output_path).parent
                if not parent.exists():
                    parent.mkdir(parents=True, exist_ok=True)

            # Create PDF with A4 format and proper margins
            pdf = FPDF(orientation='P', unit='mm', format='A4')
            pdf.set_auto_page_break(auto=True, margin=self.bottom_margin)
            
            # Set margins
            pdf.set_left_margin(self.left_margin)
            pdf.set_right_margin(self.right_margin)
            pdf.set_top_margin(self.top_margin)

            # Default font settings
            default_font_family = "Arial"
            default_font_size = 11

            # Helper function to write text with proper wrapping
            def write_line(text, style='', size=None, align='L', ln=True):
                if size is None:
                    size = default_font_size
                pdf.set_font(default_font_family, style=style, size=size)
                safe_text = self.clean_text(text)
                pdf.cell(self.content_width, size/2, safe_text, ln=ln, align=align)

            def write_multiline(text, style='', size=None, line_height=6):
                if size is None:
                    size = default_font_size
                pdf.set_font(default_font_family, style=style, size=size)
                safe_text = self.clean_text(text)
                pdf.multi_cell(self.content_width, line_height, safe_text)

            # Start document
            pdf.add_page()

            # Title Page
            pdf.set_font(default_font_family, 'B', 18)
            pdf.cell(self.content_width, 15, "AI-POWERED DATA ANALYSIS REPORT", ln=True, align='C')
            pdf.ln(5)

            pdf.set_font(default_font_family, 'I', 12)
            pdf.cell(self.content_width, 8, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
            pdf.ln(15)

            # Executive Summary Section
            pdf.set_font(default_font_family, 'B', 14)
            write_line("EXECUTIVE SUMMARY", 'B', 14, 'L')
            pdf.ln(5)

            pdf.set_font(default_font_family, '', 11)
            if insights:
                for i, insight in enumerate(insights[:6], 1):
                    clean_insight = self.clean_text(insight.replace('**', ''))
                    write_multiline(f"{i}. {clean_insight}", size=11, line_height=5)
                    pdf.ln(2)
            else:
                write_multiline("No insights generated from the data analysis.", size=11, line_height=5)

            # Dataset Overview Section
            pdf.add_page()
            pdf.set_font(default_font_family, 'B', 14)
            write_line("DATASET OVERVIEW", 'B', 14, 'L')
            pdf.ln(8)

            shape = analysis_results.get('shape', (0, 0))
            missing_total = sum(analysis_results.get('missing_values', {}).values()) if analysis_results.get('missing_values') else 0
            duplicates = analysis_results.get('duplicates', 0)
            numeric_cols_count = len(analysis_results.get('numeric_columns', []))
            categorical_cols_count = len(analysis_results.get('categorical_columns', []))

            overview_data = [
                f"Total Rows: {shape[0]:,}",
                f"Total Columns: {shape[1]}",
                f"Missing Values: {missing_total:,}",
                f"Duplicate Rows: {duplicates}",
                f"Numeric Columns: {numeric_cols_count}",
                f"Categorical Columns: {categorical_cols_count}"
            ]

            pdf.set_font(default_font_family, '', 11)
            for item in overview_data:
                write_multiline(f"• {item}", size=11, line_height=6)
                pdf.ln(1)

            # Data Types Summary
            pdf.ln(5)
            pdf.set_font(default_font_family, 'B', 12)
            write_line("DATA TYPES SUMMARY", 'B', 12, 'L')
            pdf.ln(3)

            pdf.set_font(default_font_family, '', 10)
            columns = analysis_results.get('columns', [])[:10]  # Show first 10 columns
            data_types = analysis_results.get('data_types', {})
            
            for col in columns:
                dtype = str(data_types.get(col, 'Unknown'))
                # Truncate long column names
                col_display = col[:30] + "..." if len(col) > 30 else col
                write_multiline(f"• {col_display}: {dtype}", size=10, line_height=5)
                pdf.ln(1)

            # Numeric Analysis Section
            pdf.add_page()
            pdf.set_font(default_font_family, 'B', 14)
            write_line("NUMERIC ANALYSIS", 'B', 14, 'L')
            pdf.ln(5)

            numeric_cols = analysis_results.get('numeric_columns', [])[:6]  # First 6 columns
            numeric_stats = analysis_results.get('numeric_stats', {})
            
            if numeric_cols:
                pdf.set_font(default_font_family, '', 10)
                for col in numeric_cols:
                    stats = numeric_stats.get(col, {})
                    if stats:
                        try:
                            line = f"• {col}: count={stats.get('count', 'N/A')}, mean={stats.get('mean', 'N/A'):.2f}, std={stats.get('std', 'N/A'):.2f}"
                        except:
                            line = f"• {col}: Statistics available"
                    else:
                        line = f"• {col}: No statistics"
                    
                    # Truncate if too long
                    if len(line) > 80:
                        line = line[:77] + "..."
                    write_multiline(line, size=10, line_height=5)
                    pdf.ln(1)
            else:
                write_multiline("No numeric columns found in the dataset.", size=10, line_height=5)

            # Categorical Analysis Section
            pdf.ln(5)
            pdf.set_font(default_font_family, 'B', 12)
            write_line("CATEGORICAL ANALYSIS", 'B', 12, 'L')
            pdf.ln(3)

            categorical_cols = analysis_results.get('categorical_columns', [])[:4]  # First 4 columns
            categorical_stats = analysis_results.get('categorical_stats', {})
            
            if categorical_cols:
                pdf.set_font(default_font_family, '', 10)
                for col in categorical_cols:
                    stats = categorical_stats.get(col, {})
                    unique_count = stats.get('unique_count', 'N/A')
                    top_categories = stats.get('top_categories', {})
                    
                    write_multiline(f"• {col}: {unique_count} unique values", size=10, line_height=5)
                    
                    # Show top 2 categories
                    if top_categories:
                        top_items = list(top_categories.items())[:2]
                        for category, count in top_items:
                            write_multiline(f"  - {category}: {count} occurrences", size=9, line_height=4)
                    pdf.ln(1)
            else:
                write_multiline("No categorical columns found in the dataset.", size=10, line_height=5)

            # Recommendations Section
            pdf.add_page()
            pdf.set_font(default_font_family, 'B', 14)
            write_line("RECOMMENDATIONS & CONCLUSIONS", 'B', 14, 'L')
            pdf.ln(8)

            recommendations = [
                "Review columns with high missing values and consider imputation strategies",
                "Remove or investigate duplicate records to ensure data quality",
                "Analyze strong correlations for feature engineering opportunities",
                "Validate data distributions and handle outliers appropriately",
                "Consider collecting more data if the dataset is small (<1000 records)",
                "Explore categorical variables for potential grouping or encoding strategies",
                "Perform additional statistical tests based on the data characteristics",
                "Consider time-series analysis if temporal patterns are present"
            ]

            pdf.set_font(default_font_family, '', 11)
            for i, recommendation in enumerate(recommendations, 1):
                write_multiline(f"{i}. {recommendation}", size=11, line_height=6)
                pdf.ln(2)

            # Data Quality Assessment
            pdf.ln(5)
            pdf.set_font(default_font_family, 'B', 12)
            write_line("DATA QUALITY ASSESSMENT", 'B', 12, 'L')
            pdf.ln(3)

            completeness_score = 100 * (1 - (missing_total / (shape[0] * shape[1]))) if shape[0] * shape[1] > 0 else 0
            
            quality_metrics = [
                f"Completeness Score: {completeness_score:.1f}%",
                f"Duplicate Rate: {(duplicates/shape[0]*100) if shape[0] > 0 else 0:.1f}%",
                f"Data Volume: {'Large' if shape[0] > 10000 else 'Medium' if shape[0] > 1000 else 'Small'} dataset",
                f"Variable Diversity: Good mix of numeric and categorical variables" if numeric_cols_count > 0 and categorical_cols_count > 0 else "Limited variable diversity"
            ]

            pdf.set_font(default_font_family, '', 10)
            for metric in quality_metrics:
                write_multiline(f"• {metric}", size=10, line_height=5)
                pdf.ln(1)

            # Final Page - Conclusion
            pdf.add_page()
            pdf.set_font(default_font_family, 'B', 14)
            write_line("CONCLUSION", 'B', 14, 'L')
            pdf.ln(8)

            conclusion_text = f"""
This comprehensive analysis of the dataset containing {shape[0]:,} records and {shape[1]} variables 
provides valuable insights for data-driven decision making. The analysis highlights key patterns, 
data quality considerations, and opportunities for further exploration.

The dataset demonstrates {completeness_score:.1f}% completeness with {numeric_cols_count} numeric 
and {categorical_cols_count} categorical variables available for analysis. The recommendations 
provided offer actionable steps for data improvement and advanced analytical modeling.

For further analysis, consider implementing machine learning models, time-series forecasting, 
or advanced statistical techniques based on the specific business objectives.
            """

            pdf.set_font(default_font_family, '', 11)
            write_multiline(conclusion_text, size=11, line_height=6)

            # Footer on last page
            pdf.ln(10)
            pdf.set_font(default_font_family, 'I', 8)
            pdf.cell(self.content_width, 4, "Generated by AI Data Storyteller - Automated Data Analysis Tool", ln=True, align='C')

            # Save PDF
            pdf.output(output_path)
            return output_path

        except Exception as e:
            print("Error generating PDF:", e)
            traceback.print_exc()
            return None

def main():
    # Header
    st.markdown('<div class="main-header"> <b>🦾 AI - Data teller</b> </div>', unsafe_allow_html=True)
        
    # Initialize session state
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = DataAnalyzer()
    if 'analysis_done' not in st.session_state:
        st.session_state.analysis_done = False
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}
    if 'insights' not in st.session_state:
        st.session_state.insights = []
    
    # Sidebar
    
    with st.sidebar:
        st.header("Upload file 🗃️")
        uploaded_file = st.file_uploader("Select one file", type=['csv', 'xlsx'])
       
        if uploaded_file is not None:
            success, message = st.session_state.analyzer.load_data(uploaded_file)
            if success:
                st.success("✅ " + message)
                if st.button("AI Analysis 💻", type="primary", use_container_width=True):
                    with st.spinner("Performing comprehensive analysis..."):
                        st.session_state.analysis_results = st.session_state.analyzer.perform_comprehensive_analysis()
                        st.session_state.insights = st.session_state.analyzer.generate_ai_insights(st.session_state.analysis_results)
                        st.session_state.analysis_done = True
                        try:
                            st.rerun()
                        except Exception:
                            try:
                                st.experimental_rerun()
                            except Exception:
                                pass
            else:
                st.error("❌ " + message)
        
        st.markdown("---")
        st.header("⚙️ Settings")
        st.selectbox("Theme", ["Light","Eye protection", "Dark","Warm"], key="theme")
        st.selectbox("Language",["English","Hindi","Marathi","Gujarati"], key = "Language")
        st.selectbox("Brightness",["10%","20%","30%","40%","50%","60%","70%","80%","90%","100%"], key="Brightness")
        st.color_picker("🎨 Pick a background color", "#ffffff", key="bg_color")
        st.color_picker("🖋️ Pick a text color", "#000000", key="text_color")
        
    
    # Main content area with tabs
    if st.session_state.analysis_done and st.session_state.analyzer.df is not None:
        tab1, tab2, tab3, tab4 = st.tabs(["   Dataset Overview    ", "   AI Insights   ", "   Visualizations   ", "   Report   "])
        st.markdown(
    """
    <style>
    /* Tab bar */
    .stTabs [data-baseweb="tab-list"] {
        background-color:#0A090 ; /* Tab container background */
        border-radius: 15px;
        padding: 5px;
    }

    /* Individual tab */
    .stTabs [data-baseweb="tab"] {
        background-color:#B1B1B1 ; /* Inactive tab */
        color: white !important;
        border-radius: 10px;
        margin-right: 15px;
    }

    /* Active tab */
    .stTabs [aria-selected="true"] {
        background-color:#96090B  !important; /* Active tab color */
        color: black !important;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)
        with tab1:
            st.header("👩‍💻 Dataset Overview")
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Rows", f"{st.session_state.analysis_results['shape'][0]:,}")
            with col2:
                st.metric("Total Columns", st.session_state.analysis_results['shape'][1])
            with col3:
                missing_total = sum(st.session_state.analysis_results['missing_values'].values())
                st.metric("Missing Values", f"{missing_total:,}")
            with col4:
                st.metric("Duplicate Rows", st.session_state.analysis_results['duplicates'])
            
            # Data preview
            st.subheader("Data Preview")
            st.dataframe(st.session_state.analyzer.df.head(10), use_container_width=True)
            
            # Data types information
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Data Types")
                dtype_df = pd.DataFrame({
                    'Column': st.session_state.analysis_results['columns'],
                    'Data Type': [str(st.session_state.analysis_results['data_types'][col]) for col in st.session_state.analysis_results['columns']]
                })
                st.dataframe(dtype_df, use_container_width=True)
            
            with col2:
                st.subheader("Missing Values Analysis")
                missing_df = pd.DataFrame({
                    'Column': list(st.session_state.analysis_results['missing_values'].keys()),
                    'Missing Count': list(st.session_state.analysis_results['missing_values'].values()),
                    'Missing %': list(st.session_state.analysis_results['missing_percentage'].values())
                })
                st.dataframe(missing_df, use_container_width=True)
        
        with tab2:
            st.header("Data teller 💀")
            
            # Display insights with checkboxes and red bars
            for i, insight in enumerate(st.session_state.insights, 1):
                col1, col2 = st.columns([0.05, 0.95])
                with col1:
                    default_value = i in [2, 5]
                    st.checkbox("", key=f"insight_{i}", value=default_value)
                with col2:
                    st.markdown(
                        f'<div style="background-color:#f5d7d7; padding: 15px; border-left: 5px solid #de0202 ; border-radius: 10px; margin: 5px 0;">{insight}</div>',
                        unsafe_allow_html=True
                    )
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.session_state.analysis_results['numeric_columns']:
                    st.subheader("📈 Numeric Statistics")
                    numeric_stats = pd.DataFrame(st.session_state.analysis_results['numeric_stats'])
                    st.dataframe(numeric_stats, use_container_width=True)
            with col2:
                if st.session_state.analysis_results['categorical_columns']:
                    st.subheader("📝 Categorical Analysis")
                    for col in st.session_state.analysis_results['categorical_columns'][:3]:
                        st.write(f"**{col}**: {st.session_state.analysis_results['categorical_stats'][col]['unique_count']} unique values")
                        top_cats = st.session_state.analysis_results['categorical_stats'][col]['top_categories']
                        st.write("Top categories:", ", ".join([f"{k} ({v})" for k, v in list(top_cats.items())[:3]]))
        
        with tab3:
            st.header("📈 Interactive Visualizations")
            visualizer = InteractiveVisualizations(st.session_state.analyzer.df)
            viz_option = st.selectbox(
                "Choose Visualization Type",
                ["Correlation Heatmap", "Distribution Analysis", "Scatter Matrix", "Categorical Analysis", "All Visualizations"]
            )
            if viz_option == "Correlation Heatmap":
                fig = visualizer.create_correlation_heatmap()
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Need at least 2 numeric columns for correlation analysis")
            elif viz_option == "Distribution Analysis":
                fig = visualizer.create_distribution_plots()
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No numeric columns found for distribution analysis")
            elif viz_option == "Scatter Matrix":
                fig = visualizer.create_scatter_matrix()
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Need at least 2 numeric columns for scatter matrix")
            elif viz_option == "Categorical Analysis":
                fig = visualizer.create_categorical_analysis()
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Need both categorical and numeric columns for this analysis")
            elif viz_option == "All Visualizations":
                col1, col2 = st.columns(2)
                with col1:
                    fig1 = visualizer.create_correlation_heatmap()
                    if fig1:
                        st.plotly_chart(fig1, use_container_width=True)
                    fig3 = visualizer.create_distribution_plots()
                    if fig3:
                        st.plotly_chart(fig3, use_container_width=True)
                with col2:
                    fig2 = visualizer.create_scatter_matrix()
                    if fig2:
                        st.plotly_chart(fig2, use_container_width=True)
                    fig4 = visualizer.create_categorical_analysis()
                    if fig4:
                        st.plotly_chart(fig4, use_container_width=True)
        
        with tab4:
            st.header("📄 Report Generation")
            st.subheader("Executive Summary")
            st.write("Generate a comprehensive PDF report with all analysis findings.")
            report_gen = ReportGenerator()
            if st.button("📥 Generate PDF Report", type="primary"):
                with st.spinner("Generating report..."):
                    try:
                        report_path = report_gen.generate_pdf_report(
                            st.session_state.analysis_results, 
                            st.session_state.insights
                        )
                        if report_path and os.path.exists(report_path):
                            with open(report_path, "rb") as file:
                                st.download_button(
                                    label="📄 Download AI Analysis Report",
                                    data=file,
                                    file_name="ai_data_analysis_report.pdf",
                                    mime="application/pdf",
                                    type="primary"
                                )
                            st.success("✅ PDF report generated successfully!")
                            # optional: remove after offering download
                            try:
                                os.remove(report_path)
                            except Exception:
                                pass
                        else:
                            st.error("Report generation failed. No PDF produced. Check app logs/console for details.")
                    except Exception as e:
                        st.error(f"Unexpected error while generating report: {str(e)}")
                        st.text(traceback.format_exc())
            # Report preview
            st.subheader("Report Preview")
            st.write("**Key sections included in the report:**")
            st.write("✅ Executive Summary")
            st.write("✅ Dataset Overview")
            st.write("✅ Numeric Analysis")
            st.write("✅ Categorical Analysis")
            st.write("✅ Data Quality Assessment")
            st.write("✅ Recommendations & Conclusions")
            st.write("✅ Professional A4 Formatting")
    
    else:
        # Welcome screen when no data is loaded
        st.markdown("""
        <div style='text-align: center; padding: 50px;'>
            <h2> Welcome to Data teller </h2>
            <p><h3>Upload your dataset to get started with Data Telling <h3></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample data option
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("Upload Sample Data 💾", use_container_width=True):
                # Create sample data
                sample_data = {
                    'Date': pd.date_range('2023-01-01', periods=100, freq='D'),
                    'Sales': np.random.normal(1000, 200, 100).cumsum(),
                    'Customers': np.random.poisson(50, 100),
                    'Region': np.random.choice(['North', 'South', 'East', 'West'], 100),
                    'Product_Category': np.random.choice(['Electronics', 'Clothing', 'Food', 'Books'], 100),
                    'Revenue': np.random.exponential(500, 100)
                }
                sample_df = pd.DataFrame(sample_data)
                
                # Load sample data
                st.session_state.analyzer.df = sample_df
                st.session_state.analysis_results = st.session_state.analyzer.perform_comprehensive_analysis()
                st.session_state.insights = st.session_state.analyzer.generate_ai_insights(st.session_state.analysis_results)
                st.session_state.analysis_done = True
                try:
                    st.rerun()
                except Exception:
                    try:
                        st.experimental_rerun()
                    except Exception:
                        pass

if __name__ == "__main__":
    main()