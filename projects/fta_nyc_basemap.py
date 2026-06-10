#!/usr/bin/env python3
"""
FTA Deadly Events on NYC Basemap
Creates an interactive map showing fatal transit incidents overlaid on NYC
"""

import pandas as pd
import folium
from folium.plugins import HeatMap, MarkerCluster
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

    # Remove any invalid coordinates and filter to NYC area (approximate bounds)
    fatal_df = fatal_df[
        (fatal_df['latitude'].notna()) &
        (fatal_df['longitude'].notna()) &
        (fatal_df['latitude'] >= 40.4) &
        (fatal_df['latitude'] <= 41.0) &
        (fatal_df['longitude'] >= -74.3) &
        (fatal_df['longitude'] <= -73.7)
    ]

    logging.info(f"Found {len(fatal_df)} fatal incidents with valid NYC coordinates")

    return fatal_df

def create_interactive_map(df):
    """Create an interactive Folium map with fatal incidents"""

    if len(df) == 0:
        logging.warning("No fatal events with coordinates found")
        return None

    # Center map on NYC
    nyc_center = [40.7128, -74.0060]

    # Create base map with multiple tile options
    m = folium.Map(
        location=nyc_center,
        zoom_start=11,
        tiles='OpenStreetMap'
    )

    # Add different basemap options
    folium.TileLayer('CartoDB positron', name='Light Map').add_to(m)
    folium.TileLayer('CartoDB dark_matter', name='Dark Map').add_to(m)

    # Color coding for event types
    event_colors = {
        'Suicide': 'purple',
        'Rail Collision': 'red',
        'Non-Rail Collision': 'orange',
        'Homicide': 'darkred',
        'Homicide not against Transit Worker': 'darkred',
        'Other': 'gray'
    }

    # Create feature groups for different event types
    feature_groups = {}
    for event_type in df['event_type'].unique():
        if pd.notna(event_type):
            feature_groups[event_type] = folium.FeatureGroup(name=event_type)

    # Add markers for each fatal incident
    for idx, row in df.iterrows():
        lat = row['latitude']
        lon = row['longitude']
        event_type = row.get('event_type', 'Unknown')
        fatalities = int(row['total_fatalities'])
        injuries = int(row['total_injuries'])
        date = row.get('incident_date', 'Unknown')
        location_type = row.get('location_type', 'Unknown')
        address = row.get('approximate_address', 'Address not available')

        # Create popup text
        popup_html = f"""
        <div style="font-family: Arial; width: 250px;">
            <h4 style="color: red; margin-bottom: 10px;">Fatal Transit Incident</h4>
            <b>Date:</b> {date}<br>
            <b>Event Type:</b> {event_type}<br>
            <b>Location Type:</b> {location_type}<br>
            <b>Fatalities:</b> {fatalities}<br>
            <b>Injuries:</b> {injuries}<br>
            <b>Address:</b> {address}<br>
            <b>Coordinates:</b> ({lat:.4f}, {lon:.4f})
        </div>
        """

        # Determine marker color and size
        color = event_colors.get(event_type, 'gray')
        radius = 5 + (fatalities * 3)  # Scale marker by fatalities

        # Create circle marker
        marker = folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            popup=folium.Popup(popup_html, max_width=300),
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.6,
            weight=2
        )

        # Add to appropriate feature group
        if event_type in feature_groups:
            marker.add_to(feature_groups[event_type])
        else:
            marker.add_to(m)

    # Add all feature groups to map
    for fg in feature_groups.values():
        fg.add_to(m)

    # Create heatmap layer
    heat_data = [[row['latitude'], row['longitude'], row['total_fatalities']]
                 for idx, row in df.iterrows()]
    heatmap = HeatMap(
        heat_data,
        name='Heatmap',
        min_opacity=0.3,
        radius=15,
        blur=20,
        gradient={0.4: 'blue', 0.6: 'yellow', 0.8: 'orange', 1.0: 'red'}
    )
    heatmap.add_to(m)

    # Add layer control
    folium.LayerControl(collapsed=False).add_to(m)

    # Add title
    title_html = '''
    <div style="position: fixed;
                top: 10px; left: 50px; width: 500px; height: 60px;
                background-color: white; border:2px solid grey; z-index:9999;
                font-size:16px; padding: 10px; opacity: 0.9;">
        <h3 style="margin: 0;">NYC Transit Fatal Incidents (FTA Data)</h3>
        <p style="margin: 5px 0 0 0; font-size: 12px;">
            Click markers for details. Toggle layers on/off.
        </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))

    return m

def print_summary(df):
    """Print summary statistics"""
    print("\n" + "="*70)
    print("NYC FATAL TRANSIT INCIDENTS SUMMARY")
    print("="*70)
    print(f"\nTotal Fatal Incidents: {len(df)}")
    print(f"Total Fatalities: {int(df['total_fatalities'].sum())}")
    print(f"Total Injuries: {int(df['total_injuries'].sum())}")

    print("\nBy Event Type:")
    print("-" * 70)
    event_summary = df.groupby('event_type').agg({
        'total_fatalities': 'sum',
        'event_type': 'count'
    }).rename(columns={'event_type': 'incidents'}).sort_values('total_fatalities', ascending=False)

    for event_type, row in event_summary.iterrows():
        print(f"  {event_type}: {int(row['incidents'])} incidents, {int(row['total_fatalities'])} deaths")

    print("\nBy Year:")
    print("-" * 70)
    df['incident_date'] = pd.to_datetime(df['incident_date'], errors='coerce')
    df['year'] = df['incident_date'].dt.year
    year_counts = df['year'].value_counts().sort_index()
    for year, count in year_counts.items():
        if pd.notna(year):
            print(f"  {int(year)}: {count} incidents")

    print("\nTop 10 Deadliest Specific Locations:")
    print("-" * 70)
    deadliest = df.nlargest(10, 'total_fatalities')[['incident_date', 'event_type',
                                                       'total_fatalities', 'latitude',
                                                       'longitude', 'approximate_address']]
    for idx, row in deadliest.iterrows():
        date = row['incident_date'].strftime('%Y-%m-%d') if pd.notna(row['incident_date']) else 'Unknown'
        print(f"  {date} | {row['event_type'][:20]:20s} | {int(row['total_fatalities'])} deaths")
        print(f"    → ({row['latitude']:.4f}, {row['longitude']:.4f}) {row.get('approximate_address', '')[:50]}")

def main():
    """Main execution function"""
    logging.info("Starting FTA NYC Fatal Events Mapping...")

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
        logging.error("No fatal incidents with coordinates found for NYC")
        return

    # Print summary
    print_summary(fatal_df)

    # Create interactive map
    logging.info("Creating interactive map...")
    map_obj = create_interactive_map(fatal_df)

    if map_obj:
        # Save map
        output_file = '/Users/Joe/fta_nyc_fatal_incidents_map.html'
        map_obj.save(output_file)
        logging.info(f"Interactive map saved to: {output_file}")

        print("\n" + "="*70)
        print("MAP CREATED SUCCESSFULLY")
        print("="*70)
        print(f"\nOpen the following file in your web browser:")
        print(f"  {output_file}")
        print("\nMap Features:")
        print("  • Click markers to see incident details")
        print("  • Toggle different event types on/off using layer control")
        print("  • Switch between different basemap styles")
        print("  • View heatmap overlay to see incident density")

if __name__ == "__main__":
    main()
