# CavemanSim

CavemanSim is a agent-based computational economics project which explores foraging and sharing decisions in limited-resource environment. We propose a framework for conducting experiments that involve population dynamics, natural selection and optimal sharing/consumption strategies.

## Authors

Bartosz Bieganowski
bartosz.bieganowski.office@gmail.com

Michał Plewnia (email)

Paweł Makuła (email)

## Repository Layout

- Caveman.py - contains caveman class which describes the agent in this simulation.

- Jungle.py - contains environment definition and describes stages of the year. Most changes to how the simulation plays out will be made to this file.

- Experiment.ipynb - contains notebook for running the actual simulation, and saving the results.

- names.csv - For "immersion", this file contains exemplary names for the caveman which are assigned at random on caveman creation.

## Agent

Each agent is a caveman with following statistics assigned at birth:

- Sex : either Male or Female
- Age : 0 for new caveman, (18, 30) for initial population, at random. Once the caveman reaches age
of 60, he/she dies of old age.
- Selfishness $σ : (0, 100)$ describes how likely it is that the caveman will choose to eat food over
sharing even when he/she is not hungry.
- Reciprocity $λ = (100 − σ): (0, 100)$ describes how likely it is that the caveman will choose to share
food even when he/she is hungry.
- Hunger $θ: (0, 100)$ describes hunger of a caveman. If hunger reaches 100, caveman dies of starvation.
- Base prowess $p_b: (0, 100)$ describes base ability of a caveman to gather food. 
- Prowess: $p = p_b − θ:  (0,100)$ actual prowess decreases as hunger increases as the starving caveman
will have less energy to gather food.

## Environment

The jungle is an environment where caveman operate, and where they find food. At the beginning of
each turn (year) new food is generated, and caveman ”society” goes through following stages:
- Foraging stage - caveman gather food. The higher the prowess of the caveman, the more likely it is
that they will find food. After finding food, each caveman decides how much food will he eat, and
how much food will he leave for sharing in the later stage. As of current version, food eaten at low hunger will restore more than eating the same amount of food at low hunger.
- Sharing phase - each caveman who has leftover foods takes a look at their relationships - the food is
shared with the caveman with highest relationship as long as his hunger is not zero. This improves
their relationship further, making it more likely for the ”saved” caveman to share food with his
”saviour” later.
- Social stage - each non-hungry $(θ < 30)$ female is now able to choose a non-hungry male (we are
assuming hungry caveman think about getting food and not creating a family) to produce a family. Family
has increased relationship with each other, taking priority in food sharing.
- Reproduction phase - each year, a jointly non-hungry family has a chance to produce offspring,
with the traits of the parents being inherited. Children cannot forage, share, or create own families
before they turn 18. The relationship of children-parent relationship is set at 100, so that they take
priority in resource sharing.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)