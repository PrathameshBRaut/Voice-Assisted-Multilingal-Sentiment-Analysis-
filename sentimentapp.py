import streamlit as st
import speech_recognition as sr
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from googletrans import Translator

# Function to perform sentiment analysis
def analyze_sentiment(audio_text):
    analyser = SentimentIntensityAnalyzer()
    vader_scores = analyser.polarity_scores(audio_text)
    return vader_scores

# Function to translate text to English
def translate_to_english(text, source_language):
    translator = Translator()
    try:
        translation = translator.translate(text, src=source_language, dest='en')
        return translation.text
    except ValueError as e:
        detected_language = translator.detect(text).lang
        if detected_language != "en":
            translated_message = translator.translate(text, src=detected_language, dest='en')
            return translated_message.text
        else:
            return text

# Map Indian regional languages to their respective language codes for speech recognition
indian_languages = {
    "Hindi": "hi-IN",
    "Bengali": "bn-IN",
    "Telugu": "te-IN",
    "Tamil": "ta-IN",
    "Marathi": "mr-IN",
    "Gujarati": "gu-IN",
    "Kannada": "kn-IN",
    "Odia": "or-IN",
    "Punjabi": "pa-IN"
}

# Streamlit app
def main():
    st.title("Voice Sentiment Analysis in Any Language with Translation")

    # Ask the user to select the language they are speaking
    selected_language = st.selectbox("Select Your Language", ["English", "Spanish", "French", "German"] + list(indian_languages.keys()))
    
    # Create a button to record voice
    if st.button("Record Voice"):
        st.write("Recording...")
        
        recognizer = sr.Recognizer()
        
        with sr.Microphone() as source:
            noise_info = st.empty()
            noise_info.write("Clearing background noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            noise_info.empty()

            message_info = st.empty()
            message_info.write("Waiting for your message...")
            
            try:
                recorded_audio = recognizer.listen(source, timeout=10)  # Adjust the timeout as needed
                message_info.empty()
                st.write("Done recording..")

                if selected_language != "English":
                    selected_language_code = indian_languages.get(selected_language, selected_language.lower())
                else:
                    selected_language_code = selected_language.lower()

                audio_text = recognizer.recognize_google(recorded_audio, language=selected_language_code)  # Use the selected language
                
                st.subheader("Message Details")
                st.write("Your message:", audio_text)
                translated_message = translate_to_english(audio_text, selected_language_code)
                st.write("Translated Message:", translated_message)

                # Perform sentiment analysis on the translated message (or original if it's in English)
                sentiment_scores = analyze_sentiment(translated_message)

                # Display sentiment scores using progress bars (scaled to [0.0, 1.0])
                st.subheader("Sentiment Analysis Results")
                st.write("Negative:")
                st.progress(sentiment_scores['neg'])
                st.write("Neutral:")
                st.progress(sentiment_scores['neu'])
                st.write("Positive:")
                st.progress(sentiment_scores['pos'])
                st.write("Compound:")
                st.progress((sentiment_scores['compound'] + 1) / 2)  # Scale to [0.0, 1.0]
                
            except sr.WaitTimeoutError:
                message_info.empty()
                st.write("Recording timed out. Please try again.")

if __name__ == "__main__":
    main()