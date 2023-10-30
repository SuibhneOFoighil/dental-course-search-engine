import os
import argparse
import googleapiclient.discovery
import googleapiclient.errors
import chromadb
from youtube_transcript_api import YouTubeTranscriptApi
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

from node import YTVideo

def main(playlist_id):

    # Define the YouTube API client
    youtube_api_key = os.environ['YOUTUBE_DATA_API_KEY']
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=youtube_api_key)

    # Get the playlist items
    playlist_items = []
    next_page_token = None
    while True:
        request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        playlist_items += response["items"]
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    # Get the video IDs from the playlist items
    video_ids = [item["contentDetails"]["videoId"] for item in playlist_items]

    # Get the transcripts for each video
    transcripts = YouTubeTranscriptApi.get_transcripts(video_ids, languages=["en"], continue_after_error=True)

    # Create the nodes
    nodes = []
    for video_id, transcript in transcripts[0].items():
        new_node = YTVideo(video_id, transcript)
        nodes.append(new_node)

    # Insert the nodes into the local persistent ChromaVectorDB
    save_path = os.path.join(os.path.dirname(__file__), '../data/')
    client = chromadb.PersistentClient(save_path)
    try:
        collection = client.create_collection(name='dental_history')
    except chromadb.db.base.UniqueConstraintError:
        collection = client.get_collection(name='dental_history')

    for node in tqdm(nodes):
        transcripts = node.get_chunk_transcripts()
        metadatas = node.get_chunk_metadatas()
        ids = node.get_chunk_ids()
        embeddings = node.get_chunk_embeddings()
        collection.add(
            embeddings=embeddings,
            documents=transcripts,
            metadatas=metadatas,
            ids=ids
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process playlist ID.')
    parser.add_argument('playlist_id', type=str, help='an integer for the playlist ID')
    args = parser.parse_args()
    main(args.playlist_id)
