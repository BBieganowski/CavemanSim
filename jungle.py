import numpy as np
import pandas as pd
from caveman import Caveman
import random

class Jungle():
    def __init__(self, num_cavemen: int, food_supply: float):

        # Population is a list of cavemen currently in the jungle
        self.population = [Caveman(i) for i in range(num_cavemen)]
        
        # Current max_id is useful if we want to add new cavemen to the jungle
        # during the simulation
        self.max_id = num_cavemen
        
        # Food supply is a float representing the amount of food in the jungle
        # 1.0 being the exact amount of food needed to sustain the current population
        self.food_supply = food_supply

        # Current food is the amount of food currently in the jungle - this is updated each turn
        # and is equal to the food supply multiplied by the number of cavemen in the jungle
        self.current_food = int(self.food_supply * len(self.population))

        # Food in belly vs hunger function is a function that takes amount of food currently in the belly
        # of a caveman and returns the amount of hunger that the caveman has
        # Useful for sharing and consumption calculation
        self.fib_hunger_function = lambda x: 100*(x-1)**2


        # Hunger vs food in belly function is a function that takes the amount of hunger that a caveman has
        # and returns the amount of food in the belly of the caveman
        # Useful for updating the hunger of a caveman
        self.hunger_fib_function = lambda x: 1 - np.sqrt(x/100)

        # Year is the current year of the simulation
        self.year = 1

        # Relationships grid is a 2D array that stores the relationships between each caveman
        # The value at index (i, j) is the relationship between caveman i and caveman j
        self.relationships_grid = np.zeros((len(self.population), len(self.population)))

        # Each year, each couple has a x% chance of having a baby
        # Initially set at zero, updated each year based on global hunger level.
        self.reproduction_rate = 0.0

        # Couples is a list of tuples that stores the families in the jungle
        self.couples = []


        # Dictionary of summary statistics by year
        self.statistics = {"Population":[],
                           "Adults":[],
                           "Children":[],
                           "Singles":[],
                           "Taken":[],
                           "Hunger Deaths":[],
                           "Old Age Deaths": [],
                           "Average Age":[],
                           "Average Hunger":[],
                           "Average Prowess":[],
                            "Average Selfishness":[],
                            "Average Reciprocity":[],
                           }
        

        self.old_age_deaths = 0
        self.hunger_deaths = 0

    def advance_year(self):
        # Advance year is the main function that advances the simulation by one year
        print(f"\n#### Year {self.year} ####")
        self.foraging_stage()
        self.sharing_stage()
        self.update_all_cavemen()
        self.social_stage()
        self.reproduction_stage()
        random.shuffle(self.population)
        self.update_statistics()
        self.year += 1     

    def update_all_cavemen(self):
        # Update all cavemen in the jungle
        for caveman in self.population:
            caveman.update_state()
            if caveman.active == False:
                self.population.remove(caveman)
                if caveman.death_cause == 'old':
                    self.old_age_deaths += 1
                else:
                    self.hunger_deaths += 1

    def foraging_stage(self):
        # Foraging stage is where each caveman hunts for food
        print("\n#### FORAGING STAGE ####")
        pops = self.get_population_dataframe()
        if pops is None:
            print("No one is alive!")
            return None
        
        # Chance of getting food is a function of prowess along with some randomness
        pops['food_get_chance'] = ((pops['prowess'] / 100) + np.random.normal(0, 0.1, len(pops))).clip(0, 1)

        # Children have a 0% chance of getting food
        pops.loc[pops['age'] < 12, 'food_get_chance'] = 0


        pops = pops.sort_values(by='food_get_chance', ascending=False)
        pops['food_gained'] = 0

        for i in range(self.current_food):
            idx = i % len(pops)
            pops.iloc[idx, pops.columns.get_loc('food_gained')] += 1

        # Food eaten is a function of hunger and selfishness
        pops['food_eaten_desired'] = (pops['selfishness'] / 100)*0.7 + (pops['hunger'] / 100)*0.3
        
        # If he is the last person alive, just let him eat all the food he wants :(
        # Otherwise, he can only eat the minimum of the food he wants and the food he's got
        if len (pops) > 1:
            pops['food_eaten'] = np.min([pops['food_gained'], pops['food_eaten_desired']], axis=0)
        else:
            pops['food_eaten'] = pops['food_gained']
        
        # Food to share is the food he has left over after eating
        pops['food_to_share'] = pops['food_gained'] - pops['food_eaten']

        # Update global hunger levels and log eating actions
        for caveman in self.population:
            idx = caveman.id
            eaten = pops.loc[idx, 'food_eaten']

            caveman.hunger = self.hunger_level_update(caveman.hunger, eaten)
            caveman.hunger = max(caveman.hunger, 0)
            print(f"Caveman {caveman.name} ({caveman.sex}) ate {eaten:.2f} food and is now at hunger {caveman.hunger:.2f}.")

            # Update global food to share
            to_share = pops.loc[idx, 'food_to_share']
            caveman.food_to_share = to_share
    
    def sharing_stage(self):
        print("\n#### SHARING STAGE ####")
        for caveman in self.population:
            # Get the relationships of this caveman
            relationships = self.relationships_grid[caveman.id]
            # As long as this caveman has food to share, keep sharing
            while caveman.food_to_share > 0:
                # rank the other cavemen by their relationship with this caveman
                # and share food with the one with the highest relationship
                relationship_ranking = np.argsort(relationships)


                max_sharings = min(len(relationship_ranking), np.inf)

                # Iterate through the cavemen in order of relationship
                for i in range(max_sharings):
                    other_caveman_id = relationship_ranking[i]
                    
                    # Don't share with dead cavemen
                    try:
                        other_caveman = [caveman for caveman in self.population if caveman.id == other_caveman_id][0]
                    except:
                        continue

                    # Don't share with yourself
                    if other_caveman_id == caveman.id:
                        continue
                
                    
                    # If the other caveman has hunger and this caveman has food to
                    # share, share food
                    if other_caveman.hunger > 0 and caveman.food_to_share > 0:
                        food_to_remove_hunger = self.food_to_remove_hunger(other_caveman.hunger)
                        food_shared = min(food_to_remove_hunger, caveman.food_to_share)
                        caveman.food_to_share -= food_shared
                        
                        self.relationships_grid[caveman.id, other_caveman.id] += self.relationship_level_update(other_caveman.hunger, food_shared)

                        other_caveman.hunger = self.hunger_level_update(other_caveman.hunger, food_shared)
                        other_caveman.hunger = max(other_caveman.hunger, 0)
                        
                        print(f"\nCaveman {caveman.name} ({caveman.sex}) shared {food_shared:.2f} food with caveman {other_caveman.name} ({other_caveman.sex}) and {other_caveman.name} now at hunger {other_caveman.hunger:.2f}.")
                        print(f"Relationship between {caveman.name} and {other_caveman.name} is now {self.relationships_grid[caveman.id, other_caveman.id]:.2f}.")
                
                    if caveman.food_to_share == 0:
                        break
                break
                        
    def social_stage(self):
        print("\n#### SOCIAL STAGE ####")
        female_caveman = [caveman for caveman in self.population if caveman.sex == "F"]
        not_hungry_females = [caveman for caveman in female_caveman if caveman.hunger < 30]

        print(f"There are currently {len(not_hungry_females)} non-hungry females in the jungle.")

        male_caveman = [caveman for caveman in self.population if caveman.sex == "M"]
        not_hungry_male_ids = [caveman.id for caveman in male_caveman if caveman.hunger < 30]
        
        print(f"There are currently {len(not_hungry_male_ids)} non-hungry males in the jungle.")

        for female in not_hungry_females:
            if female.is_taken or female.age < 16:
                continue
            top_relationships = np.argsort(self.relationships_grid[female.id])
            for i in np.flip(top_relationships):
                # Check if relationship is high enough
                if self.relationships_grid[female.id][i] > 10:
                    if i in not_hungry_male_ids:
                        if self.get_caveman_by_id(i).is_taken or self.get_caveman_by_id(i).age < 16:
                            continue
                        self.couples.append((female.id, i))
                        self.relationships_grid[female.id, i] += 10
                        female.is_taken = True
                        self.get_caveman_by_id(i).is_taken = True
                        print(f"Caveman {female.name} (F) and caveman {self.get_caveman_by_id(i).name} (M) have formed a family!")
                        break    

    def reproduction_stage(self):
        print("\n#### REPRODUCTION STAGE ####")
        
        # Updating reproduction rate based on global hunger level
        average_hunger = np.mean([caveman.hunger for caveman in self.population])
        self.reproduction_rate = (-0.01*average_hunger) + 0.5
        print(f"Average hunger is {average_hunger:.2f} and reproduction rate is {self.reproduction_rate:.2f}.")

        # Reproduction itself
        for i in self.couples:

            try:
                parent1 = self.get_caveman_by_id(i[0])
                parent2 = self.get_caveman_by_id(i[1])
            except IndexError:
                continue


            if np.random.rand() < self.reproduction_rate:
                kid_selfishness = int(np.mean([parent1.selfishness, parent2.selfishness]) + np.random.randint(-5, 5))
                kid_base_prowess = int(np.mean([parent1.base_prowess, parent2.base_prowess]) + np.random.randint(-5, 5))
                self.add_caveman(id = self.max_id, age = 1, selfishness=kid_selfishness, base_prowess=kid_base_prowess)
                
                new_caveman = self.population[-1]
                print(f"The gods have blessed {self.get_caveman_by_id(i[0]).name} ({self.get_caveman_by_id(i[0]).sex}) and {self.get_caveman_by_id(i[1]).name} ({self.get_caveman_by_id(i[1]).sex}) with a new caveman - they named him {new_caveman.name}!")
                # Set parent-child relationship
                self.relationships_grid[i[0], new_caveman.id] = 300
                self.relationships_grid[i[1], new_caveman.id] = 300

    def get_population_dataframe(self):
        # Get a dataframe of the current population
        if len(self.population) == 0:
            return None
        df = pd.DataFrame([c.__dict__ for c in self.population])
        df.set_index('id', inplace=True)
        return df

    def update_statistics(self):

        # print total population
        population = len(self.population)

        adults = len([caveman for caveman in self.population if caveman.age > 16])
        children = len([caveman for caveman in self.population if caveman.age <= 16])

        # print number of singles and taken people
        taken_list = len([caveman for caveman in self.population if caveman.is_taken == True])
        singles_list = len([caveman for caveman in self.population if caveman.is_taken == False])

        current_old_deahts = self.old_age_deaths
        current_hunger_deaths = self.hunger_deaths

        # Get average age
        average_age = np.mean([caveman.age for caveman in self.population])

        # Get average hunger
        average_hunger = np.mean([caveman.hunger for caveman in self.population])

        # Get average prowess
        average_prowess = np.mean([caveman.prowess for caveman in self.population])

        # Get average selfishness
        average_selfishness = np.mean([caveman.selfishness for caveman in self.population])

        # Get average reciprocity
        average_reciprocity = np.mean([caveman.reciprocity for caveman in self.population])


        self.statistics['Population'].append(population)
        self.statistics['Adults'].append(adults)
        self.statistics['Children'].append(children)

        self.statistics['Singles'].append(taken_list)
        self.statistics['Taken'].append(singles_list)

        self.statistics['Hunger Deaths'].append(current_old_deahts)
        self.statistics['Old Age Deaths'].append(current_hunger_deaths)

        self.statistics['Average Age'].append(average_age)
        self.statistics['Average Hunger'].append(average_hunger)
        self.statistics['Average Prowess'].append(average_prowess)
        self.statistics['Average Selfishness'].append(average_selfishness)
        self.statistics['Average Reciprocity'].append(average_reciprocity)

    def add_caveman(self, id, age, selfishness, base_prowess):

        # Add a new caveman to the jungle
        self.population.append(Caveman(self.max_id, age=age, selfishness=selfishness, base_prowess=base_prowess))
        self.max_id += 1
        self.relationships_grid = np.pad(self.relationships_grid, ((0, 1), (0, 1)), 'constant')

    def food_to_remove_hunger(self, hunger):
        current_fib = self.hunger_fib_function(hunger)
        return 1-current_fib
    
    def hunger_level_update(self, initial_hunger, food_eaten):
        # Update hunger level
        current_fib = self.hunger_fib_function(initial_hunger)
        new_fib = current_fib + food_eaten
        return self.fib_hunger_function(new_fib)

    def relationship_level_update(self, initial_hunger, food_shared):
        # Update hunger level
        current_fib = self.hunger_fib_function(initial_hunger)
        new_fib = current_fib + food_shared
        new_hunger = self.fib_hunger_function(new_fib)
        return -(new_hunger - initial_hunger)

    def get_caveman_by_id(self, id):
        return [caveman for caveman in self.population if caveman.id == id][0]