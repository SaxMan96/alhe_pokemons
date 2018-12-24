import csv
from typing import Dict, Set
import numpy as np


class Pokemon:
    def __init__(self, row):
        self.name = row[0]
        self.pokedex_number = int(row[1])
        self.generation = int(row[2])
        self.is_legendary = bool(int(row[3]))
        self.types = [row[4]]
        if row[5]:
            self.types.append(row[5])
        self.health = int(row[6])
        self.attack = int(row[7])
        self.defense = int(row[8])
        self.special_attack = int(row[9])
        self.special_defense = int(row[10])
        self.speed = int(row[11])
        self.base_total = int(row[12])
        self.vulnerability_against = {
            "bug": float(row[13]),
            "dark": float(row[14]),
            "dragon": float(row[15]),
            "electric": float(row[16]),
            "fairy": float(row[17]),
            "fight": float(row[18]),
            "fire": float(row[19]),
            "flying": float(row[20]),
            "ghost": float(row[21]),
            "grass": float(row[22]),
            "ground": float(row[23]),
            "ice": float(row[24]),
            "normal": float(row[25]),
            "poison": float(row[26]),
            "psychic": float(row[27]),
            "rock": float(row[28]),
            "steel": float(row[29]),
            "water": float(row[30]),
        }
        self.capture_rate = int(row[31])

    def get_damage_taken_multiplier(self, enemy) -> float:
        return max(self.vulnerability_against[enemy_type] for enemy_type in enemy.types)

    def get_number_of_turns_to_get_killed(self, enemy) -> float:
        defense_coefficient = 10
        damage_taken = (enemy.attack * self.get_damage_taken_multiplier(enemy)) / (defense_coefficient * self.defense)
        return self.health/damage_taken

    def score_fight(self, enemy) -> float:
        turns_to_kill_enemy = np.ceil(enemy.get_number_of_turns_to_get_killed(self))
        turns_to_get_killed = np.ceil(self.get_number_of_turns_to_get_killed(enemy))
        if turns_to_kill_enemy < turns_to_get_killed:
            return 1.0  # 'self' wins
        if turns_to_kill_enemy > turns_to_get_killed:
            return 0.0  # 'self' loses
        return 0.5  # draw

    def type_as_one_string(self):
        return ' '.join(sorted(self.types))

    def get_useful_numeric_parameters(self) -> np.array:
        return np.array([
            self.health,
            self.attack,
            self.defense,
            self.vulnerability_against["bug"],
            self.vulnerability_against["dark"],
            self.vulnerability_against["dragon"],
            self.vulnerability_against["electric"],
            self.vulnerability_against["fairy"],
            self.vulnerability_against["fight"],
            self.vulnerability_against["fire"],
            self.vulnerability_against["flying"],
            self.vulnerability_against["ghost"],
            self.vulnerability_against["grass"],
            self.vulnerability_against["ground"],
            self.vulnerability_against["ice"],
            self.vulnerability_against["normal"],
            self.vulnerability_against["poison"],
            self.vulnerability_against["psychic"],
            self.vulnerability_against["rock"],
            self.vulnerability_against["steel"],
            self.vulnerability_against["water"],
            self.capture_rate
        ])


class PokemonList(list):
    @classmethod
    def from_file(cls, filename="data.csv"):
        pokemon_list = cls()
        with open(filename, newline='') as file:
            reader = csv.reader(file, delimiter=';')
            iter_reader = iter(reader)
            next(iter_reader)
            for row in iter_reader:
                pokemon_list.append(Pokemon(row))
        return pokemon_list

    def to_numpy_array(self) -> np.array:
        all_types = set(pokemon.type_as_one_string() for pokemon in self)
        types_to_float_map = map_strings_to_numbers(all_types)
        max_numeric_values = self.max_values_of_useful_numeric_parameters()
        data = np.empty((len(self), max_numeric_values.size + 1))
        for index, pokemon in enumerate(self):
            data[index, 0] = types_to_float_map[pokemon.type_as_one_string()]
            data[index, 1:] = np.true_divide(pokemon.get_useful_numeric_parameters(), max_numeric_values)
        return data

    def max_values_of_useful_numeric_parameters(self) -> np.array:
        array = self[0].get_useful_numeric_parameters()
        for pokemon in self[1:]:
            array = np.maximum(array, pokemon.get_useful_numeric_parameters())
        return array

def map_strings_to_numbers(strings: Set[str]) -> Dict[str, float]:
    step = 1.0 / len(strings)
    number = 1.0
    retval = {}
    for string in sorted(list(strings)):
        retval[string] = number
        number -= step
    return retval
