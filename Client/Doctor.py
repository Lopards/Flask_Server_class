#sesli iletişim uygulamasının arayüzsüz hali için yapıldı.
#Rise Together
#Emirhan Said ERDEM

# İlk Olarak İP adresinizi enter_room fonksiyonunda gerekli yere yazın
# Kodu başlatın İlk mesajı gönderdikten sonra biraz bekleyin. (2-3 saniye)
# Ses göndermek için Oda kurulduktan sonra 'm' tuşuna basın




import pyaudio
import numpy as np
import threading
import random
import socketio
from string import ascii_uppercase
from cryptography.fernet import Fernet
import keyboard
import base64

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

        self.efekt = None
        self.room_code = ""
        self.Event = threading.Event()
        self.set_output_stream()
        ######***************########
        print("Lütfen Göndereceğiniz metnin hangi efektle Okunacağını seçiniz.\n")
        
        self.enter_room()
        
        #self.create_connection()                                
       
        
        #self.start_communication() #ses göndermeyi başlat
        #time.sleep(3)
        #self.yazi_gonder_t()

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
        #sio.on("liste", self.hoparlor_liste_al) #hoparlör listesi için dinle
        
        self.create_room(name, room_code)
        sio.on("message_student",self.receive_text)
        sio.on("data2", self.get_sound) #gelen sesleri dinle

        self.yazi_gonder_t()
        self.start_communication()

        @sio.on("connect")
        def on_connect():
            sio.emit("baglan", {"name": name, "room": room_code})

        @sio.event
        def disconnect():
            print("Bağlantı kesildi.")
        
        

    def create_room(self, name, room_code): #Kullanıcının Oda kurmasını sağlar
        print("oda oluşturuldu")

        sio.connect("http://192.168.1.33:5000")  # IP adresinize göre güncelleyin.
        sio.emit("create_room", {"name": name, "room": room_code})



    def send_audio_e(self):
        print("ses aktarımı başladı")
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
        )

        try:
            while not self.Event.is_set():
                #while keyboard.is_pressed("m"):
                    data = stream.read(self.CHUNK)
                    audio_data = np.frombuffer(data, dtype=np.int16)


                    audio_data = audio_data.tobytes()

                    try:
                        sio.emit("audio_data", {"audio_data": audio_data})
                        audio_data = None
                    except Exception as e:
                        print("hata",e)

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
            if  data:
                audio_data = data.get("audio_data2", b"")
                self.stream.write(audio_data)
            elif not data:
                print("Data yok")
            
        except Exception as e:
            print("Ses alma hatası:", str(e))
    def set_output_stream(self):
       
        if self.stream is None:
            
            p = pyaudio.PyAudio()
            try:
                
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
        else:
            print("dolu")


    def yazi_gonder(self):
        room = self.room_code
        efekt = input("0: Erkek - 1: Kadın- 2: Çocuk - 3:Babanne - 4: Dede\n")
        name = "Doktor"
        while True:
            try:
                #message = self.server_erkek.metin_yeri.toPlainText()
                
                message = input("\nGöndereceğiniz Metin girin: ")
                
                # Anahtar oluştur
                key = self.generate_key()  # text için key oluştur

                encrypted_message = self.encrypt_message(message, key)  # Mesajı şifrele

                # flaskta ki message olayına şifreli mesajı- room-efekt ve keyi sözcük içinde emitle
                sio.emit("message_doktor",{
                        "data": encrypted_message.decode(),
                        "room": room,
                        "name": name,
                        "efekt": int(efekt),
                        "key": key,
                    },
                )
            except KeyboardInterrupt:
                pass

            #sio.wait()

            #sio.disconnect()

            #################******######################

    def yazi_gonder_t(self):
        
        
        t1 = threading.Thread(target=self.yazi_gonder)
        t1.start()

    def receive_text(self,message):
       
        if "message" in message:
                text = message.get("message", "")  # Şifreli mesaj içeriğini al
                key = message.get("key", "")  # Anahtarı al
                user = message.get("name","")
                if text == "has entered the room":
                    pass
                else:
                    # Mesajı çöz

                    key = base64.urlsafe_b64decode(key.decode("utf-8"))  # Anahtarı çöz
                    decrypted_message = self.decrypt_message(text, key)
                    print("\n",user,":", decrypted_message)

        else:
                print(message)
                pass


    def generate_key(self):
        return Fernet.generate_key()  # key oluştur

    def encrypt_message(self, message, key):  # keyi ve mesajı al
        cipher_suite = Fernet(key)  # şifreli paketi oluştur
        encrypted_message = cipher_suite.encrypt(
            message.encode()
        )  # şifrelenmiş mesajı oluştur ve return et
        return encrypted_message
    def decrypt_message(self, encrypted_message, key):  # gelen şifreli metni ve keyi alıyoruz.
        cipher_suite = Fernet(base64.urlsafe_b64encode(key).decode("utf-8"))
        decrypted_message = cipher_suite.decrypt(
            encrypted_message
        ).decode()  # şifreleri çözüp normal asıl metnimize ulaşıyoruz
        return decrypted_message

        
    
if __name__ == "__main__":
    chat_app = server_erkek_page()
    #chat_app.yazi_gonder_t()
