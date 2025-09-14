import pandas as pd
import numpy as np

def aggregate_flu_data(file_path):
    """
    Aggregate flu vaccination data by:
    1. County (Geography)
    2. Year (Season/Survey Year) 
    3. Dimension Type (Age, Setting, etc.)
    """
    
    print("Loading cleaned flu vaccination data...")
    df = pd.read_csv(file_path)
    
    print(f"Original data shape: {df.shape}")
    print(f"Available columns: {list(df.columns)}")
    
    # Check unique dimension types
    print(f"\nUnique Dimension Types:")
    print(df['Dimension Type'].value_counts())
    
    # Check unique dimensions within each type
    print(f"\nSample dimensions by type:")
    for dim_type in df['Dimension Type'].unique():
        if pd.notna(dim_type):
            sample_dims = df[df['Dimension Type'] == dim_type]['Dimension'].unique()[:5]
            print(f"  {dim_type}: {list(sample_dims)}")
    
    # 1. AGGREGATE BY COUNTY
    print("\n" + "="*50)
    print("1. AGGREGATING BY COUNTY")
    print("="*50)
    
    county_agg = df.groupby('Geography').agg({
        'Estimate (%)': ['mean', 'median', 'std', 'min', 'max', 'count'],
        'ci_lower': 'mean',
        'ci_upper': 'mean',
        'Season/Survey Year': ['min', 'max'],
        'FIPS': 'first'
    }).round(2)
    
    # Flatten column names
    county_agg.columns = ['_'.join(col).strip() for col in county_agg.columns]
    county_agg = county_agg.rename(columns={
        'Estimate (%)_mean': 'avg_vaccination_rate',
        'Estimate (%)_median': 'median_vaccination_rate',
        'Estimate (%)_std': 'std_vaccination_rate',
        'Estimate (%)_min': 'min_vaccination_rate',
        'Estimate (%)_max': 'max_vaccination_rate',
        'Estimate (%)_count': 'record_count',
        'ci_lower_mean': 'avg_ci_lower',
        'ci_upper_mean': 'avg_ci_upper',
        'Season/Survey Year_min': 'first_year',
        'Season/Survey Year_max': 'last_year',
        'FIPS_first': 'FIPS'
    })
    
    county_agg = county_agg.reset_index()
    county_agg = county_agg.sort_values('avg_vaccination_rate', ascending=False)
    
    print(f"County aggregation: {len(county_agg)} counties")
    print("Top 10 counties by average vaccination rate:")
    print(county_agg[['Geography', 'avg_vaccination_rate', 'record_count']].head(10))
    
    # 2. AGGREGATE BY YEAR
    print("\n" + "="*50)
    print("2. AGGREGATING BY YEAR")
    print("="*50)
    
    year_agg = df.groupby('Season/Survey Year').agg({
        'Estimate (%)': ['mean', 'median', 'std', 'min', 'max', 'count'],
        'ci_lower': 'mean',
        'ci_upper': 'mean',
        'Geography': 'nunique'
    }).round(2)
    
    # Flatten column names
    year_agg.columns = ['_'.join(col).strip() for col in year_agg.columns]
    year_agg = year_agg.rename(columns={
        'Estimate (%)_mean': 'avg_vaccination_rate',
        'Estimate (%)_median': 'median_vaccination_rate',
        'Estimate (%)_std': 'std_vaccination_rate',
        'Estimate (%)_min': 'min_vaccination_rate',
        'Estimate (%)_max': 'max_vaccination_rate',
        'Estimate (%)_count': 'record_count',
        'ci_lower_mean': 'avg_ci_lower',
        'ci_upper_mean': 'avg_ci_upper',
        'Geography_nunique': 'county_count'
    })
    
    year_agg = year_agg.reset_index()
    year_agg = year_agg.sort_values('Season/Survey Year')
    
    print(f"Year aggregation: {len(year_agg)} years")
    print("Yearly trends:")
    print(year_agg[['Season/Survey Year', 'avg_vaccination_rate', 'county_count', 'record_count']])
    
    # 3. AGGREGATE BY DIMENSION TYPE
    print("\n" + "="*50)
    print("3. AGGREGATING BY DIMENSION TYPE")
    print("="*50)
    
    # First, aggregate by dimension type
    dim_type_agg = df.groupby('Dimension Type').agg({
        'Estimate (%)': ['mean', 'median', 'std', 'min', 'max', 'count'],
        'ci_lower': 'mean',
        'ci_upper': 'mean',
        'Geography': 'nunique',
        'Season/Survey Year': 'nunique'
    }).round(2)
    
    # Flatten column names
    dim_type_agg.columns = ['_'.join(col).strip() for col in dim_type_agg.columns]
    dim_type_agg = dim_type_agg.rename(columns={
        'Estimate (%)_mean': 'avg_vaccination_rate',
        'Estimate (%)_median': 'median_vaccination_rate',
        'Estimate (%)_std': 'std_vaccination_rate',
        'Estimate (%)_min': 'min_vaccination_rate',
        'Estimate (%)_max': 'max_vaccination_rate',
        'Estimate (%)_count': 'record_count',
        'ci_lower_mean': 'avg_ci_lower',
        'ci_upper_mean': 'avg_ci_upper',
        'Geography_nunique': 'county_count',
        'Season/Survey Year_nunique': 'year_count'
    })
    
    dim_type_agg = dim_type_agg.reset_index()
    dim_type_agg = dim_type_agg.sort_values('avg_vaccination_rate', ascending=False)
    
    print(f"Dimension type aggregation: {len(dim_type_agg)} dimension types")
    print("Vaccination rates by dimension type:")
    print(dim_type_agg[['Dimension Type', 'avg_vaccination_rate', 'record_count']])
    
    # 4. AGGREGATE BY DIMENSION (specific categories within each type)
    print("\n" + "="*50)
    print("4. AGGREGATING BY SPECIFIC DIMENSIONS")
    print("="*50)
    
    dimension_agg = df.groupby(['Dimension Type', 'Dimension']).agg({
        'Estimate (%)': ['mean', 'median', 'std', 'min', 'max', 'count'],
        'ci_lower': 'mean',
        'ci_upper': 'mean',
        'Geography': 'nunique',
        'Season/Survey Year': 'nunique'
    }).round(2)
    
    # Flatten column names
    dimension_agg.columns = ['_'.join(col).strip() for col in dimension_agg.columns]
    dimension_agg = dimension_agg.rename(columns={
        'Estimate (%)_mean': 'avg_vaccination_rate',
        'Estimate (%)_median': 'median_vaccination_rate',
        'Estimate (%)_std': 'std_vaccination_rate',
        'Estimate (%)_min': 'min_vaccination_rate',
        'Estimate (%)_max': 'max_vaccination_rate',
        'Estimate (%)_count': 'record_count',
        'ci_lower_mean': 'avg_ci_lower',
        'ci_upper_mean': 'avg_ci_upper',
        'Geography_nunique': 'county_count',
        'Season/Survey Year_nunique': 'year_count'
    })
    
    dimension_agg = dimension_agg.reset_index()
    dimension_agg = dimension_agg.sort_values(['Dimension Type', 'avg_vaccination_rate'], ascending=[True, False])
    
    print(f"Specific dimension aggregation: {len(dimension_agg)} dimension combinations")
    
    # Show top dimensions by vaccination rate for each type
    for dim_type in dimension_agg['Dimension Type'].unique():
        if pd.notna(dim_type):
            top_dims = dimension_agg[dimension_agg['Dimension Type'] == dim_type].head(5)
            print(f"\nTop 5 {dim_type} dimensions by vaccination rate:")
            print(top_dims[['Dimension', 'avg_vaccination_rate', 'record_count']].to_string(index=False))
    
    # 5. CREATE COMBINED AGGREGATIONS FOR VISUALIZATIONS
    print("\n" + "="*50)
    print("5. CREATING COMBINED AGGREGATIONS FOR VISUALIZATIONS")
    print("="*50)
    
    # County-Year aggregation
    county_year_agg = df.groupby(['Geography', 'Season/Survey Year']).agg({
        'Estimate (%)': ['mean', 'count'],
        'ci_lower': 'mean',
        'ci_upper': 'mean'
    }).round(2)
    
    county_year_agg.columns = ['_'.join(col).strip() for col in county_year_agg.columns]
    county_year_agg = county_year_agg.rename(columns={
        'Estimate (%)_mean': 'avg_vaccination_rate',
        'Estimate (%)_count': 'record_count',
        'ci_lower_mean': 'avg_ci_lower',
        'ci_upper_mean': 'avg_ci_upper'
    })
    county_year_agg = county_year_agg.reset_index()
    
    # Year-Dimension Type aggregation
    year_dim_agg = df.groupby(['Season/Survey Year', 'Dimension Type']).agg({
        'Estimate (%)': ['mean', 'count'],
        'ci_lower': 'mean',
        'ci_upper': 'mean'
    }).round(2)
    
    year_dim_agg.columns = ['_'.join(col).strip() for col in year_dim_agg.columns]
    year_dim_agg = year_dim_agg.rename(columns={
        'Estimate (%)_mean': 'avg_vaccination_rate',
        'Estimate (%)_count': 'record_count',
        'ci_lower_mean': 'avg_ci_lower',
        'ci_upper_mean': 'avg_ci_upper'
    })
    year_dim_agg = year_dim_agg.reset_index()
    
    print(f"County-Year aggregation: {len(county_year_agg)} combinations")
    print(f"Year-Dimension Type aggregation: {len(year_dim_agg)} combinations")
    
    return {
        'county_agg': county_agg,
        'year_agg': year_agg,
        'dimension_type_agg': dim_type_agg,
        'dimension_agg': dimension_agg,
        'county_year_agg': county_year_agg,
        'year_dimension_agg': year_dim_agg
    }

def save_aggregated_data(aggregations, output_dir='aggregated_data'):
    """Save all aggregated DataFrames to CSV files"""
    import os
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Save each aggregation
    for name, df in aggregations.items():
        filename = f"{output_dir}/{name}.csv"
        df.to_csv(filename, index=False)
        print(f"Saved {filename}: {len(df)} records")
    
    print(f"\nAll aggregated data saved to '{output_dir}' directory")

if __name__ == "__main__":
    # Load and aggregate the data
    aggregations = aggregate_flu_data('Flu_shot_cleaned.csv')
    
    # Save aggregated data
    save_aggregated_data(aggregations)
    
    print("\n" + "="*60)
    print("AGGREGATION COMPLETE - READY FOR VISUALIZATIONS")
    print("="*60)
    print("Available aggregated datasets:")
    for name, df in aggregations.items():
        print(f"  - {name}: {len(df)} records")
