#!/usr/bin/env python3
"""
FTA Deadly Events Visualization for New York
Creates maps showing locations of fatal transit incidents
"""

import pandas as pd
import matplotlib.pyplot as plt
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def load_fta_data():
    """Load FTA Major Safety Events data from data.transportation.gov"""
    url = "https://data.transportation.gov/resource/9ivb-8ae9.json"

    try:
        logging.info("Downloading FTA Major Safety Events data...")
        df = pd.read_json(url + "?$limit=50000")
        logging.info(f"Successfully loaded {len(df)} safety events")
        return df
    except Exception as e:
        logging.error(f"Failed to load data: {e}")
        return None

def filter_new_york_data(df):
    """Filter data for New York transit agencies"""
    logging.info("Filtering for New York transit agencies...")

    # Filter by agency names containing New York, NYC, MTA, etc.
    ny_keywords = ['NEW YORK', 'NYC', 'MTA', 'METROPOLITAN TRANSPORTATION']
    ny_data = df[df['agency'].str.upper().str.contains('|'.join(ny_keywords), na=False)]

    logging.info(f"Found {len(ny_data)} incidents in New York")
    return ny_data

def prepare_fatal_events(df):
    """Extract events with fatalities and valid coordinates"""
    logging.info("Filtering for fatal events with location data...")

    # Filter for events with fatalities
    fatal_df = df[df['total_fatalities'] > 0].copy()
    logging.info(f"Found {len(fatal_df)} fatal incidents")

    # Filter for events with valid coordinates
    fatal_df = fatal_df[fatal_df['latitude'].notna() & fatal_df['longitude'].notna()]

    # Convert to numeric
    fatal_df['latitude'] = pd.to_numeric(fatal_df['latitude'], errors='coerce')
    fatal_df['longitude'] = pd.to_numeric(fatal_df['longitude'], errors='coerce')

    # Remove any invalid coordinates
    fatal_df = fatal_df[fatal_df['latitude'].notna() & fatal_df['longitude'].notna()]

    logging.info(f"Found {len(fatal_df)} fatal incidents with valid coordinates")

    return fatal_df

def create_visualizations(df):
    """Create multiple visualizations of fatal events"""

    if len(df) == 0:
        logging.warning("No fatal events with coordinates found")
        return

    # Create figure with multiple subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    fig.suptitle('New York Transit Fatal Incidents - Location Analysis (FTA Data)',
                 fontsize=16, fontweight='bold')

    # 1. Scatter plot of all fatal incidents
    ax1 = axes[0, 0]
    scatter = ax1.scatter(df['longitude'], df['latitude'],
                         c=df['total_fatalities'],
                         s=df['total_fatalities']*100,
                         alpha=0.6, cmap='Reds', edgecolors='black', linewidth=0.5)
    ax1.set_xlabel('Longitude', fontsize=10)
    ax1.set_ylabel('Latitude', fontsize=10)
    ax1.set_title(f'Fatal Incidents by Location (n={len(df)})', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    cbar1 = plt.colorbar(scatter, ax=ax1)
    cbar1.set_label('Number of Fatalities', fontsize=9)

    # 2. Heat map style - density of incidents
    ax2 = axes[0, 1]
    hex_plot = ax2.hexbin(df['longitude'], df['latitude'],
                          gridsize=30, cmap='YlOrRd', mincnt=1)
    ax2.set_xlabel('Longitude', fontsize=10)
    ax2.set_ylabel('Latitude', fontsize=10)
    ax2.set_title('Incident Density Heatmap', fontsize=12, fontweight='bold')
    cbar2 = plt.colorbar(hex_plot, ax=ax2)
    cbar2.set_label('Number of Incidents', fontsize=9)

    # 3. Fatal incidents by event type
    ax3 = axes[1, 0]
    if 'event_type' in df.columns:
        event_colors = {'Suicide': 'purple', 'Rail Collision': 'red',
                       'Non-Rail Collision': 'orange', 'Homicide': 'darkred',
                       'Other': 'gray'}

        for event_type in df['event_type'].unique():
            if pd.notna(event_type):
                subset = df[df['event_type'] == event_type]
                color = event_colors.get(event_type, 'gray')
                ax3.scatter(subset['longitude'], subset['latitude'],
                           label=event_type, alpha=0.6, s=50, c=color, edgecolors='black', linewidth=0.5)

        ax3.set_xlabel('Longitude', fontsize=10)
        ax3.set_ylabel('Latitude', fontsize=10)
        ax3.set_title('Fatal Incidents by Event Type', fontsize=12, fontweight='bold')
        ax3.legend(fontsize=8, loc='best')
        ax3.grid(True, alpha=0.3)

    # 4. Statistics table
    ax4 = axes[1, 1]
    ax4.axis('off')

    # Calculate statistics
    stats_text = "FATAL INCIDENT STATISTICS\n" + "="*40 + "\n\n"
    stats_text += f"Total Fatal Incidents: {len(df)}\n"
    stats_text += f"Total Fatalities: {int(df['total_fatalities'].sum())}\n"
    stats_text += f"Total Injuries: {int(df['total_injuries'].sum())}\n\n"

    stats_text += "By Event Type:\n" + "-"*40 + "\n"
    if 'event_type' in df.columns:
        event_stats = df.groupby('event_type').agg({
            'total_fatalities': 'sum',
            'event_type': 'count'
        }).rename(columns={'event_type': 'incidents'})
        for idx, row in event_stats.iterrows():
            stats_text += f"{idx}: {int(row['incidents'])} incidents, {int(row['total_fatalities'])} deaths\n"

    stats_text += "\n" + "By Location Type:\n" + "-"*40 + "\n"
    if 'location_type' in df.columns:
        loc_counts = df['location_type'].value_counts().head(5)
        for loc, count in loc_counts.items():
            stats_text += f"{loc}: {count}\n"

    stats_text += "\n" + "Temporal Distribution:\n" + "-"*40 + "\n"
    if 'year' in df.columns:
        year_counts = df['year'].value_counts().sort_index()
        for year, count in year_counts.items():
            stats_text += f"{int(year)}: {count} incidents\n"

    ax4.text(0.1, 0.9, stats_text, transform=ax4.transAxes,
            fontsize=9, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    plt.tight_layout()

    # Save the figure
    output_file = '/Users/Joe/fta_deadly_events_map.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    logging.info(f"Visualization saved to: {output_file}")

    plt.show()

    return output_file

def print_deadliest_locations(df):
    """Print detailed information about deadliest locations"""
    print("\n" + "="*70)
    print("DEADLIEST LOCATIONS ANALYSIS")
    print("="*70)

    if len(df) == 0:
        print("\nNo fatal incidents with location data found.")
        return

    # Group by approximate location (round coordinates)
    df['lat_rounded'] = df['latitude'].round(3)
    df['lon_rounded'] = df['longitude'].round(3)

    location_fatalities = df.groupby(['lat_rounded', 'lon_rounded']).agg({
        'total_fatalities': 'sum',
        'incident_date': 'count',
        'event_type': lambda x: x.mode()[0] if len(x) > 0 else 'Unknown',
        'location_type': lambda x: x.mode()[0] if len(x) > 0 else 'Unknown'
    }).rename(columns={'incident_date': 'num_incidents'})

    location_fatalities = location_fatalities.sort_values('total_fatalities', ascending=False)

    print("\nTop 15 Deadliest Locations (by approximate coordinates):")
    print("-" * 70)
    print(f"{'Latitude':<12} {'Longitude':<12} {'Deaths':<8} {'Incidents':<10} {'Type':<20}")
    print("-" * 70)

    for idx, row in location_fatalities.head(15).iterrows():
        lat, lon = idx
        print(f"{lat:<12.3f} {lon:<12.3f} {int(row['total_fatalities']):<8} "
              f"{int(row['num_incidents']):<10} {str(row['event_type']):<20}")

    # Print incidents with highest single fatality count
    print("\n" + "="*70)
    print("SINGLE DEADLIEST INCIDENTS")
    print("="*70)

    deadliest = df.nlargest(10, 'total_fatalities')
    for idx, row in deadliest.iterrows():
        print(f"\nDate: {row['incident_date']}")
        print(f"Location: ({row['latitude']:.4f}, {row['longitude']:.4f})")
        print(f"Event Type: {row.get('event_type', 'Unknown')}")
        print(f"Location Type: {row.get('location_type', 'Unknown')}")
        print(f"Fatalities: {int(row['total_fatalities'])}")
        print(f"Injuries: {int(row['total_injuries'])}")
        if 'approximate_address' in row and pd.notna(row['approximate_address']):
            print(f"Address: {row['approximate_address']}")

def main():
    """Main execution function"""
    logging.info("Starting FTA Deadly Events Visualization...")

    # Load data
    df = load_fta_data()
    if df is None:
        logging.error("Cannot proceed without data")
        return

    # Filter for New York
    ny_df = filter_new_york_data(df)

    # Get fatal events with coordinates
    fatal_df = prepare_fatal_events(ny_df)

    if len(fatal_df) == 0:
        logging.error("No fatal incidents with coordinates found for New York")
        return

    # Print detailed location analysis
    print_deadliest_locations(fatal_df)

    # Create visualizations
    output_file = create_visualizations(fatal_df)

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nVisualization saved to: {output_file}")

if __name__ == "__main__":
    main()
