import requests
import time
from sys import exit
from os import path
from lib.config import *

def fancy_error(function_name, message, err=None):
    print(f'[Error] {function_name}: {message}')
    if err: 
        print(f'[Error] {function_name}: {err}')
    exit()

def fancy_warning(function_name, message, err=None):
    print(f'[Warning] {function_name}: {message}')
    if err: 
        print(f'[Warning] {function_name}: {err}')

def get_group_info(group_id):
    url = f"https://groups.roblox.com/v1/groups/{group_id}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        fancy_warning("get_group_info()", f"Error fetching group info for group {group_id}.", f"HTTP status code {response.status_code}")
        return None

def get_group_members(group_id, cursor=None):
    url = f"https://groups.roblox.com/v1/groups/{group_id}/users?limit=100&sortOrder=Asc"
    if not cursor == None:
        url += f'&cursor={cursor}'

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        fancy_warning("get_group_members()", f"Error fetching members for group {group_id}", f"HTTP status code {response.status_code}")
        return None

def get_all_members_in_group(group_id, cursor=None):
    members = []
    if verbose:
        print(f'[Info] Getting all members in group {group_id}.')

    data = get_group_members(group_id)
    request_count = 1
    if verbose:
        print(f'[Info] Roblox API request {request_count}... ({request_delay} second delay)')

    while data["nextPageCursor"]:
        try:
            for member in data["data"]:
                members.append([member["user"]["userId"], member["user"]["username"], member["user"]["displayName"]]) #save a shit ton of api requests

            time.sleep(request_delay) # avoid timeout
            data = get_group_members(group_id, data["nextPageCursor"])
            request_count += 1
            if verbose:
                print(f'[Info] Roblox API request {request_count}...')
            if not data:
                fancy_error("get_all_members_in_group()", "data returned None. Likely a timeout from the Roblox API.")
        except Exception as e:
            fancy_error("get_all_members_in_group()", "General request error, likely a timeout from the Roblox API.", e)
    
    return members

def get_group_score(group_id):
    wordlist = set(expand_list(matchlist))
    member_objects = get_all_members_in_group(group_id)
    group_score = 0

    if verbose:
        print(f'[Info] Calculating group score for group {group_id}.')

    # get stuff
    members = funny_func(member_objects, 0)
    usernames = funny_func(member_objects, 1)
    display_names = funny_func(member_objects, 2) 
    matched_members = match_usernames(usernames, display_names, members, wordlist)
    with open(path.realpath(users_output_file), 'w') as users_file:
        for member in matched_members:
            group_score += 1
            if verbose:
                print(f'[Info] Found user: https://www.roblox.com/users/{member}/profile')
            users_file.write(f'https://www.roblox.com/users/{member}/profile\n')
    
    return group_score
        

def get_user_groups(user_id):
    url = f"https://groups.roblox.com/v1/users/{user_id}/groups/roles"
    response = requests.get(url)
    if verbose:
        print(f'[Info] Getting groups for user {user_id}.')
    
    if response.status_code == 200:
        data = response.json()
        return [group["group"]["id"] for group in data["data"]]
    else:
        fancy_warning("get_user_groups()", f"Error fetching groups for user {user_id}. Likely API ban.")

def match_string(string, match_list):
    match_score = 0

    for match_str in match_list:
        if match_str in string:
            match_score = match_score + 1
    
    return match_score

def match_usernames(name_list, display_list, id_list, match_list):
    final_list = []

    if verbose:
        print(f'[Info] Filtering group users...')

    if name_list == None or display_list == None or id_list == None:
        fancy_error("match_usernames()", "An error happened somewhere, that the script didnt catch since one of the lists is empty.")

    if not len(name_list) == len(display_list):
        fancy_error("match_usernames()", "The length of the username list is not the same as the length of the display name list.")

    for i in range(len(name_list)):
        id = id_list[i]
        username = name_list[i]
        display_name = display_list[i]

        if not username == None and not display_name == None:
            match_score = match_string(username, match_list) + match_string(display_name, match_list)

            if match_score >= match_score_limit:
                final_list.append(id)
    
    return final_list

def funny_func(object, index):
    funny = []
    
    for i in object:
        funny.append(i[index])
    
    return funny

# boilerplate
def expand_list(list):
    final_list = []

    # this can be improved but i dont want to improve it
    if verbose:
        print(f'[Info] Expanding wordlist...')
    for w in list:
        word = w.strip()
        final_list.append(word)
        final_list.append(word.upper())
        final_list.append(word.lower())

        # x
        final_list.append(word.replace("a", "x"))
        final_list.append(word.replace("e", "x"))
        final_list.append(word.replace("i", "x"))
        final_list.append(word.replace("o", "x"))
        final_list.append(word.replace("u", "x"))
        final_list.append(word.replace("y", "x"))

        final_list.append(word.replace("a", "x").upper())
        final_list.append(word.replace("e", "x").upper())
        final_list.append(word.replace("i", "x").upper())
        final_list.append(word.replace("o", "x").upper())
        final_list.append(word.replace("u", "x").upper())
        final_list.append(word.replace("y", "x").upper())

        final_list.append(word.replace("a", "x").lower())
        final_list.append(word.replace("e", "x").lower())
        final_list.append(word.replace("i", "x").lower())
        final_list.append(word.replace("o", "x").lower())
        final_list.append(word.replace("u", "x").lower())
        final_list.append(word.replace("y", "x").lower())

        #z
        final_list.append(word.replace("a", "z"))
        final_list.append(word.replace("e", "z"))
        final_list.append(word.replace("i", "z"))
        final_list.append(word.replace("o", "z"))
        final_list.append(word.replace("u", "z"))
        final_list.append(word.replace("y", "z"))

        final_list.append(word.replace("a", "z").upper())
        final_list.append(word.replace("e", "z").upper())
        final_list.append(word.replace("i", "z").upper())
        final_list.append(word.replace("o", "z").upper())
        final_list.append(word.replace("u", "z").upper())
        final_list.append(word.replace("y", "z").upper())

        final_list.append(word.replace("a", "z").lower())
        final_list.append(word.replace("e", "z").lower())
        final_list.append(word.replace("i", "z").lower())
        final_list.append(word.replace("o", "z").lower())
        final_list.append(word.replace("u", "z").lower())
        final_list.append(word.replace("y", "z").lower())
    return final_list