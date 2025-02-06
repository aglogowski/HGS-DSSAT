def extract_tables(file_path):
    tables = []  # List to store tables
    current_table = []  # Temp list to store rows of the current table

    with open(file_path, 'r') as file:
        for line in file:
            line = line.rstrip()  # Strip trailing whitespace
            if line.startswith('@'):  # Start of a new table
                if current_table:  # Save the current table if one exists
                    
                    tables.append(current_table)
                line=line[1:].split()
                current_table = [line]  # Start a new table without '@'
            elif line == '':  # Empty line signals the end of the current table
                if current_table:  # Save the current table
                    tables.append(current_table)
                    current_table = []  # Reset for the next table
            else:
                if current_table:  # Add data to the current table
                    line=line.split()
                    current_table.append(line)

    if current_table:  # Append the last table if the file doesn't end with an empty line
        tables.append(current_table)

    return tables
