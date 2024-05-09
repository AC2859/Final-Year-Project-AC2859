import serial
import pynmea2
import folium
import csv
from folium.plugins import MarkerCluster

# Initialize the map with specific coordinates and zoom level to view Bath
mymap = folium.Map(location=[51.376271, -2.36662], zoom_start=14)
marker_cluster = MarkerCluster().add_to(mymap)

# Open the serial port
ser = serial.Serial('COM4', 9600)  

# Open a CSV file to store the received data
with open('serial_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)

    # Variables to accumulate additional text and count lines
    additional_text = ""
    count_lines = []
    snr_info = ""

    # Read data from serial port and update map
    while True:
        # Read line from serial port
        line = ser.readline().decode('utf-8', errors='ignore').strip()

        try:
            # Write the received data to the CSV file
            csvwriter.writerow([line])
            
            # Check if it's a GPGGA sentence
            if line.startswith('$GPGGA'):
                try:
                    # Parse NMEA sentence
                    msg = pynmea2.parse(line)
                    
                    # Extract latitude, longitude, and altitude
                    lat = msg.latitude
                    lon = msg.longitude
                    alt = msg.altitude
                    time = msg.timestamp.strftime('%H:%M:%S')  # Extract time and format it
                    
                    # Create marker with popup content including latitude, longitude, altitude, count lines, snr info, and additional text
                    popup_content = f"Time: {time}<br>Latitude: {lat}<br>Longitude: {lon}<br>Altitude: {alt} meters<br>"
                    
                    # Include count lines in popup content
                    for count_line in count_lines:
                        popup_content += count_line + "<br>"
                    
                    # Include snr info in popup content
                    popup_content += snr_info + "<br>"
                    
                    # Include additional text in popup content
                    popup_content += additional_text
                    
                    # Add marker to the marker cluster
                    marker = folium.Marker([lat, lon], popup=popup_content)
                    marker.add_to(marker_cluster)
                    
                    # Reset additional text, count lines, and snr info
                    additional_text = ""
                    count_lines = []
                    snr_info = ""
                    
                    # Save the map as HTML file
                    mymap.save('map.html')
                except pynmea2.ParseError:
                    pass
            elif line.startswith('count'):
                # Check if the line starts with "count"
                count_lines.append(line)
                
            elif "****" in line:
                # Accumulate additional text until delimiter "****" is encountered
                additional_text += line.split("****")[0].strip() + "<br>"
        except Exception as e:
            print(f"An error occurred: {e}")
