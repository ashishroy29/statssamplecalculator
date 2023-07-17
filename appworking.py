from flask import Flask, jsonify
from statsmodels.stats.proportion import proportion_effectsize
from scipy.stats import norm
import math

app = Flask(__name__)

def calculate_adjusted_sample_sizes():
    # Baseline conversion rate (control group)
    baseline_rate = 0.50

    # Expected minimum detectable effect size
    effect_size = 0.09

    # Desired statistical power (usually between 0.8 and 0.95)
    power = 0.90

    # Significance level (alpha)
    alpha = 0.05

    # Custom population size
    population_size = 896000

    # Stratified sampling factors (e.g., age, gender, location)
    strata_factors = ['age']  # , 'gender'

    # Stratified sampling proportions for each factor
    strata_proportions = {'age': [0.40, 0.39, 0.21]}  # , 'gender': [1.0,1.0]

    adjusted_sample_sizes = []

    for factor in strata_factors:
        p_control = baseline_rate * strata_proportions[factor][0]
        p_experiment = (baseline_rate + effect_size) * strata_proportions[factor][1]
        variance = p_control * (1 - p_control) + p_experiment * (1 - p_experiment)
        z_alpha = abs(norm.ppf(alpha / 2))
        z_beta = abs(norm.ppf(power))
        sample_size = (z_alpha * math.sqrt(variance) + z_beta * math.sqrt(variance + effect_size ** 2)) ** 2 / effect_size ** 2
        adjusted_sample_size = sample_size / (1 + (sample_size - 1) / population_size)
        adjusted_sample_sizes.append(adjusted_sample_size)

    return adjusted_sample_sizes

@app.route('/calculate_sample_sizes', methods=['GET'])
def get_adjusted_sample_sizes():
    adjusted_sample_sizes = calculate_adjusted_sample_sizes()
    return jsonify({'adjusted_sample_sizes': adjusted_sample_sizes})

if __name__ == '__main__':
    app.run()