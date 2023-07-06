print_mood = """
1 = Happiest,
2 = Happy,
3 = Neutral,
4 = Angry,
5 = Burning
"""

print_muscle_groups = """
    1.Biceps
    2.Triceps
    3.Shoulders (including deltoids)
    4.Chest (including pectoralis major and minor)
    5.Legs (including quadriceps, hamstrings, calves)
    6. Back (including latissimus dorsi, rhomboids, trapezius)
    7.Abdominals (abs)
    8.Glutes (buttocks)
    9.Forearms (including wrist flexors and extensors)
    10.Calves (gastrocnemius and soleus)
    11.Hips (including hip flexors and hip abductors/adductors)
    12.Neck (including sternocleidomastoid and trapezius)
"""
muscle_groups = {
    1: "Biceps",
    2: "Triceps",
    3: "Shoulders",
    4: "Chest",
    5: "Legs",
    6: "Back",
    7: "Abs",
    8: "Glutes",
    9: "Forearms",
    10: "Calves",
    11: "Hips",
    12: "Neck"
}


class moodNumError(Exception):
    def __init__(self, message):
        self.message = message


class isWorkoutExist(Exception):
    def __init__(self, message):
        self.message = message


class lineLength(Exception):
    def __init__(self, message):
        self.message = message
