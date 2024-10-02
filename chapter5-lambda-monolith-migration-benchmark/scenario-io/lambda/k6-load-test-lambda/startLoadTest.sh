#!/bin/bash

# Function to execute load test and generate report
execute_load_test() {
    local scenario_file="$1"
    local output_folder="$2"
    local run_counter="$3"
    local vu=$(echo "$scenario_file" | grep -oP '\d+vu' | grep -oP '\d+')
    local json_output_file="${output_folder}/k6-report-${scenario_file}.json"
    local html_output_file="${output_folder}/k6-report-${scenario_file}.html"

    echo "Running load test for ${vu}vu amount with scenario file ${scenario_file} (Run $run_counter)..."

    export K6_WEB_DASHBOARD=true
    export K6_WEB_DASHBOARD_EXPORT="$html_output_file"
    k6 run "$scenario_file" --out json="$json_output_file"
}

# Find all scenario files matching the pattern and sort them by rps value in ascending order
scenario_files=$(ls tesina-migration-scenario-io-*-*.js | sort -t '-' -k 5,5n)

# Execute load tests in 4 loops
for ((i=1; i<=4; i++)); do

    echo "Starting Test Run (Loop) $i..."

    # Create a folder for each test run
    test_folder="run-${i}-$(TZ='America/Argentina/Buenos_Aires' date +'%Y-%m-%d-%H-%M-%S')"
    mkdir -p "$test_folder"

    # Execute load tests sequentially for each scenario file found
    for scenario_file in $scenario_files; do

        # Execute load test for each vu within the current run
        execute_load_test "$scenario_file" "$test_folder" "$i"

        echo "Test completed and reports generated in folder: $test_folder"
    done

    echo "Test Run (Loop) $i completed."

done

echo "All load tests completed."
