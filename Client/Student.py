#sesli iletişim uygulamasının arayüzsüz hali için yapıldı.
#Rise Together

#Emirhan Said ERDEM

import threading
import pyaudio
import numpy as np
import mysql.connector
import socketio
from cryptography.fernet import Fernet
import base64
import os
import time
sio = socketio.Client()


class istemci_page():
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
        self.kullanici_ad = input("kullanici adini giriniz:\n")
        self.oda_kodu_ID()

        #self.start_communication()
    def oda_kodu_ID(self):

        """
        MySQL veritabanına bağlantı oluşturur.
        """
        ID = self.kullanici_ad
        print(ID)
        try:
                connection = mysql.connector.connect(
                host="rise.czfoe4l74xhi.eu-central-1.rds.amazonaws.com",
                user="admin",
                password="Osmaniye12!",
                database="rise_data")
                cursor = connection.cursor()
                query = "SELECT oda_kodu FROM veriler WHERE kullanici_ad = %s"
                cursor.execute(query, (ID,))
                kullanici_verileri = cursor.fetchone()

                self.oda_kodu = kullanici_verileri[0]
                print(self.oda_kodu)

                connection.commit()
                connection.close()

                self.enter_room()

        except Exception as e:
            print("mysql baglanti hata",e)
        

    def enter_room(self):  # flask ile kurulan odaya giriş yapılıyor. Ses ve metin alışverişi başlatılıyor
        room = self.oda_kodu
        print(self.oda_kodu)
        name = "öğrenci"

        self.receive_text()

        @sio.event
        def connect():
            print("Connected to server")
            sio.emit('baglan', {"name": name, "room": room})

        # self.send_output_device_list()
        #sio.on("index", self.select_output_device)

        sio.on("data1", self.get_sound)

        sio.connect("http://192.168.1.45:5000", auth={"name": name, "room": room})
        sio.wait()



    def receive_text(self):

        @sio.on(
            "message"
        )  # flask projesindeki message olayına 'on' ile bağlanıyoruz. bu şekilde mesaj gönderildiğinde handle_message aktif olacak
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
                    #self.istemci.metin_yeri.insertPlainText(f"Mesaj: {decrypted_message}\n")  # Çözülmüş mesajı pyqt5 alanına ekle ve efekte göre okut
                    if efekt == 0:
                        #read_man(decrypted_message)
                        print(decrypted_message)
                    elif efekt == 1:
                        #read_text__woman_thread(decrypted_message)
                        print(decrypted_message)
                    elif efekt == 2:
                        #read_children(decrypted_message)
                        print(decrypted_message)
                    elif efekt == 3:
                        #read_old_woman(decrypted_message)
                        print(decrypted_message)
                    elif efekt == 4:
                        #read_old_man(decrypted_message)
                        print(decrypted_message)
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
        if not self.Event.is_set() and self.stream is None:

            
            try:
                self.Event.set()
                print("set yapıldı.")
                time.sleep(0.1)
                p = pyaudio.PyAudio()
                self.stream = p.open(
                    output=True,
                    format=pyaudio.paInt16,
                    channels=self.CHANNELS,
                    rate=self.RATE,
                    frames_per_buffer=self.CHUNK,

                )
            except OSError as e:
                print("Hoparlör bağlantısı yapılamadı:", e)
                self.stream = None
                ##### ********** ######
            




        try:

            if data:
                audio_data = data.get("audio_data", b"")
                # print(audio_data)
                #if self.is_running_recv:
                    # self.play_button_clicked()
                #↓self.play_server_output(audio_data)
                self.stream.write(audio_data)
            elif not data:
                print("dadta yok")

        except Exception as e:
            print("Ses alma hatası:", str(e))


    def send_audio(self):
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
                data = stream.read(self.CHUNK)
                audio_data = np.frombuffer(data, dtype=np.int16)

                audio_data = audio_data.tobytes()

                sio.emit("audio_data2", {
                    "audio_data2": audio_data})  # Bytlara dönüştürülen ses verilerini 'audio_data' sözcüğü ile emitle emitle
        except Exception as e:
            print("hata", e)
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    def start_communication(self):
        threading.Thread(target=self.send_audio).start()

    def play_button_clicked(self):

        # ☺while True:
        try:
             
             self.set_output_stream()

                # self.stop_event.clear()
        except Exception as e:
            print("hoparlör seçiminde hata:", e)
        # self.play_server_output(data)

    def set_output_stream(self):
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
            ##### ********** ######

    def play_server_output(self, data):
        
        if self.output_stream is not None:
            try:
                self.output_stream.write(data)
                print(data)
            except OSError as e:
                print("Hoparlör bağlantısı koparıldı:", e)
                self.output_stream.close()
                self.output_stream.stop_stream()
                self.output_stream = None

        else:
            print("Hoparlör seçiniz...")

if __name__ == "__main__":
        app = istemci_page()
        while True:
            pass  # Programın kapanmaması için sonsuz döngü
