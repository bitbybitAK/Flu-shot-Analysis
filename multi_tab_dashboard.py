import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from dash import Dash, html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc

# Load data once at startup
print("Loading data...")
df_original = pd.read_csv('Flu_shot_cleaned.csv')
df_county_year = pd.read_csv('aggregated_data/county_year_agg.csv')
df_county_agg = pd.read_csv('aggregated_data/county_agg.csv')
df_year_agg = pd.read_csv('aggregated_data/year_agg.csv')
df_dimension_agg = pd.read_csv('aggregated_data/dimension_agg.csv')

# Initialize Dash app with Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Flu Vaccination Analysis Dashboard"

# Define color schemes
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e', 
    'success': '#2ca02c',
    'danger': '#d62728',
    'warning': '#ff7f0e',
    'info': '#17becf',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

def create_national_trends_tab():
    """Create National Trends tab content"""
    # National average line with CI
    fig = go.Figure()
    
    # Add CI band
    fig.add_trace(go.Scatter(
        x=df_year_agg['Season/Survey Year'].tolist() + df_year_agg['Season/Survey Year'].tolist()[::-1],
        y=df_year_agg['avg_ci_upper'].tolist() + df_year_agg['avg_ci_lower'].tolist()[::-1],
        fill='toself',
        fillcolor='rgba(31, 119, 180, 0.15)',
        line=dict(color='rgba(31,119,180,0)'),
        name='95% CI',
        hoverinfo='skip'
    ))
    
    # Add main line
    fig.add_trace(go.Scatter(
        x=df_year_agg['Season/Survey Year'],
        y=df_year_agg['avg_vaccination_rate'],
        mode='lines+markers',
        name='National Average',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=6),
        hovertemplate='Year: %{x}<br>Rate: %{y:.1f}%<br>CI: %{customdata[0]:.1f}% - %{customdata[1]:.1f}%<extra></extra>',
        customdata=np.column_stack((df_year_agg['avg_ci_lower'], df_year_agg['avg_ci_upper']))
    ))
    
    # Add policy markers
    policy_years = {2009: 'H1N1 Pandemic', 2018: 'Coverage Expansion', 2020: 'COVID-19', 2021: 'COVID-19 Vaccines'}
    for year, label in policy_years.items():
        if year in df_year_agg['Season/Survey Year'].values:
            val = df_year_agg[df_year_agg['Season/Survey Year'] == year]['avg_vaccination_rate'].iloc[0]
            fig.add_trace(go.Scatter(
                x=[year], y=[val],
                mode='markers',
                marker=dict(color=COLORS['danger'], size=10, symbol='star'),
                name=f'{year}: {label}',
                hovertemplate=f'<b>{year}</b><br>{label}<br>Rate: %{{y:.1f}}%<extra></extra>'
            ))
    
    fig.update_layout(
        title='U.S. Flu Vaccination Trends (2009-2023)',
        xaxis_title='Year',
        yaxis_title='Vaccination Rate (%)',
        height=500,
        showlegend=True
    )
    
    return dbc.Card([
        dbc.CardBody([
            html.H4("National Trends", className="card-title"),
            html.P("This chart shows the overall U.S. flu vaccination rate trends over time, with 95% confidence intervals and key policy events marked."),
            dcc.Graph(figure=fig)
        ])
    ])

def create_county_comparisons_tab():
    """Create County Comparisons tab content"""
    # Top 10 vs Bottom 10 counties
    county_avg = df_county_agg.sort_values('avg_vaccination_rate', ascending=False)
    top_10 = county_avg.head(10)
    bottom_10 = county_avg.tail(10)
    
    fig = go.Figure()
    
    # Top 10 counties
    fig.add_trace(go.Bar(
        y=top_10['Geography'],
        x=top_10['avg_vaccination_rate'],
        orientation='h',
        name='Top 10 Counties',
        marker_color=COLORS['success'],
        hovertemplate='<b>%{y}</b><br>Rate: %{x:.1f}%<br>CI: %{customdata[0]:.1f}% - %{customdata[1]:.1f}%<extra></extra>',
        customdata=np.column_stack((top_10['avg_ci_lower'], top_10['avg_ci_upper']))
    ))
    
    # Bottom 10 counties
    fig.add_trace(go.Bar(
        y=bottom_10['Geography'],
        x=bottom_10['avg_vaccination_rate'],
        orientation='h',
        name='Bottom 10 Counties',
        marker_color=COLORS['danger'],
        hovertemplate='<b>%{y}</b><br>Rate: %{x:.1f}%<br>CI: %{customdata[0]:.1f}% - %{customdata[1]:.1f}%<extra></extra>',
        customdata=np.column_stack((bottom_10['avg_ci_lower'], bottom_10['avg_ci_upper']))
    ))
    
    fig.update_layout(
        title='Top 10 vs Bottom 10 Performing Counties',
        xaxis_title='Average Vaccination Rate (%)',
        yaxis_title='County',
        height=600,
        barmode='group'
    )
    
    return dbc.Card([
        dbc.CardBody([
            html.H4("County Performance Comparison", className="card-title"),
            html.P("This chart compares the highest and lowest performing counties by average vaccination rate, highlighting the significant disparities across regions."),
            dcc.Graph(figure=fig)
        ])
    ])

def create_demographic_disparities_tab():
    """Create Demographic Disparities tab content"""
    # Age group analysis
    age_data = df_dimension_agg[df_dimension_agg['Dimension Type'] == 'Age'].sort_values('avg_vaccination_rate', ascending=True)
    
    fig = go.Figure()
    
    colors = []
    for i, row in age_data.iterrows():
        if i < 3:  # Bottom 3
            colors.append(COLORS['danger'])
        elif i >= len(age_data) - 3:  # Top 3
            colors.append(COLORS['success'])
        else:
            colors.append(COLORS['info'])
    
    fig.add_trace(go.Bar(
        y=age_data['Dimension'],
        x=age_data['avg_vaccination_rate'],
        orientation='h',
        marker_color=colors,
        hovertemplate='<b>%{y}</b><br>Rate: %{x:.1f}%<br>CI: %{customdata[0]:.1f}% - %{customdata[1]:.1f}%<extra></extra>',
        customdata=np.column_stack((age_data['avg_ci_lower'], age_data['avg_ci_upper']))
    ))
    
    fig.update_layout(
        title='Vaccination Rates by Age Group',
        xaxis_title='Vaccination Rate (%)',
        yaxis_title='Age Group',
        height=500
    )
    
    return dbc.Card([
        dbc.CardBody([
            html.H4("Demographic Disparities", className="card-title"),
            html.P("This chart shows vaccination rates across different age groups, with top performers in green and bottom performers in red."),
            dcc.Graph(figure=fig)
        ])
    ])

def create_settings_tab():
    """Create Settings of Vaccination tab content"""
    # Setting analysis
    setting_data = df_dimension_agg[df_dimension_agg['Dimension Type'].isin(['>=18 Years', '18-49 Years', '50-64 Years', '>=65 Years'])]
    setting_data = setting_data[setting_data['Dimension'].isin(['Medical Setting', 'Non-Medical Setting', 'Pharmacy/Store', 'Workplace'])]
    
    # Pivot for grouped bar chart
    pivot_data = setting_data.pivot_table(
        index='Dimension Type', 
        columns='Dimension', 
        values='avg_vaccination_rate', 
        aggfunc='mean'
    ).fillna(0)
    
    fig = go.Figure()
    
    settings = ['Medical Setting', 'Non-Medical Setting', 'Pharmacy/Store', 'Workplace']
    colors = [COLORS['success'], COLORS['info'], COLORS['warning'], COLORS['danger']]
    
    for setting, color in zip(settings, colors):
        if setting in pivot_data.columns:
            fig.add_trace(go.Bar(
                x=pivot_data.index,
                y=pivot_data[setting],
                name=setting,
                marker_color=color,
                hovertemplate=f'<b>{setting}</b><br>Age Group: %{{x}}<br>Rate: %{{y:.1f}}%<extra></extra>'
            ))
    
    fig.update_layout(
        title='Vaccination Rates by Setting and Age Group',
        xaxis_title='Age Group',
        yaxis_title='Vaccination Rate (%)',
        height=500,
        barmode='group'
    )
    
    return dbc.Card([
        dbc.CardBody([
            html.H4("Vaccination Settings Analysis", className="card-title"),
            html.P("This chart shows how vaccination rates vary by setting type across different age groups, revealing significant disparities between medical and workplace settings."),
            dcc.Graph(figure=fig)
        ])
    ])

def create_outlier_analysis_tab():
    """Create Outlier Analysis tab content"""
    # Sample size vs rate scatter plot
    recent_data = df_county_year[df_county_year['Season/Survey Year'] == df_county_year['Season/Survey Year'].max()]
    
    # Calculate outlier scores
    rate_q25 = recent_data['avg_vaccination_rate'].quantile(0.25)
    rate_q75 = recent_data['avg_vaccination_rate'].quantile(0.75)
    ci_width_q75 = (recent_data['avg_ci_upper'] - recent_data['avg_ci_lower']).quantile(0.75)
    
    recent_data['is_outlier'] = (
        (recent_data['avg_vaccination_rate'] < rate_q25) | 
        (recent_data['avg_vaccination_rate'] > rate_q75) |
        ((recent_data['avg_ci_upper'] - recent_data['avg_ci_lower']) > ci_width_q75)
    )
    
    fig = go.Figure()
    
    # Normal points
    normal_data = recent_data[~recent_data['is_outlier']]
    fig.add_trace(go.Scatter(
        x=normal_data['record_count'],
        y=normal_data['avg_vaccination_rate'],
        mode='markers',
        name='Normal',
        marker=dict(color=COLORS['primary'], size=6, opacity=0.6),
        hovertemplate='<b>%{text}</b><br>Sample: %{x}<br>Rate: %{y:.1f}%<extra></extra>',
        text=normal_data['Geography']
    ))
    
    # Outlier points
    outlier_data = recent_data[recent_data['is_outlier']]
    fig.add_trace(go.Scatter(
        x=outlier_data['record_count'],
        y=outlier_data['avg_vaccination_rate'],
        mode='markers',
        name='Outliers',
        marker=dict(color=COLORS['danger'], size=8),
        hovertemplate='<b>%{text}</b><br>Sample: %{x}<br>Rate: %{y:.1f}%<extra></extra>',
        text=outlier_data['Geography']
    ))
    
    # Label top 5 outliers
    top_outliers = outlier_data.nlargest(5, 'avg_vaccination_rate')
    for _, row in top_outliers.iterrows():
        fig.add_annotation(
            x=row['record_count'], y=row['avg_vaccination_rate'],
            text=row['Geography'],
            showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1,
            arrowcolor='black', bgcolor='rgba(255,255,255,0.9)',
            ax=20, ay=-20, font=dict(size=10)
        )
    
    fig.update_layout(
        title='Sample Size vs Vaccination Rate (Outlier Analysis)',
        xaxis_title='Sample Size (Records)',
        yaxis_title='Vaccination Rate (%)',
        height=500
    )
    
    return dbc.Card([
        dbc.CardBody([
            html.H4("Outlier Analysis", className="card-title"),
            html.P("This scatter plot identifies counties with unusual vaccination rates or wide confidence intervals, helping to identify data quality issues or exceptional cases."),
            dcc.Graph(figure=fig)
        ])
    ])

# App layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Flu Vaccination Analysis Dashboard", className="text-center mb-4"),
            html.P("Comprehensive analysis of flu vaccination trends, disparities, and patterns across U.S. counties (2009-2023)", 
                   className="text-center text-muted mb-4")
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Tabs([
                dbc.Tab(create_national_trends_tab(), label="National Trends", tab_id="national"),
                dbc.Tab(create_county_comparisons_tab(), label="County Comparisons", tab_id="counties"),
                dbc.Tab(create_demographic_disparities_tab(), label="Demographic Disparities", tab_id="demographics"),
                dbc.Tab(create_settings_tab(), label="Vaccination Settings", tab_id="settings"),
                dbc.Tab(create_outlier_analysis_tab(), label="Outlier Analysis", tab_id="outliers")
            ])
        ])
    ])
], fluid=True)

if __name__ == '__main__':
    print("Starting dashboard server...")
    print("Open your browser to: http://localhost:8050")
    app.run(host='0.0.0.0', port=8050, debug=False)
