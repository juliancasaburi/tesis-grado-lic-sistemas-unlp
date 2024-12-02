import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import fsolve

# Constants
HOURS_PER_MONTH = 730  # Average hours per month according to AWS's calculator
SECONDS_IN_MONTH = HOURS_PER_MONTH * 60 * 60
LCU_COST_PER_HOUR = 0.008  # Cost per LCU per hour in dollars

# AWS Lambda costs (N.Virginia us-east-1 region)
LAMBDA_REQUEST_COST_PER_MILLION = 0.20  # Cost per 1 million requests
LAMBDA_MEMORY_MB = 1536
LAMBDA_EXECUTION_TIME_MS = 194  # Execution time in milliseconds

# Lambda tiered pricing for GB-seconds
LAMBDA_COMPUTE_COST_PER_GB_SECOND_TIER_1 = 0.0000166667  # First 6 billion GB-seconds
LAMBDA_COMPUTE_COST_PER_GB_SECOND_TIER_2 = 0.000015  # Next 9 billion GB-seconds
LAMBDA_COMPUTE_COST_PER_GB_SECOND_TIER_3 = 0.0000133333  # Beyond 15 billion GB-seconds
TIER_1_LIMIT = 6_000_000_000  # 6 billion GB-seconds
TIER_2_LIMIT = 9_000_000_000  # 9 billion GB-seconds (additional to Tier 1)
TIER_3_LIMIT = TIER_1_LIMIT + TIER_2_LIMIT  # 15 billion GB-seconds total

# EC2 costs (N.Virginia us-east-1 region) for t3.small
EC2_BASIC_MONTHLY_COST_RESERVED = 9.49  # t3.small instance cost for reserved EC2
EC2_BASIC_MONTHLY_COST_ON_DEMAND = 15.18  # t3.small instance cost for on-demand EC2

ALB_FIXED_MONTHLY_COST = 16.43  # Monthly fixed cost for Application Load Balancer (ALB)

# Calculate the number of instances required based on RPS
def calculate_instance_count(rps):
    return max(2, ((rps - 0.01) // 10 + 1) * 2)

# Monthly cost for High Availability (HA) with 2 instances per 10 RPS
def ec2_ha_monthly_cost(rps, reserved=True):
    instance_count = calculate_instance_count(rps)
    monthly_cost = (EC2_BASIC_MONTHLY_COST_RESERVED if reserved else EC2_BASIC_MONTHLY_COST_ON_DEMAND) * instance_count
    return monthly_cost

def calculate_alb_cost(processed_bytes_gb_per_hour = 1, new_connections_per_second = 10, average_connection_duration_seconds = 1):
    # Constants
    LCU_COST_PER_HOUR = 0.008  # LCU price per hour
    HOURS_PER_MONTH = 730  # Number of hours in a month

    # Calculate LCUs based on the provided dimensions
    processed_bytes_lcus = processed_bytes_gb_per_hour / 1  # 1 GB processed per hour per LCU
    new_connections_lcus = new_connections_per_second / 25  # 25 new connections per second per LCU
    active_connections = new_connections_per_second * average_connection_duration_seconds
    active_connections_lcus = active_connections / 3000  # 3000 active connections per LCU

    # Assuming there are no paid rules being used for this calculation
    paid_rules_lcus = 0  # Change as per your actual usage

    # Determine the maximum LCUs
    max_lcus = max(processed_bytes_lcus, new_connections_lcus, active_connections_lcus, paid_rules_lcus)

    # Calculate monthly ALB cost
    alb_monthly_cost = max_lcus * LCU_COST_PER_HOUR * HOURS_PER_MONTH
    return alb_monthly_cost

# Calculate Lambda cost with tiered pricing
def lambda_cost(rps):
    # Compute the number of requests per month
    monthly_requests = np.float32(rps) * np.float32(SECONDS_IN_MONTH)

    # Memory allocation and execution time
    memory_gb = LAMBDA_MEMORY_MB / 1024  # Convert MB to GB
    execution_time_seconds = LAMBDA_EXECUTION_TIME_MS / 1000  # Convert ms to seconds
    total_compute_seconds = monthly_requests * execution_time_seconds

    # Total GB-seconds for compute
    total_gb_seconds = total_compute_seconds * memory_gb

    # Calculate compute cost based on tiered pricing
    if total_gb_seconds <= TIER_1_LIMIT:
        compute_cost = total_gb_seconds * LAMBDA_COMPUTE_COST_PER_GB_SECOND_TIER_1
    elif total_gb_seconds <= TIER_3_LIMIT:
        tier_1_cost = TIER_1_LIMIT * LAMBDA_COMPUTE_COST_PER_GB_SECOND_TIER_1
        tier_2_cost = (total_gb_seconds - TIER_1_LIMIT) * LAMBDA_COMPUTE_COST_PER_GB_SECOND_TIER_2
        compute_cost = tier_1_cost + tier_2_cost
    else:
        tier_1_cost = TIER_1_LIMIT * LAMBDA_COMPUTE_COST_PER_GB_SECOND_TIER_1
        tier_2_cost = (TIER_3_LIMIT - TIER_1_LIMIT) * LAMBDA_COMPUTE_COST_PER_GB_SECOND_TIER_2
        tier_3_cost = (total_gb_seconds - TIER_3_LIMIT) * LAMBDA_COMPUTE_COST_PER_GB_SECOND_TIER_3
        compute_cost = tier_1_cost + tier_2_cost + tier_3_cost

    # Request cost
    request_cost = monthly_requests * LAMBDA_REQUEST_COST_PER_MILLION / 1_000_000  # Calculate request cost

    return compute_cost + request_cost

# Calculate EC2 high availability cost (On-Demand)
def ec2_ha_cost_on_demand(rps):
    return ec2_ha_monthly_cost(rps, reserved=False) + ALB_FIXED_MONTHLY_COST + calculate_alb_cost(new_connections_per_second = rps)

# Generate data
rps_values = np.arange(0, 21, 0.1)  # From 0 to 20 RPS, incrementing by 1
lambda_costs = np.array([lambda_cost(rps) for rps in rps_values])
ec2_ha_costs_on_demand = np.array([ec2_ha_cost_on_demand(rps) for rps in rps_values])

# Find the intersection, rounded up to the next integer
def find_intersection(func1, func2):
    breakeven_rps = fsolve(lambda x: func1(x) - func2(x), 250)[0]
    return int(round(breakeven_rps, 1))  # Round to one decimal place

# Finding breakeven points
breakeven_lambda_ec2_ha_on_demand = find_intersection(lambda_cost, ec2_ha_cost_on_demand)

# Plotting
plt.figure(figsize=(16, 8))

# Lambda Costs
plt.plot(rps_values, lambda_costs, label='AWS Lambda', linestyle='--', color='orange')

# EC2 HA Costs (On-Demand)
plt.plot(rps_values, ec2_ha_costs_on_demand, label='EC2 High Availability (HA) - On-Demand', linestyle=':', color='purple')

# Annotations font
plt.rc('font', size=12)
plt.legend(fontsize=12)

plt.annotate(f'EC2 HA On-Demand Break-even: {breakeven_lambda_ec2_ha_on_demand} RPS\nLambda Cost: ${lambda_cost(breakeven_lambda_ec2_ha_on_demand):.2f}',
             xy=(breakeven_lambda_ec2_ha_on_demand, lambda_cost(breakeven_lambda_ec2_ha_on_demand)),
             xytext=(breakeven_lambda_ec2_ha_on_demand, lambda_cost(breakeven_lambda_ec2_ha_on_demand) - 50),
             arrowprops=dict(facecolor='black', arrowstyle='->'))

# Plot configuration
plt.title('AWS Lambda vs EC2 Costs (with horizontal scaling)', fontsize=16)
plt.xlabel('Requests per Second (RPS)', fontsize=14)
plt.ylabel('Monthly Cost (USD)', fontsize=14)
plt.grid(True)
plt.tight_layout()
plt.legend()
plt.xlim(0, 20)
plt.xticks(np.arange(0, 21, 1))

# Save the plot
plt.savefig('cost_comparison_breakeven_lambda_vs_ec2.png')
