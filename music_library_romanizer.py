import os
import music_tag
import uroman

FORBIDDEN_CHARACTERS = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']

# Function to find paths, directories, and files in the given root path
def scan_directory(root_path):
    directory_paths = []
    file_paths = []

    for dirpath, dirnames, filenames in os.walk(root_path, topdown=False):
        directory_paths.extend([os.path.join(dirpath, dirname) for dirname in dirnames])
        file_paths.extend([os.path.join(dirpath, filename) for filename in filenames])

    return directory_paths, file_paths

# Function to process and romanize a string if string contains CJK characters
def process_string(str, uroman_consructor, replace_forbidden=False):
    try:
        romanized_str = uroman_consructor.romanize_string(str)

        if str != romanized_str:
            romanized_str = ''
            temp = ''
            
            for char in str:
                romanized_char = uroman_consructor.romanize_string(char)

                if char == romanized_char:
                    if len(temp) > 0:
                        temp = uroman_consructor.romanize_string(temp)
                        romanized_str += temp.title().strip()
                        temp = ''

                    romanized_str += char
                else:
                    temp += char
            
            if len(temp) > 0:
                temp = uroman_consructor.romanize_string(temp)
                romanized_str += temp.title().strip()

            if replace_forbidden:
                for forbidden_char in FORBIDDEN_CHARACTERS:
                    romanized_str = romanized_str.replace(forbidden_char, '-')

            return romanized_str

        return str
    
    except Exception as e:
        print(f"Error processing value '{str}': {e}")
        return str

# Function to transliterate tags with string values in a music file
def transliterate_tags(file_path, uroman_consructor):
    song = music_tag.load_file(file_path)
    print(f"Processing file: {file_path}")

    for tag in ['album', 'albumartist', 'artist', 'composer', 'tracktitle']:
        if song[tag]:
            value = str(song[tag])
            processed_value = process_string(value, uroman_consructor)

            if value != processed_value:
                print(f"Transliterating {tag} from '{value}' to '{processed_value}'")
                song[tag] = processed_value
            
    song.save()

# Function to transliterate filenames
def transliterate_filename(file_path, uroman_consructor):
    song_filename, song_extension = os.path.splitext(os.path.basename(file_path))
    song_directory = os.path.dirname(file_path)
    processed_song_filename = process_string(song_filename, uroman_consructor, replace_forbidden=True)

    if song_filename != processed_song_filename:
        new_file_path = os.path.join(song_directory, processed_song_filename + song_extension)

        try:
            os.rename(file_path, new_file_path)
            print(f"Renamed file from '{file_path}' to '{new_file_path}'")
        except Exception as e: 
            print(f"Error renaming file '{file_path}': {e}")

# Function to transliterate directory names
def transliterate_directory_name(directory_path, uroman_consructor):
    directory = os.path.basename(directory_path)
    processed_dirname = process_string(directory, uroman_consructor, replace_forbidden=True)

    if directory != processed_dirname:
        old_dir_path = os.path.join(os.path.dirname(directory_path), directory)
        new_dir_path = os.path.join(os.path.dirname(directory_path), processed_dirname)
        try:
            os.rename(old_dir_path, new_dir_path)
            print(f"Renamed directory from '{old_dir_path}' to '{new_dir_path}'")
        except Exception as e:
            print(f"Error renaming directory '{old_dir_path}': {e}")

def main():
    uroman_consructor = uroman.Uroman()

    try:
        music_library_path = r'{}'.format(input("Enter the path to your music library: ").strip())
    except Exception as e:
        print(f"Error reading input: {e}")
        return

    directory_paths, file_paths = scan_directory(music_library_path)
    
    for file_path in file_paths:
        extension = os.path.splitext(file_path)[1]

        if extension.lower() in ['.mp3', '.flac', '.wav', '.m4a']:
            transliterate_tags(file_path, uroman_consructor)
        
        transliterate_filename(file_path, uroman_consructor)

    for directory_path in directory_paths:
        transliterate_directory_name(directory_path, uroman_consructor)

if __name__ == "__main__":
    main()
