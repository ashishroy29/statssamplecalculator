from flask import Flask, jsonify, request, render_template
from statsmodels.stats.proportion import proportion_effectsize
from scipy.stats import norm
import math

app = Flask(__name__)

def calculate_adjusted_sample_sizes(baseline_rate, effect_size, power, alpha, population_size, strata_factors, strata_proportions):
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate_sample_sizes', methods=['POST'])
def get_adjusted_sample_sizes():
    data = request.form

    baseline_rate = float(data['baseline_rate'])
    effect_size = float(data['effect_size'])
    power = float(data['power'])
    alpha = float(data['alpha'])
    population_size = float(data['population_size'])
    strata_factors = data['strata_factors'].split(',')
    
    strata_proportions_raw = data['strata_proportions'].split('\r\n')
    strata_proportions = {}
    for line in strata_proportions_raw:
        factor, p1, p2 = line.split(',')
        strata_proportions[factor] = [float(p1), float(p2)]

    adjusted_sample_sizes = calculate_adjusted_sample_sizes(
        baseline_rate, effect_size, power, alpha, population_size, strata_factors, strata_proportions
    )

    return jsonify({'adjusted_sample_sizes': adjusted_sample_sizes})

if __name__ == '__main__':
    app.run()