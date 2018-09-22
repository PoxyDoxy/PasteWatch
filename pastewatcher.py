'''
PasteWatch - Watches Pastebin.com.
REQUIRES LIFETIME ACCOUNT + CURRENT IP WHITELISTED.
Coded By PoxyDoxy
Coded using Python3.5 on Debain 8.6
'''
import os
import json
import urllib
import urllib.request

# Variables for you to adjust
alert_on_find = True # Alerts you on Find
save_on_find = True # Saves to Folder on Find
keyword_file = "watch_keywords.txt" # File to store your Keywords, created on startup.
saves_folder = "pastefinds" # Folder to store found pastes, created on startup.

# Alert Variables
# Email
alert_email = False
email = "admin@localhost"
# HTTP GET (WIP)
alert_http_post = False # WIP
http_post = "http://localhost" # WIP

posts_to_fetch = 100 # API Maximum is 100
time_between_scans = 60 # Seconds between scans, API Recommends 60s

# More Variables, you probably shouldn't touch these.
pastebin_archive_url = "https://scrape.pastebin.com/api_scraping.php?limit=" + str(posts_to_fetch)
pastebin_scrape_url = "https://scrape.pastebin.com/api_scrape_item.php?i="
no_access_error = "DOES NOT HAVE ACCESS." # Part of the Error message shown by pastebin when your IP does not have access.
processed_list = "processed_pastes.txt" # File to store previously checked paste IDs.

# Temporary Variables, DO NOT ADJUST THESE.
keywords = ""
key_list = []

def send_alert(key, text, word):
    print("Alert On Find: WIP.")

def save_paste(key, text):
    print("Save On Find: WIP.")

def check_paste(key):
    paste_content = ""
    # Fetch Content.
    try:
        paste_content = url_fetch(pastebin_scrape_url + str(key))
    except:
        pass # Maybe the paste no longer exists, do a simple skip.
    if paste_content != "":
        # Check Content for Each KeyWord.
        triggered = False
        triggered_word = ""
        for word in keywords:
            if word.lower() in paste_content.lower():
                triggered = True
                triggered_word = word
                break # We only need to trigger once
        if triggered:
            if alert_on_find:
                send_alert(key, paste_content, triggered_word)
            if save_on_find:
                save_paste(key, paste_content)

def url_fetch(url):
    return urllib.request.urlopen(url, timeout=10).read().decode('utf-8')

def get_recent_pastes():
    try:
        json_content = url_fetch(pastebin_archive_url)
        if no_access_error not in json_content.upper():
            pastes = json.loads(json_content)
            for paste in pastes:
                key_list.append(paste["key"].lower())
            if len(key_list) < 1:
                exit('Error: Could not fetch any keys.')
        else:
            exit('Error: Your IP Does not have Access.')
    except:
        exit('Error: Could not Fetch PasteBin Archive.')

def startup_checks():
    # Check for Keyword File
    if not os.path.isfile(keyword_file):
        # Create Empty File
        open(keyword_file, 'a').close()
        exit('Error: "' + keyword_file + '" has been created. Please fill it with keywords.')

    try:
        file = open(keyword_file, "r")
        global keywords
        keywords = file.read().splitlines()
        file.close()
    except:
        exit('Error: Could not open Keyword file, check file permission.')

    if len(keywords) == 0:
        exit('Error: Please fill "' + keyword_file + '" with keywords.')

def main():
    startup_checks()

    # Prechecks are done, let us begin.
    print(" |> PasteWatch (" + str(len(keywords)) + " keywords loaded)")

    # Populates Fresh 100 Paste ID Keys
    get_recent_pastes()

    for key in key_list:
        check_paste(key)

if __name__ == '__main__':
    main()