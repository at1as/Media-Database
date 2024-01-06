# Script to prepare JSON data files to be imported into AirTable as CSV

import pandas as pd
from datetime import datetime

media_types = ['movie', 'series', 'standup']

for media_type in media_types:

    # Load the JSON file into a pandas DataFrame
    df = pd.read_json(f'_data/{media_type}_data.json')
    
    # Swap rows and columns such that every row is a movie
    df_transposed = df.transpose()
    
    # Reorder the columns
    if media_type == 'movie' or media_type == 'standup':
        top_precedence_cols = ["title", "rating", "year", "genre", "description", "director", "stars", ]
    else:
        top_precedence_cols = ["title", "rating", "year", "genre", "description", "creator", "stars", ]
    
    desired_column_order = top_precedence_cols + [col for col in df_transposed.columns if col not in top_precedence_cols]
    df_transposed = df_transposed[desired_column_order]
    
    # Define a function to remove '[' and ']' characters from a specific field
    def remove_brackets(data):
        if isinstance(data, str):
            return data.replace('[', '').replace(']', '').replace('"', '')
        if isinstance(data, list):
            return ', '.join(map(str, data)).replace('[', '').replace(']', '').replace('"', '')
        return data
    
    if media_type == 'movie' or media_type == 'standup':
        cleanup_columns = ['genre', 'languages', 'stars', 'director']
    else:
        cleanup_columns = ['genre', 'languages', 'stars', 'creator']
    
    for k in cleanup_columns:
        # Apply the function to the specified column
        df_transposed[k] = df_transposed[k].apply(remove_brackets)
    
    # Get the current date and time for the filename suffix
    current_datetime = datetime.now().strftime('%Y_%m_%d-%H_%M')
    
    # Construct the output filename with the timestamp
    output_filename = f'{media_type}_csv_{current_datetime}.csv'
    
    # Save the subset to the CSV file
    df_transposed.to_csv(output_filename, index=False)

