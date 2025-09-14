import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

def create_county_trends_chart():
    """
    Create line chart showing flu vaccination rates by year for each county
    with confidence intervals as shaded areas
    """
    
    print("Loading county-year aggregated data...")
    df = pd.read_csv('aggregated_data/county_year_agg.csv')
    
    print(f"Data shape: {df.shape}")
    print(f"Years covered: {df['Season/Survey Year'].min()} - {df['Season/Survey Year'].max()}")
    print(f"Number of counties: {df['Geography'].nunique()}")
    
    # Get unique years and counties
    years = sorted(df['Season/Survey Year'].unique())
    counties = df['Geography'].unique()
    
    print(f"Years: {years}")
    print(f"Sample counties: {counties[:10]}")
    
    # Create the main line chart
    fig = go.Figure()
    
    # Use a predefined color palette
    colors = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
        '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5',
        '#c49c94', '#f7b6d3', '#c7c7c7', '#dbdb8d', '#9edae5'
    ]
    
    # Add lines for each county (limit to first 50 for performance)
    counties_to_plot = counties[:50]  # Limit to first 50 counties for better performance
    
    for i, county in enumerate(counties_to_plot):
        county_data = df[df['Geography'] == county].sort_values('Season/Survey Year')
        
        if len(county_data) > 1:  # Only plot counties with multiple data points
            color = colors[i % len(colors)]
            
            # Add the main line
            fig.add_trace(go.Scatter(
                x=county_data['Season/Survey Year'],
                y=county_data['avg_vaccination_rate'],
                mode='lines+markers',
                name=county,
                line=dict(color=color, width=2),
                marker=dict(size=4),
                hovertemplate=f'<b>{county}</b><br>' +
                             'Year: %{x}<br>' +
                             'Vaccination Rate: %{y:.1f}%<br>' +
                             'CI: %{customdata[0]:.1f}% - %{customdata[1]:.1f}%<br>' +
                             'Records: %{customdata[2]}<extra></extra>',
                customdata=np.column_stack((
                    county_data['avg_ci_lower'],
                    county_data['avg_ci_upper'],
                    county_data['record_count']
                )),
                showlegend=True
            ))
            
            # Add confidence interval as shaded area
            fig.add_trace(go.Scatter(
                x=county_data['Season/Survey Year'].tolist() + county_data['Season/Survey Year'].tolist()[::-1],
                y=county_data['avg_ci_upper'].tolist() + county_data['avg_ci_lower'].tolist()[::-1],
                fill='tonexty' if i > 0 else 'tozeroy',
                fillcolor=color.replace('rgb', 'rgba').replace(')', ', 0.1)'),
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip",
                showlegend=False,
                name=f'{county} CI'
            ))
    
    # Calculate national average for reference line
    national_avg = df.groupby('Season/Survey Year')['avg_vaccination_rate'].mean().reset_index()
    
    # Add national average line
    fig.add_trace(go.Scatter(
        x=national_avg['Season/Survey Year'],
        y=national_avg['avg_vaccination_rate'],
        mode='lines+markers',
        name='National Average',
        line=dict(color='red', width=4, dash='dash'),
        marker=dict(size=6),
        hovertemplate='<b>National Average</b><br>' +
                     'Year: %{x}<br>' +
                     'Vaccination Rate: %{y:.1f}%<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Flu Vaccination Rates by County Over Time (First 50 Counties)<br><sub>With 95% Confidence Intervals</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Year',
        yaxis_title='Vaccination Rate (%)',
        hovermode='closest',
        width=1200,
        height=700,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        margin=dict(r=200)  # Make room for legend
    )
    
    # Update axes
    fig.update_xaxes(
        title_font=dict(size=14),
        tickfont=dict(size=12),
        dtick=1  # Show every year
    )
    
    fig.update_yaxes(
        title_font=dict(size=14),
        tickfont=dict(size=12),
        range=[0, 100]  # Set y-axis range to 0-100%
    )
    
    return fig

def create_simplified_county_trends():
    """
    Create a simplified version showing only top/bottom performing counties
    to avoid overcrowding
    """
    
    print("\nCreating simplified county trends chart...")
    df = pd.read_csv('aggregated_data/county_year_agg.csv')
    
    # Calculate average vaccination rate by county
    county_avg = df.groupby('Geography')['avg_vaccination_rate'].mean().reset_index()
    county_avg = county_avg.sort_values('avg_vaccination_rate', ascending=False)
    
    # Select top 10 and bottom 10 counties
    top_counties = county_avg.head(10)['Geography'].tolist()
    bottom_counties = county_avg.tail(10)['Geography'].tolist()
    selected_counties = top_counties + bottom_counties
    
    print(f"Top 10 counties: {top_counties}")
    print(f"Bottom 10 counties: {bottom_counties}")
    
    # Filter data for selected counties
    df_selected = df[df['Geography'].isin(selected_counties)]
    
    fig = go.Figure()
    
    # Color counties based on performance
    for county in selected_counties:
        county_data = df_selected[df_selected['Geography'] == county].sort_values('Season/Survey Year')
        
        if len(county_data) > 1:
            # Color: green for top performers, red for bottom performers
            color = 'green' if county in top_counties else 'red'
            line_style = 'solid' if county in top_counties else 'dash'
            
            fig.add_trace(go.Scatter(
                x=county_data['Season/Survey Year'],
                y=county_data['avg_vaccination_rate'],
                mode='lines+markers',
                name=f"{county} ({'Top' if county in top_counties else 'Bottom'})",
                line=dict(color=color, width=3, dash=line_style),
                marker=dict(size=5),
                hovertemplate=f'<b>{county}</b><br>' +
                             'Year: %{x}<br>' +
                             'Vaccination Rate: %{y:.1f}%<br>' +
                             'CI: %{customdata[0]:.1f}% - %{customdata[1]:.1f}%<extra></extra>',
                customdata=np.column_stack((
                    county_data['avg_ci_lower'],
                    county_data['avg_ci_upper']
                ))
            ))
            
            # Add confidence interval
            fig.add_trace(go.Scatter(
                x=county_data['Season/Survey Year'].tolist() + county_data['Season/Survey Year'].tolist()[::-1],
                y=county_data['avg_ci_upper'].tolist() + county_data['avg_ci_lower'].tolist()[::-1],
                fill='tonexty',
                fillcolor=f'rgba(0, 255, 0, 0.1)' if county in top_counties else 'rgba(255, 0, 0, 0.1)',
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip",
                showlegend=False,
                name=f'{county} CI'
            ))
    
    # Add national average
    national_avg = df.groupby('Season/Survey Year')['avg_vaccination_rate'].mean().reset_index()
    fig.add_trace(go.Scatter(
        x=national_avg['Season/Survey Year'],
        y=national_avg['avg_vaccination_rate'],
        mode='lines+markers',
        name='National Average',
        line=dict(color='blue', width=4, dash='dot'),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title={
            'text': 'Flu Vaccination Rates: Top 10 vs Bottom 10 Counties<br><sub>With 95% Confidence Intervals</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title='Year',
        yaxis_title='Vaccination Rate (%)',
        hovermode='closest',
        width=1200,
        height=700,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        margin=dict(r=250)
    )
    
    fig.update_xaxes(dtick=1)
    fig.update_yaxes(range=[0, 100])
    
    return fig

def create_regional_trends():
    """
    Create trends by grouping counties into regions
    """
    
    print("\nCreating regional trends chart...")
    df = pd.read_csv('aggregated_data/county_year_agg.csv')
    
    # Simple regional grouping based on county names (this is a simplified approach)
    # In a real analysis, you'd use proper state/region mapping
    def get_region(county_name):
        if any(state in county_name for state in ['California', 'Los Angeles', 'San Francisco', 'San Diego']):
            return 'West Coast'
        elif any(state in county_name for state in ['New York', 'Connecticut', 'Massachusetts', 'New Jersey']):
            return 'Northeast'
        elif any(state in county_name for state in ['Texas', 'Florida', 'Georgia', 'North Carolina']):
            return 'South'
        elif any(state in county_name for state in ['Illinois', 'Michigan', 'Ohio', 'Wisconsin']):
            return 'Midwest'
        else:
            return 'Other'
    
    df['Region'] = df['Geography'].apply(get_region)
    
    # Calculate regional averages
    regional_avg = df.groupby(['Region', 'Season/Survey Year'])['avg_vaccination_rate'].mean().reset_index()
    
    fig = go.Figure()
    
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    
    for i, region in enumerate(regional_avg['Region'].unique()):
        region_data = regional_avg[regional_avg['Region'] == region].sort_values('Season/Survey Year')
        
        fig.add_trace(go.Scatter(
            x=region_data['Season/Survey Year'],
            y=region_data['avg_vaccination_rate'],
            mode='lines+markers',
            name=region,
            line=dict(color=colors[i % len(colors)], width=3),
            marker=dict(size=6),
            hovertemplate=f'<b>{region}</b><br>' +
                         'Year: %{x}<br>' +
                         'Vaccination Rate: %{y:.1f}%<extra></extra>'
        ))
    
    fig.update_layout(
        title={
            'text': 'Flu Vaccination Rates by Region Over Time',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title='Year',
        yaxis_title='Vaccination Rate (%)',
        hovermode='closest',
        width=1200,
        height=600
    )
    
    fig.update_xaxes(dtick=1)
    fig.update_yaxes(range=[0, 100])
    
    return fig

def create_state_level_trends():
    """
    Create trends at state level by aggregating counties
    """
    
    print("\nCreating state-level trends chart...")
    df = pd.read_csv('aggregated_data/county_year_agg.csv')
    
    # Extract state from county name (simplified approach)
    def extract_state(county_name):
        # This is a simplified approach - in practice you'd use proper FIPS codes
        if 'California' in county_name or 'Los Angeles' in county_name:
            return 'California'
        elif 'Texas' in county_name:
            return 'Texas'
        elif 'Florida' in county_name:
            return 'Florida'
        elif 'New York' in county_name:
            return 'New York'
        elif 'Connecticut' in county_name:
            return 'Connecticut'
        elif 'Massachusetts' in county_name:
            return 'Massachusetts'
        else:
            return 'Other States'
    
    df['State'] = df['Geography'].apply(extract_state)
    
    # Calculate state averages
    state_avg = df.groupby(['State', 'Season/Survey Year'])['avg_vaccination_rate'].mean().reset_index()
    
    fig = go.Figure()
    
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
    
    for i, state in enumerate(state_avg['State'].unique()):
        state_data = state_avg[state_avg['State'] == state].sort_values('Season/Survey Year')
        
        if len(state_data) > 1:  # Only plot states with multiple data points
            fig.add_trace(go.Scatter(
                x=state_data['Season/Survey Year'],
                y=state_data['avg_vaccination_rate'],
                mode='lines+markers',
                name=state,
                line=dict(color=colors[i % len(colors)], width=3),
                marker=dict(size=6),
                hovertemplate=f'<b>{state}</b><br>' +
                             'Year: %{x}<br>' +
                             'Vaccination Rate: %{y:.1f}%<extra></extra>'
            ))
    
    fig.update_layout(
        title={
            'text': 'Flu Vaccination Rates by State Over Time',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title='Year',
        yaxis_title='Vaccination Rate (%)',
        hovermode='closest',
        width=1200,
        height=600
    )
    
    fig.update_xaxes(dtick=1)
    fig.update_yaxes(range=[0, 100])
    
    return fig

if __name__ == "__main__":
    print("Creating flu vaccination trend visualizations...")
    
    # Create the main comprehensive chart
    print("\n1. Creating comprehensive county trends chart...")
    fig1 = create_county_trends_chart()
    fig1.write_html("county_trends_comprehensive.html")
    print("Saved: county_trends_comprehensive.html")
    
    # Create simplified chart
    print("\n2. Creating simplified county trends chart...")
    fig2 = create_simplified_county_trends()
    fig2.write_html("county_trends_simplified.html")
    print("Saved: county_trends_simplified.html")
    
    # Create regional trends
    print("\n3. Creating regional trends chart...")
    fig3 = create_regional_trends()
    fig3.write_html("regional_trends.html")
    print("Saved: regional_trends.html")
    
    # Create state trends
    print("\n4. Creating state-level trends chart...")
    fig4 = create_state_level_trends()
    fig4.write_html("state_trends.html")
    print("Saved: state_trends.html")
    
    print("\n" + "="*60)
    print("VISUALIZATION COMPLETE!")
    print("="*60)
    print("Generated files:")
    print("  - county_trends_comprehensive.html (first 50 counties)")
    print("  - county_trends_simplified.html (top/bottom 10 counties)")
    print("  - regional_trends.html (regional groupings)")
    print("  - state_trends.html (state-level trends)")
    print("\nOpen these HTML files in your browser to view the interactive charts!")
