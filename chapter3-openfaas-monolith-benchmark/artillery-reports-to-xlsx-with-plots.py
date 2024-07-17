import os
import json
import pandas as pd
import matplotlib.pyplot as plt

# Define a custom sorting key function
def custom_sort_key(label):
    if label.endswith('1000 RPS'):
        return 1001  # Ensure '1000 RPS' comes after '800 RPS'
    else:
        return int(label.split()[0])  # Extract the RPS value and convert to integer for sorting

def process_json_file(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Extracting data from summaries and aggregate
    response_times = data['aggregate'].get('summaries', {}).get('http.response_time', {})
    counters = data['aggregate'].get('counters', {})

    # Calculating statistics for response times
    min_rt = response_times.get('min', None)
    max_rt = response_times.get('max', None)
    mean_rt = response_times.get('mean', None)
    median_rt = response_times.get('median', None)
    p90_rt = response_times.get('p90', None)
    p99_rt = response_times.get('p99', None)

    # Getting data from counters
    http_codes_200 = counters.get('http.codes.200', None)
    http_responses = counters.get('http.responses', None)

    return [min_rt, max_rt, mean_rt, median_rt, p90_rt, p99_rt, http_codes_200, http_responses]

def extract_scenario_environment_date_rps(json_path):
    # Extract scenario and environment from the file path
    parts = os.path.dirname(json_path).split('/')
    scenario = parts[-5] + "/" + parts[-4]  # Extracting the scenario
    environment = parts[-2]  # Extracting the environment
    test_run_date = parts[-1]  # Extracting the test run date

    # Extracting RPS from the filename
    filename = os.path.basename(json_path)
    rps = filename.split('-')[1].split('rps')[0]

    return scenario, environment, test_run_date, rps

def main():
    # Get the folder path from where the script is called
    folder_path = os.getcwd()

    # Collecting paths of JSON files starting with 'report'
    json_files = []
    for root, dirs, files in os.walk(folder_path):
        # Check if 'm5.large' is in any of the directory names
        if any("m5.large" in d for d in dirs):
            continue  # Skip this directory and its subdirectories

        for file in files:
            if file.startswith('report') and file.endswith('.json'):
                json_files.append(os.path.join(root, file))

    # Creating a DataFrame to store the results
    columns = ['Scenario', 'Environment', 'Test Run', 'File', 'RPS (Requests Per Second)', 'Min Response Time', 'Max Response Time', 'Mean Response Time',
               'Median Response Time', 'P90 Response Time', 'P99 Response Time',
               'HTTP Codes 200', 'HTTP Responses']
    results_df = pd.DataFrame(columns=columns)

    # Processing each JSON file
    for json_file in json_files:
        relative_path = os.path.relpath(json_file, folder_path)
        stats = process_json_file(json_file)
        if stats is not None:
            scenario, environment, test_run_date, rps = extract_scenario_environment_date_rps(json_file)
            new_row = pd.Series([scenario, environment, test_run_date, relative_path, rps] + stats, index=columns)
            results_df = pd.concat([results_df, new_row.to_frame().T], ignore_index=True)

    # Calculating average mean response time per scenario, environment, and RPS
    avg_mean_per_scenario_environment_rps = results_df.groupby(['Scenario', 'Environment', 'RPS (Requests Per Second)'])['Mean Response Time'].mean().reset_index()
    avg_mean_per_scenario_environment_rps.rename(columns={'Mean Response Time': 'Mean Response Time (Average per scenario + environment + RPS)'}, inplace=True)

    # Merging average mean response time into the main DataFrame
    results_df = pd.merge(results_df, avg_mean_per_scenario_environment_rps, on=['Scenario', 'Environment', 'RPS (Requests Per Second)'], how='left')

    # Writing results to Excel
    results_excel_path = os.path.join(folder_path, 'results.xlsx')
    results_df.to_excel(results_excel_path, index=False)
    print(f"Results written to {results_excel_path}")

    # Plotting
    print(f"Generating images")
    for scenario_env, group in avg_mean_per_scenario_environment_rps.groupby(['Scenario', 'Environment']):
        scenario, environment = scenario_env
        fig, ax = plt.subplots(figsize=(10, 10))

        # Sort the group by RPS (Requests Per Second) using the custom sorting key
        group = group.sort_values(by='RPS (Requests Per Second)', key=lambda x: x.map(custom_sort_key))

        for index, row in group.iterrows():
            ax.plot(row['RPS (Requests Per Second)'], row['Mean Response Time (Average per scenario + environment + RPS)'], marker='o', label=f"{scenario}/{environment} ({row['RPS (Requests Per Second)']} RPS)")
            # Add text annotations
            ax.text(row['RPS (Requests Per Second)'], row['Mean Response Time (Average per scenario + environment + RPS)'], f"{row['Mean Response Time (Average per scenario + environment + RPS)']:.2f}", ha='center', va='bottom')

        ax.set_xlabel('RPS (Requests Per Second)')
        ax.set_ylabel('Mean Response Time in ms (Average per scenario + environment + RPS)')
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax.grid(True)

        # Adjust layout to include extra space
        fig.subplots_adjust(left=0.1, right=0.75, bottom=0.1, top=0.9)

        # Save the plot as PNG with tight bounding box
        fig.savefig(f'{scenario.replace("/", "_")}_{environment}_average_mean_plot.png', bbox_inches='tight')  
        plt.close(fig)  # Close the figure to free memory

if __name__ == "__main__":
    main()
