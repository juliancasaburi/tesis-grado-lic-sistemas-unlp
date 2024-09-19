import os
import orjson
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

# Define a custom sorting key function
def custom_sort_key(label):
    if label.endswith('1000 VU'):
        return 1001  # Ensure '1000 VU' comes after '800 VU'
    else:
        return int(label.split()[0])  # Extract the VU value and convert to integer for sorting

def process_json_file(json_path):
    response_times = []
    http_codes_200 = 0
    http_codes_fail = 0

    with open(json_path, 'r') as f:
        for line in f:
            entry = orjson.loads(line)
            if entry['type'] == 'Point':
                if entry['metric'] == 'http_req_duration':
                    response_times.append(entry['data']['value'])
                elif entry['metric'] == 'http_req_failed':
                    if entry['data']['value'] == 0:
                        http_codes_200 += 1
                    else:
                        http_codes_fail += 1

    request_count = len(response_times)

    if not response_times:
        return [None] * 9 + [response_times]

    min_rt = np.min(response_times)
    max_rt = np.max(response_times)
    mean_rt = np.mean(response_times)
    median_rt = np.median(response_times)
    p90_rt = np.percentile(response_times, 90)
    p99_rt = np.percentile(response_times, 99)

    return [request_count, min_rt, max_rt, mean_rt, median_rt, p90_rt, p99_rt, http_codes_200, http_codes_fail, response_times]

def extract_scenario_environment_date_vu(json_path):
    parts = os.path.dirname(json_path).split('/')
    scenario = parts[-5]  # Extracting the scenario
    architecture = parts[-4]  # Extracting the architecture
    environment = parts[-2]  # Extracting the environment
    test_run_date = parts[-1]  # Extracting the test run date

    filename = os.path.basename(json_path)
    vu = filename.split('-')[-1].split('vu')[0]  # Extract the number before 'vu'

    return scenario, architecture, environment, test_run_date, vu

def process_file(json_file, folder_path, columns):
    relative_path = os.path.relpath(json_file, folder_path)
    stats = process_json_file(json_file)
    if stats is not None:
        scenario, architecture, environment, test_run_date, vu = extract_scenario_environment_date_vu(json_file)
        new_row = pd.Series([scenario, architecture, environment, test_run_date, relative_path, vu] + stats, index=columns)
        return new_row.to_frame().T
    return pd.DataFrame(columns=columns)

def main():
    folder_path = os.getcwd()
    results_excel_path = os.path.join(folder_path, 'results.xlsx')

    # Check if the Excel file already exists
    if os.path.exists(results_excel_path):
        print(f"{results_excel_path} already exists. Skipping data processing and proceeding with plotting.")
        results_df = pd.read_excel(results_excel_path)
    else:
        print(f"Generating {results_excel_path}...")

        json_files = []
        for root, dirs, files in os.walk(folder_path):
            if any("m5.large" in d for d in dirs):
                continue  # Skip this directory and its subdirectories

            for file in files:
                if file.startswith('k6-report') and file.endswith('.json') and 'warmup' not in file:
                    json_files.append(os.path.join(root, file))

        columns = ['Scenario', 'Architecture', 'Environment', 'Test Run', 'File', 'VU (Virtual Users)', 'Request Count',
                   'Min Response Time', 'Max Response Time', 'Mean Response Time', 'Median Response Time',
                   'P90 Response Time', 'P99 Response Time', 'HTTP Codes 200', 'HTTP Codes Fail', 'Response Times']

        results_df = pd.DataFrame(columns=columns)
        temp_csvs = []

        for json_file in tqdm(json_files, desc="Processing JSON files"):
            result_df = process_file(json_file, folder_path, columns)
            temp_csv = json_file + '.csv'
            result_df.to_csv(temp_csv, index=False)
            temp_csvs.append(temp_csv)

        for temp_csv in temp_csvs:
            temp_df = pd.read_csv(temp_csv)
            results_df = pd.concat([results_df, temp_df], ignore_index=True)
            os.remove(temp_csv)

        # Write results to Excel
        results_df.to_excel(results_excel_path, index=False)
        print(f"Results written to {results_excel_path}")

    # Now proceed with plotting
    print(f"Generating images")
    metrics = ['Mean Response Time', 'P99 Response Time', 'Max Response Time']

    # Group by scenario, environment, and architecture
    avg_response_times = results_df.groupby(['Scenario', 'Environment', 'Architecture', 'VU (Virtual Users)'])[['Mean Response Time', 'P99 Response Time', 'Max Response Time']].mean().reset_index()

    for (scenario, environment), group in avg_response_times.groupby(['Scenario', 'Environment']):
        for metric in metrics:
            fig, ax = plt.subplots(figsize=(18, 10))

            # Plot each architecture using horizontal bars
            architectures = group['Architecture'].unique()
            bar_width = 0.8
            spacing = 0.1
            index = np.arange(len(group['VU (Virtual Users)'].unique()))  # X locations for VU

            for i, architecture in enumerate(architectures):
                arch_group = group[group['Architecture'] == architecture]
                y = arch_group['VU (Virtual Users)']
                x = arch_group[metric]

                # Calculate the offset for each architecture
                offset = i * (bar_width + spacing)

                # Create horizontal bar plot with larger bars
                ax.barh(y + offset, x, bar_width, label=architecture, alpha=0.7)

                # Annotate each bar with the corresponding X value
                for j, value in enumerate(x):
                    ax.text(value, y.iloc[j] + offset, f'{value:.2f}', fontsize=12, ha='left', va='center')  # Increase font size

            ax.set_xlabel(f'{metric} in ms', fontsize=12)  # Increase X-axis label font size
            ax.set_ylabel('VU (Virtual Users)', fontsize=12)  # Increase Y-axis label font size
            ax.set_title(f'{metric} for Scenario: {scenario}, Environment: {environment}', fontsize=16)  # Increase title font size
            ax.legend(loc='best', fontsize=12)  # Increase legend font size
            ax.grid(True, which='both', linestyle='--', linewidth=0.5)

            # Ensure Y-axis only has integer values (for VU)
            ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

            # Set the Y-axis ticks to only those VUs that have data
            ax.set_yticks(group['VU (Virtual Users)'].unique())

            # Save the plot
            fig.savefig(f'{scenario.replace("/", "_")}_{environment.replace("/", "_")}_{metric.replace(" ", "_").lower()}_plot_horizontal.png', bbox_inches='tight')
            plt.close(fig)

if __name__ == "__main__":
    main()


