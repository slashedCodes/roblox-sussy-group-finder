import pyjson5
from os import path
from sys import exit

try:
    with open(path.realpath("config.json5"), 'r') as file:
        config = pyjson5.decode(file.read())
        verbose = config["verbose"]

        if verbose:
            print(f'[Info] Reading configuration file...')

        initial_groups = config["initial_groups"]
        matchlist = config["matchlist"]
        match_score_limit = config["match_score_limit"]
        request_delay = config["request_delay"]

        group_output_file = config["group_output_file"]
        users_output_file = config["users_output_file"]
        group_maximum_members = config["group_maximum_members"]
        group_minimum_matches = config["group_minimum_matches"]
        maximum_friend_count = config["maximum_friend_count"]

        mode = config["mode"]
        auto_retry_after_timeout = config["auto_retry_after_timeout"]

        caching = config["caching"]
        cache_folder = config["cache_folder"]
        minimum_user_match_score = config["minimum_user_match_score"]
except Exception as e:
    print(f'[Error] config.py: Error reading configuration.')
    print(f'[Error] config.py: {e}')
    exit()