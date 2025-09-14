import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

def create_county_choropleth_map():
    """
    Create choropleth map of counties colored by vaccination rate for most recent year
    """
    
    print("Loading county-year aggregated data...")
    df = pd.read_csv('aggregated_data/county_year_agg.csv')
    
    print(f"Data shape: {df.shape}")
    print(f"Years available: {sorted(df['Season/Survey Year'].unique())}")
    
    # Get the most recent year
    most_recent_year = df['Season/Survey Year'].max()
    print(f"Most recent year: {most_recent_year}")
    
    # Filter data for most recent year
    recent_data = df[df['Season/Survey Year'] == most_recent_year].copy()
    print(f"Counties in {most_recent_year}: {len(recent_data)}")
    
    # Check FIPS codes
    print(f"FIPS codes available: {recent_data['FIPS'].notna().sum()}")
    print(f"Sample FIPS codes: {recent_data['FIPS'].head(10).tolist()}")
    
    # Create the choropleth map
    fig = go.Figure(data=go.Choropleth(
        locations=recent_data['FIPS'],  # FIPS codes
        z=recent_data['avg_vaccination_rate'],  # Vaccination rates
        text=recent_data['Geography'],  # County names for hover
        locationmode='geojson-id',  # Use FIPS codes
        colorscale='RdYlGn',  # Red-Yellow-Green color scale
        reversescale=False,  # Higher values = greener
        marker_line_color='white',
        marker_line_width=0.5,
        colorbar_title="Vaccination Rate (%)",
        hovertemplate='<b>%{text}</b><br>' +
                     'FIPS: %{location}<br>' +
                     'Vaccination Rate: %{z:.1f}%<br>' +
                     'Year: ' + str(most_recent_year) + '<br>' +
                     'Records: %{customdata[0]}<extra></extra>',
        customdata=recent_data['record_count']
    ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': f'Flu Vaccination Rates by County - {most_recent_year}<br><sub>Choropleth Map (FIPS Codes)</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        geo=dict(
            scope='usa',
            projection=go.layout.geo.Projection(type='albers usa'),
            showlakes=True,
            lakecolor='rgb(255, 255, 255)',
            showland=True,
            landcolor='rgb(217, 217, 217)',
            showocean=True,
            oceancolor='rgb(230, 245, 255)',
            showrivers=True,
            rivercolor='rgb(255, 255, 255)',
            showcoastlines=True,
            coastlinecolor='rgb(255, 255, 255)',
            countrycolor='rgb(255, 255, 255)',
            countrywidth=0.5,
            subunitcolor='rgb(255, 255, 255)',
            subunitwidth=0.5
        ),
        width=1200,
        height=700,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    # Add statistics text
    stats_text = f"""
    <b>Statistics for {most_recent_year}:</b><br>
    Counties: {len(recent_data):,}<br>
    Average Rate: {recent_data['avg_vaccination_rate'].mean():.1f}%<br>
    Highest Rate: {recent_data['avg_vaccination_rate'].max():.1f}%<br>
    Lowest Rate: {recent_data['avg_vaccination_rate'].min():.1f}%
    """
    
    fig.add_annotation(
        text=stats_text,
        xref="paper", yref="paper",
        x=0.02, y=0.98,
        showarrow=False,
        align="left",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="black",
        borderwidth=1
    )
    
    return fig, recent_data

def create_multi_year_choropleth():
    """
    Create choropleth maps for multiple recent years
    """
    
    print("\nCreating multi-year choropleth maps...")
    df = pd.read_csv('aggregated_data/county_year_agg.csv')
    
    # Get recent years (last 5 years with data)
    recent_years = sorted(df['Season/Survey Year'].unique())[-5:]
    print(f"Recent years: {recent_years}")
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=[f'Year {year}' for year in recent_years],
        specs=[[{"type": "choropleth"} for _ in range(3)] for _ in range(2)]
    )
    
    for i, year in enumerate(recent_years):
        year_data = df[df['Season/Survey Year'] == year].copy()
        
        if len(year_data) > 0:
            row = (i // 3) + 1
            col = (i % 3) + 1
            
            fig.add_trace(go.Choropleth(
                locations=year_data['FIPS'],
                z=year_data['avg_vaccination_rate'],
                text=year_data['Geography'],
                locationmode='geojson-id',
                colorscale='RdYlGn',
                reversescale=False,
                marker_line_color='white',
                marker_line_width=0.3,
                colorbar_title="Rate (%)",
                showscale=(i == 0),  # Only show colorbar for first subplot
                hovertemplate='<b>%{text}</b><br>' +
                             'Rate: %{z:.1f}%<br>' +
                             'Year: ' + str(year) + '<extra></extra>'
            ), row=row, col=col)
    
    fig.update_layout(
        title={
            'text': 'Flu Vaccination Rates by County - Recent Years<br><sub>Multi-Year Comparison</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        geo=dict(
            scope='usa',
            projection=go.layout.geo.Projection(type='albers usa'),
            showlakes=True,
            lakecolor='rgb(255, 255, 255)',
            showland=True,
            landcolor='rgb(217, 217, 217)',
            showocean=True,
            oceancolor='rgb(230, 245, 255)',
            showrivers=True,
            rivercolor='rgb(255, 255, 255)',
            showcoastlines=True,
            coastlinecolor='rgb(255, 255, 255)',
            countrycolor='rgb(255, 255, 255)',
            countrywidth=0.5,
            subunitcolor='rgb(255, 255, 255)',
            subunitwidth=0.5
        ),
        width=1400,
        height=800,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    return fig

def create_state_level_choropleth():
    """
    Create state-level choropleth map
    """
    
    print("\nCreating state-level choropleth map...")
    df = pd.read_csv('aggregated_data/county_year_agg.csv')
    
    # Get most recent year
    most_recent_year = df['Season/Survey Year'].max()
    recent_data = df[df['Season/Survey Year'] == most_recent_year].copy()
    
    # Extract state FIPS (first 2 digits of county FIPS)
    recent_data['State_FIPS'] = recent_data['FIPS'].astype(str).str[:2].astype(int)
    
    # Calculate state averages
    state_avg = recent_data.groupby('State_FIPS').agg({
        'avg_vaccination_rate': 'mean',
        'Geography': 'count'
    }).reset_index()
    
    state_avg.columns = ['State_FIPS', 'avg_vaccination_rate', 'county_count']
    
    print(f"States with data: {len(state_avg)}")
    
    # Create state choropleth
    fig = go.Figure(data=go.Choropleth(
        locations=state_avg['State_FIPS'],
        z=state_avg['avg_vaccination_rate'],
        locationmode='USA-states',
        colorscale='RdYlGn',
        reversescale=False,
        marker_line_color='white',
        marker_line_width=1,
        colorbar_title="Vaccination Rate (%)",
        hovertemplate='<b>State FIPS: %{location}</b><br>' +
                     'Vaccination Rate: %{z:.1f}%<br>' +
                     'Counties: %{customdata[0]}<br>' +
                     'Year: ' + str(most_recent_year) + '<extra></extra>',
        customdata=state_avg['county_count']
    ))
    
    fig.update_layout(
        title={
            'text': f'Flu Vaccination Rates by State - {most_recent_year}<br><sub>State-Level Aggregation</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        geo=dict(
            scope='usa',
            projection=go.layout.geo.Projection(type='albers usa'),
            showlakes=True,
            lakecolor='rgb(255, 255, 255)',
            showland=True,
            landcolor='rgb(217, 217, 217)',
            showocean=True,
            oceancolor='rgb(230, 245, 255)',
            showrivers=True,
            rivercolor='rgb(255, 255, 255)',
            showcoastlines=True,
            coastlinecolor='rgb(255, 255, 255)',
            countrycolor='rgb(255, 255, 255)',
            countrywidth=0.5,
            subunitcolor='rgb(255, 255, 255)',
            subunitwidth=0.5
        ),
        width=1200,
        height=700,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    return fig, state_avg

def create_choropleth_with_confidence_intervals():
    """
    Create choropleth map with confidence interval information
    """
    
    print("\nCreating choropleth with confidence intervals...")
    df = pd.read_csv('aggregated_data/county_year_agg.csv')
    
    # Get most recent year
    most_recent_year = df['Season/Survey Year'].max()
    recent_data = df[df['Season/Survey Year'] == most_recent_year].copy()
    
    # Create choropleth with confidence interval info in hover
    fig = go.Figure(data=go.Choropleth(
        locations=recent_data['FIPS'],
        z=recent_data['avg_vaccination_rate'],
        text=recent_data['Geography'],
        locationmode='geojson-id',
        colorscale='RdYlGn',
        reversescale=False,
        marker_line_color='white',
        marker_line_width=0.5,
        colorbar_title="Vaccination Rate (%)",
        hovertemplate='<b>%{text}</b><br>' +
                     'FIPS: %{location}<br>' +
                     'Vaccination Rate: %{z:.1f}%<br>' +
                     'CI: %{customdata[0]:.1f}% - %{customdata[1]:.1f}%<br>' +
                     'Records: %{customdata[2]}<br>' +
                     'Year: ' + str(most_recent_year) + '<extra></extra>',
        customdata=np.column_stack((
            recent_data['avg_ci_lower'],
            recent_data['avg_ci_upper'],
            recent_data['record_count']
        ))
    ))
    
    fig.update_layout(
        title={
            'text': f'Flu Vaccination Rates by County - {most_recent_year}<br><sub>With 95% Confidence Intervals in Hover</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        geo=dict(
            scope='usa',
            projection=go.layout.geo.Projection(type='albers usa'),
            showlakes=True,
            lakecolor='rgb(255, 255, 255)',
            showland=True,
            landcolor='rgb(217, 217, 217)',
            showocean=True,
            oceancolor='rgb(230, 245, 255)',
            showrivers=True,
            rivercolor='rgb(255, 255, 255)',
            showcoastlines=True,
            coastlinecolor='rgb(255, 255, 255)',
            countrycolor='rgb(255, 255, 255)',
            countrywidth=0.5,
            subunitcolor='rgb(255, 255, 255)',
            subunitwidth=0.5
        ),
        width=1200,
        height=700,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    return fig

if __name__ == "__main__":
    print("Creating county choropleth maps...")
    
    # Create main county choropleth
    print("\n1. Creating main county choropleth map...")
    fig1, recent_data = create_county_choropleth_map()
    fig1.write_html("county_choropleth_main.html")
    print("Saved: county_choropleth_main.html")
    
    # Create multi-year comparison
    print("\n2. Creating multi-year choropleth maps...")
    try:
        from plotly.subplots import make_subplots
        fig2 = create_multi_year_choropleth()
        fig2.write_html("county_choropleth_multi_year.html")
        print("Saved: county_choropleth_multi_year.html")
    except Exception as e:
        print(f"Multi-year map creation failed: {e}")
    
    # Create state-level choropleth
    print("\n3. Creating state-level choropleth map...")
    fig3, state_data = create_state_level_choropleth()
    fig3.write_html("state_choropleth.html")
    print("Saved: state_choropleth.html")
    
    # Create choropleth with confidence intervals
    print("\n4. Creating choropleth with confidence intervals...")
    fig4 = create_choropleth_with_confidence_intervals()
    fig4.write_html("county_choropleth_with_ci.html")
    print("Saved: county_choropleth_with_ci.html")
    
    # Print summary statistics
    print(f"\n📊 SUMMARY FOR {recent_data['Season/Survey Year'].iloc[0]}:")
    print(f"   Counties mapped: {len(recent_data):,}")
    print(f"   Average vaccination rate: {recent_data['avg_vaccination_rate'].mean():.1f}%")
    print(f"   Highest rate: {recent_data['avg_vaccination_rate'].max():.1f}%")
    print(f"   Lowest rate: {recent_data['avg_vaccination_rate'].min():.1f}%")
    print(f"   States represented: {recent_data['FIPS'].astype(str).str[:2].nunique()}")
    
    print("\n" + "="*60)
    print("CHOROPLETH MAPS COMPLETE!")
    print("="*60)
    print("Generated files:")
    print("  - county_choropleth_main.html (main county map)")
    print("  - county_choropleth_with_ci.html (with confidence intervals)")
    print("  - state_choropleth.html (state-level aggregation)")
    print("  - county_choropleth_multi_year.html (multi-year comparison)")
    print("\nOpen these HTML files in your browser to view the interactive maps!")
