import pandas as pd
import numpy as np
import re

def load_and_clean_flu_data(file_path):
    """
    Load and clean flu vaccination data according to specifications:
    - Convert "Estimate (%)" to numeric
    - Split "95% CI (%)" into ci_lower and ci_upper columns
    - Ensure "Season/Survey Year" is integer
    - Drop rows with missing values in key columns
    """
    
    print("Loading flu vaccination data...")
    df = pd.read_csv(file_path)
    
    print(f"Original data shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst few rows:")
    print(df.head())
    
    # Convert "Estimate (%)" to numeric
    print("\nConverting 'Estimate (%)' to numeric...")
    df['Estimate (%)'] = pd.to_numeric(df['Estimate (%)'], errors='coerce')
    
    # Split "95% CI (%)" into ci_lower and ci_upper
    print("Splitting '95% CI (%)' into ci_lower and ci_upper...")
    
    def parse_ci(ci_string):
        """Parse confidence interval string like '45.2-67.8' or '45.2 - 67.8'"""
        if pd.isna(ci_string):
            return np.nan, np.nan
        
        # Remove any non-numeric characters except dots, dashes, and spaces
        ci_clean = str(ci_string).strip()
        
        # Handle different formats
        if '-' in ci_clean:
            parts = ci_clean.split('-')
            if len(parts) == 2:
                try:
                    lower = float(parts[0].strip())
                    upper = float(parts[1].strip())
                    return lower, upper
                except ValueError:
                    return np.nan, np.nan
        
        return np.nan, np.nan
    
    # Apply the parsing function
    ci_parsed = df['95% CI (%)'].apply(parse_ci)
    df['ci_lower'] = [x[0] for x in ci_parsed]
    df['ci_upper'] = [x[1] for x in ci_parsed]
    
    # Ensure "Season/Survey Year" is integer
    print("Converting 'Season/Survey Year' to integer...")
    df['Season/Survey Year'] = pd.to_numeric(df['Season/Survey Year'], errors='coerce').astype('Int64')
    
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
    
    return df_clean

if __name__ == "__main__":
    # Load and clean the data
    cleaned_data = load_and_clean_flu_data('Flu_shot.csv')
    
    # Save cleaned data
    output_file = 'Flu_shot_cleaned.csv'
    cleaned_data.to_csv(output_file, index=False)
    print(f"\nCleaned data saved to: {output_file}")
    
    # Display sample of cleaned data
    print("\nSample of cleaned data:")
    print(cleaned_data.head(10))
