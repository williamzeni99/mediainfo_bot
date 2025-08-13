from httpx import URL
import tmdbsimple as tmdb 


class TMDB_RESULT:

    img_path = URL("https://image.tmdb.org/t/p/original")

    def __init__(self, data=None):
        self.genres_ids=[]
        self.id=-1
        self.title = ""
        self.vote_average = 0
        self.poster_path = ""
        self.overview = ""
        self.media_type = ""
        self.release_date = ""

        if data:
            self._parse_data(data)
        
    def _parse_data(self, data):
        self.id = data.get('id', -1)
        self.genres_ids = data.get('genre_ids', [])
        self.vote_average = data.get('vote_average', 0)
        self.poster_path = data.get('poster_path', "")
        self.overview = data.get('overview', "")
        
        # Handle title/name difference
        if 'title' in data:  # Movie
            self.title = data.get('title', "")
            self.media_type = "movie"
            self.release_date = data.get('release_date', "")
        elif 'name' in data:  # TV Show
            self.title = data.get('name', "")
            self.media_type = "tv"
            self.release_date = data.get('first_air_date', "")
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
        return str(self.img_path.join(self.poster_path))


    def download_poster(self, path: str) -> None:
        """Download poster image to specified path"""
        if not self.poster_path:
            print("No poster path available.")
            return
        
        full_url = self.img_path.join(self.poster_path)
        try:
            response = tmdb.requests.get(full_url)
            response.raise_for_status()
            with open(path, 'wb') as file:
                file.write(response.content)
            print(f"Poster downloaded to {path}")
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
        message_text += f"📺 Type: {result.media_type}\n"
        message_text += f"⭐ Rating: {result.vote_average}/10\n"
        message_text += f"🆔 ID: {result.id}\n"
        message_text += f"🎭 Genres: {genres_str}\n"
        message_text += f"📅 Release Date: {result.release_date}\n\n"
        message_text += f"📝 {result.overview}{'...' if len(result.overview) > 300 else ''}"

        return message_text
    
