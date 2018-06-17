import traceback

from datetime import datetime as dt
from reddit import RedditYoutubeVideos
from youtube import YoutubeClient


class RedditPlaylist:

    def __init__(self, reddit_client, youtube_client, subreddit, youtube_playlist_id, playlist_size=10):
        self.reddit_client = reddit_client
        self.youtube_client = youtube_client
        self.subreddit = subreddit
        self.youtube_playlist_id = youtube_playlist_id
        self.playlist_size = playlist_size

    def update(self):
        """grab reddit_client data, populate youtube playlist"""
        try:

            # get 10 ten youtube videos from r/videos
            reddit_videos = self.reddit_client.get_reddit_videos(subreddit=self.subreddit,
                                                                 period='day',
                                                                 limit=2*self.playlist_size)

            valid_videos = {video.id: video for video in reddit_videos if video.id}
            # verify video_ids with Youtube
            youtube_videos = [self.youtube_client.get_video(video_id) for video_id in valid_videos][:self.playlist_size]

            # generate new playlist description
            header = "This playlist was updated automatically at {0}".format(dt.now().strftime('%m/%d/%y %H:%M:%S'))
            reddit_video_list_str = '\r\n'.join(['{0}. {1}'.format(i + 1, valid_videos[x.id].reddit_submission_title)
                                                 for i, x in enumerate(youtube_videos)])
            description = header + '\r\n\r\n' + reddit_video_list_str

            # print video titles
            print("#"*100 + '\r\n' + description + '\r\n' + "#"*100 + "\n")

            # get playlist
            youtube_playlist = self.youtube_client.get_playlist(self.youtube_playlist_id)
            # update playlist metadata
            youtube_playlist.update(title='r\\'+str(self.subreddit), description=description, privacy_status='Public')
            # clear playlist
            youtube_playlist.clear()

            # populate playlist
            for youtube_video in youtube_videos:
                # existing videos only
                if youtube_video.title is not None:
                    youtube_playlist.add_video(youtube_video.id)

        except Exception as e:
            traceback.print_exc()


if __name__ == '__main__':

    print('#'*50)
    print("Script started at {0}".format(dt.now().strftime('%m/%d/%y %H:%M:%S')))

    # connect to reddit_client
    reddit_client = RedditYoutubeVideos()
    # connect to youtube
    my_channel_id = 'UC0exDb_XPQxlt-95mbwEv5w'
    youtube_client = YoutubeClient(my_channel_id)

    # playlists
    playlist_ids = {
        'videos': 'PLinG0ekH7Ldv_gJLKqiVxA4XZE9Xkvyjk',
        'youtubehaiku': 'PLinG0ekH7Ldtx6fks9Mxo6XEV7jLG02fB',
        'music': 'PLinG0ekH7Lds_yvZZxkOOd93GWFb87FUl'
    }

    # create RedditPlaylist objects
    playlists = [RedditPlaylist(reddit_client=reddit_client,
                                youtube_client=youtube_client,
                                subreddit=subreddit,
                                youtube_playlist_id=playlist_id) for subreddit, playlist_id in playlist_ids.items()]

    for playlist in playlists:
        playlist.update()
