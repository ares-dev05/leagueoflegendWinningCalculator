# leagueoflegendWinningCalculator

# How to enter the virtual env
python -m venv "F:\workspace\leagueoflegendWinningCalculator"
cd "F:\workspace\leagueoflegendWinningCalculator"
.\Scripts\activate
python -m pip install -r requirements-all.txt

pip freeze > requirements.txt

# Run the project
flask run --port 4040

# MongoDB Access
username: lol
password: LeXuqMIbJBgsujrQ

# How to use the API
All heroes have their id number. For example, Hero "Annie" has unique number 1. And in the team, each hero has to have the role. For example, Top Jungle Middle Bottom Support. When you call the API, you have to input the config, team, enemy param. Here is the example input. In team or enemy, first param is role and next param is Hero unique number.

{
    "config": {
        "ignoreChampionWinrates": false,
        "riskLevel": "medium",
        "minGames": 1000
    },
    "team": [
        [
            4,
            "147"
        ],
        [
            3,
            "96"
        ],
        [
            1,
            "245"
        ],
        [
            0,
            "106"
        ],
        [
            2,
            "68"
        ]
    ],
    "enemy": [
        [
            3,
            "223"
        ],
        [
            2,
            "63"
        ],
        [
            0,
            "34"
        ],
        [
            1,
            "24"
        ],
        [
            4,
            "16"
        ]
    ]
}