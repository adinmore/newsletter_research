import pandas as pd
import nltk
import re
import numpy as np
from nltk.corpus import stopwords
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import jensenshannon
from sklearn.metrics import pairwise_distances
from sklearn.cluster import AgglomerativeClustering
from sklearn.manifold import MDS
import matplotlib.pyplot as plt


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

# Imports, combines, and cleans all of the raw text data
week1 = pd.read_excel("path1")
week2 = pd.read_excel("path2")
week3 = pd.read_excel("path3")
week4 = pd.read_excel("path4")
data = pd.concat([week1, week2, week3, week4])
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
  min_topic_size=10,
  nr_topics=50,
  verbose=False
)

# Trains the topic model on the text corpus
# Calculates probabilities for each text doc in relation to the topics and prints topics
topics, probabilities = topic_model.fit_transform(docs)
print(topic_model.get_topic_info())

# Associates each filtered document with its probability for each topic
data = data.copy()
data["topic"] = topics
data["prob"] = list(probabilities)
prob_matrix = np.vstack(data["prob"].values)
prob_df = pd.DataFrame(prob_matrix)
prob_df["media_name"] = data["media_name"].values
prob_df["topic"] = data["topic"].values

# Removes the outlier documents to reduce noise
prob_df = prob_df[prob_df["topic"] != -1]

# Calculates the probability distribution for each media outlet
outlet_dists = {}
for outlet, group in prob_df.groupby("media_name"):
  # Calculates and normalizes the outlet distribution
  dist = group.drop(columns=["media_name", "topic"]).mean(axis=0).values
  dist = dist / (dist.sum() + 1e-12)

  # Stores the result
  outlet_dists[outlet] = dist

# Sets up the outlet distributions for clustering
val_outlets = list(outlet_dists.keys())
X = np.vstack([outlet_dists[o] for o in val_outlets])

# Determines the distance between each pair of outlets' topic distributions using the Jensen-Shannon Divergence measurement
D = pairwise_distances(X, metric=jensenshannon)

# Creates the similarity matrix for the media outlets
outlet_sims = 1 - D

# Configures the clustering model
cluster_model = AgglomerativeClustering(
  n_clusters=None,
  metric="precomputed",
  linkage="average",
  distance_threshold=0.25
)

# Clusters the media outlets and stores the result
labels = cluster_model.fit_predict(D)
clusters = pd.DataFrame({
  "media_name": val_outlets,
  "cluster": labels
})

# Creates a MDS visualization
mds = MDS(n_components=2, dissimilarity="precomputed", random_state=42)
coords = mds.fit_transform(D)

plt.figure(figsize=(8,6))
plt.scatter(coords[:,0], coords[:,1], c=labels)

for i, outlet in enumerate(val_outlets):
  plt.annotate(outlet, (coords[i,0], coords[i,1]), fontsize=9)

plt.title("Media Outlet Topic Similarity (MDS)")
plt.show()

# Saves the data
sims_df = pd.DataFrame(outlet_sims, index=val_outlets, columns=val_outlets)
clusters.to_excel("outlet_clusters.xlsx")
sims_df.to_excel("outlet_sims.xlsx")