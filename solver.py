from __future__ import annotations
import random
from typing import List
import numpy as np

class Solver:
    # some features that can be implemented:
    # - other search methods (simulated annealing, genetic algorithm...)
    # - optional search trace (solutions generated in each iterations with goal functions) - now everything is printed

    def __init__(self, all_fights_results: np.array):
        self.team_results_history = np.zeros((1, 7))
        self.fights = all_fights_results

    def random_search(self, iterations: int = 100) -> (float, List[int]):
        team = PokemonTeam(self.fights)
        best_team = team.copy()
        best_score = 0.0
        for i in range(iterations):
            team_results = team.goal_function()
            score = team_results[0][-1]
            self.team_results_history = np.append(self.team_results_history, team_results, axis=0)
            print(f"{i}: team {team}, scores: {score}") #" best pokemon index: {team.best_pokemon_index()}")
            if score > best_score:
                print(f"updating best score ({score} > {best_score})")
                best_score = score
                best_team = team.copy()
            team = team.random_neighbor()
        return best_score, best_team

    def get_team_results_history(self):
        return self.team_results_history


class PokemonTeam(list):
    all_fights_results: np.array = np.empty(0)
    number_of_all_pokemons: int = 0
    default_team_size: int = 6

    @classmethod
    def initialize_global(cls, all_fights_results: np.array):
        number_of_all_pokemons = all_fights_results.shape[0]
        if number_of_all_pokemons <= cls.default_team_size:
            raise ValueError(f"number of all pokemons (got {number_of_all_pokemons}) " +
                             f"must be greater than default team size ({cls.default_team_size})")
        if all_fights_results.shape != (number_of_all_pokemons, number_of_all_pokemons):
            raise ValueError(f"all_fights_results array should be square matrix, got shape {all_fights_results.shape}")
        cls.all_fights_results = all_fights_results
        cls.number_of_all_pokemons = number_of_all_pokemons

    def __init__(self, indices_in_team: List[int] = None):
        if indices_in_team is None:
            super().__init__(range(self.default_team_size))
        else:
            if len(indices_in_team) >= self.number_of_all_pokemons:
                raise ValueError(f"cannot initialize pokemon team - team size (got {len(indices_in_team)}) " +
                                 f"must be less than number of all pokemons (got {self.number_of_all_pokemons})")
            super().__init__(indices_in_team)

    def random_neighbor(self) -> PokemonTeam:
        index_to_be_replaced = random.randrange(len(self))
        new_pokemon_index = self.random_index_outside_of_team()
        new_team = self.copy()
        new_team[index_to_be_replaced] = new_pokemon_index
        return new_team

    def random_index_outside_of_team(self) -> int:
        index_in_enemies_list = random.randrange(self.number_of_all_pokemons - len(self))
        for index_in_pokemons_list in range(self.number_of_all_pokemons):
            if index_in_enemies_list == 0:
                return index_in_pokemons_list
            if index_in_pokemons_list not in self:
                index_in_enemies_list -= 1
        raise RuntimeError("this code should be unreachable")

    def goal_function(self) -> np.array:
        team_score = np.zeros(len(self) + 1)
        for enemy_index in range(self.number_of_all_pokemons):
            fight_result = self.score_fights(enemy_index)
            team_score[:-1] = np.add(team_score[:-1], fight_result)
            team_score[-1] += np.sum(fight_result)/len(self)
        return team_score.reshape((1, len(self) + 1))

    def score_fights(self, enemy_index: int) -> np.array:
        points_against_given_enemy = np.empty(len(self))
        for list_index, pokemon_index in enumerate(self):
            points_against_given_enemy[list_index] = self.all_fights_results[pokemon_index, enemy_index]
        return points_against_given_enemy
