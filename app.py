from flask import Flask, jsonify, render_template, request
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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        baseline_rate = float(request.form['baseline_rate'])
        effect_size = float(request.form['effect_size'])
        power = float(request.form['power'])
        alpha = float(request.form['alpha'])
        population_size = int(request.form['population_size'])
        strata_factors = [factor.strip() for factor in request.form['strata_factors'].split(',')]
        strata_proportions = {}
        for factor in strata_factors:
            strata_proportions[factor] = [float(prop.strip()) for prop in request.form[f'{factor}_proportions'].split(',')]

        adjusted_sample_sizes = calculate_adjusted_sample_sizes(
            baseline_rate, effect_size, power, alpha, population_size, strata_factors, strata_proportions
        )

        return render_template('output.html', adjusted_sample_sizes=adjusted_sample_sizes)
    else:
        return render_template('input.html')

if __name__ == '__main__':
    app.run()
