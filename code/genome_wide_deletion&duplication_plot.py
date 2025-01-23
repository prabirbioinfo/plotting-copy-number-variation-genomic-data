import pandas as pd
import plotly.graph_objects as go
import glob
import os

# Path to the folder containing the input files
file_path = "path_to_CNV_analysis/"
file_list = glob.glob(os.path.join(file_path, "*.xls"))

# Initialize a list to store individual DataFrames
dataframes = []

# Loop through all files and process them
for file in file_list:
    # Read each file (assumes tab-delimited .xls format)
    df = pd.read_csv(file, sep="\t")
    
    # Add a 'Sample' column derived from the filename
    df['Sample'] = os.path.basename(file).replace('.xls', '')
    
    # Append the DataFrame to the list
    dataframes.append(df)

# Combine all DataFrames into a single DataFrame
combined_df = pd.concat(dataframes, ignore_index=True)

# Verify column names and process coordinates if necessary
if 'Chromosome' not in combined_df.columns and 'coordinates' in combined_df.columns:
    # Assuming 'coordinates' column exists in "Chromosome:Start-End" format
    combined_df[['Chromosome', 'Position']] = combined_df['coordinates'].str.split(':', expand=True)
    combined_df[['Start', 'End']] = combined_df['Position'].str.split('-', expand=True)
    
    # Convert 'Start' and 'End' columns to integers
    combined_df['Start'] = combined_df['Start'].astype(int)
    combined_df['End'] = combined_df['End'].astype(int)
    
    # Drop the intermediate 'Position' column
    combined_df.drop('Position', axis=1, inplace=True)

# List of unique samples
samples = combined_df['Sample'].unique()

# Create Plotly figures for deletions and duplications
fig_deletion = go.Figure()
fig_duplication = go.Figure()

# Loop through each sample to generate separate plots
for sample in samples:
    sample_df = combined_df[combined_df['Sample'] == sample]
    
    # Separate deletion and duplication data
    deletion_df = sample_df[sample_df['CNV_type'] == 'deletion']
    duplication_df = sample_df[sample_df['CNV_type'] == 'duplication']
    
    # Add scatter plot for deletions
    fig_deletion.add_trace(go.Scatter(
        x=deletion_df['Chromosome'], 
        y=deletion_df['CNV_size'],
        mode='markers',
        name=f'{sample} - Deletion',
        marker=dict(color='red'),
        hovertext=deletion_df[['Sample', 'Chromosome', 'CNV_size', 'Start', 'End']].astype(str).agg('<br>'.join, axis=1)
    ))
    
    # Add scatter plot for duplications
    fig_duplication.add_trace(go.Scatter(
        x=duplication_df['Chromosome'], 
        y=duplication_df['CNV_size'],
        mode='markers',
        name=f'{sample} - Duplication',
        marker=dict(color='blue'),
        hovertext=duplication_df[['Sample', 'Chromosome', 'CNV_size', 'Start', 'End']].astype(str).agg('<br>'.join, axis=1)
    ))

# Update layout for the deletion plot
fig_deletion.update_layout(
    title='Genome-wide CNV Size Distribution - Deletions',
    xaxis_title="Chromosome",
    yaxis_title="CNV Size (bp)",
    hovermode='closest',
    height=900,
    showlegend=True,
)

# Update layout for the duplication plot
fig_duplication.update_layout(
    title='Genome-wide CNV Size Distribution - Duplications',
    xaxis_title="Chromosome",
    yaxis_title="CNV Size (bp)",
    hovermode='closest',
    height=900,
    showlegend=True,
)

# Save the plots to separate HTML files
output_file_deletion = 'genomewide_CNV_deletion_plot.html'
output_file_duplication = 'genomewide_CNV_duplication_plot.html'
fig_deletion.write_html(output_file_deletion)
fig_duplication.write_html(output_file_duplication)

print(f"The deletion plot has been saved as {output_file_deletion}.")
print(f"The duplication plot has been saved as {output_file_duplication}.")

