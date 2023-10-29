import argparse
import googleapiclient.discovery
import googleapiclient.errors
from youtube_transcript_api import YouTubeTranscriptApi
from chroma_vector_db import ChromaVectorDB

def main(playlist_id):
    # Define the YouTube API client
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey="YOUR_API_KEY_HERE")

    # Get the playlist items
    playlist_items = []
    next_page_token = None
    while True:
        request = youtube.playlistItems().list(
            part="snippet",
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
    video_ids = [item["snippet"]["resourceId"]["videoId"] for item in playlist_items]

    # Get the metadata for each video
    videos = []
    for video_id in video_ids:
        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        response = request.execute()
        videos += response["items"]

    # Get the transcripts for each video
    transcripts = []
    for video_id in video_ids:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcripts.append(transcript)
        except:
            transcripts.append([])

    # Chunk the transcripts into nodes
    nodes = []
    for transcript in transcripts:
        for i in range(0, len(transcript), 10):
            nodes.append(transcript[i:i+10])

    # Insert the nodes into the local persistent ChromaVectorDB
    db = ChromaVectorDB("YOUR_DB_PATH_HERE")
    for node in nodes:
        db.insert(node)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process playlist ID.')
    parser.add_argument('playlist_id', type=str, help='an integer for the playlist ID')
    args = parser.parse_args()
    main(args.playlist_id)
