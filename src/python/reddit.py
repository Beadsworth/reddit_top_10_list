import praw
import reddit_secret

from urllib import parse


def is_youtube_video(submission):
    """determine if reddit_client submission is a youtube video"""
    return submission.media is not None \
           and 'type' in submission.media \
           and 'oembed' in submission.media \
           and 'title' in submission.media['oembed']\
           and 'youtube.com' in submission.media['type']


def video_id_from_url(url):
    """
    Examples:
    - http://youtu.be/SA2iWivDJiE
    - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    - http://www.youtube.com/embed/SA2iWivDJiE
    - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    - https://www.youtube.com/attribution_link?a=LCwtEiE4d5w&u=%2Fwatch%3Fv%3D8sg8lY-leE8%26feature%3Dshare
    """
    query = parse.urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com', 'm.youtube.com'):
        if query.path == '/watch':
            p = parse.parse_qs(query.query)
            return p['v'][0]
        if query.path == '/attribution_link':
            p = parse.parse_qs(query.query)
            return p['a'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]

    # fail?
    return None


class YoutubeVideo:

    def __init__(self, submission):

        self.subreddit = submission.subreddit.display_name
        self.url = submission.url
        self.media_type = submission.media['type']
        self.media_title = submission.media['oembed']['title']
        self.reddit_submission_title = submission.title
        self.id = video_id_from_url(self.url)


class RedditYoutubeVideos:

    def __init__(self):
        self.client = praw.Reddit(user_agent=reddit_secret.user_agent,
                                  client_id=reddit_secret.client_id,
                                  client_secret=reddit_secret.client_secret)

    def get_reddit_videos(self, subreddit='videos', period='day', limit=10):
        """return list of YoutubeVideo objects"""
        factor = 10
        extended_limit = limit * factor
        extended_list = (YoutubeVideo(submission) for submission
                         in self.client.subreddit(subreddit).top(time_filter=period, limit=extended_limit)
                         if is_youtube_video(submission))
        # only return videos with valid IDs
        return [video for video in extended_list if video.id is not None][:limit]


if __name__ == '__main__':
    reddit = RedditYoutubeVideos()

    for video in reddit.get_reddit_videos():
        print("{0:<25} {1:<25}".format(video.media_title, video.id))

