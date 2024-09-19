import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import fsolve

# Constants
SECONDS_IN_MONTH = 730 * 60 * 60  # According to AWS's calculator

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

# EC2 costs (N.Virginia us-east-1 region) for t3.micro
EC2_BASIC_MONTHLY_COST_RESERVED = 4.16  # t3.micro instance cost for reserved EC2
EC2_BASIC_MONTHLY_COST_ON_DEMAND = 7.64  # t3.micro instance cost for on-demand EC2
EC2_HA_MONTHLY_COST_RESERVED = EC2_BASIC_MONTHLY_COST_RESERVED * 2  # High Availability (HA) EC2 with reserved pricing
EC2_HA_MONTHLY_COST_ON_DEMAND = EC2_BASIC_MONTHLY_COST_ON_DEMAND * 2  # HA EC2 with on-demand pricing

ELB_COST = 16.43  # Monthly fixed cost for Application Load Balancer (ALB)

# CloudWatch costs (N.Virginia us-east-1 region)
CLOUDWATCH_LOGGING_COST_PER_RPS = 0  # Example cost per RPS for CloudWatch logging

# Calculate Lambda cost with tiered pricing
def lambda_cost(rps):
    # Compute the number of requests per month
    monthly_requests = rps * SECONDS_IN_MONTH  # total requests

    # Memory allocation and execution time
    memory_gb = LAMBDA_MEMORY_MB / 1024  # Convert MB to GB
    execution_time_seconds = LAMBDA_EXECUTION_TIME_MS / 1000  # Convert ms to seconds
    total_compute_seconds = monthly_requests * execution_time_seconds

    # Total GB-seconds for compute
    total_gb_seconds = total_compute_seconds * memory_gb

    # Compute cost based on tiered pricing
    compute_cost = total_gb_seconds * LAMBDA_COMPUTE_COST_PER_GB_SECOND_TIER_1  # Since 106K GB-seconds is in tier 1

    # Request cost
    request_cost = monthly_requests * LAMBDA_REQUEST_COST_PER_MILLION / 1_000_000  # Calculate request cost

    print("RPS: ", rps, "Total compute seconds:", total_compute_seconds, "Total GB-seconds: ", total_gb_seconds, "Compute Cost: ", compute_cost, "Request Cost: ", request_cost, "Total Cost: ", request_cost + compute_cost)

    return compute_cost + request_cost

# Calculate single EC2 basic cost with CloudWatch (Reserved)
def ec2_basic_cost_with_cloudwatch_reserved(rps):
    cloudwatch_cost = CLOUDWATCH_LOGGING_COST_PER_RPS * rps * SECONDS_IN_MONTH / 1_000_000
    return EC2_BASIC_MONTHLY_COST_RESERVED + cloudwatch_cost

# Calculate single EC2 basic cost with CloudWatch (On-Demand)
def ec2_basic_cost_with_cloudwatch_on_demand(rps):
    cloudwatch_cost = CLOUDWATCH_LOGGING_COST_PER_RPS * rps * SECONDS_IN_MONTH / 1_000_000
    return EC2_BASIC_MONTHLY_COST_ON_DEMAND + cloudwatch_cost

# Calculate EC2 high availability cost with CloudWatch (Reserved)
def ec2_ha_cost_reserved(rps):
    cloudwatch_cost = CLOUDWATCH_LOGGING_COST_PER_RPS * rps * SECONDS_IN_MONTH / 1_000_000
    return EC2_HA_MONTHLY_COST_RESERVED + ELB_COST + cloudwatch_cost

# Calculate EC2 high availability cost with CloudWatch (On-Demand)
def ec2_ha_cost_on_demand(rps):
    cloudwatch_cost = CLOUDWATCH_LOGGING_COST_PER_RPS * rps * SECONDS_IN_MONTH / 1_000_000
    return EC2_HA_MONTHLY_COST_ON_DEMAND + ELB_COST + cloudwatch_cost

# Generate data
rps_values = np.arange(0, 1001, 50)  # From 0 to 1000 RPS, incrementing by 50
lambda_costs = np.array([lambda_cost(rps) for rps in rps_values])
ec2_basic_costs_with_cloudwatch_reserved = np.array([ec2_basic_cost_with_cloudwatch_reserved(rps) for rps in rps_values])
ec2_basic_costs_with_cloudwatch_on_demand = np.array([ec2_basic_cost_with_cloudwatch_on_demand(rps) for rps in rps_values])
ec2_ha_costs_reserved = np.array([ec2_ha_cost_reserved(rps) for rps in rps_values])
ec2_ha_costs_on_demand = np.array([ec2_ha_cost_on_demand(rps) for rps in rps_values])

# Define the intersection function
def find_intersection(func1, func2):
    return int(fsolve(lambda x: func1(x) - func2(x), 500)[0])

# Finding breakeven points
breakeven_lambda_ec2_basic_reserved = find_intersection(lambda_cost, ec2_basic_cost_with_cloudwatch_reserved)
breakeven_lambda_ec2_basic_on_demand = find_intersection(lambda_cost, ec2_basic_cost_with_cloudwatch_on_demand)
breakeven_lambda_ec2_ha_reserved = find_intersection(lambda_cost, ec2_ha_cost_reserved)
breakeven_lambda_ec2_ha_on_demand = find_intersection(lambda_cost, ec2_ha_cost_on_demand)

# Plotting
plt.figure(figsize=(12, 8))

# Lambda Costs
plt.plot(rps_values, lambda_costs, label='AWS Lambda', linestyle='--', color='orange')

# EC2 Basic Costs with CloudWatch (Reserved)
plt.plot(rps_values, ec2_basic_costs_with_cloudwatch_reserved, label='EC2 Basic (Reserved)', linestyle='-', color='green')

# EC2 Basic Costs with CloudWatch (On-Demand)
plt.plot(rps_values, ec2_basic_costs_with_cloudwatch_on_demand, label='EC2 Basic (On-Demand)', linestyle='-', color='red')

# EC2 HA Costs (Reserved)
plt.plot(rps_values, ec2_ha_costs_reserved, label='EC2 High Availability (Reserved)', linestyle=':', color='blue')

# EC2 HA Costs (On-Demand)
plt.plot(rps_values, ec2_ha_costs_on_demand, label='EC2 High Availability (On-Demand)', linestyle=':', color='purple')

# Annotations for breakeven points
plt.annotate(f'Breakeven EC2 HA Reserved: {breakeven_lambda_ec2_ha_reserved} RPS\nCost: ${lambda_cost(breakeven_lambda_ec2_ha_reserved):.2f}',
             xy=(breakeven_lambda_ec2_ha_reserved, lambda_cost(breakeven_lambda_ec2_ha_reserved)),
             xytext=(breakeven_lambda_ec2_ha_reserved, lambda_cost(breakeven_lambda_ec2_ha_reserved) + 300),
             arrowprops=dict(facecolor='black', arrowstyle='->'))

plt.annotate(f'Breakeven EC2 HA On-Demand: {breakeven_lambda_ec2_ha_on_demand} RPS\nCost: ${lambda_cost(breakeven_lambda_ec2_ha_on_demand):.2f}',
             xy=(breakeven_lambda_ec2_ha_on_demand, lambda_cost(breakeven_lambda_ec2_ha_on_demand)),
             xytext=(breakeven_lambda_ec2_ha_on_demand + 200, lambda_cost(breakeven_lambda_ec2_ha_on_demand) + 100),
             arrowprops=dict(facecolor='black', arrowstyle='->'))

# Plot configuration
plt.title('AWS Lambda vs EC2 Costs', fontsize=16)
plt.xlabel('Requests per Second (RPS)', fontsize=14)
plt.ylabel('Monthly Cost (USD)', fontsize=14)
plt.grid(True)
plt.legend()
plt.tight_layout()

# Save the plot
plt.savefig('cost_comparison_breakeven_lambda_vs_ec2.png')
