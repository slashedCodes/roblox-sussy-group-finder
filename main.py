##################################################
#               grandpa finder 9000              #        
#                   by slashed                   #     
#                                                #     
# use responsibly. this might get you api banned #                              
##################################################

# funny #
print(f'[Roblox grandpa finder 9000]')
print(f'[     use responsibly.     ]')
print(f'--------------------------------------------------') # divider here because no divider (skill issue) :skull:

# Imports #
from lib.utils import *
from lib.config import *

# Functions and stuff #
def menu():
    divider()
    print(f'1. Run the main script')
    print(f'2. Clean up the group output file')
    print(f'3. Clean up the users output file')
    print(f'4. Clean up the users output file with ban check')
    choice = input("> ")

    if choice == "1":
        main()
    elif choice == "2":
        clean_groups_output_file(group_output_file)
    elif choice == "3":
        clean_users_output_file(users_output_file, False)
    elif choice == "4":
        clean_users_output_file(users_output_file, True)
    else:
        fancy_error("menu()", "Invalid choice. Exitting..")
    
    divider()

def main():
    wordlist = set(expand_list(matchlist))

    if verbose:
        print(f'[Info] The script is set to the {"full mode" if mode == 1 else "partial mode"} mode.')
        print(f'[Info] Auto retry after timeout mode is {"on" if auto_retry_after_timeout else "off"}.')
        divider()

    with open(users_output_file, "a", buffering=1) as users_file:
        with open(group_output_file, "a", buffering=1) as groups_file:
            for group_id in initial_groups:
                member_objects = get_all_members_in_group(group_id)

                members = tuple_to_array(member_objects, 0)
                usernames = tuple_to_array(member_objects, 1)
                display_names = tuple_to_array(member_objects, 2) 
                matched_members = match_usernames(usernames, display_names, members, wordlist)

                for member in matched_members:
                    users_file.write(f'https://roblox.com/users/{member}/profile\n')
                    if verbose: print(f'[Info] Found user: https://roblox.com/users/{member}/profile')
                    
                    friend_count = get_user_friend_count(member)
                    if friend_count <= maximum_friend_count:
                        friends = get_user_friends(member)
                        # I don't put these in variables because i dont have a use for them.
                        matched_friends = match_usernames(tuple_to_array(friends, 0), tuple_to_array(friends, 1), tuple_to_array(friends, 2), wordlist)
                    
                        # Explanation of why the script does not look at the groups that the friends are in:
                        # 1. Very taxxing for the Roblox API
                        # 2. The way I made the script, it doesn't handle duplicated well.
                        #    This would cause the script to go on forever.
                        # 3. It would take 3x the time for a minimal result.
                        # 4. The code would be twice as messy. No I'm not putting this whole script in a function.
                        # 5. I don't want to. Maybe in a future release.
                        
                        for friend in matched_friends:
                            users_file.write(f'https://roblox.com/users/{friend}/profile\n')
                            if verbose: print(f'[Info] Found user: https://roblox.com/users/{friend}/profile')
                    else:
                        if verbose: print(f'[Info] User {member} has more than {maximum_friend_count} friends. Skipping friend check.')


                    if mode == 1:
                        member_group_ids = get_user_groups(member)
                        for member_group_id in member_group_ids:
                            group_info = get_group_info(member_group_id)

                            if group_info == "timeout" and auto_retry_after_timeout: # Catch the first timeout
                                if verbose:
                                    print(f'[Info] Timeout error on get_group_info(). Waiting {request_delay * 2} seconds and retrying.')
                                time.sleep(request_delay * 2) # Wait twice the amount of time

                                group_info = get_group_info(member_group_id) # Try again...
                            elif group_info == "timeout":
                                fancy_error("get_group_info()", "Timeout error.", "HTTP code 429.")
                            
                            if group_info == "timeout": # In this case this would be the second timeout.
                                fancy_error("get_group_info()", "Timeout error number 2. Try increasing the request delay or wait a little and run the script again.")

                            if not group_info: continue

                            if group_info["memberCount"] > group_maximum_members:
                                print(f'[Info] Group {member_group_id} with {group_info["memberCount"]} members is above the limit of {group_maximum_members} group members. Skipping...')
                                continue

                            group_score = get_group_score(member_group_id)
                            if group_score >= group_minimum_matches:
                                if verbose: print(f'[Info] Found group: https://roblox.com/groups/{member_group_id}/x - {group_score}')

                                groups_file.write(f"https://roblox.com/groups/{member_group_id}/x - {group_score}\n")
                            else:
                                if verbose: print(f'[Info] Group {group_id} has less than {group_minimum_matches} matches. It will not be added to the text file.')
    
    if mode == 1: 
        # clean the stuff up if you finish the script in mode 1 (somehow)
        clean_groups_output_file(group_output_file)
        clean_users_output_file(users_output_file, True) # clean with ban check


if __name__ == "__main__":
    menu()