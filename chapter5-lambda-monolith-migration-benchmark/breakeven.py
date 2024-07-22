import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import fsolve

# Constants
SECONDS_IN_MONTH = 30 * 24 * 60 * 60

# AWS Lambda costs
LAMBDA_REQUEST_COST_PER_MILLION = 0.20
LAMBDA_COMPUTE_COST_PER_GB_SECOND = 0.00001667
LAMBDA_MEMORY_MB = 128
LAMBDA_EXECUTION_TIME_MS = 16

# EC2 costs
EC2_BASIC_MONTHLY_COST = 19.05  # t3.medium instance cost for basic EC2
EC2_HA_MONTHLY_COST = EC2_BASIC_MONTHLY_COST * 2 # t3.medium instance cost for HA EC2 (two instances)
ELB_COST = 16.43  # Monthly fixed cost for Application Load Balancer (ALB)

# CloudWatch costs
CLOUDWATCH_LOGGING_COST_PER_RPS = 0.00075  # Example cost per RPS for CloudWatch logging

# Calculate Lambda cost
def lambda_cost(rps):
    monthly_requests = (rps / 1_000_000) * SECONDS_IN_MONTH
    invocation_cost = monthly_requests * LAMBDA_REQUEST_COST_PER_MILLION
    compute_cost = (monthly_requests * LAMBDA_EXECUTION_TIME_MS / 1000) * (LAMBDA_MEMORY_MB / 1024) * LAMBDA_COMPUTE_COST_PER_GB_SECOND
    return invocation_cost + compute_cost

# Calculate single EC2 basic cost including CloudWatch
def ec2_basic_cost_with_cloudwatch(rps):
    cloudwatch_cost = CLOUDWATCH_LOGGING_COST_PER_RPS * rps * SECONDS_IN_MONTH / 1_000_000
    return EC2_BASIC_MONTHLY_COST + cloudwatch_cost

# Calculate single EC2 basic cost without CloudWatch
def ec2_basic_cost_without_cloudwatch(rps):
    return EC2_BASIC_MONTHLY_COST

# Calculate EC2 high availability cost (two instances, ELB, CloudWatch)
def ec2_ha_cost(rps):
    cloudwatch_cost = CLOUDWATCH_LOGGING_COST_PER_RPS * rps * SECONDS_IN_MONTH / 1_000_000
    return EC2_HA_MONTHLY_COST + ELB_COST + cloudwatch_cost

# Generate data
rps_values = np.arange(0, 1001, 50)  # From 0 to 1000 RPS, incrementing by 50
lambda_costs = np.array([lambda_cost(rps) for rps in rps_values])
ec2_basic_costs_with_cloudwatch = np.array([ec2_basic_cost_with_cloudwatch(rps) for rps in rps_values])
ec2_basic_costs_without_cloudwatch = np.array([ec2_basic_cost_without_cloudwatch(rps) for rps in rps_values])
ec2_ha_costs = np.array([ec2_ha_cost(rps) for rps in rps_values])

# Define the intersection function
def find_intersection(func1, func2):
    return int(fsolve(lambda x: func1(x) - func2(x), 500)[0])

# Finding breakeven points
breakeven_lambda_ec2_basic_with_cloudwatch = find_intersection(lambda_cost, ec2_basic_cost_with_cloudwatch)
breakeven_lambda_ec2_basic_without_cloudwatch = find_intersection(lambda_cost, ec2_basic_cost_without_cloudwatch)
breakeven_lambda_ec2_ha = find_intersection(lambda_cost, ec2_ha_cost)

# Plotting
plt.figure(figsize=(12, 8))

# Lambda Costs
plt.plot(rps_values, lambda_costs, label='AWS Lambda', linestyle='--', color='orange')

# EC2 Basic Costs with CloudWatch
plt.plot(rps_values, ec2_basic_costs_with_cloudwatch, label='EC2 Basic + CloudWatch', linestyle='-', color='green')

# EC2 Basic Costs without CloudWatch
plt.plot(rps_values, ec2_basic_costs_without_cloudwatch, label='EC2 Basic', linestyle='-.', color='red')

# EC2 HA Costs
plt.plot(rps_values, ec2_ha_costs, label='EC2 High Availability', linestyle=':', color='blue')

# Annotations for breakeven points
plt.annotate(f'Breakeven EC2 Basic: {breakeven_lambda_ec2_basic_without_cloudwatch} RPS\nCost: ${lambda_cost(breakeven_lambda_ec2_basic_without_cloudwatch):.2f}',
             xy=(breakeven_lambda_ec2_basic_without_cloudwatch, lambda_cost(breakeven_lambda_ec2_basic_without_cloudwatch)),
             xytext=(breakeven_lambda_ec2_basic_without_cloudwatch + 200, lambda_cost(breakeven_lambda_ec2_basic_without_cloudwatch) + 10),
             arrowprops=dict(facecolor='black', arrowstyle='->'))

plt.annotate(f'Breakeven EC2 Basic + CloudWatch: {breakeven_lambda_ec2_basic_with_cloudwatch} RPS\nCost: ${lambda_cost(breakeven_lambda_ec2_basic_with_cloudwatch):.2f}',
             xy=(breakeven_lambda_ec2_basic_with_cloudwatch, lambda_cost(breakeven_lambda_ec2_basic_with_cloudwatch)),
             xytext=(breakeven_lambda_ec2_basic_with_cloudwatch + 200, lambda_cost(breakeven_lambda_ec2_basic_with_cloudwatch) + 50),
             arrowprops=dict(facecolor='black', arrowstyle='->'),
             rotation=5)

plt.annotate(f'Breakeven EC2 High Availability: {breakeven_lambda_ec2_ha} RPS\nCost: ${lambda_cost(breakeven_lambda_ec2_ha):.2f}',
             xy=(breakeven_lambda_ec2_ha, lambda_cost(breakeven_lambda_ec2_ha)),
             xytext=(breakeven_lambda_ec2_ha + 200, lambda_cost(breakeven_lambda_ec2_ha) + 300),
             arrowprops=dict(facecolor='black', arrowstyle='->'))

plt.xlabel('Requests Per Second (RPS)')
plt.ylabel('Monthly Cost (USD)')
plt.title('Cost Comparison: AWS Lambda vs EC2 in Different Scenarios')
plt.legend()
plt.grid(True)
plt.axhline(y=0, color='k')
plt.axvline(x=0, color='k')
plt.xticks(np.arange(0, 1001, 50))  # Set ticks on x-axis every 50 RPS units
plt.ylim(bottom=0)  # Ensure y-axis starts from 0
plt.xlim(0, 1000)  # Set x-axis limits from 0 to 1000

# Save the plot as a PNG file with the specified name
plt.savefig('aws_lambda_vs_ec2_cost_comparison.png')

plt.show()
