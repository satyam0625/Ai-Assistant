import speech_recognition as sr
import pyttsx3
import datetime
import random
import requests
import webbrowser
import os
import threading
import time
from groq import Groq
import wikipedia

# Initialize text-to-speech engine with error handling
try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    voice_set = False
    for voice in voices:
        if "DAVID" in voice.id.upper():
            engine.setProperty('voice', voice.id)
            voice_set = True
            break
    if not voice_set:
        engine.setProperty('voice', voices[0].id)  # Fallback to first available voice
    engine.setProperty('rate', 160)
    print("Text-to-speech engine initialized successfully.")
except Exception as e:
    print(f"Error initializing text-to-speech engine: {e}. Voice output will be disabled.")

# Groq setup
client = Groq(api_key="") # Enter your api key 

# Weather API setup
WEATHER_API_KEY = "442f210f584740d1a3b75058250903"
WEATHER_BASE_URL = "http://api.weatherapi.com/v1/current.json"

# News API setup
NEWS_API_KEY = "your_newsapi_key_here"  # Replace with your NewsAPI key
NEWS_BASE_URL = "https://newsapi.org/v2/top-headlines"

# Dictionary of websites
websites = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "twitter": "https://www.twitter.com",
    "linkedin": "https://www.linkedin.com",
    "wikipedia": "https://www.wikipedia.org",
    "amazon": "https://www.amazon.com",
    "netflix": "https://www.netflix.com",
    "github": "https://www.github.com",
    "reddit": "https://www.reddit.com",
    "stackoverflow": "https://www.stackoverflow.com",
    "spotify": "https://www.spotify.com",
    "twitch": "https://www.twitch.tv",
    "discord": "https://www.discord.com"
}

# To-do list storage
todo_list = []

# Dictionary to store information about your friends
friends = {
    "alice": {
        "description": "Alice is a cheerful person who loves painting and hiking. We've been friends since college.",
        "interests": ["art", "nature"],
        "last_met": "last month"
    },
    "bob": {
        "description": "Bob is a tech enthusiast who enjoys coding and gaming. We met at a hackathon.",
        "interests": ["technology", "gaming"],
        "last_met": "two weeks ago"
    }
}

# Global variables
stop_speaking = False
listening = False
voice_enabled = True
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Speak function with error handling
def speak(text):
    global stop_speaking, voice_enabled
    if not voice_enabled:
        print(f"Voice output disabled. Response: {text}")
        return
    stop_speaking = False
    print(f"Jarvis: {text}")
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in speech output: {e}. Switching to text-only mode.")
        voice_enabled = False

# Listen for stop command
def listen_for_stop():
    global stop_speaking
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        while not stop_speaking:
            try:
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=2)
                command = recognizer.recognize_google(audio).lower()
                if "stop" in command:
                    stop_speaking = True
                    engine.stop()
                    print("Speech stopped by voice command.")
                    break
            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print(f"Connection issue with speech recognition: {e}. Check internet or try again.")
                break
            except Exception as e:
                print(f"Stop listener error: {e}")
                break
            time.sleep(0.1)

# Speak with stop functionality
def speak_with_stop(text):
    global stop_speaking
    if not voice_enabled:
        print(f"Voice output disabled. Response: {text}")
        return
    stop_speaking = False
    stop_thread = threading.Thread(target=listen_for_stop, daemon=True)
    stop_thread.start()
    speak(text)
    stop_thread.join(timeout=1)

# Stop speaking immediately
def stop_speaking_now():
    global stop_speaking
    stop_speaking = True
    if voice_enabled:
        engine.stop()
    print("Speech stopped manually.")

# Listen function with debug logging
def listen():
    global voice_enabled
    print("Listening...")
    with microphone as source:
        try:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            print("Could not understand audio. Ensure microphone is working.")
            return ""
        except sr.RequestError as e:
            print(f"Speech recognition service error: {e}. Switching to text input mode.")
            voice_enabled = False
            return ""
        except Exception as e:
            print(f"Listen error: {e}")
            return ""

# Process typed command
def process_typed_command():
    command = input("Enter command: ").lower()
    if command:
        print(f"You typed: {command}")
        response = process_command(command)
        speak_with_stop(response)

# Utility functions
def get_weather(command="weather"):
    city = "Delhi"
    if "in" in command:
        city = command.split("in")[1].strip()
    params = {"key": WEATHER_API_KEY, "q": city}
    response = requests.get(WEATHER_BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return f"The weather in {city} is {data['current']['temp_c']} degrees Celsius with {data['current']['condition']['text']}, boss."
    return f"Weather data for {city} is unavailable, boss."

def get_news():
    params = {"country": "in", "apiKey": NEWS_API_KEY}
    response = requests.get(NEWS_BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        headlines = [article["title"] for article in data["articles"][:3]]
        return "Here are the latest headlines, boss: " + ". ".join(headlines) + "."
    return "News data unavailable, boss."

def set_timer(command):
    try:
        minutes = int(command.split("for")[1].split("minute")[0].strip())
        seconds = minutes * 60
        threading.Thread(target=lambda: [time.sleep(seconds), speak("Time’s up, boss!")]).start()
        return f"Timer set for {minutes} minutes, boss."
    except:
        return "Please say something like ‘set a timer for 5 minutes’, boss."

def get_wikipedia(command):
    try:
        query = command.replace("tell me about", "").strip()
        summary = wikipedia.summary(query, sentences=2)
        return f"Here’s what I found about {query}, boss: {summary}"
    except:
        return "I couldn’t find that on Wikipedia, boss."

def tell_about_friend(command):
    for friend in friends:
        if friend in command:
            friend_info = friends[friend]
            return f"{friend_info['description']} They are interested in {', '.join(friend_info['interests'])}, and I last met them {friend_info['last_met']}, boss."
    return "I don’t have information about that friend, boss. Please add them first or check the name."

def system_command(command):
    if "shutdown" in command:
        os.system("shutdown /s /t 1")
        return "Shutting down your computer, boss."
    elif "restart" in command:
        os.system("shutdown /r /t 1")
        return "Restarting your computer, boss."
    return "I didn’t understand that system command, boss."

def manage_todo(command):
    if "add" in command:
        task = command.split("add")[1].strip()
        todo_list.append(task)
        return f"Added {task} to your to-do list, boss."
    elif "show" in command or "list" in command:
        if todo_list:
            return "Your to-do list, boss: " + ", ".join(todo_list) + "."
        return "Your to-do list is empty, boss."
    return "Say ‘add [task]’ or ‘show my to-do list’, boss."

def get_fun_fact():
    facts = [
        "Octopuses have three hearts, boss.",
        "India has more languages than any other country, boss.",
        "Honey never spoils, boss."
    ]
    return random.choice(facts)

def get_groq_response(command):
    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are Jarvis, a highly professional and sophisticated AI assistant. Address the user as 'boss' and respond with formality, clarity, and courtesy, providing accurate and helpful information."},
                {"role": "user", "content": command}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Apologies, boss, I seem to have encountered an issue: {str(e)}"

# Process commands
def process_command(command):
    if "hello jarvis" in command:
        today = datetime.datetime.now().strftime("%B %d, %Y")
        return f"Good day, boss. It is {today}."
    elif "time" in command:
        return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}, boss."
    elif "joke" in command:
        return random.choice(["Why don’t skeletons fight? They lack the guts, boss.", "I told my wife her eyebrows were too high. She looked surprised, boss."])
    elif "weather" in command:
        return get_weather(command)
    elif "news" in command:
        return get_news()
    elif "set a timer" in command or "timer" in command:
        return set_timer(command)
    elif "tell me about my friend" in command:
        return tell_about_friend(command)
    elif "tell me about" in command:
        return get_wikipedia(command)
    elif "shutdown" in command or "restart" in command:
        return system_command(command)
    elif "to-do" in command or "todo" in command:
        return manage_todo(command)
    elif "fun fact" in command:
        return get_fun_fact()
    elif "calculate" in command:
        try:
            parts = command.split()
            num1, op, num2 = float(parts[1]), parts[2], float(parts[3])
            if op == "plus": return f"The result is {num1 + num2}, boss."
            elif op == "minus": return f"The result is {num1 - num2}, boss."
            elif op == "times": return f"The result is {num1 * num2}, boss."
            elif op == "divided": return f"The result is {num1 / num2}, boss."
        except:
            return "Please say something like ‘calculate 5 plus 3’, boss."
    elif "open" in command:
        for site in websites:
            if site in command:
                webbrowser.open(websites[site])
                return f"Opening {site}, boss."
        return "I don’t recognize that website, boss."
    elif "play music" in command:
        music_path = "C:/path/to/your/music.mp3"
        if os.path.exists(music_path):
            os.startfile(music_path)
            return "Playing music, boss."
        return "Music file not found, boss."
    elif "play video" in command:
        video_path = "C:/path/to/your/video.mp4"
        if os.path.exists(video_path):
            os.startfile(video_path)
            return "Playing video, boss."
        return "Video file not found, boss."
    elif "play" in command and "on youtube" in command:
        query = command.replace("play", "").replace("on youtube", "").strip()
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        return f"Searching for {query} on YouTube, boss."
    elif "goodbye" in command:
        return "Farewell, boss. Until next time."
    else:
        return get_groq_response(command)

# Start listening function for continuous listening
def start_listening():
    global listening
    if not listening:
        listening = True
        listen_thread = threading.Thread(target=jarvis_loop, daemon=True)
        listen_thread.start()
        print("Listening started...")

# Main JARVIS loop for continuous listening
def jarvis_loop():
    global listening
    speak_with_stop("Hello boss, Jarvis here. How may I serve you today?")
    while listening:
        command = listen()
        if command:
            response = process_command(command)
            speak_with_stop(response)
            if "goodbye" in command:
                listening = False
                print("Jarvis has stopped. Goodbye.")
                break
    listening = False

# Main execution
if __name__ == "__main__":
    print("JARVIS Assistant - Console Mode")
    print("1. Start continuous listening")
    print("2. Enter a command")
    print("3. Stop speaking")
    print("4. Exit")
    while True:
        choice = input("Choose an option (1-4): ")
        if choice == "1":
            start_listening()
        elif choice == "2":
            process_typed_command()
        elif choice == "3":
            stop_speaking_now()
        elif choice == "4":
            print("Exiting JARVIS...")
            break
        else:
            print("Invalid option. Choose 1, 2, 3, or 4.")
