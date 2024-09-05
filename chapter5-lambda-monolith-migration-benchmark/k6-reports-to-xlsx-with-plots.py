import os
import orjson
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

# Define a custom sorting key function
def custom_sort_key(label):
    if label.endswith('1000 RPS'):
        return 1001  # Ensure '1000 RPS' comes after '800 RPS'
    else:
        return int(label.split()[0])  # Extract the RPS value and convert to integer for sorting

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

def extract_architecture_environment_date_rps(json_path):
    parts = os.path.dirname(json_path).split('/')
    architecture = parts[-3]  # Extracting the architecture
    test_run_date = parts[-1]  # Extracting the test run date

    filename = os.path.basename(json_path)
    rps = filename.split('-')[-1].split('rps')[0]  # Extract the number before 'rps'

    return architecture, test_run_date, rps

def process_file(json_file, folder_path, columns):
    relative_path = os.path.relpath(json_file, folder_path)
    stats = process_json_file(json_file)
    if stats is not None:
        architecture, test_run_date, rps = extract_architecture_environment_date_rps(json_file)
        new_row = pd.Series([architecture, test_run_date, relative_path, rps] + stats, index=columns)
        return new_row.to_frame().T
    return pd.DataFrame(columns=columns)

def main():
    folder_path = os.getcwd()

    json_files = []
    for root, dirs, files in os.walk(folder_path):
        if any("m5.large" in d for d in dirs):
            continue  # Skip this directory and its subdirectories

        for file in files:
            if file.startswith('k6-report') and file.endswith('.json') and 'warmup' not in file:
                json_files.append(os.path.join(root, file))

    columns = ['Architecture', 'Test Run', 'File', 'RPS (Requests per Second)', 'Request Count', 'Min Response Time', 'Max Response Time', 'Mean Response Time',
               'Median Response Time', 'P90 Response Time', 'P99 Response Time',
               'HTTP Codes 200', 'HTTP Codes Fail', 'Response Times']
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

    avg_response_times = results_df.groupby(['Architecture', 'RPS (Requests per Second)'])[['Mean Response Time', 'P99 Response Time']].mean().reset_index()
    avg_response_times.rename(columns={
        'Mean Response Time': 'Mean Response Time (Average per architecture + RPS)',
        'P99 Response Time': 'P99 Response Time (Average per architecture + RPS)'
    }, inplace=True)

    results_df = pd.merge(results_df, avg_response_times, on=['Architecture', 'RPS (Requests per Second)'], how='left')

    results_excel_path = os.path.join(folder_path, 'results.xlsx')
    results_df.to_excel(results_excel_path, index=False)
    print(f"Results written to {results_excel_path}")

    print(f"Generating images")
    for architecture_env, group in avg_response_times.groupby(['Architecture']):
        architecture_str = architecture_env[0]
        group['RPS (Requests per Second)'] = group['RPS (Requests per Second)'].astype(str)  # Convert to string for sorting
        group = group.sort_values(by='RPS (Requests per Second)', key=lambda x: x.map(custom_sort_key))

        fig, ax = plt.subplots(figsize=(10, 10))
        for index, row in group.iterrows():
            ax.plot(row['RPS (Requests per Second)'], row['Mean Response Time (Average per architecture + RPS)'], marker='o', label=f"{architecture_str} ({row['RPS (Requests per Second)']} RPS)")
            ax.text(row['RPS (Requests per Second)'], row['Mean Response Time (Average per architecture + RPS)'], f"{row['Mean Response Time (Average per architecture + RPS)']:.2f}", ha='center', va='bottom')
        ax.set_xlabel('RPS (Requests per Second)')
        ax.set_ylabel('Mean Response Time in ms (Average per architecture + RPS)')
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax.grid(True)
        fig.subplots_adjust(left=0.1, right=0.75, bottom=0.1, top=0.9)
        fig.savefig(f'{architecture_str.replace("/", "_")}_average_mean_plot.png', bbox_inches='tight')
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(10, 10))
        for index, row in group.iterrows():
            ax.plot(row['RPS (Requests per Second)'], row['P99 Response Time (Average per architecture + RPS)'], marker='x', label=f"{architecture_str} ({row['RPS (Requests per Second)']} RPS)")
            ax.text(row['RPS (Requests per Second)'], row['P99 Response Time (Average per architecture + RPS)'], f"{row['P99 Response Time (Average per architecture + RPS)']:.2f}", ha='center', va='top')
        ax.set_xlabel('RPS (Requests per Second)')
        ax.set_ylabel('P99 Response Time in ms (Average per architecture + RPS)')
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax.grid(True)
        fig.subplots_adjust(left=0.1, right=0.75, bottom=0.1, top=0.9)
        fig.savefig(f'{architecture_str.replace("/", "_")}_p99_plot.png', bbox_inches='tight')
        plt.close(fig)

    print(f"Generating latency measurement images")
    for architecture_env, group in results_df.groupby(['Architecture']):
        architecture_str = architecture_env[0]
        fig, ax = plt.subplots(figsize=(10, 10))

        for index, row in group.iterrows():
            response_times = eval(row['Response Times'])
            rps_values = [row['RPS (Requests per Second)']] * len(response_times)
            ax.scatter(rps_values, response_times, label=f"{architecture_str} ({row['RPS (Requests per Second)']} RPS)", alpha=0.6)

        ax.set_xlabel('RPS (Requests per Second)')
        ax.set_ylabel('Response Time in ms')
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax.grid(True)
        fig.subplots_adjust(left=0.1, right=0.75, bottom=0.1, top=0.9)
        fig.savefig(f'{architecture_str.replace("/", "_")}_all_latency_plot.png', bbox_inches='tight')
        plt.close(fig)

if __name__ == "__main__":
    main()
