import os
import json
import pandas as pd

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
            results_df = results_df.append(pd.Series([scenario, environment, test_run_date, relative_path, rps] + stats, index=columns), ignore_index=True)

    # Writing results to Excel
    results_excel_path = os.path.join(folder_path, 'results.xlsx')
    results_df.to_excel(results_excel_path, index=False)
    print(f"Results written to {results_excel_path}")

if __name__ == "__main__":
    main()
