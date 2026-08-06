import json

def extract_fields(text: str) -> dict:
    """
    Extracts fields from raw text using an AI model.

    Args:
    text (str): Raw text from a PDF form.

    Returns:
    dict: A dictionary with keys 'name', 'dob', 'id_number', 'address', 'income', 'category'.
          If a field cannot be found in the text, its value will be None.
    """
    # Call the AI model to extract fields
    ai_model_input = f"Extract fields from text: {text}"
    ai_model_output = json.loads(ai_model(ai_model_input))

    # Initialize the output dictionary with all None values
    output = {'name': None, 'dob': None, 'id_number': None, 'address': None, 'income': None, 'category': None}

    # Update the output dictionary with the extracted fields
    for key, value in ai_model_output.items():
        if key in output:
            output[key] = value

    return output