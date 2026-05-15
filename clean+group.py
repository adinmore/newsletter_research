import pandas as pd


# Assigns a group to the article based on its media outlet attribute
def classify_group(outlet):
  if (outlet == "index.hu" or outlet == "origo.hu" or outlet == "blikk.hu"):
    return "hsa"
  elif (outlet == "24.hu" or outlet == "444.hu" or outlet == "atlatszo.hu"):
    return "hid"
  elif (outlet == "orf.at" or outlet == "krone.at" or outlet == "derstandard.at" or outlet == "heute.at" or outlet == "kontrast.at"):
    return "at"
  
# Assigns a subgroup to the article based on its media outlet attribute
def classify_subgroup(outlet):
  if (outlet == "index.hu" or outlet == "origo.hu" or outlet == "blikk.hu"):
    return "hsa"
  elif (outlet == "24.hu" or outlet == "444.hu" or outlet == "atlatszo.hu"):
    return "hid"
  elif (outlet == "orf.at"):
    return "atgov"
  elif (outlet == "krone.at" or outlet == "derstandard.at"):
    return "atr"
  elif (outlet == "heute.at" or outlet == "kontrast.at"):
    return "atl"


# Read each group's data into a separate dataframe and then combine them
hsa_df = pd.read_excel("path1")
hid_df = pd.read_excel("path2")
at_df = pd.read_excel("path3")
data = pd.concat([hsa_df, hid_df, at_df])

# Rename columns
data = data.rename(columns={"id": "gid", "indexed_date":"sgid"})

# Drop unneccessary columns
data = data.drop(columns=["language", "media_url", "publish_date", "title", "url"])

# Filters the dataframes for empty or NULL entries
data = data.loc[data["content"] != ""]
data = data.loc[data["content"] != "NULL"]

# Assigns group and subgroup attributes for each entry
data["gid"] = data["media_name"].apply(classify_group)
data["sgid"] = data["media_name"].apply(classify_subgroup)

# Saves a local copy of the updated sheet
save_file = "apr20-apr26_data.xlsx"
data.to_excel(save_file, index=False)