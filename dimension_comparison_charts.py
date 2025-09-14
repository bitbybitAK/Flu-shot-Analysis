import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

def create_dimension_comparison_charts():
    """
    Create bar charts comparing vaccination rates by Dimension (Age group, Setting)
    with highlighting for top 3 and bottom 3 categories each year
    """
    
    print("Loading dimension aggregated data...")
    df = pd.read_csv('aggregated_data/dimension_agg.csv')
    
    print(f"Data shape: {df.shape}")
    print(f"Dimension types: {df['Dimension Type'].unique()}")
    print(f"Years covered: {df['year_count'].max()}")
    
    # Create separate charts for each dimension type
    dimension_types = df['Dimension Type'].unique()
    
    for dim_type in dimension_types:
        if pd.notna(dim_type):
            print(f"\nCreating chart for: {dim_type}")
            create_dimension_type_chart(df, dim_type)
    
    # Create combined overview chart
    create_overview_chart(df)
    
    # Create year-by-year comparison
    create_yearly_comparison_chart()

def create_dimension_type_chart(df, dimension_type):
    """
    Create bar chart for a specific dimension type
    """
    
    # Filter data for this dimension type
    dim_data = df[df['Dimension Type'] == dimension_type].copy()
    
    if len(dim_data) == 0:
        print(f"No data found for {dimension_type}")
        return
    
    # Sort by vaccination rate
    dim_data = dim_data.sort_values('avg_vaccination_rate', ascending=True)
    
    # Create bar chart
    fig = go.Figure()
    
    # Color bars based on performance
    colors = []
    for i, row in dim_data.iterrows():
        if i < 3:  # Bottom 3
            colors.append('red')
        elif i >= len(dim_data) - 3:  # Top 3
            colors.append('green')
        else:
            colors.append('lightblue')
    
    # Add bars
    fig.add_trace(go.Bar(
        y=dim_data['Dimension'],
        x=dim_data['avg_vaccination_rate'],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='black', width=1)
        ),
        hovertemplate='<b>%{y}</b><br>' +
                     'Vaccination Rate: %{x:.1f}%<br>' +
                     'Records: %{customdata[0]}<br>' +
                     'Counties: %{customdata[1]}<br>' +
                     'Years: %{customdata[2]}<extra></extra>',
        customdata=np.column_stack((
            dim_data['record_count'],
            dim_data['county_count'],
            dim_data['year_count']
        )),
        name=dimension_type
    ))
    
    # Add confidence interval error bars
    fig.add_trace(go.Scatter(
        x=dim_data['avg_vaccination_rate'],
        y=dim_data['Dimension'],
        mode='markers',
        marker=dict(
            size=0,
            color='rgba(0,0,0,0)'
        ),
        error_x=dict(
            type='data',
            symmetric=False,
            array=dim_data['avg_ci_upper'] - dim_data['avg_vaccination_rate'],
            arrayminus=dim_data['avg_vaccination_rate'] - dim_data['avg_ci_lower'],
            visible=True,
            color='black',
            thickness=2
        ),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': f'Flu Vaccination Rates by {dimension_type}<br><sub>Top 3 (Green) vs Bottom 3 (Red) Categories</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        xaxis_title='Vaccination Rate (%)',
        yaxis_title=dimension_type,
        height=max(400, len(dim_data) * 30),  # Dynamic height based on number of categories
        width=1000,
        hovermode='closest',
        showlegend=False
    )
    
    # Update axes
    fig.update_xaxes(range=[0, 100])
    fig.update_yaxes(autorange="reversed")  # Reverse y-axis to show highest at top
    
    # Save chart
    filename = f"dimension_chart_{dimension_type.replace(' ', '_').replace('/', '_')}.html"
    fig.write_html(filename)
    print(f"Saved: {filename}")

def create_overview_chart(df):
    """
    Create overview chart showing all dimension types
    """
    
    print("\nCreating overview chart...")
    
    # Calculate average vaccination rate by dimension type
    overview_data = df.groupby('Dimension Type')['avg_vaccination_rate'].agg(['mean', 'count']).reset_index()
    overview_data = overview_data.sort_values('mean', ascending=True)
    
    fig = go.Figure()
    
    # Color bars
    colors = []
    for i, row in overview_data.iterrows():
        if i < 2:  # Bottom 2
            colors.append('red')
        elif i >= len(overview_data) - 2:  # Top 2
            colors.append('green')
        else:
            colors.append('lightblue')
    
    fig.add_trace(go.Bar(
        y=overview_data['Dimension Type'],
        x=overview_data['mean'],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='black', width=1)
        ),
        hovertemplate='<b>%{y}</b><br>' +
                     'Avg Vaccination Rate: %{x:.1f}%<br>' +
                     'Categories: %{customdata[0]}<extra></extra>',
        customdata=overview_data['count'],
        name='Dimension Types'
    ))
    
    fig.update_layout(
        title={
            'text': 'Flu Vaccination Rates by Dimension Type<br><sub>Overview of All Categories</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        xaxis_title='Average Vaccination Rate (%)',
        yaxis_title='Dimension Type',
        height=400,
        width=1000,
        hovermode='closest',
        showlegend=False
    )
    
    fig.update_xaxes(range=[0, 100])
    fig.update_yaxes(autorange="reversed")
    
    fig.write_html("dimension_overview.html")
    print("Saved: dimension_overview.html")

def create_yearly_comparison_chart():
    """
    Create year-by-year comparison showing top 3 and bottom 3 categories
    """
    
    print("\nCreating yearly comparison chart...")
    
    # Load the year-dimension aggregated data
    df_year = pd.read_csv('aggregated_data/year_dimension_agg.csv')
    
    # Get unique years
    years = sorted(df_year['Season/Survey Year'].unique())
    
    # Create subplots for each year
    fig = make_subplots(
        rows=len(years), 
        cols=1,
        subplot_titles=[f'Year {year}' for year in years],
        vertical_spacing=0.05
    )
    
    for i, year in enumerate(years):
        year_data = df_year[df_year['Season/Survey Year'] == year].copy()
        year_data = year_data.sort_values('avg_vaccination_rate', ascending=True)
        
        # Color bars
        colors = []
        for j, row in year_data.iterrows():
            if j < 3:  # Bottom 3
                colors.append('red')
            elif j >= len(year_data) - 3:  # Top 3
                colors.append('green')
            else:
                colors.append('lightblue')
        
        # Add bars for this year
        fig.add_trace(go.Bar(
            y=year_data['Dimension Type'],
            x=year_data['avg_vaccination_rate'],
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='black', width=1)
            ),
            hovertemplate=f'<b>Year {year}</b><br>' +
                         'Dimension: %{y}<br>' +
                         'Rate: %{x:.1f}%<br>' +
                         'Records: %{customdata[0]}<extra></extra>',
            customdata=year_data['record_count'],
            name=f'Year {year}',
            showlegend=False
        ), row=i+1, col=1)
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Flu Vaccination Rates by Dimension Type - Yearly Comparison<br><sub>Top 3 (Green) vs Bottom 3 (Red) Each Year</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        height=200 * len(years),
        width=1200,
        hovermode='closest'
    )
    
    # Update axes
    for i in range(len(years)):
        fig.update_xaxes(range=[0, 100], row=i+1, col=1)
        fig.update_yaxes(autorange="reversed", row=i+1, col=1)
    
    fig.write_html("dimension_yearly_comparison.html")
    print("Saved: dimension_yearly_comparison.html")

def create_detailed_dimension_analysis():
    """
    Create detailed analysis showing specific dimensions with confidence intervals
    """
    
    print("\nCreating detailed dimension analysis...")
    
    df = pd.read_csv('aggregated_data/dimension_agg.csv')
    
    # Focus on Age and Setting dimensions
    age_setting_data = df[df['Dimension Type'].isin(['Age', '>=18 Years', '6 Months - 17 Years', 
                                                   '18-49 Years', '50-64 Years', '>=65 Years', '18-64 Years'])]
    
    # Sort by vaccination rate
    age_setting_data = age_setting_data.sort_values('avg_vaccination_rate', ascending=True)
    
    fig = go.Figure()
    
    # Color bars
    colors = []
    for i, row in age_setting_data.iterrows():
        if i < 3:  # Bottom 3
            colors.append('red')
        elif i >= len(age_setting_data) - 3:  # Top 3
            colors.append('green')
        else:
            colors.append('lightblue')
    
    # Add bars
    fig.add_trace(go.Bar(
        y=age_setting_data['Dimension'],
        x=age_setting_data['avg_vaccination_rate'],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='black', width=1)
        ),
        hovertemplate='<b>%{y}</b><br>' +
                     'Type: %{customdata[0]}<br>' +
                     'Vaccination Rate: %{x:.1f}%<br>' +
                     'CI: %{customdata[1]:.1f}% - %{customdata[2]:.1f}%<br>' +
                     'Records: %{customdata[3]}<extra></extra>',
        customdata=np.column_stack((
            age_setting_data['Dimension Type'],
            age_setting_data['avg_ci_lower'],
            age_setting_data['avg_ci_upper'],
            age_setting_data['record_count']
        )),
        name='Age & Setting Dimensions'
    ))
    
    # Add confidence interval error bars
    fig.add_trace(go.Scatter(
        x=age_setting_data['avg_vaccination_rate'],
        y=age_setting_data['Dimension'],
        mode='markers',
        marker=dict(
            size=0,
            color='rgba(0,0,0,0)'
        ),
        error_x=dict(
            type='data',
            symmetric=False,
            array=age_setting_data['avg_ci_upper'] - age_setting_data['avg_vaccination_rate'],
            arrayminus=age_setting_data['avg_vaccination_rate'] - age_setting_data['avg_ci_lower'],
            visible=True,
            color='black',
            thickness=2
        ),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        title={
            'text': 'Detailed Flu Vaccination Analysis: Age Groups & Settings<br><sub>Top 3 (Green) vs Bottom 3 (Red) Categories</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        xaxis_title='Vaccination Rate (%)',
        yaxis_title='Dimension',
        height=max(600, len(age_setting_data) * 40),
        width=1200,
        hovermode='closest',
        showlegend=False
    )
    
    fig.update_xaxes(range=[0, 100])
    fig.update_yaxes(autorange="reversed")
    
    fig.write_html("dimension_detailed_analysis.html")
    print("Saved: dimension_detailed_analysis.html")

if __name__ == "__main__":
    print("Creating dimension comparison bar charts...")
    
    # Create all charts
    create_dimension_comparison_charts()
    create_detailed_dimension_analysis()
    
    print("\n" + "="*60)
    print("DIMENSION COMPARISON CHARTS COMPLETE!")
    print("="*60)
    print("Generated files:")
    print("  - dimension_overview.html (all dimension types)")
    print("  - dimension_detailed_analysis.html (age groups & settings)")
    print("  - dimension_yearly_comparison.html (year-by-year comparison)")
    print("  - dimension_chart_*.html (individual dimension type charts)")
    print("\nOpen these HTML files in your browser to view the interactive charts!")
