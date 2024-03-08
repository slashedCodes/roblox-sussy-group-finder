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
        print(f'[Info] Caching is turned {"on" if caching else "off"}.')
        divider()
    
    if caching: initialize_cache_files()

    with open(users_output_file, "a", buffering=1) as users_file:
        with open(group_output_file, "a", buffering=1) as groups_file:
            for group_id in initial_groups:
                member_objects = get_all_members_in_group(group_id)

                members = tuple_to_array(member_objects, 0)
                usernames = tuple_to_array(member_objects, 1)
                display_names = tuple_to_array(member_objects, 2) 
                matched_members = match_usernames(usernames, display_names, members, wordlist)

                for i in matched_members:
                    member = i[0] # trickery and foolery (check match_usernames function for explanation)
                    add_user(member, users_file)
                    
                    friend_count = get_user_friend_count(member)
                    if friend_count <= maximum_friend_count:
                        friends = get_user_friends(member)
                        # I don't put these in variables because i dont have a use for them.
                        matched_friends = match_usernames(tuple_to_array(friends, 0), tuple_to_array(friends, 1), tuple_to_array(friends, 2), wordlist)
                        
                        for friend in matched_friends:
                            add_user(friend, users_file)
                    else:
                        if verbose: print(f'[Info] User {member} has more than {maximum_friend_count} friends. Skipping friend check.')

                    if mode == 1:
                        member_group_ids = get_user_groups(member)
                        for member_group_id in member_group_ids:
                            add_group(member_group_id, groups_file)
    
    if mode == 1: 
        # clean the stuff up if you finish the script in mode 1 (somehow)
        clean_groups_output_file(group_output_file)
        clean_users_output_file(users_output_file, True) # clean with ban check


if __name__ == "__main__":
    menu()