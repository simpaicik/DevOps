"""Kayıt formunda önerilen hazır hareket listesi (kas grubuna göre)."""

EXERCISES_BY_GROUP = {
    "Göğüs": [
        "Bench Press", "Incline Bench Press", "Decline Bench Press", "Close-Grip Bench Press",
        "Dumbbell Bench Press", "Incline Dumbbell Press", "Decline Dumbbell Press",
        "Dumbbell Fly", "Incline Dumbbell Fly", "Cable Crossover", "Low-to-High Cable Fly",
        "High-to-Low Cable Fly", "Pec Deck", "Chest Press Makinesi", "Incline Chest Press Makinesi",
        "Smith Machine Bench Press", "Smith Machine Incline Press", "Floor Press", "Push-Up",
        "Incline Push-Up", "Decline Push-Up", "Weighted Push-Up", "Chest Dip", "Dumbbell Pullover",
        "Svend Press", "Landmine Press",
    ],
    "Sırt": [
        "Deadlift", "Sumo Deadlift", "Rack Pull", "Barbell Row", "Pendlay Row",
        "Yates Row", "Dumbbell Row", "Chest-Supported Dumbbell Row", "T-Bar Row",
        "Seated Cable Row", "Wide-Grip Cable Row", "Lat Pulldown", "Close-Grip Lat Pulldown",
        "Reverse-Grip Lat Pulldown", "Single-Arm Lat Pulldown", "Straight-Arm Pulldown",
        "Pull-Up", "Chin-Up", "Weighted Pull-Up", "Assisted Pull-Up", "Neutral-Grip Pull-Up",
        "Inverted Row", "Machine Row", "Meadows Row", "Seal Row", "Back Extension",
        "Good Morning", "Superman",
    ],
    "Omuz": [
        "Overhead Press", "Seated Barbell Press", "Push Press", "Dumbbell Shoulder Press",
        "Seated Dumbbell Press", "Arnold Press", "Shoulder Press Makinesi",
        "Smith Machine Shoulder Press", "Lateral Raise", "Cable Lateral Raise",
        "Machine Lateral Raise", "Front Raise", "Cable Front Raise", "Plate Front Raise",
        "Rear Delt Fly", "Reverse Pec Deck", "Face Pull", "Upright Row", "Barbell Shrug",
        "Dumbbell Shrug", "Trap Bar Shrug", "Y-Raise", "Landmine Shoulder Press",
    ],
    "Biceps": [
        "Barbell Curl", "EZ-Bar Curl", "Dumbbell Curl", "Alternating Dumbbell Curl",
        "Hammer Curl", "Cross-Body Hammer Curl", "Incline Dumbbell Curl", "Preacher Curl",
        "Machine Preacher Curl", "Concentration Curl", "Cable Curl", "Rope Hammer Curl",
        "Bayesian Cable Curl", "Spider Curl", "Reverse Curl", "Zottman Curl", "Drag Curl",
    ],
    "Triceps": [
        "Triceps Pushdown", "Rope Pushdown", "Reverse-Grip Pushdown", "Overhead Cable Extension",
        "Overhead Dumbbell Extension", "Skull Crusher", "Dumbbell Skull Crusher",
        "Triceps Dip", "Bench Dip", "Triceps Kickback", "Cable Kickback", "JM Press",
        "Diamond Push-Up", "Triceps Dip Makinesi", "Tate Press",
    ],
    "Ön kol": [
        "Wrist Curl", "Reverse Wrist Curl", "Farmer's Walk", "Plate Pinch", "Dead Hang",
    ],
    "Bacak": [
        "Back Squat", "Front Squat", "High-Bar Squat", "Low-Bar Squat", "Box Squat",
        "Pause Squat", "Goblet Squat", "Smith Machine Squat", "Hack Squat", "Pendulum Squat",
        "Leg Press", "Single-Leg Leg Press", "Bulgarian Split Squat", "Split Squat",
        "Walking Lunge", "Reverse Lunge", "Dumbbell Lunge", "Step-Up", "Leg Extension",
        "Single-Leg Leg Extension", "Lying Leg Curl", "Seated Leg Curl", "Standing Leg Curl",
        "Nordic Curl", "Romanian Deadlift", "Dumbbell Romanian Deadlift", "Stiff-Leg Deadlift",
        "Single-Leg Romanian Deadlift", "Trap Bar Deadlift", "Sissy Squat", "Belt Squat",
        "Adductor Makinesi", "Abductor Makinesi", "Cossack Squat", "Pistol Squat",
    ],
    "Kalça": [
        "Hip Thrust", "Barbell Glute Bridge", "Single-Leg Hip Thrust", "Hip Thrust Makinesi",
        "Cable Kickback (Kalça)", "Glute Kickback Makinesi", "Cable Pull-Through",
        "Frog Pump", "Kettlebell Swing",
    ],
    "Baldır": [
        "Standing Calf Raise", "Seated Calf Raise", "Leg Press Calf Raise",
        "Smith Machine Calf Raise", "Single-Leg Calf Raise", "Donkey Calf Raise",
        "Tibialis Raise",
    ],
    "Karın / Core": [
        "Crunch", "Cable Crunch", "Machine Crunch", "Decline Crunch", "Bicycle Crunch",
        "Sit-Up", "Hanging Leg Raise", "Hanging Knee Raise", "Lying Leg Raise",
        "Captain's Chair Leg Raise", "Ab Wheel Rollout", "Plank", "Side Plank",
        "Russian Twist", "Pallof Press", "Woodchopper", "Dead Bug", "Hollow Body Hold",
        "Mountain Climber", "V-Up", "Dragon Flag",
    ],
    "Tüm vücut / Olimpik": [
        "Clean", "Power Clean", "Hang Clean", "Clean and Jerk", "Snatch", "Power Snatch",
        "Thruster", "Burpee", "Turkish Get-Up", "Kettlebell Clean and Press", "Sled Push",
        "Sled Pull", "Battle Rope", "Box Jump", "Wall Ball", "Medicine Ball Slam",
    ],
    "Kardiyo": [
        "Koşu Bandı", "Eliptik Bisiklet", "Kondisyon Bisikleti", "Kürek Makinesi",
        "Merdiven Makinesi", "İp Atlama",
    ],
}

DEFAULT_EXERCISES = [name for group in EXERCISES_BY_GROUP.values() for name in group]
