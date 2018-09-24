'''
PasteWatch - Watches Pastebin.com.
https://github.com/PoxyDoxy/PasteWatch

REQUIRES PASTEBIN.COM LIFETIME ACCOUNT + CURRENT IP WHITELISTED.

This bot uses 2 keyword lists, "Important" and "UnImportant". 
In Discord, this allows you to have 2 channels, with 2 notification settings in your discord server.

Make sure you set 'hook_url_important' and 'hook_url_unimportant'.

Coded By PoxyDoxy
Coded using Python3.5 on Debain 8.6
'''

import os
import json
import time
import urllib
import requests

# Variables for you to adjust
alert_important_on_find = True # Alerts you on Find of an Important Keyword
alert_unimportant_on_find = True # Alerts you on Find of an Unimportant Keyword

save_important_on_find = True # Saves important .txt to Folder, also allows Discord to Attach Txt File.
save_unimportant_on_find = True # Saves unimportant .txt to Folder, also allows Discord to Attach Txt File.

loop_scan = True # Loops every 'time_between_scans' seconds. Set as False to run once. 

keyword_file_important = "watch_keywords_important.txt" # File to store your Important Keywords, created on startup.
keyword_file_unimportant = "watch_keywords_unimportant.txt" # File to store your UnImportant Keywords, created on startup.

saves_folder_important = "foundpastes_important" # Folder to store found important pastes, created on startup.
saves_folder_unimportant = "foundpastes_unimportant" # Folder to store found unimportant pastes, created on startup.

# |============= A L E R T === S E T T I N G S =============/
# Alert - Console
alert_console = True

# Alert - Discord
alert_discord = True
# SET THE 2 HOOKS BELOW, OR YOUR DISCORD NOTIFICATIONS WILL NOT WORK.
hook_url_important = "https://discordapp.com/api/webhooks/xxxxxxxxxxxxxxxxxx/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
hook_url_unimportant = "https://discordapp.com/api/webhooks/xxxxxxxxxxxxxxxxxx/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
# |=========================================================|

posts_to_fetch = 100 # API Maximum is 100
time_between_scans = 60 # Seconds between scans, API Recommends 60s

# More Variables, you probably shouldn't touch these.
pastebin_archive_url = "https://scrape.pastebin.com/api_scraping.php?limit=" + str(posts_to_fetch)
pastebin_scrape_url = "https://scrape.pastebin.com/api_scrape_item.php?i="
pastebin_viewing_url = "https://pastebin.com/"
no_access_error = "DOES NOT HAVE ACCESS." # Part of the Error message shown by pastebin when your IP does not have access.
checked_pastes_file = "checked_pastes.txt" # File to store previously checked paste IDs.

# Temporary Variables, DO NOT ADJUST THESE.
keywords_important = ""
keywords_unimportant = ""
key_list = []
old_checked_pastes = []
fresh_checked_pastes = []
new_items_scanned = 0

def send_alert_console(key, word):
    if word in keywords_important:
        print("ALERT: Important Paste Found! Word: " + str(word).lower() + " : " + str(key).lower() + ".")
    else:
        print("Alert: Paste Found! Word: " + str(word).lower() + " : " + str(key).lower() + ".")

def send_alert_discord(key, word):
    if word in keywords_important:
        # Post the Important message to the Discord webhook
        data = {"content": "IMPORTANT PASTE FOUND!\nWord: `" + word + "`.\nURL: `" + pastebin_viewing_url + str(key) + "`"}
        files = {}
        if save_important_on_find:
            txt_path = os.path.join(saves_folder_important, key.lower() + ".txt")
            if os.path.isfile(txt_path):
                # File exists, upload it.
                files = {'upload_file': open(txt_path,'rb')}
            else:
                print("Error: Could not upload " + str(key) + ".txt to Discord. File does not exist.")
        result = requests.post(hook_url_important, files=files, data=data)
    else:
        # Post the UnImportant message to the Discord webhook
        data = {"content": "Paste Found!\nWord: `" + word + "`.\nURL: `" + pastebin_viewing_url + str(key) + "`"}
        files = {}
        if save_unimportant_on_find:
            txt_path = os.path.join(saves_folder_unimportant, key.lower() + ".txt")
            if os.path.isfile(txt_path):
                # File exists, upload it.
                files = {'upload_file': open(txt_path,'rb')}
            else:
                print("Error: Could not upload " + str(key) + ".txt to Discord. File does not exist.")
        result = requests.post(hook_url_unimportant, files=files, data=data)

def send_alert(key, text, word):
    if alert_console:
        send_alert_console(key, word)

    if alert_discord:
        send_alert_discord(key, word)

def save_paste(key, text, word):
    # Check for Important Folder
    temp_local_folder = saves_folder_important

    if word in keywords_unimportant:
        # Switch to Unimportant Folder
        temp_local_folder = saves_folder_unimportant

    if os.path.isdir(temp_local_folder):
        # Check for existing file
        txt_path = os.path.join(temp_local_folder, key.lower() + ".txt")
        if not os.path.isfile(txt_path):
            # Create File with Text inside
            text_file = open(txt_path, "w")
            text_file.write(text)
            text_file.close()
        else:
            print("Warning: Tried to save an already existing paste: " + str(key).lower() + ".")

def check_paste(key):
    paste_content = ""
    # Fetch Content.
    try:
        paste_content = url_fetch(pastebin_scrape_url + str(key))
    except:
        pass # Maybe the paste no longer exists, do a simple skip.
    if paste_content != "":
        #================================|
        #       I M P O R T A N T       |
        # Check Content for Each KeyWord.
        triggered = False
        triggered_word = ""

        # Check Important Keywords First
        for word in keywords_important:
            if word.lower() in paste_content.lower():
                triggered = True
                triggered_word = word
                break # We only need to trigger once

        if triggered:
            # Save First, so Discord can attach saved .txt file.
            if save_important_on_find:
                save_paste(key, paste_content, triggered_word)
            # Then Alert
            if alert_important_on_find:
                send_alert(key, paste_content, triggered_word)

        #================================|
        #     U N I M P O R T A N T     |
        # Check Content for Each KeyWord.
        triggered = False
        triggered_word = ""

        # Then Check Unimportant Keywords
        for word in keywords_unimportant:
            if word.lower() in paste_content.lower():
                triggered = True
                triggered_word = word
                break # We only need to trigger once

        if triggered:
            # Save First, so Discord can attach saved .txt file.
            if save_unimportant_on_find:
                save_paste(key, paste_content, triggered_word)
            # Then Alert
            if alert_unimportant_on_find:
                send_alert(key, paste_content, triggered_word)
            
def url_fetch(url):
    return urllib.request.urlopen(url, timeout=10).read().decode('utf-8')

def get_recent_pastes():
    global new_items_scanned
    try:
        json_content = url_fetch(pastebin_archive_url)
        if no_access_error not in json_content.upper():
            pastes = json.loads(json_content)
            for paste in pastes:
                if not paste["key"].lower() in old_checked_pastes:
                    # If paste is not previously scanned, scan it. 
                    key_list.append(paste["key"].lower())
                    new_items_scanned = new_items_scanned + 1
                # Scanned or Not, add to Fresh Checked List.
                fresh_checked_pastes.append(paste["key"].lower())
            if len(pastes) < 1:
                print('Error: Could not fetch any keys.')
        else:
            exit('Error: Your IP Does not have Access.')
    except:
        print('Error: Could not Fetch PasteBin Archive. Is your internet up?')

def startup_checks():
    # Check for Important + Unimportant Keyword File
    if not os.path.isfile(keyword_file_important):
        # Create Empty File
        open(keyword_file_important, 'a').close()
        print('Error: "' + keyword_file_important + '" has been created. Please fill it with keywords.')

    if not os.path.isfile(keyword_file_unimportant):
        # Create Empty File
        open(keyword_file_unimportant, 'a').close()
        print('Error: "' + keyword_file_unimportant + '" has been created. Please fill it with keywords.')

    # Fetch Important Keywords
    try:
        file = open(keyword_file_important, "r")
        global keywords_important
        keywords_important = file.read().splitlines()
        # Strip Whitespace
        keywords_important = list(map(str.strip, keywords_important))
        # Convert to Lower for comparing
        keywords_important = list(map(str.lower, keywords_important))
        file.close()
    except:
        exit('Error: Could not open Important Keyword file, check file permission.')

    # Fetch Unimportant Keywords
    try:
        file = open(keyword_file_unimportant, "r")
        global keywords_unimportant
        keywords_unimportant = file.read().splitlines()
        # Strip Whitespace
        keywords_unimportant = list(map(str.strip, keywords_unimportant))
        # Convert to Lower for comparing
        keywords_unimportant = list(map(str.lower, keywords_unimportant))
        file.close()
    except:
        exit('Error: Could not open UnImportant Keyword file, check file permission.')

    if not os.path.isfile(checked_pastes_file):
        # Create Empty File
        open(checked_pastes_file, 'a').close()

    try:
        file = open(checked_pastes_file, "r")
        global old_checked_pastes
        old_checked_pastes = file.read().splitlines()
        file.close()
    except:
        exit('Error: Could not open CheckedPastes file, check file permission.')

    if save_important_on_find:
        try:
            if not os.path.isdir(saves_folder_important):
                os.makedirs(saves_folder_important)
        except:
            exit('Error: Could not create the important save folder "' + save_important_on_find + '".')

    if save_unimportant_on_find:
        try:
            if not os.path.isdir(saves_folder_unimportant):
                os.makedirs(saves_folder_unimportant)
        except:
            exit('Error: Could not create the unimportant save folder "' + save_important_on_find + '".')

    if (len(keywords_important) == 0) & (len(keywords_unimportant) == 0):
        exit('Error: Please provide at least 1 keyword to search for.')

    if loop_scan:
        if time_between_scans <= 0:
            exit('Error: Please set a loop time of 1 or above.')

def main():
    global keywords_important
    global keywords_unimportant
    global key_list
    global old_checked_pastes
    global fresh_checked_pastes
    global new_items_scanned

    while True:
        startup_checks()

        # Prechecks are done, let us begin.
        print(" |> PasteWatch (" + str(len(keywords_important)) + " important / " + str(len(keywords_unimportant)) + " unimportant) keywords loaded")

        # Populates Fresh 100 Paste ID Keys
        get_recent_pastes()

        if new_items_scanned >= 1:
            print("New Pastes to Scan: " + str(new_items_scanned) + ".")
            #print("Pastes Fetched.")

            for key in key_list:
                check_paste(key)
                #print("+1 Paste checked")

            # Save Recent Scan History to avoid Rescanning later on.
            try:
                with open(checked_pastes_file, "w") as text_file:
                    for paste in fresh_checked_pastes:
                        text_file.write("%s\n" % paste)
            except:
                exit('Error: Could not save recently checked paste history. Check file Permissions.')

        if not loop_scan:
            break

        print("Sleeping for " + str(time_between_scans) + " Seconds")
        time.sleep(time_between_scans)
        # Clear Terminal
        os.system('cls' if os.name == 'nt' else 'clear')

        # Reset Variables
        keywords_important = ""
        keywords_unimportant = ""
        key_list = []
        old_checked_pastes = []
        fresh_checked_pastes = []
        new_items_scanned = 0

if __name__ == '__main__':
    main()