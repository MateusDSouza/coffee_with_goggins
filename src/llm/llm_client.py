from ollama import Client


def get_ai_client(provider="ollama"):
    """
    Returns the initialized client and the model name.
    """
    if provider == "ollama":
        client = Client(host="http://localhost:11434")
        model_name = "dolphin-llama3"
        return client, model_name
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def generate_message(client, model_name, contact_name):
    """
    Generates the motivational message using the HoLLyM persona.
    """
    system_instruction = (
        "You are HoLLyM, a passionate and poetic Catholic evangelizer. "
        "Your mission is to spread the Gospel and remind people of Jesus' infinite love. "
        "You always invite people to repent, go to confession, and receive the Eucharist. "
        "You encourage them to turn away from a life of sin and stand strong with faith. "
        "Keep your tone warm, zealous, and inspiring."
    )

    user_prompt = (
        f"Present yourself. Write a short 'good morning' WhatsApp message for my friend {contact_name}. "
        "Add a versicle of the Holy Bible. Include an emoji. Keep it under 4 sentences."
    )

    response = client.chat(
        model=model_name,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response["message"]["content"]
