#!/bin/bash

# Function to execute load test and generate report
execute_load_test() {
    local scenario_file="$1"
    local output_folder="$2"
    local rps=$(echo "$scenario_file" | grep -oP '\d+rps' | grep -oP '\d+')
    local output_file="${output_folder}/report-${rps}rps.json"

    echo "Running load test for ${rps}rps with scenario file ${scenario_file} (Run $run_counter)..."
    artillery run "$scenario_file" --output "$output_file"
}

# Function to generate HTML reports
generate_html_reports() {
    local output_folder="$1"
    echo "Generating HTML reports in ${output_folder}..."

    # Loop through each .json file in the specified folder
    for file in "${output_folder}"/*.json; do
        # Check if the file is a regular file
        if [ -f "$file" ]; then
            # Run artillery report with the filename and save in the same folder
            artillery report "$file" -o "${output_folder}/$(basename "${file}" .json).html"
        fi
    done
}

# Find all scenario files matching the pattern and sort them by RPS value in descending order
scenario_files=$(ls tesina-scenario-*-*rps.yml | sort -r)
warmup_file="warmup.yml"

# Initialize run counter
run_counter=1

# Execute load tests sequentially for each scenario file found
for scenario_file in $scenario_files; do
    if [[ "$scenario_file" != "$warmup_file" ]]; then
        # Run the warmup scenario before each test run
        echo "Running warmup load test with scenario file ${warmup_file} (Run $run_counter)..."
        artillery run "$warmup_file" --output /dev/null

        # Display run counter before the test
        echo "Starting Test Run $run_counter..."

        # Create a folder for each test run
        test_folder="run-${run_counter}-$(TZ='America/Argentina/Buenos_Aires' date +'%Y-%m-%d-%H-%M-%S')"
        mkdir -p "$test_folder"

        # Execute load test for each RPS within the current run
        for rps_scenario_file in $scenario_files; do
            if [[ "$rps_scenario_file" != "$warmup_file" ]]; then
                execute_load_test "$rps_scenario_file" "$test_folder"
            fi
        done

        generate_html_reports "$test_folder"

        echo "Test completed and reports generated in folder: $test_folder"

        # Increment run counter
        ((run_counter++))
    fi
done

echo "All load tests completed."
