# Marketing Analytics - Homework 2

Roman Ghukasyan | GH3781001

This experiment compares Epsilon-Greedy and Thompson Sampling for four advertisements with mean rewards `[1, 2, 3, 4]`. Each algorithm runs for 20,000 trials with normal rewards of variance 1. Epsilon-Greedy uses epsilon `1/t`. Thompson Sampling uses known precision 1 and a Normal(0, 1) prior for each ad's mean. The random seed is 42.

## Run

```bash
pip install -r requirements.txt
python Bandit.py
```

`Bandit.py` runs both experiments, logs cumulative and average rewards and regrets, writes `rewards.csv`, and saves the figures in `plots/`. Running it again replaces the previous results.

## Files

- `Bandit.py`: the main implementation and executable workflow. The supplied abstract `Bandit` class is preserved, and both subclasses implement its required methods. The code is documented with Pyment-generated docstrings completed with parameter descriptions.
- `HW2.ipynb`: runs the same workflow and presents the plots, short discussion, and bonus proposal.
- `rewards.csv`: 40,000 observations with columns `Bandit`, `Reward`, and `Algorithm`. Ads are numbered 1 to 4.
- `plots/learning_process.png`: estimated mean rewards for all ads on linear and logarithmic trial axes.
- `plots/cumulative_comparison.png`: cumulative rewards and cumulative regrets for both algorithms.

Cumulative regret is the sum of `4 - true_mean_of_selected_ad` over all trials. It measures the expected reward lost by selecting weaker ads and is nonnegative.
