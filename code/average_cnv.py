import pandas as pd
import glob
import os
import seaborn as sns
import matplotlib.pyplot as plt

# Path to the folder containing the input files
file_path = "/path_to_CNV_analysis/" 
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

# Check if the dataframes list is empty
if not dataframes:
    print("No data frames were added. Please check the files and the format.")
else:
    # Combine all DataFrames into a single DataFrame
    combined_df = pd.concat(dataframes, ignore_index=True)

    # Extract Chromosome, Start, and End information from the 'coordinates' column
    combined_df[['Chromosome', 'Position']] = combined_df['coordinates'].str.split(':', expand=True)
    combined_df[['Start', 'End']] = combined_df['Position'].str.split('-', expand=True)

    # Convert 'Start' and 'End' columns to integers
    combined_df['Start'] = combined_df['Start'].astype(int)
    combined_df['End'] = combined_df['End'].astype(int)

    # Drop the intermediate 'Position' column
    combined_df.drop('Position', axis=1, inplace=True)

    # Create a new column for CNV_size, while keeping deletion and duplication in base pairs (bp)
    combined_df['CNV_size_kb'] = combined_df['CNV_size'] / 1000  # Convert to kilobases (kb)

    # Create a new column for CNV_size only for deletion and duplication types in base pairs (bp)
    combined_df['Total Deletion and Duplication (kb)'] = combined_df.apply(
        lambda row: row['CNV_size_kb'] if row['CNV_type'] in ['deletion', 'duplication'] else 0, axis=1
    )

    # Group by Chromosome and calculate the total CNV size for deletion and duplication combined in kilobases
    total_deletion_duplication = combined_df.groupby('Chromosome')['Total Deletion and Duplication (kb)'].sum()

    # Pivot the dataframe to create a matrix of CNV_size by Chromosome and CNV_type (with sizes in base pairs and total in kilobases)
    heatmap_data = combined_df.pivot_table(index='Chromosome', columns='CNV_type', values='CNV_size', aggfunc='mean')

    # Add a new column for Total Deletion and Duplication CNV size in kilobases (kb)
    heatmap_data['Total Deletion and Duplication (kb)'] = total_deletion_duplication

    # Ensure that "deletion" and "duplication" are both represented
    if 'deletion' not in heatmap_data.columns:
        heatmap_data['deletion'] = 0  # Add a column for "deletion" if it's missing

    if 'duplication' not in heatmap_data.columns:
        heatmap_data['duplication'] = 0  # Add a column for "duplication" if it's missing

    # Create the heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="YlGnBu", cbar_kws={'label': 'CNV Size (bp) for Deletion & Duplication / Total CNV Size (kb)'})

    # Add titles and labels
    plt.title('Average CNV Size by Chromosome, CNV Type and Total CNV Size (Deletion + Duplication)')
    plt.xlabel('CNV Type / Total CNV Type')
    plt.ylabel('Chromosome')

    # Show the heatmap
    plt.tight_layout()
    plt.savefig('avg_cnv_size_with_total_deletion_duplication_kb.png', dpi=300)  # Save as an image
    plt.show()

