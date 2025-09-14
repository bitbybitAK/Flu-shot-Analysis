import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

def create_county_choropleth_map():
    """
    Create choropleth map of counties colored by vaccination rate for most recent year
    """
    
    print("Loading county aggregated data...")
    df = pd.read_csv('aggregated_data/county_agg.csv')
    
    print(f"Data shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"FIPS codes available: {df['FIPS'].notna().sum()}")
    print(f"Sample FIPS codes: {df['FIPS'].head(10).tolist()}")
    
    # Filter out counties without FIPS codes
    df_with_fips = df[df['FIPS'].notna()].copy()
    print(f"Counties with FIPS codes: {len(df_with_fips)}")
    
    # Get the most recent year for each county
    most_recent_year = df_with_fips['last_year'].max()
    print(f"Most recent year in data: {most_recent_year}")
    
    # Filter for counties that have data in the most recent year
    recent_counties = df_with_fips[df_with_fips['last_year'] == most_recent_year].copy()
    print(f"Counties with data in {most_recent_year}: {len(recent_counties)}")
    
    # Sort by vaccination rate for better visualization
    recent_counties = recent_counties.sort_values('avg_vaccination_rate', ascending=False)
    
    # Create the choropleth map
    fig = go.Figure(data=go.Choropleth(
        locations=recent_counties['FIPS'],  # FIPS codes
        z=recent_counties['avg_vaccination_rate'],  # Vaccination rates
        text=recent_counties['Geography'],  # County names for hover
        locationmode='geojson-id',  # Use FIPS codes
        colorscale='RdYlGn',  # Red-Yellow-Green color scale
        reversescale=False,  # Higher values = greener
        marker_line_color='white',
        marker_line_width=0.5,
        colorbar_title="Vaccination Rate (%)",
        hovertemplate='<b>%{text}</b><br>' +
                     'FIPS: %{location}<br>' +
                     'Vaccination Rate: %{z:.1f}%<br>' +
                     'CI: %{customdata[0]:.1f}% - %{customdata[1]:.1f}%<br>' +
                     'Records: %{customdata[2]}<br>' +
                     'Years: %{customdata[3]}-%{customdata[4]}<extra></extra>',
        customdata=np.column_stack((
            recent_counties['avg_ci_lower'],
            recent_counties['avg_ci_upper'],
            recent_counties['record_count'],
            recent_counties['first_year'],
            recent_counties['last_year']
        ))
    ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': f'Flu Vaccination Rates by County - Most Recent Data<br><sub>Choropleth Map (FIPS Codes) - {len(recent_counties)} Counties</sub>',
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
    <b>Statistics:</b><br>
    Counties: {len(recent_counties):,}<br>
    Average Rate: {recent_counties['avg_vaccination_rate'].mean():.1f}%<br>
    Highest Rate: {recent_counties['avg_vaccination_rate'].max():.1f}%<br>
    Lowest Rate: {recent_counties['avg_vaccination_rate'].min():.1f}%<br>
    Data Years: {recent_counties['first_year'].min()}-{recent_counties['last_year'].max()}
    """
    
    fig.add_annotation(
        text=stats_text,
        xref="paper", yref="paper",
        x=0.02, y=0.98,
        showarrow=False,
        align="left",
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="black",
        borderwidth=1,
        font=dict(size=12)
    )
    
    return fig, recent_counties

def create_state_level_choropleth():
    """
    Create state-level choropleth map
    """
    
    print("\nCreating state-level choropleth map...")
    df = pd.read_csv('aggregated_data/county_agg.csv')
    
    # Filter counties with FIPS codes
    df_with_fips = df[df['FIPS'].notna()].copy()
    
    # Extract state FIPS (first 2 digits of county FIPS)
    df_with_fips['State_FIPS'] = df_with_fips['FIPS'].astype(str).str[:2].astype(int)
    
    # Calculate state averages
    state_avg = df_with_fips.groupby('State_FIPS').agg({
        'avg_vaccination_rate': 'mean',
        'Geography': 'count',
        'avg_ci_lower': 'mean',
        'avg_ci_upper': 'mean'
    }).reset_index()
    
    state_avg.columns = ['State_FIPS', 'avg_vaccination_rate', 'county_count', 'avg_ci_lower', 'avg_ci_upper']
    
    print(f"States with data: {len(state_avg)}")
    print(f"State FIPS range: {state_avg['State_FIPS'].min()} - {state_avg['State_FIPS'].max()}")
    
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
                     'CI: %{customdata[1]:.1f}% - %{customdata[2]:.1f}%<extra></extra>',
        customdata=np.column_stack((
            state_avg['county_count'],
            state_avg['avg_ci_lower'],
            state_avg['avg_ci_upper']
        ))
    ))
    
    fig.update_layout(
        title={
            'text': 'Flu Vaccination Rates by State<br><sub>State-Level Aggregation</sub>',
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

def create_choropleth_by_year():
    """
    Create choropleth maps for specific years using the original data
    """
    
    print("\nCreating choropleth maps by year...")
    df = pd.read_csv('Flu_shot_cleaned.csv')
    
    # Get unique years
    years = sorted(df['Season/Survey Year'].unique())
    print(f"Available years: {years}")
    
    # Get most recent year
    most_recent_year = years[-1]
    print(f"Most recent year: {most_recent_year}")
    
    # Filter for most recent year
    recent_data = df[df['Season/Survey Year'] == most_recent_year].copy()
    
    # Calculate county averages for the year
    county_avg = recent_data.groupby(['Geography', 'FIPS']).agg({
        'Estimate (%)': 'mean',
        'ci_lower': 'mean',
        'ci_upper': 'mean',
        'Season/Survey Year': 'count'
    }).reset_index()
    
    county_avg.columns = ['Geography', 'FIPS', 'avg_vaccination_rate', 'avg_ci_lower', 'avg_ci_upper', 'record_count']
    
    # Filter counties with FIPS codes
    county_avg = county_avg[county_avg['FIPS'].notna()].copy()
    
    print(f"Counties with data in {most_recent_year}: {len(county_avg)}")
    
    # Create choropleth
    fig = go.Figure(data=go.Choropleth(
        locations=county_avg['FIPS'],
        z=county_avg['avg_vaccination_rate'],
        text=county_avg['Geography'],
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
            county_avg['avg_ci_lower'],
            county_avg['avg_ci_upper'],
            county_avg['record_count']
        ))
    ))
    
    fig.update_layout(
        title={
            'text': f'Flu Vaccination Rates by County - {most_recent_year}<br><sub>Choropleth Map (FIPS Codes) - {len(county_avg)} Counties</sub>',
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
    
    return fig, county_avg

def create_choropleth_with_quantiles():
    """
    Create choropleth map with quantile-based color scaling
    """
    
    print("\nCreating choropleth with quantile-based scaling...")
    df = pd.read_csv('aggregated_data/county_agg.csv')
    
    # Filter counties with FIPS codes
    df_with_fips = df[df['FIPS'].notna()].copy()
    
    # Create quantile-based color scale
    quantiles = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    quantile_values = df_with_fips['avg_vaccination_rate'].quantile(quantiles).tolist()
    
    print(f"Quantile values: {[f'{q:.1f}%' for q in quantile_values]}")
    
    # Create custom colorscale
    colorscale = [
        [0.0, 'rgb(220, 20, 60)'],      # Dark red
        [0.2, 'rgb(255, 99, 71)'],      # Tomato
        [0.4, 'rgb(255, 165, 0)'],      # Orange
        [0.6, 'rgb(255, 255, 0)'],      # Yellow
        [0.8, 'rgb(144, 238, 144)'],    # Light green
        [1.0, 'rgb(0, 128, 0)']         # Green
    ]
    
    fig = go.Figure(data=go.Choropleth(
        locations=df_with_fips['FIPS'],
        z=df_with_fips['avg_vaccination_rate'],
        text=df_with_fips['Geography'],
        locationmode='geojson-id',
        colorscale=colorscale,
        reversescale=False,
        marker_line_color='white',
        marker_line_width=0.5,
        colorbar_title="Vaccination Rate (%)",
        hovertemplate='<b>%{text}</b><br>' +
                     'FIPS: %{location}<br>' +
                     'Vaccination Rate: %{z:.1f}%<br>' +
                     'CI: %{customdata[0]:.1f}% - %{customdata[1]:.1f}%<br>' +
                     'Records: %{customdata[2]}<extra></extra>',
        customdata=np.column_stack((
            df_with_fips['avg_ci_lower'],
            df_with_fips['avg_ci_upper'],
            df_with_fips['record_count']
        ))
    ))
    
    fig.update_layout(
        title={
            'text': 'Flu Vaccination Rates by County - Quantile-Based Scaling<br><sub>Choropleth Map (FIPS Codes)</sub>',
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
    
    return fig, df_with_fips

if __name__ == "__main__":
    print("Creating county choropleth maps...")
    
    # Create main county choropleth
    print("\n1. Creating main county choropleth map...")
    fig1, recent_data = create_county_choropleth_map()
    fig1.write_html("county_choropleth_main.html")
    print("Saved: county_choropleth_main.html")
    
    # Create state-level choropleth
    print("\n2. Creating state-level choropleth map...")
    fig2, state_data = create_state_level_choropleth()
    fig2.write_html("state_choropleth.html")
    print("Saved: state_choropleth.html")
    
    # Create choropleth by year
    print("\n3. Creating choropleth by year...")
    fig3, county_data = create_choropleth_by_year()
    fig3.write_html("county_choropleth_by_year.html")
    print("Saved: county_choropleth_by_year.html")
    
    # Create quantile-based choropleth
    print("\n4. Creating quantile-based choropleth...")
    fig4, quantile_data = create_choropleth_with_quantiles()
    fig4.write_html("county_choropleth_quantiles.html")
    print("Saved: county_choropleth_quantiles.html")
    
    # Print summary statistics
    print(f"\n�� SUMMARY:")
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
    print("  - state_choropleth.html (state-level aggregation)")
    print("  - county_choropleth_by_year.html (most recent year)")
    print("  - county_choropleth_quantiles.html (quantile-based scaling)")
    print("\nOpen these HTML files in your browser to view the interactive maps!")
