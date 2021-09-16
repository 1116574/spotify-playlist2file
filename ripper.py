import argparse, re, sys, platform
import requests, bs4

parser = argparse.ArgumentParser(description='Get a txt of all songs in a spotify playlist')
parser.add_argument('spotify_url', type=str, help='url to playlist')
parser.add_argument('-f', '--format', type=str, help='output format. Default is `plain` meaning nice, human readable output.', choices=['plain', 'csv', 'csv_split_artists'], default='plain')
parser.add_argument('-e', '--encoding', type=str, help='encoding of output. useful if piping doesnt work properly. Default is utf-8 for linux and utf-16 for windows when piping')
args = parser.parse_args()

spotify_url = args.spotify_url
format = args.format
encoding = args.encoding

# Windows based terminals (cmd, ps) use utf-16 (why??)
# in turn, this fixes piping behaviour for windows users
if platform.system() == 'Windows' and encoding == None and not sys.stdout.isatty():  # isatty checks if its piping or a terminal
    sys.stdout.reconfigure(encoding='utf=16')


# Download spotify website

if not re.match(r'.+open\.spotify\.com\/playlist.+', spotify_url):  # TODO add force flag
    print('Error: URL does not conform to spotify standard playlist URL')
    sys.exit(1)

songs = []

playlist_website = requests.get(spotify_url)

parsed = bs4.BeautifulSoup(playlist_website.text, features='html.parser')  # We are searching for <meta> because its easier then parsing through spotifies mimified website
for song in parsed.find_all('meta'):
    if song.get('property') == 'music:song':
        tmp = song.get('content')
        songs.append(tmp)  # We extract URL of the song (name isnt in the <meta>)


# Print it out

for song in songs:
    resp = requests.get(song).text  # Now we connect to urls found earlier
    bs = bs4.BeautifulSoup(resp, features='html.parser')
    # print(bs.title.string)  # Yes, we extract song title and author from <title> with use of regex
    extracted = re.match(r'(.+) - song by (.+) \| Spotify', bs.title.string)
    if format == 'plain':
        print(f'{extracted[1]} by {extracted[2]}')
    elif format == 'csv':
        name = extracted[1]
        author = extracted[2].replace(',', ';')
        print(f'{name}, {author}')
    elif format == 'csv_split_artists':
        print(f'{extracted[1]}, {extracted[2]}')

# Note: this is horribly inefficient, and for large playlists will make a lot of requests. Better approach would be to extract info from playlist website itself,
# but its so mimified with css classes looking like base64 credentials that this is just simpler to do.
