class Playlist:
    def __init__(self):
        self._song = []
        # self._song = [{"name": "test_duration", "duration": "123"}]

    def add_song(self, name, duration):
        try:
            clean_name = name.strip()
            if not clean_name:
                raise ValueError("Название не может быть пустотой")

            float_duration = float(duration)
            if float_duration <= 0:
                raise ValueError("Продолжительность должна быть больше нуля")

            song = {
                "name": name,
                "duration": float_duration,
            }
            self._song.append(song)
            print("Песня добавлена")

        except ValueError as e:
            if "could not convert string to float:" in str(e):
                print("Ошибка: длительность должна быть числом")
            else:
                print(f"Ошибка:{e}")
        except (AttributeError, ValueError):
            print("Ошибка: название должно быть строкой, а длительность-числом")

    def remove_song(self, name):
        try:
            search_name = name.strip().lower()
            for song in self._song:
                if song['name'].strip().lower() == search_name:
                    self._song.remove(song)
                    print("Песня удалена")
                    return

            print(f"песня {name} не найдена в плейлисте")

        except (AttributeError, TypeError):
            print("Ошибка: некоректное название")

    def total_duration(self):
        try:
            duration_pl = sum(song["duration"] for song in self._song)
            return duration_pl
        except (KeyError, TypeError):
            print("Ошибка: некоректна длительность треков")
            return 0

    def __len__(self):
        return len(self._song)

    def display(self):
        if not self._song:
            print("Плейлист пуст")
        else:
            print(f"Кол-во треков: {len(self)}, Длительность плейлиста: {self.total_duration()}")
            for index, song in enumerate(self._song):
                print(f"{index + 1}. {song['name']} {song['duration']} секунд")


if __name__ == "__main__":
    playlist = Playlist()
    print(playlist.total_duration())
    print(len(playlist))
    playlist.display()
    playlist.add_song("Song 1", 200)
    playlist.add_song("Song 2", 300)
    playlist.add_song("Song 3", 400)
    playlist.add_song("Song 4", 500.33)
    print(len(playlist))
    print(playlist.total_duration())
    playlist.remove_song("Song 1")
    print(playlist.total_duration())
    print("")
    playlist.remove_song("мьлмля")
    playlist.add_song("Song 3", "2 min")
    playlist.add_song(123, 120)
    playlist.add_song("  ", 120)
    playlist.remove_song(300)
    print("")
    playlist.display()