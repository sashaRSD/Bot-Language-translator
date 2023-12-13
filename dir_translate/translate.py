from googletrans import Translator
from dir_translate import dictionary


def translate_fun(text, src, to_lang):
    try:
        translator = Translator()
        if to_lang.startswith("zh"):
            translation = translator.translate(text=text, src=src, dest=to_lang.replace("_", "-"))
        else:
            translation = translator.translate(text=text, src=src, dest=to_lang)
        ret = [f"{dictionary.language_base[translation.src]} —» {dictionary.language_base[to_lang]}", translation.text]
        return ret
    except Exception as ex:
        print(ex)
        return ["Не могу понять, что за язык...", "Введите больше слов!"]
