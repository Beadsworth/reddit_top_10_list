from youtube_api import get_authenticated_service,  list_videos, list_playlists, list_playlist_items, \
    insert_playlists, delete_playlists, delete_playlist_items, insert_playlist_items, update_playlists


class Video:

    def refresh(self):
        """init or refresh an existing object"""
        response = list_videos(self.client, part='snippet,statistics', id=self.id)
        #TODO fix this handling of bad ids
        if len(response['items']) > 0:
            video_dict = response['items'][0]

            self.title = video_dict['snippet']['title']
            self.description = video_dict['snippet']['description']
            self.published_at = video_dict['snippet']['publishedAt']
            self.view_count = video_dict['statistics']['viewCount']

        return self

    def __init__(self, client, video_id):

        self.client = client
        self.id = video_id

        self.title = None
        self.description = None
        self.published_at = None
        self.view_count = None

        self.refresh()


class PlaylistItem:

    def refresh(self):
        """init or refresh an existing object"""
        response = list_playlist_items(self.client, part='snippet', id=self.id)
        playlist_item_dict = response['items'][0]

        self.position = playlist_item_dict['snippet']['position']
        self.playlist_id = playlist_item_dict['snippet']['playlistId']
        self.video_id = playlist_item_dict['snippet']['resourceId']['videoId']

        return self

    def __init__(self, client, playlist_item_id):

        self.client = client
        self.id = playlist_item_id

        self.position = None
        self.playlist_id = None
        self.video_id = None

        self.refresh()

    @property
    def video(self):
        return Video(client=self.client, video_id=self.video_id)

    #TODO determine if refresh possible
    def delete(self):
        delete_playlist_items(self.client, id=self.id, onBehalfOfContentOwner='')


class Playlist:

    def refresh(self):
        """init or refresh an existing object"""
        response = list_playlists(self.client, part='snippet,status', id=self.id)
        playlist_item_dict = response['items'][0]

        self.title = playlist_item_dict['snippet']['title']
        self.description = playlist_item_dict['snippet']['description']
        self.published_at = playlist_item_dict['snippet']['publishedAt']
        self.privacy_status = playlist_item_dict['status']['privacyStatus']

        return self

    def __init__(self, client, playlist_id):

        self.client = client
        self.id = playlist_id

        self.title = None
        self.description = None
        self.published_at = None
        self.privacy_status = None

        self.refresh()

    @property
    def playlist_items(self):
        """playlist_items for a playlist"""
        response = list_playlist_items(self.client, part='id', playlistId=self.id, maxResults=50)
        return {item['id']: PlaylistItem(client=self.client, playlist_item_id=item['id']) for item in response['items']}

    def update(self, title=None, description=None, tags='', privacy_status=None):
        """update playlist info"""
        if title is None:
            title = self.title
        if description is None:
            description = self.description
        if privacy_status is None:
            privacy_status = self.privacy_status

        response = update_playlists(self.client,
                                    {'id': self.id,
                                     'snippet.title': title,
                                     'snippet.description': description,
                                     'snippet.tags[]': tags,
                                     'status.privacyStatus': privacy_status},
                                    part='snippet,status',
                                    onBehalfOfContentOwner='')

        self.refresh()
        return self

    #TODO determine if refresh is possible
    def delete(self):
        delete_playlists(self.client, id=self.id, onBehalfOfContentOwner='')

    def remove_playlist_item(self, playlist_item_id):
        self.playlist_items[playlist_item_id].delete()
        return self

    def clear(self):
        for playlist_item_id, playlist_item in self.playlist_items.items():
            playlist_item.delete()

        return self

    def add_video(self, video_id):
        """add video to playlist and return playlist_item"""
        response = insert_playlist_items(self.client,
                                         {'snippet.playlistId': self.id,
                                          'snippet.resourceId.kind': 'youtube#video',
                                          'snippet.resourceId.videoId': video_id,
                                          'snippet.position': ''},
                                         part='snippet',
                                         onBehalfOfContentOwner='')

        return self


class YoutubeClient:

    def __init__(self, channel_id):
        """create YoutubeClient client"""
        self.client = get_authenticated_service()
        self.channel_id = channel_id

    def get_video(self, video_id):
        """get one single video"""
        return Video(client=self.client, video_id=video_id)

    def get_playlist_item(self, playlist_item_id):
        """get one single playlist_item"""
        return PlaylistItem(client=self.client, playlist_item_id=playlist_item_id)

    def get_playlist(self, playlist_id):
        """get one single playlist"""
        return Playlist(client=self.client, playlist_id=playlist_id)

    def get_channel_playlists(self, channel_id):
        """get the playlists of one channel"""
        response = list_playlists(self.client, part='id', channelId=channel_id, maxResults=50)
        return {item['id']: Playlist(client=self.client, playlist_id=item['id']) for item in response['items']}

    def create_playlist(self, title, description='', tags='', default_language='', privacy_status=''):
        response = insert_playlists(self.client,
                                    {'snippet.title': title,
                                     'snippet.description': description,
                                     'snippet.tags[]': tags,
                                     'snippet.defaultLanguage': default_language,
                                     'status.privacyStatus': privacy_status},
                                    part='snippet,status',
                                    onBehalfOfContentOwner='')

        return self.get_playlist(response['id'])


    # def most_popular(self):
    #     response = videos_list_most_popular(self.client,
    #                                         part='snippet,contentDetails,statistics',
    #                                         chart='mostPopular',
    #                                         regionCode='US',
    #                                         maxResults=10,
    #                                         videoCategoryId='')
    #
    #     return [Video(video_dict) for video_dict in response['items']]


if __name__ == '__main__':
    # connect to youtube
    my_channel_id = 'UC0exDb_XPQxlt-95mbwEv5w'
    youtube = YoutubeClient(my_channel_id)
    print(youtube.get_playlist('PLinG0ekH7Ldtx6fks9Mxo6XEV7jLG02fB').title)
