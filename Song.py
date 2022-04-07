import youtube_dl

class Song():
    def __init__(self):
        self.opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(id)s%(ext)s',
            'restrictfilenames': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
        }
    
    def verifyArgs(self, args):
        if 'list='in args and 'http' in args:
            result = self.extractToPlaylist(args)
        else:
            result = self.extractToUrl(args)        

        return result

    def extractToUrl(self, url) -> dict:
        with youtube_dl.YoutubeDL(self.opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        if 'entries' in info:
            info = info['entries'][0]

        return {'title': info['title'], 'url': info['webpage_url'], 'formats': info['formats'][0]['url']}

    def extractToPlaylist(self, url) -> list:
        path = 'https://www.youtube.com/watch?v='
        playlist = []

        with youtube_dl.YoutubeDL(self.opts) as ydl:
            info = ydl.extract_info(url, download=False, process=False)

        if 'entries' in info:
            for entry in info['entries']:
                playlist.append({'title': entry['title'], 'url': path + entry['url']})
        else:
            playlist = self.extractToPlaylist(info['url'])

        
        playlist[0] = self.extractToUrl(playlist[0]['url'])

        return playlist

        