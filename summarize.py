import sys
import chromadb
import openai
import os
import numpy as np
from tqdm import tqdm
from node import is_null
from utils import extract_reference_numbers
from sklearn.cluster import KMeans

openai.api_key = os.environ['OPENAI_API_KEY']

def main():
    if len(sys.argv) != 2:
        print("Usage: python summarize.py <num_vectors>")
        sys.exit(1)

    num_vectors = int(sys.argv[1])
    print(f"Summarizing {num_vectors} vectors...")

    # Load the ChromaVectorDB
    save_path = os.path.join(os.path.dirname(__file__), 'data/')
    client = chromadb.PersistentClient(save_path)
    try:
        collection = client.create_collection(name='dental_history')
    except chromadb.db.base.UniqueConstraintError:
        collection = client.get_collection(name='dental_history')

    query = collection.get(include=['embeddings', 'documents', 'metadatas'])
    docs = query['documents']
    metadata = query['metadatas']
    ids = query['ids']
    num_docs = len(docs)

    #Make lookup table for documents by id
    doc_lookup = {}
    for i, doc in enumerate(docs):
        doc_lookup[ids[i]] = doc

    #Make a lookup table for metadata by id
    metadata_lookup = {}
    for i, data in enumerate(metadata):
        metadata_lookup[ids[i]] = data

    print(f"Found {num_docs} documents.")

    # summarize long documents it with Best Vector Representation
    if (num_docs > 11):
        # Get the embeddings
        vectors = query['embeddings']

        #Fit K-Means
        kmeans = KMeans(n_clusters=num_vectors, random_state=42, n_init=10).fit(vectors)

        # Find the closest embeddings to the centroids
        # First, create an empty list that will hold your closest points
        closest_indices = []

        # Loop through the number of clusters you have
        for i in range(num_vectors):

            # Get the list of distances from that particular cluster center
            distances = np.linalg.norm(vectors - kmeans.cluster_centers_[i], axis=1)

            # Find the list position of the closest one (using argmin to find the smallest distance)
            closest_index = np.argmin(distances)

            # Append that position to your closest indices list
            closest_indices.append(closest_index)

        selected_indices = sorted(closest_indices)
        selected_docs = [docs[i] for i in selected_indices]
        selected_times = [metadata[i]['timestamp'] for i in selected_indices]
        selected_ids = [ids[i] for i in selected_indices]
        # sort docs by timestamp
        selected_docs, selected_ids, selected_times = zip(*sorted(zip(selected_docs, selected_ids, selected_times), key=lambda x: x[2]))

        #Get the next and previous indices for each selected doc
        selected_prev = [metadata[i]['prev'] for i in selected_indices]
        selected_next = [metadata[i]['next'] for i in selected_indices]

        #Get the next and previous docs for each selected doc
        selected_prev_docs = [doc_lookup[i] if not is_null(i) else None for i in selected_prev]
        selected_next_docs = [doc_lookup[i] if not is_null(i) else None for i in selected_next]

        #Format the content for display
        formatted_content = []
        for i, doc in enumerate(selected_docs):
            prev_doc = selected_prev_docs[i]
            next_doc = selected_next_docs[i]
            formatted_content.append(f'{prev_doc if prev_doc else None} {doc} {next_doc if next_doc else None}')

        summaries = []

        #Summarize each of the selected docs
        print("SUMMARIZING each of the selected docs...")
        for content in tqdm(formatted_content):

            summary_prompt = f"""
            You will be given a passage from the transcript of the University of Michigan course: "History of Orthodontics with Dr. Lysle Johnston". It will be enclosed in triple backticks (```).
            Your goal is to give a summary of so that the reader can understand the main points of the passage without reading the entire passage.
            ```{content}```
            SUMMARY:
            """

            result = openai.Completion.create(
                model="gpt-3.5-turbo-instruct",
                prompt=summary_prompt,
                temperature=0,
                max_tokens=1000,
            )

            summary = result['choices'][0]['text']
            summaries.append(summary)

        print("Section SUMMARIES:")
        print(summaries)

        str_summaries = '\n\n'.join(summaries)

        #Combine the summaries
        combining_prompt = f"""
        You are teaching assistant for a University of Michigan course: "History of Orthodontics with Dr. Lysle Johnston". Your job is to summarize the course for the students. You have been given {num_vectors} summaries of the course. Your job is to combine the summaries into 3 main themes and write a summary for each theme.
        
        %Style Instructions%
        Focus on 3 main themes. Try and group the summaries into 3 groups. Then, write a summary for each group.

        %Formatting Instructions%
        If you make a claim, you must reference the supporting summaries. Only cite the reference numbers and always cite them individually in your response, like so: 'I have always supported dogs (1)(2).' or 'I have always supported dogs (1) and cats (2).'

        %Summaries%
        {str_summaries}
        """
        print("COMBINING the summaries...")
        # Generate summaries from the selected docs
        result = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{'role': 'system', 'content': combining_prompt}],
            temperature=0
        )

        final_summary = result['choices'][0]['message']['content']

        print("final themes:")
        print(final_summary)

        #extract citations
        used_citations = extract_reference_numbers(final_summary)
        print("citations:")
        print(used_citations)

        #Retrieve the video_id and timestamp for each citation
        citations = {}  
        for citation in used_citations:
            id_number = selected_ids[int(citation)-1]
            video_id = metadata_lookup[id_number]['video_id']
            timestamp = metadata_lookup[id_number]['timestamp']
            citations[citation] = f"https://www.youtube.com/watch?v={video_id}&t={timestamp}"
        
        #Save the final summary
        save_path = os.path.join(os.path.dirname(__file__), 'data/')
        with open(save_path + 'final_summary.txt', 'w') as f:
            f.write(final_summary)

        #Save the citations
        with open(save_path + 'citations.txt', 'w') as f:
            f.write(str(citations))
            
    else:
        print("Not enough documents to summarize with Best Vector Representative method.")
        exit(1)

if __name__ == '__main__':
    main()
