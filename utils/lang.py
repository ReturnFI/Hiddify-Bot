import json

class Language:
    def __init__(self, lang_file):
        self.lang_file = lang_file
        self.language_data = self.load_language()

    def load_language(self):
        with open(self.lang_file, 'r', encoding='utf-8') as file:
            return json.load(file)

    def get_string(self, lang_code, key):
        return self.language_data.get(lang_code, {}).get(key, f'[{key}]')

lang = Language('language/lang.json')
