from flask import Flask, request, jsonify
import datetime
from groq import Groq

app = Flask(__name__)

# Set the API key as an environment variable
api_key = "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"

# Initialize the Groq client with the API key
client = Groq(api_key)

@app.route('/calculate-menstrual-phase', methods=['POST'])
def calculate_menstrual_phase():
    data = request.get_json()
    start_date = data['startDate']
    end_date = data['endDate']
    cycle_length = data['cycleLength']

    # Convert start and end dates to datetime objects
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    # Calculate menstrual phase
    today = datetime.datetime.today()
    cycle_day = (today - start_date).days + 1
    period_length = (end_date - start_date).days + 1

    if cycle_day <= 5:
        phase = 'menstruation'
    elif cycle_day <= 14:
        phase = 'follicular'
    elif cycle_day <= 21:
        phase = 'ovulation'
    else:
        phase = 'luteal'

    # Generate menstrual cycle information using Groq API
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": f"Provide detailed recommendations for the {phase} phase of the menstrual cycle. Break down into clear, separate sections: 1. Describe the hormonal changes happening in this phase, 2. List specific nutrition recommendations, 3. Outline the best exercise approaches."
            },
            {
                "role": "assistant",
                "content": ""
            }
        ],
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    # Get the generated menstrual cycle information
    menstrual_cycle_info = ""
    for chunk in completion:
        menstrual_cycle_info += chunk.choices[0].delta.content or ""

    # Parse Groq output
    sections = menstrual_cycle_info.split('1. ')
    hormone_info = sections[1].split('2. ')[0].strip()
    nutrition_recommendations = sections[1].split('2. ')[1].split('3. ')[0].strip()
    exercise_recommendations = sections[1].split('3. ')[1].strip()

    # Create output
    output = {
        'cycleDay': cycle_day,
        'phase': phase.capitalize(),
        'periodLength': period_length,
        'cycleLength': cycle_length,
        'hormoneInfo': hormone_info,
        'foodRecommendations': nutrition_recommendations,
        'exerciseRecommendations': exercise_recommendations
    }

    return jsonify(completion)

if __name__ == '__main__':
    app.run(debug=True)