import os
import glob
import music_tag
import uroman

FORBIDDEN_CHARACTERS = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']

# Function to process and romanize a string if string contains CJK characters
def process_string(value, uroman_consructor, replace_forbidden=False):
    try:
        romanized_value = uroman_consructor.romanize_string(value)

        if value != romanized_value:
            romanized_value = romanized_value.title()

            if replace_forbidden:
                for char in FORBIDDEN_CHARACTERS:
                    romanized_value = romanized_value.replace(char, ' - ')

            return romanized_value
        
        return value
    
    except Exception as e:
        print(f"Error processing value '{value}': {e}")
        return value

# Function to find all music files in the given path
def find_music_files(path):
    music_files = []

    for ext in ('*.mp3', '*.flac', '*.wav', '*.m4a'):
        music_files.extend(glob.glob(os.path.join(path, '**', ext), recursive=True))

    return music_files

# Function to transliterate necessary tags in a music file
def transliterate_tags(song_file_path, uroman_consructor):
    song = music_tag.load_file(song_file_path)
    print(f"Processing file: {song_file_path}")
    
    for tag in ['album', 'albumartist', 'artist', 'composer', 'tracktitle']:
        if song[tag]:
            value = str(song[tag])
            processed_value = process_string(value, uroman_consructor)

            if value != processed_value:
                print(f"Transliterating {tag} from '{value}' to '{processed_value}'")
                song[tag] = processed_value
            
    song.save()

# Function to transliterate the filename of a music file
def transliterate_filenames(file_path, uroman_consructor):
    song_filename, song_extension = os.path.splitext(os.path.basename(file_path))
    song_directory = os.path.dirname(file_path)
    processed_song_filename = process_string(song_filename, uroman_consructor, replace_forbidden=True)

    if song_filename != processed_song_filename:
        new_file_path = os.path.join(song_directory, processed_song_filename + song_extension)
        os.rename(file_path, new_file_path)
        print(f"Renamed file from '{file_path}' to '{new_file_path}'")

# Function to transliterate directory names
def transliterate_directory_names(root_path, uroman_consructor):
    for dirpath, dirnames, filenames in os.walk(root_path, topdown=False):
        for dirname in dirnames:
            processed_dirname = process_string(dirname, uroman_consructor, replace_forbidden=True)

            if dirname != processed_dirname:
                old_dir_path = os.path.join(dirpath, dirname)
                new_dir_path = os.path.join(dirpath, processed_dirname)

                try:
                    os.rename(old_dir_path, new_dir_path)
                    print(f"Renamed directory from '{old_dir_path}' to '{new_dir_path}'")
                except Exception as e:
                    print(f"Error renaming directory '{old_dir_path}': {e}")

def main():
    uroman_consructor = uroman.Uroman()
    music_library_path = r'{}'.format(input("Enter the path to your music library: ").strip())
    music_files = find_music_files(music_library_path)

    for music_file in music_files:
        transliterate_tags(music_file, uroman_consructor)
        transliterate_filenames(music_file, uroman_consructor)

    transliterate_directory_names(music_library_path, uroman_consructor)

if __name__ == "__main__":
    main()
