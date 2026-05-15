import pandas as pd
import nltk
import re
import numpy as np
from nltk.corpus import stopwords
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from scipy.stats import entropy
from scipy.spatial.distance import jensenshannon


# The following code was developed with the assistance of AI (ChatGPT)
# Cleans up the scraped text by removing whitespace and stopwords
def cleaner(text):
  text = text.lower()
  text = re.sub(r"\s+", " ", text)
  text = re.sub(r"[^\w\s]", "", text)

  tokens = text.split()
  tokens = [t for t in tokens if t not in stop]

  return " ".join(tokens)


# Retrieves stopword lists for hungarian and german
nltk.download("stopwords")
hu = set(stopwords.words("hungarian"))
de = set(stopwords.words("german"))
stop = hu.union(de)

# Imports and cleans the raw text data for one week
data_file = "path"
data = pd.read_excel(data_file)
data = data.dropna()
data = data[data["content"].str.strip() != ""]
docs = data["content"].astype(str).apply(cleaner).tolist()
data = data.reset_index(drop=True)

# Imports a multilingual embedding model and configures the BERTopic model accordingly
embed_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
topic_model = BERTopic(
  embedding_model=embed_model,
  language="multilingual",
  calculate_probabilities=True,
  min_topic_size=20,
  verbose=False
)

# Trains the topic model on the text corpus and reduces the number of topics
topic_model.fit_transform(docs)
topic_model.reduce_topics(docs, nr_topics=30)

# Calculates probabilities for each text doc in relation to the topics and prints topics
topics, probabilities = topic_model.transform(docs)
print(topic_model.get_topic_info())

# Associates each filtered document with its probability for each topic
data = data.copy()
data["topic"] = topics
data["prob"] = list(probabilities)
prob_matrix = np.vstack(data["prob"].values)
prob_df = pd.DataFrame(prob_matrix)
prob_df["gid"] = data["gid"].values
prob_df["topic"] = data["topic"].values

# Removes the outlier documents to reduce noise
prob_df = prob_df[prob_df["topic"] != -1]

# Calculates the topical variation for each group using the Shannon Entropy measure
group_dists = {}
group_top_vars = []
for gid, group in prob_df.groupby("gid"):
  # Calculates and normalizes the group distribution
  dist = group.drop(columns=["gid"]).mean(axis=0).values
  dist = dist / (dist.sum() + 1e-12)

  # Computes the Shannon Entropy for the group, storing the result
  group_dists[gid] = dist
  group_top_vars.append({
    "group": gid,
    "entropy": entropy(dist, base=2)
  })

# Sets up a matrix for comparing the topical similarity of each group
val_groups = list(group_dists.keys())
n = len(val_groups)
group_sims = np.zeros((n,n))

# Determines the topical similarity of each group using Jensen-Shannon Divergence measurement
for i, g1 in enumerate(val_groups):
  for j, g2 in enumerate(val_groups):
    dist1 = group_dists[g1]
    dist2 = group_dists[g2]
    similarity = 1 - jensenshannon(dist1, dist2)
    group_sims[i,j] = similarity

# Saves the data
top_vars_df = pd.DataFrame(group_top_vars)
sims_df = pd.DataFrame(group_sims, index=val_groups, columns=val_groups)
top_vars_df.to_excel("apr13-apr19_top_vars.xlsx", index=False)
sims_df.to_excel("apr13-apr19_sims.xlsx", index=False)
