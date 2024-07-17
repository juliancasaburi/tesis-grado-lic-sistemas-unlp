#!/bin/bash

# Function to execute load test and generate report
execute_load_test() {
    local rps="$1"
    local output_file="report-${rps}rps.json"
    local scenario_file="tesina-scenario-network-lambda-load-test-${rps}rps.yml"

    echo "Running load test for ${rps}rps..."
    artillery run "$scenario_file" --output "$output_file"
}

# Execute load tests sequentially
execute_load_test 1
execute_load_test 100
execute_load_test 200
execute_load_test 400
execute_load_test 800
execute_load_test 1000

echo "All load tests completed."

echo "Generating HTML reports..."

# Loop through each .json file in the current directory
for file in *.json; do
    # Check if the file is a regular file
    if [ -f "$file" ]; then
        # Run artillery report with the filename
        artillery report "$file"
    fi
done

echo "HTML reports generated."
