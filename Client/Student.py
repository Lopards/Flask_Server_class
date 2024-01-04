# sesli iletişim uygulamasının arayüzsüz hali için yapıldı.
# Rise Together
# Emirhan Said ERDEM

# İlk olarak enter_room fonksiyonundaki ip adresinizi güncelleyin ve kodu çalıştırın
# Kullanıcı adınızı ardından Doktor tarafının oluşturduğu odanın kodunu girin artık iletişime başlayabilirsiniz.


import threading
import pyaudio
import numpy as np
import mysql.connector
import socketio
from cryptography.fernet import Fernet
import base64
import os
import time
import keyboard
from src_text.metin_oku import *

sio = socketio.Client()


class istemci_page:
    def __init__(self) -> None:
        super().__init__()
        # ses iletiminde sesin özellikleri:
        self.FORMAT = pyaudio.paInt16
        self.CHUNK = 1024
        self.CHANNELS = 1
        self.RATE = 44100
        self.PITCH_SHIFT_FACTOR = 1.2
        self.stream = None
        self.output_stream = None

        self.Event = threading.Event()
        self.oda_kodu = ""
        self.set_output_stream()  # hoparlör bağlantısı en başta yapılıyor.
        self.kullanici_ad = input("kullanici adini giriniz:\n")
        

        self.enter_room()

    def enter_room(self,):  # flask ile kurulan odaya giriş yapılıyor. Ses ve metin alışverişi başlatılıyor
        try:
            room = input("Lütfen Girmek istediğiniz odanın Kodunu yazınız:")

            name = self.kullanici_ad

            self.receive_text()
            self.yazi_gonder_t()
            # self.start_communication()
            sio.on("data1", self.get_sound)

            @sio.event
            def connect():  # flaska adımız ve oda bilgisi gönderiliyor.
                sio.emit("baglan", {"name": name, "room": room})

            sio.connect("http://YOUR_IP_ADRESS:5000", auth={"name": name, "room": room})
            # sio.wait()
        except:
            print("Yanlış oda Kodu girmiş olabilirsiniz Lütfen tekrar yazınız.")

    def receive_text(self):
        @sio.on("message")  # flask projesindeki message olayına 'on' ile bağlanıyoruz. bu şekilde mesaj gönderildiğinde handle_message aktif olacak
        def handle_message(message):
            if "message" in message:
                text = message.get("message", "")  # Şifreli mesaj içeriğini al
                efekt = message.get("efekt", "")  # Efekti al
                key = message.get("key", "")  # Anahtarı al

                if text == "has entered the room":
                    pass
                else:
                    # Mesajı çöz

                    key = base64.urlsafe_b64decode(key.decode("utf-8"))  # Anahtarı çöz
                    decrypted_message = self.decrypt_message(text, key)

                    print(decrypted_message)

                    if efekt == 0:
                        read_man(decrypted_message)

                    elif efekt == 1:
                        read_text__woman_thread(decrypted_message)

                    elif efekt == 2:
                        read_children(decrypted_message)

                    elif efekt == 3:
                        read_old_woman(decrypted_message)

                    elif efekt == 4:
                        read_old_man(decrypted_message)

            else:
                print(message)
                pass

    def decrypt_message(
        self, encrypted_message, key
    ):  # gelen şifreli metni ve keyi alıyoruz.
        cipher_suite = Fernet(base64.urlsafe_b64encode(key).decode("utf-8"))
        decrypted_message = cipher_suite.decrypt(
            encrypted_message
        ).decode()  # şifreleri çözüp normal asıl metnimize ulaşıyoruz
        return decrypted_message

    def get_sound(self, data):
        try:
            if data:
                audio_data = data.get("audio_data", b"")
                self.output_stream.write(audio_data)
            elif not data:
                print("Data yok")

        except Exception as e:
            print("Ses alma hatası:", str(e))

    def send_audio(self):
        print("a2")
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
        )

        try:
            while True:
                data = stream.read(self.CHUNK)
                audio_data = np.frombuffer(data, dtype=np.int16)

                audio_data = audio_data.tobytes()
                # stream.write(audio_data)
                sio.emit("audio_data2", {"audio_data2": audio_data})  # Bytlara dönüştürülen ses verilerini 'audio_data' sözcüğü ile emitle emitle
        except Exception as e:
            print("hata", e)
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    def start_communication(self):
        threading.Thread(target=self.send_audio).start()

    def yazi_gonder(self):
        room = self.oda_kodu

        name = self.kullanici_ad
        while True:
            try:
                message = input("Göndereceğiniz Metin girin: ")

                # Anahtar oluştur
                key = self.generate_key()  # text için key oluştur

                encrypted_message = self.encrypt_message(message, key)  # Mesajı şifrele

                # flaskta ki message olayına şifreli mesajı- room-efekt ve keyi sözcük içinde emitle
                sio.emit(
                    "message_student",
                    {
                        "data": encrypted_message.decode(),
                        "room": room,
                        "name": name,
                        "key": key,
                    },
                )
            except KeyboardInterrupt:
                pass

    def yazi_gonder_t(self):
        t1 = threading.Thread(target=self.yazi_gonder)
        t1.start()

    def generate_key(self):
        return Fernet.generate_key()  # key oluştur

    def encrypt_message(self, message, key):  # keyi ve mesajı al
        cipher_suite = Fernet(key)  # şifreli paketi oluştur
        encrypted_message = cipher_suite.encrypt(message.encode())
        return encrypted_message  # şifrelenmiş mesajı oluştur ve return et

    def set_output_stream(self):  # hoaprlörü ayarlar
        if self.output_stream is None:
            p = pyaudio.PyAudio()
            try:
                self.output_stream = p.open(
                    output=True,
                    format=pyaudio.paInt16,
                    channels=self.CHANNELS,
                    rate=self.RATE,
                    frames_per_buffer=self.CHUNK,
                )

            except OSError as e:
                print("Hoparlör bağlantısı yapılamadı:", e)
                self.output_stream = None
        else:
            print("dolu")


if __name__ == "__main__":
    app = istemci_page()
