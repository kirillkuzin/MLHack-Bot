import speech_recognition as sr
import pydub


class Statement:
    def __init__(self, statement_dict):
        self.confidence = statement_dict['confidence']
        self.text = statement_dict['transcript'].lower()

    def __repr__(self):
        return "[{}] {}".format(self.confidence, self.text)

    def __str__(self):
        return self.text

    def __gt__(self, other):
        return self.confidence > other.confidence


class Recognizer:
    def __init__(self, google_threshold=0.5):
        self.recognizer = sr.Recognizer()
        self.google_threshold = google_threshold

    def recognize(self, ogg_path: str):
        audio_file = self._get_audio_file_from_ogg(ogg_path)
        audio_data = self._get_audio_data_from_audio_file(audio_file)
        statements = []
        try:
            json = self.recognizer.recognize_google(audio_data,
                                                    language="en_US",
                                                    show_all=True)
            statements = self._json_to_statements(json)
        except sr.UnknownValueError:
            print("[GoogleSR] Неизвестное выражение")
        except sr.RequestError as e:
            print("[GoogleSR] Не могу получить данные; {0}".format(e))
        recognized_text = self._choose_best_statement(statements)
        if recognized_text is None:
            return None
        return self._correct_sentence(recognized_text.text)

    def _json_to_statements(self, json):
        statements = []
        if len(json) != 0:
            for json_dict in json['alternative']:
                if 'confidence' not in json_dict:
                    json_dict['confidence'] = self.google_threshold + 0.1
                statements.append(Statement(json_dict))
        return statements

    def _get_audio_data_from_audio_file(self,
                                        audio_file: sr.AudioFile):
        with audio_file as source:
            # self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
            audio_data = self.recognizer.record(source)
        return audio_data

    @staticmethod
    def _get_audio_file_from_ogg(ogg_path: str) -> sr.AudioFile:
        wav_path = ogg_path[:-3] + 'wav'
        ogg_file = pydub.AudioSegment.from_ogg(ogg_path)
        ogg_file.export(out_f=wav_path, format='wav')
        return sr.AudioFile(wav_path)

    @staticmethod
    def _choose_best_statement(statements):
        if statements:
            return max(statements, key=lambda s: s.confidence)
        else:
            return None

    def _correct_sentence(self, sentence):
        sentence = sentence[0].upper() + sentence[1:]
        sentence = self._correct_i(sentence)
        return sentence

    @staticmethod
    def _correct_i(sentence):
        sentence = sentence.replace(' i ', ' I ')
        sentence = sentence.replace(' i.', ' I.')
        return sentence
