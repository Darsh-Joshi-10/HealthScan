import ollama

# Define the model and the question
desiredModel = 'phi3:mini'
questionToAsk = 'Write me a professional looking report about a patient named ABC, aged 62 and X-ray dignosis show signs of pneumonia, symptoms are coughing, high fever and difficulty in breathing. The report should contain information about pneumonia and should be strictly in English. The information provided about the patient should not be included in the report.'

# Send the question to the model
response = ollama.chat(model=desiredModel, messages=[
    {
        'role': 'user',
        'content': questionToAsk,
    },
])

# Extract the response content
OllamaResponse = response['message']['content']

# Print the response to the console
print(OllamaResponse)

# Save the response to a text file
with open("OutputOllama.txt", "w", encoding="utf-8") as text_file:
    text_file.write(OllamaResponse)