import json
import openpyxl
import webbrowser

# Construct the file name for the extracted email data to be processed
sender_name = input("Name of Sender: ")
file_name = "mail_scraper (" + sender_name + ").json"

# Open the Excel data sheet
book = openpyxl.load_workbook("research_data.xlsx")
sheet = book["raw_data"]

# Open the json email data
# For each email, add a new row to the data sheet with the extracted email fields
with open(file_name, "r", encoding="utf-8") as j_data:
    data = json.load(j_data)
    count = 1
    for email in data:
        sender = email["sender"]
        subject = email["subject"]
        date = email["date"] + " 2026"
        links = email["links"]

        # Parse links list
        links = links[1:len(links)-2]
        links = links.replace('\\', '')
        links = links.split(',')

        # Sender-specific link filtering
        if sender_name == "24":
            links = links[1:]
            # Remove links to the weather page
            links = [l for l in links if "kiderul" not in l]
        elif sender_name == "origo":
            links = links[1:len(links)-17]
            # Remove duplicate links
            links = links[::2]
        elif sender_name == "dS":
            links = [l for l in links if ".gif" not in l]
            links = links[:len(links)-3]
            links = links[::2]
        elif sender_name == "heute":
            links = links[1::2]
            links = links[:5] + links[6:]
        
        # Standard basic link filtering
        links = [l for l in links if ".png" not in l]
        links = [l for l in links if ".gif" not in l]
        links = list(set(links))
        
        '''
        if count == 4:
            for l in links:
                print(l)
                webbrowser.open(l)
                input()
        '''
        
        # Reformat for Excel cell
        links = ";".join(links)

        email_row = [sender, subject, date, links]
        sheet.append(email_row)
        count += 1

# Save the new data in the sheet
book.save("research_Data.xlsx")