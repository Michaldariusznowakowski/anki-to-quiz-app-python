# This script uses anki database to create quiz.
![image](https://github.com/Michaldariusznowakowski/ankiTest/blob/main/other_files/test.png?raw=true)
# Features
1. Export decks to docx file  
2. Start a test with a deck  
2.1. Answers are shuffled.  
2.2. Score is calculated.  
2.3. Wrong answered questions are showed in the end.  

# How to use
Remember to close anki before using this script!
## Create a deck using this model:
https://github.com/Michaldariusznowakowski/ankiTest/raw/main/other_files/Model.apkg
## How model works:
### 1. Front side:
![image](https://github.com/Michaldariusznowakowski/ankiTest/blob/main/other_files/card.png?raw=true)
### 2. Back side:
![image](https://github.com/Michaldariusznowakowski/ankiTest/blob/main/other_files/card_correct.png?raw=true)
## 3. Fields:
![image](https://github.com/Michaldariusznowakowski/ankiTest/blob/main/other_files/card_edit.png?raw=true)
3.1. You can add images to question. Don't try to add images to answer. It will not work.  
3.2. You can leave some answer fields empty. It will not be showed in the test.  
3.3. You need to add in last field correct answers, in format as ABCD... (without spaces, commas, etc.) example: ABCD or ABD or A  
3.4. This model works in android app!

# How to install
## 1. Install python 3.10
## 2. Multiple options:
### 2.1. Use pip to install:
```
pip install -e git+https://github.com/Michaldariusznowakowski/ankiTest#egg=AnkiTest --user
py -m StartAnkiTest
or 
StartAnkiTest.exe
if this did not works, you need to add Python/Scripts to path
Or just manualy start it C:\Users\XXXX\AppData\Roaming\Python\PythonXXX\Scripts\StartAnkiTest.exe
To remove: pip uninstall AnkiTest
```
After install you will see in console path to script. You can use it to run script.
### 2.2. Download zip file from github and run commands from console:
```
py -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
py start\core.py
```
### 2.3. Download ready to use exe file from github releases and run it.
You can find it on the right side of the page.


