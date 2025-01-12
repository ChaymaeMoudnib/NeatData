    # Call OpenAI API to get a response
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # You can choose different engines like GPT-4 or others
            prompt=user_message,
            max_tokens=150,
            temperature=0.7  # Controls the randomness of the response
        )
        
        bot_message = response.choices[0].text.strip()  # Extract the reply from OpenAI's response
        
    except Exception as e:
        bot_message = "Sorry, I couldn't process your request. Please try again later."
    
    # Return the bot's reply as a JSON response
    return jsonify({"reply": bot_message})