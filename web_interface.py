#!/usr/bin/env python3
"""
Web Interface for Scenario Outcome Analyzer
Streamlit-based UI for easy interaction
"""

import streamlit as st
import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from scenario_analyzer import ScenarioAnalyzer, ScenarioAnalysis
from datetime import datetime
import os

# Page config
st.set_page_config(
    page_title="Scenario Outcome Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.outcome-card {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
    margin: 1rem 0;
}
.metric-card {
    background-color: #e8f4fd;
    padding: 1rem;
    border-radius: 0.5rem;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None

def create_probability_chart(outcomes):
    """Create probability visualization"""
    df = pd.DataFrame([
        {
            'Outcome': f"Outcome {i+1}",
            'Description': outcome.description[:50] + "..." if len(outcome.description) > 50 else outcome.description,
            'Probability': outcome.probability * 100,
            'Impact': outcome.impact_level,
            'Confidence': outcome.confidence_score * 100
        }
        for i, outcome in enumerate(outcomes)
    ])
    
    fig = px.bar(
        df, 
        x='Outcome', 
        y='Probability',
        color='Impact',
        hover_data=['Description', 'Confidence'],
        title="Outcome Probabilities",
        color_discrete_map={
            'Low': '#90EE90',
            'Medium': '#FFD700', 
            'High': '#FF6B6B'
        }
    )
    
    fig.update_layout(
        xaxis_title="Outcomes",
        yaxis_title="Probability (%)",
        showlegend=True
    )
    
    return fig

def create_impact_confidence_scatter(outcomes):
    """Create impact vs confidence scatter plot"""
    df = pd.DataFrame([
        {
            'Outcome': f"Outcome {i+1}",
            'Impact_Score': {'Low': 1, 'Medium': 2, 'High': 3}[outcome.impact_level],
            'Confidence': outcome.confidence_score * 100,
            'Probability': outcome.probability * 100,
            'Description': outcome.description[:30] + "..."
        }
        for i, outcome in enumerate(outcomes)
    ])
    
    fig = px.scatter(
        df,
        x='Confidence',
        y='Impact_Score',
        size='Probability',
        hover_data=['Description'],
        title="Impact vs Confidence Analysis",
        labels={'Impact_Score': 'Impact Level', 'Confidence': 'Confidence (%)'}
    )
    
    fig.update_yaxis(
        tickmode='array',
        tickvals=[1, 2, 3],
        ticktext=['Low', 'Medium', 'High']
    )
    
    return fig

def display_outcome_cards(outcomes):
    """Display outcomes as cards"""
    for i, outcome in enumerate(outcomes):
        with st.container():
            st.markdown(f"""
            <div class="outcome-card">
                <h4>🎯 Outcome {i+1}: {outcome.description}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Probability", f"{outcome.probability:.1%}")
            with col2:
                st.metric("Impact", outcome.impact_level)
            with col3:
                st.metric("Confidence", f"{outcome.confidence_score:.1%}")
            with col4:
                st.metric("Timeline", outcome.timeline)
            
            # Expandable details
            with st.expander(f"Details for Outcome {i+1}"):
                st.write("**Risk Factors:**")
                for risk in outcome.risk_factors:
                    st.write(f"⚠️ {risk}")
                
                st.write("**Opportunities:**")
                for opp in outcome.opportunities:
                    st.write(f"🎯 {opp}")

def main():
    """Main Streamlit application"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🎯 Scenario Outcome Analyzer</h1>', unsafe_allow_html=True)
    st.markdown("**Analyze situations and explore possible outcomes with AI-powered insights**")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input("OpenAI API Key (Optional)", type="password", 
                               help="Leave empty to use rule-based analysis")
        
        # Model selection
        model = st.selectbox("AI Model", 
                           ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
                           help="Choose AI model for analysis")
        
        # Analysis history
        st.header("📚 Analysis History")
        if st.session_state.analysis_history:
            for i, analysis in enumerate(reversed(st.session_state.analysis_history[-5:])):
                if st.button(f"Analysis {len(st.session_state.analysis_history)-i}", key=f"history_{i}"):
                    st.session_state.current_analysis = analysis
        else:
            st.write("No previous analyses")
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["🔍 New Analysis", "📊 Visualizations", "📋 Export"])
    
    with tab1:
        st.header("Describe Your Situation")
        
        # Input form
        with st.form("scenario_form"):
            situation = st.text_area(
                "Situation Description",
                placeholder="Describe the situation you want to analyze...",
                height=150,
                help="Provide as much detail as possible for better analysis"
            )
            
            # Additional context
            st.subheader("Additional Context (Optional)")
            col1, col2 = st.columns(2)
            
            with col1:
                industry = st.selectbox("Industry", 
                                      ["", "Technology", "Healthcare", "Finance", "Education", "Retail", "Other"])
                timeline = st.selectbox("Timeline", 
                                      ["", "Immediate", "Short-term", "Medium-term", "Long-term"])
            
            with col2:
                budget = st.selectbox("Budget Range", 
                                    ["", "Low", "Medium", "High", "Very High"])
                risk_tolerance = st.selectbox("Risk Tolerance", 
                                            ["", "Conservative", "Moderate", "Aggressive"])
            
            submitted = st.form_submit_button("🚀 Analyze Scenario", type="primary")
        
        if submitted and situation:
            with st.spinner("Analyzing scenario..."):
                # Prepare context
                context = {}
                if industry: context['industry'] = industry
                if timeline: context['timeline'] = timeline
                if budget: context['budget'] = budget
                if risk_tolerance: context['risk_tolerance'] = risk_tolerance
                
                # Initialize analyzer
                analyzer = ScenarioAnalyzer(api_key=api_key if api_key else None, model=model)
                
                # Perform analysis
                try:
                    analysis = analyzer.analyze(situation, context)
                    st.session_state.current_analysis = analysis
                    st.session_state.analysis_history.append(analysis)
                    st.success("✅ Analysis completed!")
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
        
        # Display current analysis
        if st.session_state.current_analysis:
            analysis = st.session_state.current_analysis
            
            st.header("📊 Analysis Results")
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Outcomes", len(analysis.outcomes))
            with col2:
                avg_prob = sum(o.probability for o in analysis.outcomes) / len(analysis.outcomes)
                st.metric("Avg Probability", f"{avg_prob:.1%}")
            with col3:
                high_impact = sum(1 for o in analysis.outcomes if o.impact_level == "High")
                st.metric("High Impact", high_impact)
            with col4:
                avg_confidence = sum(o.confidence_score for o in analysis.outcomes) / len(analysis.outcomes)
                st.metric("Avg Confidence", f"{avg_confidence:.1%}")
            
            # Context factors
            st.subheader("🔍 Context Factors")
            for factor in analysis.context_factors:
                st.write(f"• {factor}")
            
            # Outcomes
            st.subheader("🎯 Possible Outcomes")
            display_outcome_cards(analysis.outcomes)
            
            # Key variables
            st.subheader("🔑 Key Variables")
            for var in analysis.key_variables:
                st.write(f"• {var}")
            
            # Recommendations
            st.subheader("💡 Recommendations")
            for rec in analysis.recommendations:
                st.write(f"• {rec}")
    
    with tab2:
        if st.session_state.current_analysis:
            analysis = st.session_state.current_analysis
            
            st.header("📊 Visual Analysis")
            
            # Probability chart
            st.subheader("Outcome Probabilities")
            prob_chart = create_probability_chart(analysis.outcomes)
            st.plotly_chart(prob_chart, use_container_width=True)
            
            # Impact vs Confidence
            st.subheader("Impact vs Confidence Analysis")
            scatter_chart = create_impact_confidence_scatter(analysis.outcomes)
            st.plotly_chart(scatter_chart, use_container_width=True)
            
            # Risk/Opportunity matrix
            st.subheader("Risk & Opportunity Overview")
            all_risks = []
            all_opps = []
            for outcome in analysis.outcomes:
                all_risks.extend(outcome.risk_factors)
                all_opps.extend(outcome.opportunities)
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Top Risks:**")
                unique_risks = list(set(all_risks))[:5]
                for risk in unique_risks:
                    st.write(f"⚠️ {risk}")
            
            with col2:
                st.write("**Top Opportunities:**")
                unique_opps = list(set(all_opps))[:5]
                for opp in unique_opps:
                    st.write(f"🎯 {opp}")
        else:
            st.info("👆 Run an analysis first to see visualizations")
    
    with tab3:
        if st.session_state.current_analysis:
            analysis = st.session_state.current_analysis
            
            st.header("📋 Export Analysis")
            
            # Format options
            export_format = st.selectbox("Export Format", ["JSON", "Text Report", "CSV Summary"])
            
            if export_format == "JSON":
                json_data = json.dumps(analysis.__dict__, indent=2, default=str)
                st.download_button(
                    "📥 Download JSON",
                    json_data,
                    f"scenario_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    "application/json"
                )
                st.code(json_data, language="json")
            
            elif export_format == "Text Report":
                text_report = analysis.formatted_output()
                st.download_button(
                    "📥 Download Report",
                    text_report,
                    f"scenario_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    "text/plain"
                )
                st.text(text_report)
            
            elif export_format == "CSV Summary":
                # Create CSV data
                csv_data = []
                for i, outcome in enumerate(analysis.outcomes):
                    csv_data.append({
                        'Outcome_ID': i+1,
                        'Description': outcome.description,
                        'Probability': outcome.probability,
                        'Impact_Level': outcome.impact_level,
                        'Confidence_Score': outcome.confidence_score,
                        'Timeline': outcome.timeline,
                        'Risk_Factors': '; '.join(outcome.risk_factors),
                        'Opportunities': '; '.join(outcome.opportunities)
                    })
                
                df = pd.DataFrame(csv_data)
                csv_string = df.to_csv(index=False)
                
                st.download_button(
                    "📥 Download CSV",
                    csv_string,
                    f"scenario_outcomes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv"
                )
                st.dataframe(df)
        else:
            st.info("👆 Run an analysis first to export results")

if __name__ == "__main__":
    main()