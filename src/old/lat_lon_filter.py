def filter_lat_lon(input_file, output_file, lat_min=30, lat_max=45, lon_min=115, lon_max=145, step=60):
    # Store valid lat/lon pairs
    valid_points = []
    
    # Open the input file in read mode
    with open(input_file, 'r') as infile:
        # Read each line from the input file
        for line in infile:
            try:
                # Split the line to extract latitude and longitude as float values
                lat, lon = map(float, line.split())

                # Check if the latitude and longitude are within the specified limits
                if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                    # Store the valid points in a list
                    valid_points.append((lat, lon))
                
            except ValueError:
                # Skip the line if it cannot be converted to floats (e.g., if it contains 'segment')
                continue

    # Filter the points by taking every `step`th point (e.g., every 60th point)
    reduced_points = valid_points[::step]

    # Write the sampled points to the output file
    with open(output_file, 'w') as outfile:
        for lat, lon in reduced_points:
            outfile.write(f"{lat:.6f} {lon:.6f}\n")

    print(f"Filtered and reduced data written to {output_file} ({len(reduced_points)} points)")


def main():
    # File paths
    input_file = 'data/asia-cil.txt'  # Replace with the actual input file path
    output_file = 'data/30-115--45-145-asia-cil.txt'  # The file to store the filtered data

    # Call the function to filter the lat/lon data and write to output
    filter_lat_lon(input_file, output_file)

    print(f"Filtered data written to {output_file}")


if __name__ == "__main__":
    main()
