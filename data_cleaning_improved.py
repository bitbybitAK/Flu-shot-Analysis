import pandas as pd
import numpy as np
import re

def load_and_clean_flu_data(file_path):
    """
    Load and clean flu vaccination data according to specifications:
    - Convert "Estimate (%)" to numeric
    - Split "95% CI (%)" into ci_lower and ci_upper columns
    - Ensure "Season/Survey Year" is integer (extract first year from ranges like "2009-10")
    - Drop rows with missing values in key columns
    """
    
    print("Loading flu vaccination data...")
    df = pd.read_csv(file_path)
    
    print(f"Original data shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Convert "Estimate (%)" to numeric
    print("\nConverting 'Estimate (%)' to numeric...")
    df['Estimate (%)'] = pd.to_numeric(df['Estimate (%)'], errors='coerce')
    
    # Split "95% CI (%)" into ci_lower and ci_upper
    print("Splitting '95% CI (%)' into ci_lower and ci_upper...")
    
    def parse_ci(ci_string):
        """Parse confidence interval string like '43.9 to 47.2' or '40.2 to 75.2 ‡'"""
        if pd.isna(ci_string):
            return np.nan, np.nan
        
        ci_clean = str(ci_string).strip()
        
        # Handle "to" format and remove special characters like ‡
        if ' to ' in ci_clean:
            parts = ci_clean.split(' to ')
            if len(parts) == 2:
                try:
                    lower = float(parts[0].strip())
                    upper = float(parts[1].strip().replace('‡', '').strip())
                    return lower, upper
                except ValueError:
                    return np.nan, np.nan
        
        return np.nan, np.nan
    
    # Apply the parsing function
    ci_parsed = df['95% CI (%)'].apply(parse_ci)
    df['ci_lower'] = [x[0] for x in ci_parsed]
    df['ci_upper'] = [x[1] for x in ci_parsed]
    
    # Convert "Season/Survey Year" to integer (extract first year from ranges)
    print("Converting 'Season/Survey Year' to integer...")
    
    def extract_year(year_string):
        """Extract first year from strings like '2009-10' or '2018'"""
        if pd.isna(year_string):
            return np.nan
        
        year_str = str(year_string).strip()
        
        # If it's a range like "2009-10", take the first year
        if '-' in year_str and len(year_str) > 4:
            try:
                return int(year_str.split('-')[0])
            except ValueError:
                return np.nan
        
        # If it's already a single year
        try:
            return int(year_str)
        except ValueError:
            return np.nan
    
    df['Season/Survey Year'] = df['Season/Survey Year'].apply(extract_year)
    
    # Identify key columns for missing value check
    key_columns = ['Estimate (%)', 'ci_lower', 'ci_upper', 'Season/Survey Year']
    
    # Check for missing values before dropping
    print(f"\nMissing values in key columns before cleaning:")
    for col in key_columns:
        missing_count = df[col].isna().sum()
        print(f"  {col}: {missing_count} missing values")
    
    # Drop rows with missing values in key columns
    print("\nDropping rows with missing values in key columns...")
    initial_rows = len(df)
    df_clean = df.dropna(subset=key_columns)
    final_rows = len(df_clean)
    dropped_rows = initial_rows - final_rows
    
    print(f"Dropped {dropped_rows} rows ({dropped_rows/initial_rows*100:.1f}% of data)")
    print(f"Final data shape: {df_clean.shape}")
    
    # Display summary statistics
    print("\nSummary statistics for cleaned data:")
    print(df_clean[['Estimate (%)', 'ci_lower', 'ci_upper', 'Season/Survey Year']].describe())
    
    # Check data types
    print("\nData types after cleaning:")
    print(df_clean.dtypes)
    
    # Show sample of cleaned data
    print("\nSample of cleaned data:")
    print(df_clean[['Geography', 'Season/Survey Year', 'Estimate (%)', 'ci_lower', 'ci_upper']].head(10))
    
    return df_clean

if __name__ == "__main__":
    # Load and clean the data
    cleaned_data = load_and_clean_flu_data('Flu_shot.csv')
    
    # Save cleaned data
    output_file = 'Flu_shot_cleaned.csv'
    cleaned_data.to_csv(output_file, index=False)
    print(f"\nCleaned data saved to: {output_file}")
    
    # Additional analysis
    print(f"\nData summary:")
    print(f"Total records: {len(cleaned_data)}")
    print(f"Unique counties: {cleaned_data['Geography'].nunique()}")
    print(f"Year range: {cleaned_data['Season/Survey Year'].min()} - {cleaned_data['Season/Survey Year'].max()}")
    print(f"Average vaccination rate: {cleaned_data['Estimate (%)'].mean():.1f}%")
