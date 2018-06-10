# -*- coding: utf-8 -*-

import httplib2
import os
import sys
import json

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


def get_authenticated_service():

    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, SCOPES)

    # storage = Storage("%s-oauth2.json" % sys.argv[0])
    storage = Storage(r'/home/jmb/reddit_top_10/youtube_api.py-oauth2.json')
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        flags = argparser.parse_args()
        credentials = run_flow(flow, storage, flags)

    return build(API_SERVICE_NAME, API_VERSION, http=credentials.authorize(httplib2.Http()))


def print_response(response):
    print(json.dumps(response, sort_keys=True, indent=4))


# Build a resource based on a list of properties given as key-value pairs.
# Leave properties with empty values out of the inserted resource.
def build_resource(properties):
    resource = {}
    for p in properties:
        # Given a key like "snippet.title", split into "snippet" and "title", where
        # "snippet" will be an object and "title" will be a property in that object.
        prop_array = p.split('.')
        ref = resource
        for pa in range(0, len(prop_array)):
            is_array = False
            key = prop_array[pa]

            # For properties that have array values, convert a name like
            # "snippet.tags[]" to snippet.tags, and set a flag to handle
            # the value as an array.
            if key[-2:] == '[]':
                key = key[0:len(key) - 2:]
                is_array = True

            if pa == (len(prop_array) - 1):
                # Leave properties without values out of inserted resource.
                if properties[p]:
                    if is_array:
                        ref[key] = properties[p].split(',')
                    else:
                        ref[key] = properties[p]
            elif key not in ref:
                # For example, the property is "snippet.title", but the resource does
                # not yet have a "snippet" object. Create the snippet object here.
                # Setting "ref = ref[key]" means that in the next time through the
                # "for pa in range ..." loop, we will be setting a property in the
                # resource's "snippet" object.
                ref[key] = {}
                ref = ref[key]
            else:
                # For example, the property is "snippet.description", and the resource
                # already has a "snippet" object.
                ref = ref[key]
    return resource


# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.items():
            if value:
                good_kwargs[key] = value
    return good_kwargs


def list_videos(client, **kwargs):
    """return video info"""
    kwargs = remove_empty_kwargs(**kwargs)
    response = client.videos().list(**kwargs).execute()
    # print_response(response)
    return response


def list_playlist_items(client, **kwargs):
    """return playlistItem info"""
    kwargs = remove_empty_kwargs(**kwargs)
    response = client.playlistItems().list(**kwargs).execute()
    # print_response(response)
    return response


def list_playlists(client, **kwargs):
    """return playlist info"""
    kwargs = remove_empty_kwargs(**kwargs)
    response = client.playlists().list(**kwargs).execute()
    # print_response(response)
    return response


def insert_playlist_items(client, properties, **kwargs):
    """add video to Playlist"""
    resource = build_resource(properties)
    kwargs = remove_empty_kwargs(**kwargs)
    response = client.playlistItems().insert(body=resource, **kwargs).execute()
    # print_response(response)
    return response


def insert_playlists(client, properties, **kwargs):
    """create Playlist"""
    resource = build_resource(properties)
    kwargs = remove_empty_kwargs(**kwargs)
    response = client.playlists().insert(body=resource, **kwargs).execute()
    # print_response(response)
    return response


def delete_playlist_items(client, **kwargs):
    """delete Playlist"""
    kwargs = remove_empty_kwargs(**kwargs)
    response = client.playlistItems().delete(**kwargs).execute()
    # print_response(response)
    return response


def delete_playlists(client, **kwargs):
    """delete Playlist"""
    kwargs = remove_empty_kwargs(**kwargs)
    response = client.playlists().delete(**kwargs).execute()
    # print_response(response)
    return response


def update_playlists(client, properties, **kwargs):
    """update playlist info"""
    resource = build_resource(properties)
    kwargs = remove_empty_kwargs(**kwargs)
    response = client.playlists().update(body=resource, **kwargs).execute()
    # print_response(response)
    return response


if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification. When
    # running in production *do not* leave this option enabled.
    # os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    pass

    # # typical use cases
    # client = get_authenticated_service()
    #
    # list_playlists(client,
    #                              part='snippet,contentDetails',
    #                              channelId='UC_x5XG1OV2P6uZZ5FSM9Ttw',
    #                              maxResults=25)
    #
    # insert_playlists(client,
    #                  {'snippet.title': 'temp3',
    #                   'snippet.description': 'wow',
    #                   'snippet.tags[]': 'tag1, tag2, tag3',
    #                   'snippet.defaultLanguage': '',
    #                   'status.privacyStatus': 'private'},
    #                  part='snippet,status',
    #                  onBehalfOfContentOwner='')
    #
    # delete_playlist_items(client,
    #                  id='REPLACE_ME',
    #                  onBehalfOfContentOwner='')
    #
    # playlist_items_list_by_playlist_id(client,
    #                                    part='snippet,contentDetails',
    #                                    maxResults=25,
    #                                    playlistId='PLBCF2DAC6FFB574DE')
    #
    # insert_playlist_items(client,
    #                       {'snippet.playlistId': '',
    #                        'snippet.resourceId.kind': 'YoutubeClient#video',
    #                        'snippet.resourceId.videoId': 'M7FIvfx5J10',
    #                        'snippet.position': ''},
    #                       part='snippet',
    #                       onBehalfOfContentOwner='')
    #
    # list_videos(client,
    #             part='snippet,contentDetails,statistics',
    #             id='Ks-_Mh1QhMc,c0KYU2j0TM4,eIho2S0ZahI')

    # list_playlist_items(client,
    #     part='snippet,contentDetails',
    #     maxResults=25,
    #     playlistId='PLBCF2DAC6FFB574DE')

    # update_playlists(client,
    #     {'id': '',
    #      'snippet.title': '',
    #      'snippet.description': '',
    #      'snippet.tags[]': '',
    #      'status.privacyStatus': ''},
    #     part='snippet,status',
    #     onBehalfOfContentOwner='')
