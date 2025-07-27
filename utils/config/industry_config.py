"""
Industry classification and Bayesian model parameters configuration.
"""

# Industry Classifications
INDUSTRY_MAPPINGS = {
    'TECH': ['AAPL', 'MSFT', 'META', ...],
    'FINANCE': ['JPM', 'BAC', ...],
    # ... other industries
}

# Bayesian Model Parameters
MODEL_CONFIG = {
    'prior_settings': {
        'industry_variance': 0.02,  # Prior for industry-level variance
        'stock_variance': 0.05,     # Prior for stock-specific variance
        'sentiment_weight': 0.6,    # Initial weight for sentiment
    },
    'mcmc_settings': {
        'chains': 4,
        'tune': 1000,
        'draws': 2000,
        'target_accept': 0.8,
    },
    'time_windows': {
        'sentiment_lag': 7,     # Days of sentiment history
        'prediction_window': 7  # Forward prediction days
    },
    'storage': {
        'posterior_dir': 'results/posterior_data',
        'history_quarters': 20,
        'save_full_posterior': True
    }
} 