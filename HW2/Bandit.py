"""Epsilon-Greedy and Thompson Sampling for four advertisements."""

from abc import ABC, abstractmethod
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from loguru import logger


BANDIT_REWARDS = [1, 2, 3, 4]
NUM_TRIALS = 20000
PRECISION = 1.0
SEED = 42
OUTPUT_DIR = Path(__file__).resolve().parent


class Bandit(ABC):
    ##==== DO NOT REMOVE ANYTHING FROM THIS CLASS ====##

    @abstractmethod
    def __init__(self, p):
        pass

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def pull(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def experiment(self):
        pass

    @abstractmethod
    def report(self):
        # store data in csv
        # print average reward (use f strings to make it informative)
        # print average regret (use f strings to make it informative)
        pass


class EpsilonGreedy(Bandit):
    """An advertisement arm with an estimated average reward."""

    def __init__(self, p):
        """Initialize the arm.

        Args:
          p: True mean reward of this ad.
        """
        self.p = p
        self.estimate = 0.0
        self.N = 0

    def __repr__(self):
        """Return the arm's true mean and current estimate."""
        return f"EpsilonGreedy(mean={self.p}, estimate={self.estimate:.3f})"

    def pull(self):
        """Generate a normal reward with mean p and variance 1."""
        return np.random.randn() + self.p

    def update(self, reward):
        """Update the sample mean after observing one reward.

        Args:
          reward: Observed reward from the selected ad.

        Returns:

        """
        self.N += 1
        self.estimate += (reward - self.estimate) / self.N

    def experiment(self, bandits, num_trials):
        """Run Epsilon-Greedy with epsilon equal to 1/t.

        Args:
          bandits: List of the four advertisement arms.
          num_trials: Number of trials.

        Returns:
          : Selected ads, rewards, and the estimate history.

        """
        rewards = np.zeros(num_trials)
        choices = np.zeros(num_trials, dtype=int)
        history = np.zeros((num_trials, len(bandits)))

        for t in range(1, num_trials + 1):
            epsilon = 1 / t
            if np.random.random() < epsilon:
                j = np.random.randint(len(bandits))
            else:
                j = np.argmax([b.estimate for b in bandits])

            reward = bandits[j].pull()
            bandits[j].update(reward)
            rewards[t - 1] = reward
            choices[t - 1] = j + 1
            history[t - 1] = [b.estimate for b in bandits]

        return choices, rewards, history

    def report(self, choices, rewards, best_mean, csv_path, append=False):
        """Save the rewards to CSV and log reward and regret totals.

        Args:
          choices: Selected ad numbers, from 1 to 4.
          rewards: Observed rewards, one per trial.
          best_mean: True mean reward of the best ad.
          csv_path: Destination of the combined rewards CSV.
          append: Append without a header when the first algorithm is saved. (Default value = False)

        Returns:
          : DataFrame with Bandit, Reward, and Algorithm columns.

        """
        total_reward = rewards.sum()
        total_regret = np.sum(best_mean - np.array(BANDIT_REWARDS)[choices - 1])
        logger.info(f"Epsilon-Greedy cumulative reward: {total_reward:.2f}")
        logger.info(f"Epsilon-Greedy cumulative regret: {total_regret:.2f}")
        logger.info(f"Epsilon-Greedy average reward: {rewards.mean():.4f}")
        logger.info(f"Epsilon-Greedy average regret: {total_regret / len(rewards):.4f}")
        data = pd.DataFrame({"Bandit": choices, "Reward": rewards,
                             "Algorithm": "EpsilonGreedy"})
        data.to_csv(csv_path, index=False, mode="a" if append else "w", header=not append)
        logger.info(f"Saved {len(data)} Epsilon-Greedy rewards to {csv_path.name}")
        return data


class ThompsonSampling(Bandit):
    """An advertisement arm with a normal posterior for its mean."""

    def __init__(self, p, precision=1.0):
        """Initialize the arm with a Normal(0, 1) prior.

        Args:
          p: True mean reward of this ad.
          precision: Known inverse reward variance, set to 1.
        """
        self.p = p
        self.precision = precision
        self.estimate = 0.0
        self.posterior_precision = 1.0
        self.N = 0

    def __repr__(self):
        """Return the arm's true mean and posterior mean."""
        return f"ThompsonSampling(mean={self.p}, estimate={self.estimate:.3f})"

    def pull(self):
        """Generate a normal reward with the known precision."""
        return np.random.randn() / np.sqrt(self.precision) + self.p

    def sample(self):
        """Draw one possible mean from the current posterior."""
        return np.random.randn() / np.sqrt(self.posterior_precision) + self.estimate

    def update(self, reward):
        """Update the posterior mean and precision using the new reward.

        Args:
          reward: Observed reward from the selected ad.

        Returns:

        """
        new_precision = self.posterior_precision + self.precision
        self.estimate = (
            self.posterior_precision * self.estimate + self.precision * reward
        ) / new_precision
        self.posterior_precision = new_precision
        self.N += 1

    def experiment(self, bandits, num_trials):
        """Select the highest posterior sample and update its arm each trial.

        Args:
          bandits: List of the four advertisement arms.
          num_trials: Number of trials.

        Returns:
          : Selected ads, rewards, and the estimate history.

        """
        rewards = np.zeros(num_trials)
        choices = np.zeros(num_trials, dtype=int)
        history = np.zeros((num_trials, len(bandits)))

        for t in range(num_trials):
            j = np.argmax([b.sample() for b in bandits])
            reward = bandits[j].pull()
            bandits[j].update(reward)
            rewards[t] = reward
            choices[t] = j + 1
            history[t] = [b.estimate for b in bandits]

        return choices, rewards, history

    def report(self, choices, rewards, best_mean, csv_path, append=False):
        """Save the rewards to CSV and log reward and regret totals.

        Args:
          choices: Selected ad numbers, from 1 to 4.
          rewards: Observed rewards, one per trial.
          best_mean: True mean reward of the best ad.
          csv_path: Destination of the combined rewards CSV.
          append: Append without a header when the first algorithm is saved. (Default value = False)

        Returns:
          : DataFrame with Bandit, Reward, and Algorithm columns.

        """
        total_reward = rewards.sum()
        total_regret = np.sum(best_mean - np.array(BANDIT_REWARDS)[choices - 1])
        logger.info(f"Thompson Sampling cumulative reward: {total_reward:.2f}")
        logger.info(f"Thompson Sampling cumulative regret: {total_regret:.2f}")
        logger.info(f"Thompson Sampling average reward: {rewards.mean():.4f}")
        logger.info(f"Thompson Sampling average regret: {total_regret / len(rewards):.4f}")
        data = pd.DataFrame({"Bandit": choices, "Reward": rewards,
                             "Algorithm": "ThompsonSampling"})
        data.to_csv(csv_path, index=False, mode="a" if append else "w", header=not append)
        logger.info(f"Saved {len(data)} Thompson Sampling rewards to {csv_path.name}")
        return data


class Visualization:
    """Save plots of the learning process and the algorithm comparison."""

    def __init__(self, output_dir):
        """Create the folder for the two required figures.

        Args:
          output_dir: Directory where the plot images will be saved.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot1(self, eg_history, ts_history, means):
        """Plot each arm's estimate on linear and logarithmic trial axes.

        Args:
          eg_history: Epsilon-Greedy estimates after each trial.
          ts_history: Thompson Sampling estimates after each trial.
          means: True mean rewards of the four ads.

        Returns:

        """
        fig, axes = plt.subplots(2, 2, figsize=(12, 7))
        for row, (name, history) in enumerate([
            ("Epsilon-Greedy", eg_history), ("Thompson Sampling", ts_history)
        ]):
            for col, scale in enumerate(["linear", "log"]):
                ax = axes[row, col]
                for j, mean in enumerate(means):
                    ax.plot(np.arange(1, len(history) + 1), history[:, j],
                            label=f"Ad {j + 1}: true mean {mean}")
                ax.set_xscale(scale)
                ax.set_title(f"{name}: {scale} scale")
                ax.set_xlabel("Trial")
                ax.set_ylabel("Estimated mean reward")
                ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(self.output_dir / "learning_process.png", dpi=150)
        plt.close(fig)
        logger.info("Saved plots/learning_process.png")

    def plot2(self, eg_rewards, ts_rewards, eg_choices, ts_choices, best_mean):
        """Compare cumulative rewards and cumulative regrets.

        Args:
          eg_rewards: Observed rewards, one per trial.
          ts_rewards: Observed rewards, one per trial.
          eg_choices: Ad numbers selected by Epsilon-Greedy.
          ts_choices: Ad numbers selected by Thompson Sampling.
          best_mean: True mean reward of the best ad.

        Returns:

        """
        trials = np.arange(1, len(eg_rewards) + 1)
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        for name, rewards, choices in [("Epsilon-Greedy", eg_rewards, eg_choices),
                                       ("Thompson Sampling", ts_rewards, ts_choices)]:
            cumulative_rewards = np.cumsum(rewards)
            cumulative_regret = np.cumsum(best_mean - np.array(BANDIT_REWARDS)[choices - 1])
            axes[0].plot(trials, cumulative_rewards, label=name)
            axes[1].plot(trials, cumulative_regret, label=name)
        for ax, title in zip(axes, ["Cumulative reward", "Cumulative regret"]):
            ax.set_title(title)
            ax.set_xlabel("Trial")
            ax.set_ylabel(title)
            ax.legend()
        fig.tight_layout()
        fig.savefig(self.output_dir / "cumulative_comparison.png", dpi=150)
        plt.close(fig)
        logger.info("Saved plots/cumulative_comparison.png")


def comparison(eg_rewards, ts_rewards, eg_choices, ts_choices, best_mean, output_dir):
    """Save a visual comparison of the two completed experiments.

    Args:
      eg_rewards: Observed rewards, one per trial.
      ts_rewards: Observed rewards, one per trial.
      eg_choices: Ad numbers selected by Epsilon-Greedy.
      ts_choices: Ad numbers selected by Thompson Sampling.
      best_mean: True mean reward of the best ad.
      output_dir: Directory where the comparison plot will be saved.

    Returns:

    """
    Visualization(output_dir).plot2(eg_rewards, ts_rewards, eg_choices, ts_choices, best_mean)


def main():
    """Run both experiments, save the CSV and plots, and log the results."""
    csv_path = OUTPUT_DIR / "rewards.csv"
    plots_dir = OUTPUT_DIR / "plots"
    best_mean = max(BANDIT_REWARDS)

    logger.info(f"Running Epsilon-Greedy: {NUM_TRIALS} trials, epsilon = 1/t")
    np.random.seed(SEED)
    eg_bandits = [EpsilonGreedy(mean) for mean in BANDIT_REWARDS]
    eg_choices, eg_rewards, eg_history = eg_bandits[0].experiment(eg_bandits, NUM_TRIALS)
    eg_bandits[0].report(eg_choices, eg_rewards, best_mean, csv_path)
    logger.debug(f"Epsilon-Greedy pulls per ad: {[b.N for b in eg_bandits]}")

    logger.info(f"Running Thompson Sampling: {NUM_TRIALS} trials, precision = {PRECISION}")
    np.random.seed(SEED)
    ts_bandits = [ThompsonSampling(mean, PRECISION) for mean in BANDIT_REWARDS]
    ts_choices, ts_rewards, ts_history = ts_bandits[0].experiment(ts_bandits, NUM_TRIALS)
    ts_bandits[0].report(ts_choices, ts_rewards, best_mean, csv_path, append=True)
    logger.debug(f"Thompson Sampling pulls per ad: {[b.N for b in ts_bandits]}")

    Visualization(plots_dir).plot1(eg_history, ts_history, BANDIT_REWARDS)
    comparison(eg_rewards, ts_rewards, eg_choices, ts_choices, best_mean, plots_dir)
    logger.success("Finished both experiments. Saved rewards.csv and two figures in plots/.")


if __name__ == "__main__":
    main()
