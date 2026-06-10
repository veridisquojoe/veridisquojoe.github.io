#!/usr/bin/env python3
"""
FTA Deadly Events on NYC Basemap with Time Slider
Creates an interactive map with time slider showing fatal transit incidents over time
"""

import pandas as pd
import folium
from folium.plugins import HeatMapWithTime, TimestampedGeoJson
import logging
import json
from datetime import datetime

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

    # Convert date
    fatal_df['incident_date'] = pd.to_datetime(fatal_df['incident_date'], errors='coerce')

    # Remove any invalid coordinates and filter to NYC area (approximate bounds)
    fatal_df = fatal_df[
        (fatal_df['latitude'].notna()) &
        (fatal_df['longitude'].notna()) &
        (fatal_df['incident_date'].notna()) &
        (fatal_df['latitude'] >= 40.4) &
        (fatal_df['latitude'] <= 41.0) &
        (fatal_df['longitude'] >= -74.3) &
        (fatal_df['longitude'] <= -73.7)
    ]

    logging.info(f"Found {len(fatal_df)} fatal incidents with valid NYC coordinates and dates")

    return fatal_df

def create_time_slider_map(df):
    """Create an interactive map with time slider"""

    if len(df) == 0:
        logging.warning("No fatal events with coordinates found")
        return None

    # Sort by date
    df = df.sort_values('incident_date')

    # Center map on NYC
    nyc_center = [40.7128, -74.0060]

    # Create base map
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
        'Suicide': '#9370DB',
        'Rail Collision': '#DC143C',
        'Non-Rail Collision': '#FF8C00',
        'Homicide': '#8B0000',
        'Homicide not against Transit Worker': '#8B0000',
        'Other': '#808080'
    }

    # Prepare features for TimestampedGeoJson
    features = []

    for idx, row in df.iterrows():
        lat = row['latitude']
        lon = row['longitude']
        event_type = row.get('event_type', 'Unknown')
        fatalities = int(row['total_fatalities'])
        injuries = int(row['total_injuries'])
        date = row['incident_date']
        location_type = row.get('location_type', 'Unknown')
        address = row.get('approximate_address', 'Address not available')

        # Format date for display
        date_str = date.strftime('%Y-%m-%d')
        date_time_str = date.strftime('%Y-%m-%dT%H:%M:%S')

        # Create popup
        popup_html = f"""
        <div style="font-family: Arial; width: 250px;">
            <h4 style="color: red; margin-bottom: 10px;">Fatal Transit Incident</h4>
            <b>Date:</b> {date_str}<br>
            <b>Event Type:</b> {event_type}<br>
            <b>Location Type:</b> {location_type}<br>
            <b>Fatalities:</b> {fatalities}<br>
            <b>Injuries:</b> {injuries}<br>
            <b>Address:</b> {address}<br>
        </div>
        """

        # Determine color and size
        color = event_colors.get(event_type, '#808080')
        radius = 5 + (fatalities * 3)

        # Create GeoJSON feature
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [lon, lat]
            },
            'properties': {
                'time': date_time_str,
                'popup': popup_html,
                'icon': 'circle',
                'iconstyle': {
                    'fillColor': color,
                    'fillOpacity': 0.7,
                    'stroke': 'true',
                    'radius': radius,
                    'weight': 2,
                    'color': '#000000'
                },
                'style': {
                    'color': color,
                    'weight': 2,
                    'fillColor': color,
                    'fillOpacity': 0.7,
                    'radius': radius
                }
            }
        }

        features.append(feature)

    # Create TimestampedGeoJson
    timestamped_geojson = TimestampedGeoJson(
        {
            'type': 'FeatureCollection',
            'features': features
        },
        period='P1M',  # Period of 1 month
        duration='P1M',  # Show events for 1 month
        add_last_point=True,
        auto_play=False,
        loop=False,
        max_speed=5,
        loop_button=True,
        date_options='YYYY-MM',
        time_slider_drag_update=True
    )

    timestamped_geojson.add_to(m)

    # Create legend
    legend_html = '''
    <div style="position: fixed;
                bottom: 50px; right: 50px;
                width: 200px;
                background-color: white;
                border:2px solid grey;
                z-index:9999;
                font-size:14px;
                padding: 10px;
                opacity: 0.9;">
        <h4 style="margin: 0 0 10px 0;">Event Types</h4>
        <p style="margin: 3px 0;">
            <span style="display:inline-block; width:15px; height:15px;
                         background-color:#DC143C; border:1px solid black;"></span>
            Rail Collision
        </p>
        <p style="margin: 3px 0;">
            <span style="display:inline-block; width:15px; height:15px;
                         background-color:#9370DB; border:1px solid black;"></span>
            Suicide
        </p>
        <p style="margin: 3px 0;">
            <span style="display:inline-block; width:15px; height:15px;
                         background-color:#FF8C00; border:1px solid black;"></span>
            Non-Rail Collision
        </p>
        <p style="margin: 3px 0;">
            <span style="display:inline-block; width:15px; height:15px;
                         background-color:#8B0000; border:1px solid black;"></span>
            Homicide
        </p>
        <p style="margin: 3px 0;">
            <span style="display:inline-block; width:15px; height:15px;
                         background-color:#808080; border:1px solid black;"></span>
            Other
        </p>
        <p style="margin: 10px 0 0 0; font-size: 11px; font-style: italic;">
            Marker size = fatalities
        </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    # Add dynamic date display box
    date_display_html = '''
    <div id="date-display" style="position: fixed;
                top: 10px; left: 50px; width: 300px; height: 100px;
                background-color: white; border:3px solid #333; z-index:9999;
                font-size:16px; padding: 15px; opacity: 0.95;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
        <h3 style="margin: 0 0 10px 0; color: #333;">NYC Transit Fatal Incidents</h3>
        <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px;
                    border-left: 5px solid #DC143C;">
            <p style="margin: 0; font-size: 28px; font-weight: bold; color: #DC143C;" id="current-date">
                Loading...
            </p>
        </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(date_display_html))

    # Add title/instructions
    title_html = '''
    <div style="position: fixed;
                top: 120px; left: 50px; width: 300px; height: auto;
                background-color: white; border:2px solid grey; z-index:9999;
                font-size:14px; padding: 10px; opacity: 0.9;">
        <p style="margin: 0; font-size: 12px;">
            Use the slider at the bottom to move through time.<br>
            Click play button to animate. Click markers for details.
        </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))

    # Add JavaScript to update the date display dynamically
    date_update_script = '''
    <script>
    // Wait for the page to load
    window.addEventListener('load', function() {
        // Function to update the date display
        function updateDateDisplay() {
            // Find the time slider element (it's added by TimestampedGeoJson)
            var timeDisplay = document.querySelector('.time-slider-text');

            if (timeDisplay) {
                var dateText = timeDisplay.textContent || timeDisplay.innerText;
                var dateElement = document.getElementById('current-date');

                if (dateElement && dateText) {
                    // Format the date nicely
                    dateElement.textContent = dateText;
                }
            }
        }

        // Update initially
        setTimeout(updateDateDisplay, 1000);

        // Update periodically to catch slider changes
        setInterval(updateDateDisplay, 100);

        // Also try to attach to slider events
        setTimeout(function() {
            var slider = document.querySelector('input[type="range"]');
            if (slider) {
                slider.addEventListener('input', updateDateDisplay);
                slider.addEventListener('change', updateDateDisplay);
            }

            // Find play button and attach listener
            var playButton = document.querySelector('.leaflet-control-timecontrol button');
            if (playButton) {
                playButton.addEventListener('click', function() {
                    // Update more frequently when playing
                    var playInterval = setInterval(updateDateDisplay, 50);
                    setTimeout(function() {
                        clearInterval(playInterval);
                    }, 60000); // Stop after 1 minute
                });
            }
        }, 2000);
    });
    </script>
    '''
    m.get_root().html.add_child(folium.Element(date_update_script))

    # Add layer control
    folium.LayerControl(collapsed=False).add_to(m)

    return m

def print_temporal_summary(df):
    """Print temporal summary statistics"""
    print("\n" + "="*70)
    print("TEMPORAL ANALYSIS OF NYC FATAL TRANSIT INCIDENTS")
    print("="*70)

    df['year'] = df['incident_date'].dt.year
    df['month'] = df['incident_date'].dt.month
    df['year_month'] = df['incident_date'].dt.to_period('M')

    print(f"\nTotal Fatal Incidents: {len(df)}")
    print(f"Date Range: {df['incident_date'].min().strftime('%Y-%m-%d')} to {df['incident_date'].max().strftime('%Y-%m-%d')}")

    print("\nIncidents by Year:")
    print("-" * 70)
    year_summary = df.groupby('year').agg({
        'total_fatalities': 'sum',
        'year': 'count'
    }).rename(columns={'year': 'incidents'})

    for year, row in year_summary.iterrows():
        print(f"  {int(year)}: {int(row['incidents'])} incidents, {int(row['total_fatalities'])} deaths")

    print("\nTop 10 Deadliest Months:")
    print("-" * 70)
    month_summary = df.groupby('year_month').agg({
        'total_fatalities': 'sum',
        'year_month': 'count'
    }).rename(columns={'year_month': 'incidents'}).sort_values('total_fatalities', ascending=False)

    for period, row in month_summary.head(10).iterrows():
        print(f"  {period}: {int(row['incidents'])} incidents, {int(row['total_fatalities'])} deaths")

    print("\nIncidents by Event Type:")
    print("-" * 70)
    event_summary = df.groupby('event_type').agg({
        'total_fatalities': 'sum',
        'event_type': 'count'
    }).rename(columns={'event_type': 'incidents'}).sort_values('total_fatalities', ascending=False)

    for event_type, row in event_summary.iterrows():
        print(f"  {event_type}: {int(row['incidents'])} incidents, {int(row['total_fatalities'])} deaths")

def main():
    """Main execution function"""
    logging.info("Starting FTA NYC Fatal Events Time Slider Map...")

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

    # Print temporal summary
    print_temporal_summary(fatal_df)

    # Create time slider map
    logging.info("Creating interactive time slider map...")
    map_obj = create_time_slider_map(fatal_df)

    if map_obj:
        # Save map
        output_file = '/Users/Joe/fta_nyc_time_slider_map.html'
        map_obj.save(output_file)
        logging.info(f"Interactive time slider map saved to: {output_file}")

        print("\n" + "="*70)
        print("TIME SLIDER MAP CREATED SUCCESSFULLY")
        print("="*70)
        print(f"\nOpen the following file in your web browser:")
        print(f"  {output_file}")
        print("\nMap Features:")
        print("  • TIME SLIDER at bottom - drag to move through months/years")
        print("  • PLAY BUTTON - auto-animate through time")
        print("  • Click markers to see incident details")
        print("  • Marker size represents number of fatalities")
        print("  • Color represents event type (see legend)")
        print("  • Switch between different basemap styles")

if __name__ == "__main__":
    main()
