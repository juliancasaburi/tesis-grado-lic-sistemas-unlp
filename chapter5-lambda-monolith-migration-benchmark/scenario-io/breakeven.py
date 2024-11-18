import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import fsolve

# Constants
HOURS_PER_MONTH = 730  # Average hours per month according to AWS's calculator
SECONDS_IN_MONTH = HOURS_PER_MONTH * 60 * 60
LCU_COST_PER_HOUR = 0.008  # Cost per LCU per hour in dollars

# AWS Lambda costs (N.Virginia us-east-1 region)
LAMBDA_REQUEST_COST_PER_MILLION = 0.20  # Cost per 1 million requests
LAMBDA_MEMORY_MB = 128
LAMBDA_EXECUTION_TIME_MS = 53  # Execution time in milliseconds

# Lambda tiered pricing for GB-seconds
LAMBDA_COMPUTE_COST_PER_GB_SECOND_TIER_1 = 0.0000166667 # First 6 billion GB-seconds
LAMBDA_COMPUTE_COST_PER_GB_SECOND_TIER_2 = 0.000015  # Next 9 billion GB-seconds
LAMBDA_COMPUTE_COST_PER_GB_SECOND_TIER_3 = 0.0000133333  # Beyond 15 billion GB-seconds
TIER_1_LIMIT = 6_000_000_000  # 6 billion GB-seconds
TIER_2_LIMIT = 9_000_000_000  # 9 billion GB-seconds (additional to Tier 1)
TIER_3_LIMIT = TIER_1_LIMIT + TIER_2_LIMIT  # 15 billion GB-seconds total

# EC2 costs (N.Virginia us-east-1 region) for m5.large
EC2_BASIC_MONTHLY_COST_RESERVED = 43.80  # m5.large instance cost for reserved EC2
EC2_BASIC_MONTHLY_COST_ON_DEMAND = 70.08  # m5.large instance cost for on-demand EC2
EC2_HA_MONTHLY_COST_RESERVED = EC2_BASIC_MONTHLY_COST_RESERVED * 2  # High Availability (HA) EC2 with reserved pricing
EC2_HA_MONTHLY_COST_ON_DEMAND = EC2_BASIC_MONTHLY_COST_ON_DEMAND * 2  # HA EC2 with on-demand pricing

ALB_FIXED_MONTHLY_COST = 16.43  # Monthly fixed cost for Application Load Balancer (ALB)

def calculate_alb_cost(rps):
    # Calculate LCUs
    processed_bytes_lcus = 1  # 1 GB per hour / 1 GB processed bytes per hour per LCU
    new_connections_lcus = rps / 25  # rps new connections per second / 25 new connections per second per LCU
    active_connections_lcus = (rps * 1) / 3000  # rps active connections / 3000 connections per LCU
    paid_rules_lcus = max(-9, 0)  # Max (-9 paid rules per request, 0)

    # Determine the maximum LCUs
    max_lcus = max(processed_bytes_lcus, new_connections_lcus, active_connections_lcus, paid_rules_lcus)

    # Calculate monthly ALB cost
    alb_monthly_cost = 1 * max_lcus * LCU_COST_PER_HOUR * HOURS_PER_MONTH
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

# Calculate single EC2 basic cost (Reserved)
def ec2_basic_cost_reserved(rps):
    return EC2_BASIC_MONTHLY_COST_RESERVED

# Calculate single EC2 basic cost (On-Demand)
def ec2_basic_cost_on_demand(rps):
    return EC2_BASIC_MONTHLY_COST_ON_DEMAND

# Calculate EC2 high availability cost (Reserved)
def ec2_ha_cost_reserved(rps):
    return EC2_HA_MONTHLY_COST_RESERVED * 2 + ALB_FIXED_MONTHLY_COST + calculate_alb_cost(rps)

# Calculate EC2 high availability costh (On-Demand)
def ec2_ha_cost_on_demand(rps):
    return EC2_HA_MONTHLY_COST_ON_DEMAND * 2 + ALB_FIXED_MONTHLY_COST + calculate_alb_cost(rps)

# Generate data
rps_values = np.arange(0, 4001, 200)  # From 0 to 4000 RPS, incrementing by 200
lambda_costs = np.array([lambda_cost(rps) for rps in rps_values])
ec2_ha_costs_reserved = np.array([ec2_ha_cost_reserved(rps) for rps in rps_values])
ec2_ha_costs_on_demand = np.array([ec2_ha_cost_on_demand(rps) for rps in rps_values])

# Define the intersection function
def find_intersection(func1, func2):
    return int(fsolve(lambda x: func1(x) - func2(x), 250)[0])

# Finding breakeven points
breakeven_lambda_ec2_ha_reserved = find_intersection(lambda_cost, ec2_ha_cost_reserved)
breakeven_lambda_ec2_ha_on_demand = find_intersection(lambda_cost, ec2_ha_cost_on_demand)

# Plotting
plt.figure(figsize=(16, 8))

# Lambda Costs
plt.plot(rps_values, lambda_costs, label='AWS Lambda', linestyle='--', color='orange')

# EC2 HA Costs (Reserved)
plt.plot(rps_values, ec2_ha_costs_reserved, label='EC2 High Availability (HA) - Reserved', linestyle=':', color='blue')

# EC2 HA Costs (On-Demand)
plt.plot(rps_values, ec2_ha_costs_on_demand, label='EC2 High Availability (HA) - On-Demand', linestyle=':', color='purple')

# Annotations for breakeven points
plt.annotate(f'EC2 HA Reserved Break-even: {breakeven_lambda_ec2_ha_reserved} RPS\nLambda Cost: ${lambda_cost(breakeven_lambda_ec2_ha_reserved):.2f}',
             xy=(breakeven_lambda_ec2_ha_reserved, lambda_cost(breakeven_lambda_ec2_ha_reserved)),
             xytext=(breakeven_lambda_ec2_ha_reserved + 500, lambda_cost(breakeven_lambda_ec2_ha_reserved - 200)),
             arrowprops=dict(facecolor='black', arrowstyle='->'))

plt.annotate(f'EC2 HA On-Demand Break-even: {breakeven_lambda_ec2_ha_on_demand} RPS\nLambda Cost: ${lambda_cost(breakeven_lambda_ec2_ha_on_demand):.2f}',
             xy=(breakeven_lambda_ec2_ha_on_demand, lambda_cost(breakeven_lambda_ec2_ha_on_demand)),
             xytext=(breakeven_lambda_ec2_ha_on_demand + 500, lambda_cost(breakeven_lambda_ec2_ha_on_demand) + 1500),
             arrowprops=dict(facecolor='black', arrowstyle='->'))

# Plot configuration
plt.title('AWS Lambda vs EC2 Costs', fontsize=16)
plt.xlabel('Requests per Second (RPS)', fontsize=14)
plt.ylabel('Monthly Cost (USD)', fontsize=14)
plt.xticks(rps_values)
plt.grid(True)
plt.legend()
plt.xlim(0, 4000)

# Save the plot
plt.savefig('cost_comparison_breakeven_lambda_vs_ec2.png')
