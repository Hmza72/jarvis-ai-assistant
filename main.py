import speech_recognition as sr
import webbrowser
import pyttsx3
import os
from datetime import datetime, date
import time
import openai
from dotenv import load_dotenv

# Load API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

recognizer = sr.Recognizer()
engine = pyttsx3.init()
reminders = []  # list for reminders

# Speak function
def speak(text):
    print(f"Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()

# Greeting
def greet_user():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        speak("Good morning!")
    elif 12 <= hour < 18:
        speak("Good afternoon!")
    else:
        speak("Good evening!")

# Tell time
def tell_time():
    current_time = datetime.now().strftime("%I:%M %p")
    speak(f"The time is {current_time}")

# Tell date
def tell_date():
    today = date.today().strftime("%B %d, %Y")
    speak(f"Today's date is {today}")

# Open Notepad or Calculator
def open_app(app_name):
    if "notepad" in app_name:
        os.system("start notepad")
        speak("Opening Notepad")
    elif "calculator" in app_name:
        os.system("start calc")
        speak("Opening Calculator")
    else:
        speak("Can't open that app.")

# Take a note
def take_note():
    speak("What should I write?")
    try:
        audio = listen_command()
        note = recognizer.recognize_google(audio)
        with open("notes.txt", "a") as f:
            f.write(note + "\n")
        speak("Note saved.")
    except:
        speak("Sorry, I couldn't save the note.")

# Play music
def play_music():
    music_folder = "YOUR_MUSIC_FOLDER_PATH"  # Replace this
    try:
        songs = [file for file in os.listdir(music_folder) if file.endswith((".mp3", ".wav"))]
        if songs:
            os.startfile(os.path.join(music_folder, songs[0]))
            speak("Playing music")
        else:
            speak("No music found.")
    except Exception as e:
        speak(f"Can't play music. Error: {str(e)}")

# Shutdown
def shutdown_system():
    speak("Shutting down.")
    os.system("shutdown /s /t 1")

# Reminder
def set_reminder(reminder_text, delay_seconds):
    reminder_time = time.time() + delay_seconds
    reminders.append((reminder_time, reminder_text))
    speak(f"Reminder set for {delay_seconds} seconds from now.")

# Check reminders
def check_reminders():
    current_time = time.time()
    for reminder in reminders[:]:
        if reminder[0] <= current_time:
            speak(f"Reminder: {reminder[1]}")
            reminders.remove(reminder)

# ChatGPT response
def ask_chatgpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Can't get response. Error: {str(e)}"

# Listen
def listen_command():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    return audio

# Wake word listener - returns full command if wake word is present
def listen_for_wake_word(wake_word="jarvis"):
    with sr.Microphone() as source:
        print("Waiting for wake word...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio).lower()
        print(f"Heard: {text}")
        if wake_word in text:
            return text
        return None
    except sr.UnknownValueError:
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# Command processor
def process_command(command):
    command = command.lower()

    if "ask chatgpt" in command or "ask chat g p t" in command or "ask ai" in command:
        prompt = command.replace("jarvis", "").replace("ask chatgpt", "")
        prompt = prompt.replace("ask chat g p t", "").replace("ask ai", "").strip()
        if not prompt:
            speak("Please tell me what you want to ask ChatGPT.")
            return True
        speak("Let me check that for you.")
        response = ask_chatgpt(prompt)
        speak(response)
        return True

    if "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
        return True

    elif "open google" in command:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")
        return True

    elif "search for" in command:
        query = command.replace("search for", "").strip()
        speak(f"Searching {query}")
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return True

    elif "what's the time" in command or "tell me the time" in command:
        tell_time()
        return True

    elif "what's the date" in command or "tell me the date" in command:
        tell_date()
        return True

    elif "greet me" in command:
        greet_user()
        return True

    elif "open notepad" in command or "open calculator" in command:
        open_app(command)
        return True

    elif "take a note" in command or "make a note" in command:
        take_note()
        return True

    elif "play music" in command:
        play_music()
        return True

    elif "shutdown system" in command:
        shutdown_system()
        return False

    elif "set reminder" in command:
        import re
        match = re.search(r'set reminder in (\d+) seconds? to (.+)', command)
        if match:
            delay = int(match.group(1))
            reminder_text = match.group(2)
            set_reminder(reminder_text, delay)
        else:
            speak("Say reminder like 'set reminder in 10 seconds to check oven'.")
        return True

    elif "exit" in command or "quit" in command:
        speak("Bye!")
        return False

    else:
        speak("I don't understand that.")
        return True

# Main program
if __name__ == "__main__":
    greet_user()
    speak("I am Jarvis. Say 'Jarvis' followed by your command.")

    while True:
        check_reminders()
        full_command = listen_for_wake_word()
        if full_command:
            try:
                print("You said:", full_command)
                speak(f"You said: {full_command}")
                if not process_command(full_command):
                    break
            except sr.UnknownValueError:
                speak("I didn't catch that.")
            except sr.RequestError as e:
                speak(f"Speech error: {e}")
