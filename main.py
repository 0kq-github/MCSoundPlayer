import glob
import PySimpleGUI as sg
import json
import os
import platform
import shutil
import csv
import pygame

class GuiRenderer:
  '''
  ウィンドウ描画
  '''
  def __init__(self):
    pygame.init()
    #soundlist.txtに格納された音声一覧を読み込み
    with open("soundlist.txt","r") as f:
      self.sounddict = {}
      self.keylist = []
      reader = csv.reader(f)
      for line in reader:
        self.sounddict[line[0]] = line[1]
        self.keylist.append(line[0])
    
  def guimain(self):
    '''
    ウィンドウ描画: PySimpleGUI
    ogg再生: pygame
    '''
    self.layout = [[sg.InputText(enable_events=True,key="input")],[sg.Listbox(self.keylist,size=(50,10),key="sounds"),sg.Button("再生")]]
    self.window = sg.Window("MCSoundPlayer",self.layout)
    while True:
      event,values = self.window.read()
      #ウィンドウを閉じたら終了
      if event == sg.WIN_CLOSED:
        break
      #再生ボタンが押されたら再生
      if event == "再生" and values["sounds"]:
        path = self.sounddict[values["sounds"][0]]
        ogg = pygame.mixer.music
        ogg.load(path)
        ogg.play()
        continue
      result = []
      #文字が入力されたら検索
      for i in self.keylist:
        if values["input"] in i:
          result.append(i)
      self.window["sounds"].update(result)


class SoundToText:
  '''
  assets/indexes/1.16.jsonから音声の情報を抽出

  '''
  def __init__(self):
    pass
  def get(self):
    '''
    取得した音声ファイルを整形してsoundlist.txtに書き込む
    '''
    oggs = glob.glob("./sounds/*/*/*.ogg")
    if os.path.exists("./soundlist.txt"):
      os.remove("./soundlist.txt")
    for i in oggs:
      path = i
      i = i.replace("./sounds\\","")
      i = i.replace("\\",".")
      i = i.replace(".ogg","")
      with open("./soundlist.txt",mode="a") as f:
        line = f"{i},{path}\n"
        f.write(line)

class SoundExtractor:
  '''
  音声ファイルを抽出
  '''
  def __init__(self):
    pass
  def main(self):
    ''' 
        Copies audio files from indescript hashed folders to named sorted folders.
        You may need to change output path.
    '''

    # This section should work on any system as well
    if platform.system() == "Windows":
        if os.path.exists(r"./assets"):
          MC_ASSETS = os.path.expandvars(r"./assets")
        else:
          MC_ASSETS = os.path.expandvars(r"%APPDATA%/.minecraft/assets")
    else:
        MC_ASSETS = os.path.expanduser(r"~/.minecraft/assets")

    # Change this if you want to put the sound files somewhere else
    OUTPUT_PATH = os.path.normpath(os.path.expandvars(os.path.expanduser(f"./")))

    # These are unlikely to change
    MC_OBJECT_INDEX = f"{MC_ASSETS}/indexes/1.16.json"
    MC_OBJECTS_PATH = f"{MC_ASSETS}/objects"
    MC_SOUNDS = r"minecraft/sounds/"

    if not os.path.exists(MC_OBJECT_INDEX):
      sg.Popup("エラー: 1.16.jsonが見つかりませんでした。\nバージョン1.16.xを起動してから再度試してください。",title="MCSoundPlayer")
      exit()
    with open(MC_OBJECT_INDEX, "r") as read_file:
        # Parse the JSON file into a dictionary
        data = json.load(read_file)

        # Find each line with MC_SOUNDS prefix, remove the prefix and keep the rest of the path and the hash
        sounds = {k[len(MC_SOUNDS):] : v["hash"] for (k, v) in data["objects"].items() if k.startswith(MC_SOUNDS)}

        print("File extraction :")
        count = 0
        layout = [[sg.Text("初期化中...")],[sg.ProgressBar(len(sounds.items()),orientation="h",key="progress",size=(40,20))]]
        window = sg.Window("MCSoundPlayer",layout)

        for fpath, fhash in sounds.items():
            window.read(timeout=0)
            count += 1
            # Ensure the paths are good to go for Windows with properly escaped backslashes in the string
            src_fpath = os.path.normpath(f"{MC_OBJECTS_PATH}/{fhash[:2]}/{fhash}")
            dest_fpath = os.path.normpath(f"{OUTPUT_PATH}/sounds/{fpath}")

            # Print current extracted file
            print(fpath)

            # Make any directories needed to put the output file into as Python expects
            os.makedirs(os.path.dirname(dest_fpath), exist_ok=True)

            # Copy the file
            shutil.copyfile(src_fpath, dest_fpath)
            window["progress"].update(count)
        window.close()
    


if __name__ == "__main__":
  if not os.path.exists("./sounds"):
    ext = SoundExtractor()
    stt = SoundToText()
    ext.main()
    stt.get()
  root = GuiRenderer()
  root.guimain()