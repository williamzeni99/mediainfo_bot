from httpx import URL
import tmdbsimple as tmdb 


class TMDB_RESULT:

    img_path = "https://image.tmdb.org/t/p/original"
    thumbnail_path = "https://image.tmdb.org/t/p/w500"

    def __init__(self, data=None):
        self.genres_ids=[]
        self.id=-1
        self.title = ""
        self.vote_average:float = 0.0
        self.poster_path = None
        self.overview = ""
        self.media_type = ""
        self.release_date = ""

        if data:
            self._parse_data(data)
        
    def _parse_data(self, data):
        self.id = data.get('id', -1)
        self.genres_ids = data.get('genre_ids', [])
        self.vote_average = round(float(data.get('vote_average', 0)), 1)
        self.poster_path = data.get('poster_path', None)
        self.overview = data.get('overview', None)
        
        # Handle title/name difference
        if 'title' in data:  # Movie
            self.title = data.get('title', None)
            self.media_type = "movie"
            self.release_date = data.get('release_date', None)
        elif 'name' in data:  # TV Show
            self.title = data.get('name', None)
            self.media_type = "tv"
            self.release_date = data.get('first_air_date', None)
        else:
            self.title = "Unknown Title"

    def get_year(self):
        """Extract year from release date"""
        if self.release_date:
            return self.release_date.split('-')[0]
        return "Unknown"
    
    def get_formatted_title(self):
        """Get title with year"""
        year = self.get_year()
        return f"{self.title} ({year})"
    
    def __str__(self):
        return f"title: {self.title}\n id: {self.id}\n" \
               f"vote_average: {self.vote_average}\n" \
               f"poster_path: {self.poster_path}\n" \
               f"overview: {self.overview}\n" \
               f"media_type: {self.media_type}\n" \
               f"release_date: {self.release_date}\n" \
               f"genres_ids: {self.genres_ids}\n"   

    def get_poster_url(self) -> str|None:
        """Get full URL for poster image"""
        if not self.poster_path:
            return None
        return self.img_path + self.poster_path
    
    def get_thumbnail_url(self) -> str|None:
        """Get full URL for thumbnail image"""
        if not self.poster_path:
            return None
        return self.thumbnail_path + self.poster_path

    def download_poster(self) -> bytes|None:
        """Download poster image to specified path"""
        if not self.poster_path:
            print("No poster path available.")
            return
        
        full_url = self.img_path + self.poster_path
        try:
            response = tmdb.requests.get(full_url)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error downloading poster: {e}")



class TMDB_WRAPPER:
    
    def __init__(self, api:str):
        self.API_KEY = api
        tmdb.API_KEY = api
    
    def search(self, title: str) -> list[TMDB_RESULT]:
        """Search for movies and TV shows"""
        try:
            search = tmdb.Search()
            results = []
            
            # Search movies
            search.movie(query=title)
            for movie_data in search.results:
                result = TMDB_RESULT(movie_data)
                results.append(result)
            
            # Search TV shows
            search.tv(query=title)
            for tv_data in search.results:
                result = TMDB_RESULT(tv_data)
                results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Error searching TMDB: {e}")
            return []

    def get_movie(self, movie_id: int) -> TMDB_RESULT:
        """Get movie details by ID"""
        try:
            movie = tmdb.Movies(movie_id)
            data = movie.info()
            return TMDB_RESULT(data)
        except Exception as e:
            print(f"Error getting movie details: {e}")
            return TMDB_RESULT()
        
    def get_tv_show(self, tv_id: int) -> TMDB_RESULT:
        """Get TV show details by ID"""
        try:
            tv = tmdb.TV(tv_id)
            data = tv.info()
            return TMDB_RESULT(data)
        except Exception as e:
            print(f"Error getting TV show details: {e}")
            return TMDB_RESULT()

    def print_result(self, result: TMDB_RESULT)-> str:
        """return a str with icons for telegram and resolves genere ids"""
        
        if result.media_type == "movie":
            x_genres = tmdb.Genres().movie_list().get('genres', [])
        else:
            x_genres = tmdb.Genres().tv_list().get('genres', [])
        
        genres = [genre['name'] for genre in x_genres if genre['id'] in result.genres_ids]
        genres_str = ', '.join(genres) if genres else "Unknown Genres"

        # Create formatted message
        message_text = f"🎬 *{result.title}*\n"
        message_text += f"⭐ Rating: {result.vote_average}/10\n"
        # add trailer link if available
        trailer = self.find_youtube_trailer(result)
        if trailer:
            message_text += f"📺 Trailer: [Watch here]({trailer})\n"       
        message_text += f"🎭 Genres: {genres_str}\n"
        message_text += f"📅 Release Date: {result.release_date}\n\n"
        if len(result.overview) + len(message_text) > 1000:
            message_text += f"📝 {result.overview[:1000-len(message_text)]}..."
        else:
            message_text += f"📝 {result.overview}"    
       
        return message_text
    
    def find_youtube_trailer(self, result: TMDB_RESULT) -> str|None:
        """Find YouTube trailer for a movie or TV show"""
        try:
            if result.media_type == "movie":
                video = tmdb.Movies(result.id).videos().get('results', [])
            else:
                video = tmdb.TV(result.id).videos().get('results', [])
            
            for item in video:
                if item['site'] == 'YouTube' and item['type'] == 'Trailer' and item['size'] == 1080:
                    return f"https://www.youtube.com/watch?v={item['key']}"
            return None
        except Exception as e:
            print(f"Error finding YouTube trailer: {e}")
            return None