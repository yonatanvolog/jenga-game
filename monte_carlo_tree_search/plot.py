import itertools
from matplotlib import pyplot as plt
import utils
from adversary.adversary import Adversary
from adversary.strategy import RandomStrategy, OptimisticStrategy, PessimisticStrategy
from environment.environment import Environment
from monte_carlo_tree_search.mcts_agent import MCTSAgent


def plot_winrate(agent, env, strategies, num_games):
    """
    Plays games with the agent against different strategies and plots the win rate as a bar chart after a fixed number of games.

    Args:
        agent (MCTSAgent): The MCTS agent to play against.
        env (Environment): Jenga environment.
        strategies (list): A list of strategies to test against.
        num_games (int): The number of games to play for each strategy.

    Returns:
        None
    """
    win_rates = []

    for strategy in strategies:
        strategy_name = strategy.__class__.__name__
        print(f"Playing {num_games} games against {strategy_name}...")
        win_rate = evaluate_winrate(agent, env, strategy, num_games)
        win_rates.append(win_rate)
        print(f"Win rate against {strategy_name} after {num_games} games: {win_rate:.2f}")

    # Bar plot of win rates
    strategy_names = [strategy.__class__.__name__ for strategy in strategies]
    plt.figure(figsize=(10, 6))
    plt.bar(strategy_names, win_rates, color=['blue', 'green', 'orange'])
    plt.xlabel('Strategy')
    plt.ylabel('Win Rate')
    plt.title(f'Win Rate After {num_games} Games Against Different Strategies')
    plt.ylim(0, 1)
    plt.grid(axis='y', linestyle='--')
    plt.savefig("mcts_winrate_against_strategies.png")


def evaluate_winrate(agent, env, strategy, num_games):
    """
    Evaluates the win rate of the MCTS agent against a specific strategy.

    Args:
        agent (MCTSAgent): The agent to be tested.
        env (Environment): Jenga environment.
        strategy (Strategy): The adversary strategy to evaluate against.
        num_games (int): Number of test games.

    Returns:
        float: The win rate of the agent against the strategy.
    """
    wins = 0
    adversary = Adversary(strategy=strategy)
    initial_state = utils.get_state_from_image(env.get_screenshot())

    for i in range(1, num_games + 1):
        print(f"Starting game {i}")
        env.reset()
        taken_actions = set()  # Reset the actions taken
        state = initial_state

        for _ in itertools.count():
            # Agent's turn
            agent_action = agent.select_action(state, taken_actions)
            if agent_action is None:
                print("No actions to take. Stopping this game")
                break
            print(f"Agent chose action {agent_action}")

            screenshot_filename, is_fallen = env.step(utils.format_action(agent_action))
            if is_fallen:
                wins += 1
                print("The tower is fallen. Stopping this game")
                break
            state = utils.get_state_from_image(screenshot_filename)
            taken_actions.add(agent_action)

            # Adversary's turn
            adversary_action = adversary.select_action(state, taken_actions, agent_action)
            if adversary_action is None:
                wins += 1
                print("No actions to take. Stopping this game")
                break
            print(f"Adversary chose action {adversary_action}")

            screenshot_filename, is_fallen = env.step(utils.format_action(adversary_action))
            if is_fallen:
                print("The tower is fallen. Stopping this game")
                break
            state = utils.get_state_from_image(screenshot_filename)
            taken_actions.add(adversary_action)

    win_rate = wins / num_games
    return win_rate


def plot_mcts_winrate():
    """
    Plays games with the MCTS agent against different strategies and plots the win rate.
    """
    env = Environment()
    agent = MCTSAgent(env)
    strategies = [RandomStrategy(), OptimisticStrategy(), PessimisticStrategy()]
    num_games = 15  # Fixed number of games to measure the win rate for each strategy

    plot_winrate(agent, env, strategies, num_games)


if __name__ == "__main__":
    plot_mcts_winrate()