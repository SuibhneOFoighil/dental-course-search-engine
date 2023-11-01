import os
from utils import get_embedding

NULL_ID = '\0'

def is_null(datum) -> bool:
    return datum == NULL_ID

from hashlib import sha256
def hash_string(string):
    return sha256(string.encode()).hexdigest()

class YTVideoChunk:
    def __init__(self, video_id, transcript, timestamp=0, prev=NULL_ID, next=NULL_ID) -> None:
        self.id = hash_string(str(video_id) + str(timestamp))
        self.transcript = transcript
        self.timestamp = timestamp
        self.prev = prev
        self.next = next

class YTVideo:
    def __init__(self, video_id, transcript, window=30) -> None:
        self.chunks = []
        self.id = video_id

        start_time = 0
        end_time = start_time + window
        lines = []
        prev_id = NULL_ID

        for i, line in enumerate(transcript):
            # past the end of the window -> create a new chunk
            if line['start'] > end_time:
                text = ' '.join(lines)
                timestamp = int(transcript[i-len(lines)]['start'])
                prev_id = self.chunks[-1].id if len(self.chunks) > 0 else NULL_ID
                new_chunk = YTVideoChunk(
                    video_id=video_id,
                    transcript=text,
                    timestamp=timestamp,
                    prev=prev_id
                )
                if prev_id != NULL_ID:
                    prev_chunk = self.chunks[-1]
                    prev_chunk.next = new_chunk.id

                self.chunks.append(new_chunk)
                start_time = line['start']
                end_time = start_time + window
                lines = []

            # add the line to the current document
            lines.append(line['text'])

        #for the case of less than one chunk (video < 30 seconds long)
        if len(self.chunks) == 0 and len(lines) > 0:
            text = ' '.join(lines)
            prev_id = self.chunks[-1].id if len(self.chunks) > 0 else None
            solo_chunk = YTVideoChunk(
                video_id=video_id,
                transcript=text
            )
            self.chunks.append(solo_chunk)

    "Returns list of transcripts from chunks"
    def get_chunk_transcripts(self) -> list:
        return [chunk.transcript if not is_null(chunk) else chunk for chunk in self.chunks]
    
    "Returns list of metadatas from chunks"
    def get_chunk_metadatas(self) -> list:
        return [
            {
                'video_id': self.id,
                'timestamp': chunk.timestamp,
                'prev': chunk.prev,
                'next': chunk.next
            } if not is_null(chunk) else chunk for chunk in self.chunks
        ]

    def get_chunk_ids(self) -> list:
        return [chunk.id if not is_null(chunk) else chunk for chunk in self.chunks]

    def get_chunk_embeddings(self) -> list:
        return [get_embedding(chunk.transcript) if not is_null(chunk) else chunk for chunk in self.chunks]