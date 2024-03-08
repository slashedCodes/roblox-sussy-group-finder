import requests, time, re, json
from sys import exit
from os import path
from os import mkdir
from lib.config import *

def divider(length=50):
    string = ""
    for i in range(length):
        string += "-"
    print(string)
    return divider

# not necesarrily tuple but i dont have a better name for this
def tuple_to_array(object, index):
    funny = []

    for i in object:
        funny.append(i[index])

    return funny

def fancy_error(function_name, message, err=None):
    print(f'[Error] {function_name}: {message}')
    if err: 
        print(f'[Error] {function_name}: {err}')
    exit()

def fancy_warning(function_name, message, err=None):
    print(f'[Warning] {function_name}: {message}')
    if err: 
        print(f'[Warning] {function_name}: {err}')

def clean_groups_output_file(path):
    if verbose: print(f'[Info] Cleaning up the groups file...')
    
    file_groups = set()

    with open(path, "r") as file: # Read the file and put every group into a set
        file_contents = file.readlines()

        for line in file_contents:
            group_id_match = re.search("groups\/(\d+)", line)
            group_score_match = re.search("-\s*(\d+)", line)
            
            if group_id_match and group_score_match:
                group_id = int(group_id_match.group(1))
                group_score = int(group_score_match.group(1))

                if group_score > group_minimum_matches: # This is for redundancy even if the script wont allow it.
                    file_groups.add((group_id, group_score))

    with open(path, "w") as file: # Erase the file, then write back to it
        for group in file_groups:
            file.write(f'https://roblox.com/groups/{group[0]}/x - {group[1]}\n')
    
def clean_users_output_file(path, banned_check=False):
    if verbose: print(f'[Info] Cleaning up the users file (ban check {"on" if banned_check else "off"})...')
    file_groups = set()

    with open(path, "r") as file: # Read the file and put every group into a set
        file_contents = file.readlines()

        for line in file_contents:
            user_id_match = re.search("users\/(\d+)", line)
            
            if user_id_match:
                user_id = int(user_id_match.group(1))
                if banned_check:
                    user_info = get_user_info(user_id)

                    if user_info and user_info["isBanned"] == False:
                        file_groups.add(user_id)
                    elif user_info and user_info["isBanned"] and verbose:
                        print(f'[Info] User {user_id} is banned. Skipping..')
                else:
                    file_groups.add(user_id)

    with open(path, "w") as file: # Erase the file, then write back to it
        for user_id in file_groups:
            file.write(f'https://roblox.com/users/{user_id}/profile\n')

def initialize_cache_files(cache_folder):
    # if the files dont exist, initialize the files.
    if verbose: print(f'[Info] Initializing cache files...')
    if not path.exists(cache_folder): mkdir(cache_folder)
    
    user_cache_path = path.join(cache_folder, "users.json")
    group_cache_path = path.join(cache_folder, "groups.json")

    if not path.exists(user_cache_path): open(user_cache_path, "w").write("[]").close()
    if not path.exists(group_cache_path): open(group_cache_path, "w").write("[]").close()

def get_cache_contents(cache_folder):
    if verbose: print(f'[Info] Getting cache file contents...')
    user_cache_path = path.join(cache_folder, "users.json")
    group_cache_path = path.join(cache_folder, "groups.json")
    
    user_cache_json = json.loads(open(user_cache_path, "r").read())
    group_cache_json = json.loads(open(group_cache_path, "r").read())

    user_cache_json.close()
    group_cache_json.close()
    return user_cache_json, group_cache_json

def write_cache_contents(cache_folder, user_cache_json=None, group_cache_json=None):
    if verbose: print(f'[Info] Writing cache file contents...')
    if user_cache_json == None and group_cache_json == None: fancy_error("write_cache_contents()", "Both arguments of the function are empty.")
    
    user_cache_path = path.join(cache_folder, "users.json")
    group_cache_path = path.join(cache_folder, "groups.json")

    if user_cache_json: open(user_cache_path, "w").write(json.dumps(user_cache_json)).close()
    if group_cache_json: open(group_cache_path, "w").write(json.dumps(group_cache_json)).close()

def get_group_info(group_id):
    url = f"https://groups.roblox.com/v1/groups/{group_id}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        if response.status_code == 429 and auto_retry_after_timeout:
            # timeout !!! xd
            fancy_warning("get_group_info()", f"Roblox API Timeout.", f"HTTP status code 429")
            return "timeout"
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
    next_page_cursor = None
    if verbose: print(f'[Info] Getting all members in group {group_id}.')

    data = get_group_members(group_id)
    next_page_cursor = data["nextPageCursor"] if data["nextPageCursor"] else None
    request_count = 1
    if verbose: print(f'[Info] Roblox API request {request_count}... ({request_delay} second delay)')

    while next_page_cursor:
        try:
            for member in data["data"]:
                members.append([member["user"]["userId"], member["user"]["username"], member["user"]["displayName"]]) #save a shit ton of api requests

            time.sleep(request_delay) # avoid timeout (most of the times)

            data = get_group_members(group_id, data["nextPageCursor"])
            next_page_cursor = data["nextPageCursor"] if data["nextPageCursor"] else None
            request_count += 1

            if verbose: print(f'[Info] Roblox API request {request_count}... ({request_delay} second delay)')

            if not data and auto_retry_after_timeout:
                fancy_warning("get_all_members_in_group()", "data returned None. Likely a timeout from the Roblox API.")
                time.sleep(request_delay * 2)

                if verbose: print(f'[Info] Roblox API request {request_count}... ({request_delay * 2} second delay)')

                data = get_group_members(group_id, data["nextPageCursor"]) # idk if the next page cursor would work but oh well
                next_page_cursor = data["nextPageCursor"] if data["nextPageCursor"] else None
            elif not data:
                fancy_error("get_all_members_in_group()", "data returned None. Likely a timeout from the Roblox API.")
        except Exception as e:
            fancy_error("get_all_members_in_group()", "General request error, likely a timeout from the Roblox API.", e)
    
    return members

def get_group_score(group_id):
    wordlist = set(expand_list(matchlist))
    if verbose: divider()

    member_objects = get_all_members_in_group(group_id)
    group_score = 0

    if verbose: print(f'[Info] Calculating group score for group {group_id}.')

    # get stuff
    members = tuple_to_array(member_objects, 0)
    usernames = tuple_to_array(member_objects, 1)
    display_names = tuple_to_array(member_objects, 2) 
    matched_members_full = match_usernames(usernames, display_names, members, wordlist)

    # caching stuff
    group_object = {
        "members": [],
        "match_score": 0,
        "id": 0
    }

    with open(path.realpath(users_output_file), 'a') as users_file:
        for i in matched_members_full:
            member = i[0]
            group_score += 1
            users_file.write(f'https://roblox.com/users/{member}/profile\n')
            if verbose: print(f'[Info] Found user: https://roblox.com/users/{member}/profile')

            # friends
            friend_count = get_user_friend_count(member)
            if friend_count <= maximum_friend_count:
                friends = get_user_friends(member)
                matched_friends = match_usernames(tuple_to_array(friends, 0), tuple_to_array(friends, 1), tuple_to_array(friends, 2), wordlist)
                
                if caching:
                    group_object["members"].append({
                        "username": usernames[i[2]],
                        "display_name": display_names[i[2]],
                        "id": members[i[0]],
                        "match_score": members[i[1]]
                    })

                for friend in matched_friends:
                    users_file.write(f'https://roblox.com/users/{friend}/profile\n')
                    if verbose: print(f'[Info] Found user: https://roblox.com/users/{friend}/profile')
            else:
                if verbose: print(f'[Info] User {member} has more than {maximum_friend_count} friends. Skipping friend check.')
    
    if caching:
        group_object["match_score"] = group_score
        group_object["id"] = group_id
    
        user_cache_json, group_cache_json = get_cache_contents(cache_folder)
        group_cache_json.append(group_object)
        write_cache_contents(cache_folder, group_cache_json=group_cache_json)

    return group_score     

def add_group(group_id, groups_file):
    # TODO: check this function out a little more
    # TODO: test the caching function (i didnt)

    group_info = get_group_info(group_id)

    if group_info == "timeout" and auto_retry_after_timeout: # Catch the first timeout
        if verbose: print(f'[Info] Timeout error on get_group_info(). Waiting {request_delay * 2} seconds and retrying.')
        time.sleep(request_delay * 2) # Wait twice the amount of time

        group_info = get_group_info(group_id) # Try again...
    elif group_info == "timeout":
        fancy_error("get_group_info()", "Timeout error.", "HTTP code 429.")

    if group_info == "timeout": # In this case this would be the second timeout.
        fancy_error("get_group_info()", "Timeout error number 2. Try increasing the request delay or wait a little and run the script again.")

    if not group_info: return None

    if group_info["memberCount"] > group_maximum_members:
        if verbose: print(f'[Info] Group {group_id} with {group_info["memberCount"]} members is above the limit of {group_maximum_members} group members. Skipping...')
        return None

    group_score = get_group_score(group_id)
    if group_score >= group_minimum_matches:
        if verbose: print(f'[Info] Found group: https://roblox.com/groups/{group_id}/x - {group_score}')
        groups_file.write(f"https://roblox.com/groups/{group_id}/x - {group_score}\n")
    else:
        if verbose: print(f'[Info] Group {group_id} has less than {group_minimum_matches} matches. It will not be added to the text file.')

def get_user_groups(user_id):
    url = f"https://groups.roblox.com/v1/users/{user_id}/groups/roles"
    if verbose: print(f'[Info] Getting groups for user {user_id}.')
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return [group["group"]["id"] for group in data["data"]]
    else:
        fancy_warning("get_user_groups()", f"Error fetching groups for user {user_id}. Likely API ban.")

def get_user_friend_count(user_id):
    url = f"https://friends.roblox.com/v1/users/{user_id}/friends/count/"
    if verbose: print(f'[Info] Getting friend count for user {user_id}.')
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data["count"]
    elif response.status_code == 400:
        return None # invalid user

def get_user_friends(user_id):
    url = f"https://friends.roblox.com/v1/users/{user_id}/friends"
    if verbose: print(f'[Info] Getting friends for user {user_id}.')
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        friends = []
        for friend in data["data"]:
            friends.append([friend["id"], friend["name"], friend["displayName"]]) # Hopefully this works

        return friends
    elif response.status_code == 400:
        return None # invalid user

def get_user_info(user_id):
    url = f"https://users.roblox.com/v1/users/{user_id}/"
    if verbose: print(f'[Info] Getting information for user {user_id}.')
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    elif response.status_code == 404:
        return None # invalid user

def search_user_cache(user_id, cache_json):
    for member in cache_json:
        if member["id"] == user_id: return member

def search_group_cache_for_user(user_id, cache_json):
    results = []

    for group in cache_json:
        for member in group["members"]: 
            if member["id"] == user_id: results.append(group)
    
    return results

def search_group_cache_for_group(group_id, cache_json):
    for group in cache_json:
        if group["id"] == group_id: return group

def get_user_score(user_id):
    if not caching:
        fancy_warning('get_user_score()', 'Caching needs to be on to get the user score.')
        return None

    wordlist = set(expand_list(matchlist))

    user_cache_json, group_cache_json = get_cache_contents()
    user_info = get_user_info(user_id)

    match_score = match_string(user_info["username"], wordlist) + match_string(user_info["displayName"], wordlist)
    group_cache_results = search_group_cache_for_user(user_id, group_cache_json)

    for result in group_cache_results:
        match_score += 1

    return match_score

def add_user(user_id, users_file):
    if caching:
        user_score = get_user_score(user_id)
        if user_score > minimum_user_match_score:
            users_file.write(f'https://roblox.com/users/{user_id}/profile\n')
            if verbose: print(f'[Info] Found user: https://roblox.com/users/{user_id}/profile')
    else:
        users_file.write(f'https://roblox.com/users/{user_id}/profile\n')
        if verbose: print(f'[Info] Found user: https://roblox.com/users/{user_id}/profile')

def match_string(string, match_list):
    match_score = 0

    for match_str in match_list:
        if match_str in string:
            match_score = match_score + 1
    
    return match_score

def match_usernames(name_list, display_list, id_list, match_list):
    final_list = []

    if verbose: print(f'[Info] Filtering group users...')

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

            if caching:
                user_cache_json, group_cache_json = get_cache_contents(cache_folder)
                user_cache_json.append({
                    "username": username,
                    "display_name": display_name,
                    "id": id,
                    "match_score": match_score
                })

                write_cache_contents(cache_folder, user_cache_json=user_cache_json)

            if match_score >= match_score_limit:
                final_list.append([id, match_score, i])

    return final_list

def expand_list(list):
    final_list = []

    # this can be improved but i dont want to improve it
    if verbose: print(f'[Info] Expanding wordlist...')

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