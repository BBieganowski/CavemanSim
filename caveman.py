import numpy as np
import pandas as pd

class Caveman():
    def __init__(self, id: int, sex = np.random.choice(['M', 'F']), age = np.random.randint(18, 30), selfishness = np.random.randint(1, 100), base_prowess = np.random.randint(1, 100), food_to_share = 0, is_taken = False, hunger = 50, active = True):
        # Unique identifier for each caveman
        self.id = id
        self.name = pd.read_csv('names.csv').sample(1).values[0][0]
        # Caveman traits
        self.sex = np.random.choice(['M', 'F'])
        
        self.age = age

        # Selfishness describes how unlikely it is that a caveman will share food
        # with another caveman
        self.selfishness = np.random.randint(1, 100)
        
        # Reciprocity describes how likely it is that a caveman will share food
        # with another caveman
        self.reciprocity = 100 - self.selfishness
        
        # Prowess describes how likely it is that a caveman will get food
        # when hunting
        self.base_prowess = np.random.randint(1, 100)
        
        # Prowess is updated each turn based prowess and hunger
        self.prowess = self.base_prowess

        # Food to share is the amount of food that a caveman is willing to share at the end of the turn
        self.food_to_share = 0

        self.is_taken = False

        self.hunger = 50
        self.active = True

    def update_state(self):
        self.hunger += 10
        if self.hunger > 100:
            self.hunger = 100
            self.die_hunger()

        self.age += 1
        if self.age > 50:
            if np.random.uniform(0, 1) < 0.2:
                self.die_old()

        self.prowess = self.base_prowess - self.hunger

    def die_hunger(self):
        print(f'Caveman {self.name} has died of hunger')
        self.active = False
        self.death_cause = 'hunger'

    def die_old(self):
        print(f'Caveman {self.name} has happily died of old age')
        self.active = False
        self.death_cause = 'old'

    def __repr__(self) -> str:
        return f"Caveman no. {self.id} of sex {self.sex} and age {self.age} with hunger level of {self.hunger}, prowess of {self.prowess} and reciprocity of {self.reciprocity}."