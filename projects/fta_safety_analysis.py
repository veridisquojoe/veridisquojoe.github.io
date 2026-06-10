#!/usr/bin/env python3
"""
FTA Major Safety Events Analysis for New York
Analyzes transit safety incidents from the Federal Transit Administration's open data
"""

import pandas as pd
import logging
from collections import Counter

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def load_fta_data():
    """Load FTA Major Safety Events data from data.transportation.gov"""
    # Socrata API endpoint for Major Safety Events dataset
    url = "https://data.transportation.gov/resource/9ivb-8ae9.json"

    try:
        # Load data with a reasonable limit (increase if needed)
        logging.info("Downloading FTA Major Safety Events data...")
        df = pd.read_json(url + "?$limit=50000")
        logging.info(f"Successfully loaded {len(df)} safety events")
        return df
    except Exception as e:
        logging.error(f"Failed to load data: {e}")
        return None

def explore_dataset(df):
    """Explore the dataset structure"""
    print("\n" + "="*70)
    print("DATASET OVERVIEW")
    print("="*70)
    print(f"\nTotal records: {len(df)}")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nData types:\n{df.dtypes}")
    print(f"\nFirst few rows:")
    print(df.head())
    print(f"\nMissing values:")
    print(df.isnull().sum())

def filter_new_york_data(df):
    """Filter data for New York transit agencies"""
    logging.info("Filtering for New York transit agencies...")

    # Look for state column or agency name patterns
    print("\nAvailable columns:", df.columns.tolist())

    # Check if there's a state field
    if 'state' in df.columns:
        ny_data = df[df['state'].str.upper() == 'NY']
    elif 'agency_name' in df.columns:
        # Filter by agency names containing New York, NYC, MTA, etc.
        ny_keywords = ['NEW YORK', 'NYC', 'MTA', 'METROPOLITAN TRANSPORTATION']
        ny_data = df[df['agency_name'].str.upper().str.contains('|'.join(ny_keywords), na=False)]
    else:
        # Try to find any relevant location field
        location_cols = [col for col in df.columns if 'location' in col.lower() or
                        'city' in col.lower() or 'state' in col.lower() or
                        'agency' in col.lower()]
        print(f"\nFound potential location columns: {location_cols}")

        if location_cols:
            # Try filtering on the first location column
            ny_data = df[df[location_cols[0]].astype(str).str.upper().str.contains('NEW YORK|NY|NYC|MTA', na=False)]
        else:
            logging.warning("Could not identify location field. Showing all data.")
            ny_data = df

    logging.info(f"Found {len(ny_data)} incidents in New York")
    return ny_data

def analyze_locations(df):
    """Analyze incident locations"""
    print("\n" + "="*70)
    print("LOCATION ANALYSIS - NEW YORK TRANSIT SAFETY INCIDENTS")
    print("="*70)

    # Find location-related columns
    location_cols = [col for col in df.columns if 'location' in col.lower() or
                    'city' in col.lower() or 'station' in col.lower() or
                    'line' in col.lower() or 'route' in col.lower()]

    print(f"\nLocation-related fields available: {location_cols}")

    if 'agency_name' in df.columns:
        print("\n--- Incidents by Transit Agency ---")
        agency_counts = df['agency_name'].value_counts()
        print(agency_counts.head(20))

    # Analyze other location fields
    for col in location_cols:
        if col in df.columns and df[col].notna().sum() > 0:
            print(f"\n--- Incidents by {col.title()} ---")
            location_counts = df[col].value_counts().head(20)
            print(location_counts)

    # If there are coordinate fields, show those
    coord_cols = [col for col in df.columns if 'lat' in col.lower() or
                  'lon' in col.lower() or 'coordinate' in col.lower()]
    if coord_cols:
        print(f"\nCoordinate fields found: {coord_cols}")

def analyze_incident_types(df):
    """Analyze types of safety incidents"""
    print("\n" + "="*70)
    print("INCIDENT TYPE ANALYSIS")
    print("="*70)

    # Find type-related columns
    type_cols = [col for col in df.columns if 'type' in col.lower() or
                'category' in col.lower() or 'event' in col.lower()]

    for col in type_cols:
        if col in df.columns and df[col].notna().sum() > 0:
            print(f"\n--- {col.title()} Distribution ---")
            type_counts = df[col].value_counts().head(15)
            print(type_counts)

def analyze_temporal_trends(df):
    """Analyze trends over time"""
    print("\n" + "="*70)
    print("TEMPORAL ANALYSIS")
    print("="*70)

    # Find date columns
    date_cols = [col for col in df.columns if 'date' in col.lower() or
                'time' in col.lower() or 'year' in col.lower()]

    print(f"\nDate-related fields: {date_cols}")

    for col in date_cols:
        if col in df.columns and df[col].notna().sum() > 0:
            try:
                df[col] = pd.to_datetime(df[col])
                print(f"\n--- Incidents by {col.title()} (Yearly) ---")
                yearly = df.groupby(df[col].dt.year).size()
                print(yearly)
            except:
                print(f"Could not parse {col} as date")

def main():
    """Main execution function"""
    logging.info("Starting FTA Safety Events Analysis for New York...")

    # Load data
    df = load_fta_data()
    if df is None:
        logging.error("Cannot proceed without data")
        return

    # Explore the full dataset first
    explore_dataset(df)

    # Filter for New York
    ny_df = filter_new_york_data(df)

    if len(ny_df) == 0:
        logging.warning("No New York data found. Showing guidance for manual filtering.")
        print("\nPlease review the dataset columns above and filter manually.")
        return

    # Analyze New York data
    analyze_locations(ny_df)
    analyze_incident_types(ny_df)
    analyze_temporal_trends(ny_df)

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nTotal incidents analyzed: {len(ny_df)}")

if __name__ == "__main__":
    main()
