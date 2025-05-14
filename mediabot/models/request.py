from enum import Enum

# all the possible request types
class RequestKind(Enum):
  TRACK_SEARCH = 0,
  TRACK_DOWNLOAD = 1,
  VIDEO_SEARCH = 2,
  VIDEO_DOWNLOAD = 3,
  TIKTOK_LINK = 4,
  INSTAGRAM_LINK = 5,
  YOUTUBE_LINK = 6,
  YOUTUBE_SEARCH = 7

class TrackSearchRequest:
  search_query: str

  def __init__(self, search_query: str):
    self.search_query = search_query

class TrackDownloadRequest:
  track_id: str

  def __init__(self, track_id: str):
    self.track_id = track_id

class TikTokLinkRequest:
  tiktok_link: str

  def __init__(self, tiktok_link: str):
    self.tiktok_link = tiktok_link

class InstagramLinkRequest:
  instagram_link: str

  def __init__(self, instagram_link: str):
    self.instagram_link = instagram_link

class InstagramPlaylistItemDownloadRequest:
  id: str
  advertisement_kind: int

  def __init__(self, id: str, advertisement_kind: int):
    self.id = id
    self.advertisement_kind = advertisement_kind

class YouTubeSearchRequest:
  search_query: str

  def __init__(self, search_query: str):
    self.search_query = search_query

class YouTubeVideoDownloadRequest:
  video_id: str

  def __init__(self, video_id: str):
    self.video_id = video_id

class YouTubeAudioDownloadRequest:
  video_id: str

  def __init__(self, video_id: str):
    self.video_id = video_id

class TrackRecognizeFromAudioRequest:
  file_id: str

  def __init__(self, file_id: str):
    self.file_id = file_id

class TrackRecognizeFromVoiceRequest:
  file_id: str

  def __init__(self, file_id: str):
    self.file_id = file_id

class TrackRecognizeFromVideoRequest:
  file_id: str

  def __init__(self, file_id: str):
    self.file_id = file_id

class TrackRecognizeFromVideoNoteRequest:
  file_id: str

  def __init__(self, file_id: str):
    self.file_id = file_id
