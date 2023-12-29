#sesli iletişim uygulamasının arayüzsüz hali için yapıldı.
#Rise Together

#Emirhan Said ERDEM


import pyaudio
import numpy as np
import threading
import speech_recognition as sr
import random
import socketio
import mysql.connector
from string import ascii_uppercase
from scipy import signal
import os
from cryptography.fernet import Fernet

sio = socketio.Client()

class server_erkek_page:
    def __init__(self) -> None:
        super().__init__()
        #ses iletiminde sesin özellikleri:
        self.FORMAT = pyaudio.paInt16
        self.CHUNK = 1024
        self.CHANNELS = 1
        self.RATE = 44100
        self.PITCH_SHIFT_FACTOR = 1.2  
        self.stream = None
        self.output_stream = None

        self.room_code = ""
        self.Event = threading.Event()

        #######***************########
        self.create_connection()                                
        self.enter_room()
        self.start_communication() #ses göndermeyi başlat
    def create_connection(self):
        """
        MySQL veritabanına bağlantı oluşturur.
        """
        kullanici_ad = "1"
        
        connection = mysql.connector.connect(
            host="rise.czfoe4l74xhi.eu-central-1.rds.amazonaws.com",
            user="admin",
            password="Osmaniye12!",
            database="rise_data",
        )
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE veriler SET oda_kodu =%s WHERE kullanici_ad = %s ",
            (self.room_code, kullanici_ad),
        )
        connection.commit()
        connection.close()
                                        #######***************########
        
    def room_name(self):  # flask için Oda kodu oluşturuyoruz
        rooms = {}
        while True:
            for _ in range(5):
                self.room_code += random.choice(ascii_uppercase)

            if self.room_code not in rooms:
                break

        
        return self.room_code
                                        #######***************########    
    
    def enter_room(self):  # odaya isim ve oda kodu ile giriş yapılıyor
        name = "Doktor"
        room_code = self.room_name()

        print(room_code)
        sio.on("liste", self.hoparlor_liste_al) #hoparlör listesi için dinle

        sio.on("data2", self.get_sound) #gelen sesleri dinle
        

        @sio.on("connect")
        def on_connect():
            print("Bağlandı.")
           
            sio.emit("baglan", {"name": name, "room": room_code})

        @sio.event
        def disconnect():
            print("Bağlantı kesildi.")
        
        self.create_room(name, room_code)

    def create_room(self, name, room_code):
        print("oda oluşturuldu")
        sio.connect(
            "http://192.168.1.45:5000"
        )  # Flask uygulamanızın adresine göre güncelleyin.
        sio.emit("create_room", {"name": name, "room": room_code})


    def send_audio_e(self):
        print("ses aktarımı başladı")
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=self.CHANNELS,
            rate=44100,
            input=True,
            frames_per_buffer=self.CHUNK,
        )

        try:
            while True:
                #while self.is_running:
                    data = stream.read(self.CHUNK, exception_on_overflow=False)
                    audio_data = np.frombuffer(data, dtype=np.int16)

                    converted_data = (
                        signal.resample(
                            audio_data, int(len(audio_data) * self.PITCH_SHIFT_FACTOR)
                        )
                        * 1.4
                    )
                    converted_data = converted_data.astype(np.int16)
                    converted_data_bytes = converted_data.tobytes()
                    audio_data = audio_data.tobytes()

                    try:
                        sio.emit("audio_data", {"audio_data": audio_data})

                    except Exception as e:
                        print("hata",e)
                    audio_data = None
        except Exception as e:
            print("hata", e)
        finally:
            print("kapandı")
            stream.stop_stream()
            stream.close()
            p.terminate()

    def start_communication(self):
        print("start başlad")

        self.t = threading.Thread(target=self.send_audio_e)
        self.t.start()


    def get_sound(self, data):
        try:
            if self.stream is None:
                p = pyaudio.PyAudio()
                self.stream = p.open(
                    format=self.FORMAT,
                    channels=self.CHANNELS,
                    rate=self.RATE,
                    output=True,
                    frames_per_buffer=1024,
                )
            if data:
                audio_data = data.get("audio_data2", b"")

                #if self.is_running_recv:
                self.stream.write(audio_data)

            else:
                print("data yok")

        except Exception as e:
            print("Ses alma hatası:", str(e))
            if self.stream is not None:
                        self.stream.close()
                        self.stream.stop_stream()


    def yazi_gonder(self):
        room = self.room_code

        name = "Doktor"

        try:
            message = self.server_erkek.metin_yeri.toPlainText()
            message = input("Göndereceğiniz Metin girin")
            secili_efekt = (
                self.server_erkek.efek_combobox.currentIndex()
            )  # comboboxda ki efekti al
            efekt = int(secili_efekt)
            efekt = input("metni okunacak efekti seçin:  0: erkek, 1:kadın, 2:çocuk, 3:yaşlı kadın(babanne), 4:yaşlı adam(dede)")

            # Anahtar oluştur
            key = self.generate_key()  # text için key oluştur

            encrypted_message = self.encrypt_message(message, key)  # Mesajı şifrele

            # flaskta ki message olayına şifreli mesajı- room-efekt ve keyi sözcük içinde emitle
            sio.emit(
                "message",
                {
                    "data": encrypted_message.decode(),
                    "room": room,
                    "name": name,
                    "efekt": efekt,
                    "key": key,
                },
            )
        except KeyboardInterrupt:
            pass

            # sio.wait()

            # sio.disconnect()

            #################******######################

    def yazi_gonder_t(self):
        t1 = threading.Thread(target=self.yazi_gonder)
        t1.start()

    def generate_key(self):
        return Fernet.generate_key()  # key oluştur

    def encrypt_message(self, message, key):  # keyi ve mesajı al
        cipher_suite = Fernet(key)  # şifreli paketi oluştur
        encrypted_message = cipher_suite.encrypt(
            message.encode()
        )  # şifrelenmiş mesajı oluştur ve return et
        return encrypted_message
    
    def hoparlor_liste_al(self, Liste):
        # öğrenci tarafından gelen hoparlor listesini al ve arayüzdeki listeye aktar
        hoparlor_liste = Liste["list"]
        print("liste geldi")
        print(hoparlor_liste)
    
    def ogr_hoparlor_sec(self):
        # Seç butonu ile ögrenci hoparlörünü seç ve seçilen indexi istemciye yolla
        #selected = self.server_erkek.ogrenci_hoparlor_liste.selectedIndexes()
        selected = input("Karşı taraftan gelen hoparlör listesinden bir hoparlör seçiniz.")
        selected_row = selected[0].row()  # İndexin ilk elemanını al
        print(selected_row)
        #sio.emit("output_device_index", {"index": selected_row}) # index sözcüğü ile gönder
        sio.emit("output_device_index", {"index": selected})
        
    
if __name__ == "__main__":
    chat_app = server_erkek_page()
