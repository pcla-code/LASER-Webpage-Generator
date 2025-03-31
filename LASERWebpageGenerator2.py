# notes: when a sample of the data arrives check for UTC-11 UTF-8 characters, br will not fire for generation of hints
import os
import pandas as pd
import random
import string

# Function to generate random string
def generate_random_string(length=4):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

'''
# Function to create the HTML content for each question
def create_html_content(curriculum, problem_set, question, answers, hints, next_page, question_number):
    # Convert answers to strings and ensure they are handled correctly
    answers = [str(answer) for answer in answers]

    hint_script = """
    <script>
        var hints = {hints};
        var hintIndex = 0;
        function showHint() {{
            if (hintIndex < hints.length) {{
                document.getElementById("hintDisplay").innerHTML = hints[hintIndex];
                hintIndex++;
            }} else {{
                document.getElementById("hintDisplay").innerHTML = "No more hints to show";
            }}
        }}
    </script>
    """.format(hints=hints)

    # Updated HTML with CSS styling for the new UI
    html_content = f"""
    <html>
    <head>
        <title>{curriculum} - {problem_set} - {question}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }}
            .container {{
                background: rgba(255, 255, 255, 0.8);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                padding: 40px;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
                text-align: center;
                max-width: 600px;
                width: 100%;
                margin: 20px;
            }}
            .header {{
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            h1 {{
                font-size: 22px;
                font-weight: normal;
                margin-bottom: 20px;
            }}
            .input-group {{
                display: flex;
                justify-content: center;
                align-items: center;
                margin-bottom: 20px;
            }}
            #answer {{
                border: none;
                border-bottom: 1px solid #000;
                padding: 10px;
                font-size: 18px;
                outline: none;
                width: 70%;
            }}
            #submit {{
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 8px 12px;
                cursor: pointer;
                font-size: 16px;
                border-radius: 5px;
                margin-left: 10px;
                font-weight: 300;
            }}
            #submit:disabled {{
                background-color: #ccc;
            }}
            #hintButton {{
                margin-top: 20px;
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 8px 12px;
                cursor: pointer;
                font-size: 16px;
                border-radius: 5px;
                margin-bottom: 20px;
                font-weight: 300;
            }}
            #nextButton {{
                display: none; /* Hidden initially */
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 8px 12px;
                cursor: pointer;
                font-size: 16px;
                border-radius: 5px;
                margin-top: 20px;
                font-weight: 300;
                text-align: center;
                text-decoration: none;
            }}
            #feedback {{
                margin-top: 20px;
                font-size: 18px;
                font-weight: bold;
                min-height: 30px;
            }}
            .correct {{
                color: green;
            }}
            .incorrect {{
                color: red;
            }}
            #hintDisplay {{
                margin-top: 10px;
                font-style: italic;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">{curriculum} - {problem_set} - Q{question_number}</div>
            <h1>{question}</h1>
            <div class="input-group">
                <input type="text" id="answer" name="answer" placeholder="Your answer">
                <input type="submit" id="submit" value="Submit" onclick="return checkAnswer()">
            </div>
            <div id="feedback"></div>

            <div id="hintDisplay"></div><br>

            <button id="hintButton" onclick="showHint()">Show Hint</button>

            <a id="nextButton" href="{next_page}">Next</a>
        </div>

    {hint_script}
    <script>
        // Trigger submit on Enter key
        document.getElementById('answer').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                e.preventDefault();
                document.getElementById('submit').click();
            }}
        }});

        function checkAnswer() {{
            var answer = document.getElementById('answer').value.trim();
            var correctAnswers = {answers}; // Corrected to ensure all answers are strings
            if (correctAnswers.map(a => a.toLowerCase()).includes(answer.toLowerCase())) {{
                document.getElementById('feedback').innerHTML = "Correct!";
                document.getElementById('feedback').className = "feedback correct";
                document.getElementById('answer').disabled = true;
                document.getElementById('submit').disabled = true;
                document.getElementById('hintButton').style.display = "none";
                document.getElementById('hintDisplay').style.display = "none";
                document.getElementById('nextButton').style.display = "inline-block"; // Show next button
            }} else {{
                document.getElementById('feedback').innerHTML = "Incorrect. Try again.";
                document.getElementById('feedback').className = "feedback incorrect";
                return false; // Prevent form submission to allow retries
            }}
            return false; // Prevent form submission
        }}
    </script>
    </body>
    </html>
    """
    return html_content
'''

# Function to create the HTML content for each question
def create_html_content(curriculum, problem_set, question, answers, hints, next_page, question_number):
    # Convert answers to strings and ensure they are handled correctly
    answers = [str(answer) for answer in answers]
    
    # Replace newlines in the question with <br> tags for HTML formatting
    formatted_question = question.replace("\n", "<br>")

    hint_script = """
    <script>
        var hints = {hints};
        var hintIndex = 0;
        function showHint() {{
            if (hintIndex < hints.length) {{
                document.getElementById("hintDisplay").innerHTML = hints[hintIndex];
                hintIndex++;
            }} else {{
                document.getElementById("hintDisplay").innerHTML = "No more hints to show";
            }}
        }}
    </script>
    """.format(hints=hints)

    # Updated HTML with CSS styling for the new UI
    html_content = f"""
    <html>
    <head>
        <title>{curriculum} - {problem_set} - Q{question_number}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }}
            .container {{
                background: rgba(255, 255, 255, 0.8);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                padding: 40px;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
                text-align: left;
                max-width: 700px;
                width: 100%;
                margin: 20px;
            }}
            .header {{
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            h1 {{
                font-size: 17px;
                font-weight: 200;
                margin-bottom: 20px;
                white-space: pre-line; /* Ensure line breaks are respected */
            }}
            .input-group {{
                display: flex;
                justify-content: center;
                align-items: center;
                margin-bottom: 20px;
            }}
            #answer {{
                border: none;
                border-bottom: 1px solid #000;
                padding: 10px;
                font-size: 18px;
                outline: none;
                width: 70%;
            }}
            #submit {{
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 8px 12px;
                cursor: pointer;
                font-size: 16px;
                border-radius: 5px;
                margin-left: 10px;
                font-weight: 300;
            }}
            #submit:disabled {{
                background-color: #ccc;
            }}
            #hintButton {{
                margin-top: 20px;
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 8px 12px;
                cursor: pointer;
                font-size: 16px;
                border-radius: 5px;
                margin-bottom: 20px;
                font-weight: 300;               
            }}
            #nextButton {{
                display: none; /* Hidden initially */
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 8px 12px;
                cursor: pointer;
                font-size: 16px;
                border-radius: 5px;
                margin-top: 20px;
                font-weight: 300;
                text-align: center;
                text-decoration: none;
            }}
            #feedback {{
                margin-top: 20px;
                font-size: 18px;
                font-weight: bold;
                min-height: 30px;
                text-align: center;
            }}
            .correct {{
                color: green;
            }}
            .incorrect {{
                color: red;
            }}
            #hintDisplay {{
                margin-top: 10px;
                font-style: italic;
                text-align: center;
            }}
            .button-center {{
                display: flex;
                justify-content: center; /* Center-align the hint button */
            }}            
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">{curriculum} - {problem_set} - Q{question_number}</div>
            <h1>{formatted_question}</h1> <!-- Using formatted question with line breaks -->
            <div class="input-group">
                <input type="text" id="answer" name="answer" placeholder="Your answer">
                <input type="submit" id="submit" value="Submit" onclick="return checkAnswer()">
            </div>
            <div id="feedback"></div>

            <div id="hintDisplay"></div><br>

            <div class="button-center">
                <button id="hintButton" onclick="showHint()">Show Hint</button>
            </div>
            <div class="button-center">
                <a id="nextButton" href="{next_page}">Next</a>
            </div>
        </div>

    {hint_script}
    <script>
        // Trigger submit on Enter key
        document.getElementById('answer').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                e.preventDefault();
                document.getElementById('submit').click();
            }}
        }});

        function checkAnswer() {{
            var answer = document.getElementById('answer').value.trim();
            var correctAnswers = {answers}; // Corrected to ensure all answers are strings
            if (correctAnswers.map(a => a.toLowerCase()).includes(answer.toLowerCase())) {{
                document.getElementById('feedback').innerHTML = "Correct!";
                document.getElementById('feedback').className = "feedback correct";
                document.getElementById('answer').disabled = true;
                document.getElementById('submit').disabled = true;
                document.getElementById('hintButton').style.display = "none";
                document.getElementById('hintDisplay').style.display = "none";
                document.getElementById('nextButton').style.display = "inline-block"; // Show next button
            }} else {{
                document.getElementById('feedback').innerHTML = "Incorrect. Try again.";
                document.getElementById('feedback').className = "feedback incorrect";
                return false; // Prevent form submission to allow retries
            }}
            return false; // Prevent form submission
        }}
    </script>
    </body>
    </html>
    """
    return html_content


# Function to create the final "Z-END" page with a unique code
def create_end_page(curriculum, problem_set):
    unique_code = generate_random_string(7)
    curriculum_code = "C" + curriculum[:3].upper()
    problem_set_code = "PS" + problem_set[:3].upper()

    html_content = f"""
    <html>
    <head>
        <title>{curriculum_code} - {problem_set_code} - Z-END</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: white;
            }}
            .container {{
                background: rgba(255, 255, 255, 0.8);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                padding: 40px;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
                text-align: center;
                max-width: 600px;
                width: 100%;
            }}
            h1 {{
                font-size: 28px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Unique Code: {unique_code}</h1>
        </div>
    </body>
    </html>
    """
    return html_content

# Function to create the filename based on the updated structure
def generate_filename(curriculum, problem_set, question_number):
    curriculum_code = "C" + curriculum[:3].upper()
    problem_set_code = "PS" + problem_set[:3].upper()
    question_code = "Q" + str(question_number)
    random_str = generate_random_string(4)
    filename = f"{curriculum_code}-{problem_set_code}-{problem_set_code}{question_code}-{random_str}.html"
    return filename

# Function to create the HTML files
def generate_webpages_from_csv(csv_file):
    # Check if output folder exists; create if not
    output_folder = "LASER-generated-webpages"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Read CSV data
    df = pd.read_csv(csv_file)

    current_curriculum = None
    current_problem_set = None
    current_question = None
    
    # Track questions for each problem set
    questions_per_problem_set = {}

    # Pre-generate filenames with random strings
    filenames = {}
    end_page_filenames = {}

    for index, row in df.iterrows():
        curriculum = row['Curriculum']
        problem_set = row['Problem Set']
        question = row['Question']

        if pd.notna(curriculum):
            current_curriculum = curriculum
        if pd.notna(problem_set):
            current_problem_set = problem_set
        
        # If question changes, we store them for later processing
        if pd.notna(question):
            current_question = question
            if current_curriculum and current_problem_set:
                key = f"{current_curriculum}-{current_problem_set}"
                if key not in questions_per_problem_set:
                    questions_per_problem_set[key] = []
                
                # Generate filename based on new structure
                question_number = len(questions_per_problem_set[key]) + 1
                filename = generate_filename(current_curriculum, current_problem_set, question_number)
                filenames[(current_curriculum, current_problem_set, current_question)] = filename
                
                questions_per_problem_set[key].append({
                    'curriculum': current_curriculum,
                    'problem_set': current_problem_set,
                    'question': question,
                    'answers': [],
                    'hints': [],
                    'filename': filename
                })

        # Collect answers and hints
        if pd.notna(row['Answer']) and current_curriculum and current_problem_set:
            key = f"{current_curriculum}-{current_problem_set}"
            questions_per_problem_set[key][-1]['answers'].append(row['Answer'])
        if pd.notna(row['Hint']) and current_curriculum and current_problem_set:
            key = f"{current_curriculum}-{current_problem_set}"
            questions_per_problem_set[key][-1]['hints'].append(row['Hint'])

    # Pre-generate the "Z-END" filenames for each problem set
    for key in questions_per_problem_set:
        curriculum, problem_set = key.split("-")
        end_page_filenames[key] = generate_filename(curriculum, problem_set, "Z-END")

    # Now we can generate the files with correct links
    for key, questions in questions_per_problem_set.items():
        for i, question_data in enumerate(questions):
            curriculum = question_data['curriculum']
            problem_set = question_data['problem_set']
            question = question_data['question']
            answers = question_data['answers']
            hints = question_data['hints']
            current_filename = question_data['filename']
            
            # Handle next page link
            if i < len(questions) - 1:
                next_filename = questions[i + 1]['filename']
            else:
                # Link to the pre-generated "Z-END" page for this problem set
                next_filename = end_page_filenames[key]
            
            # Generate HTML content
            question_number = i + 1
            html_content = create_html_content(curriculum, problem_set, question, answers, hints, next_filename, question_number)
            with open(os.path.join(output_folder, current_filename), 'w', encoding='utf-8') as file:
                file.write(html_content)
        
        # Generate final "Z-END" page for this problem set
        curriculum, problem_set = key.split("-")
        end_page_html = create_end_page(curriculum, problem_set)
        with open(os.path.join(output_folder, end_page_filenames[key]), 'w', encoding='utf-8') as file:
            file.write(end_page_html)

    print(f"Webpages successfully generated in {output_folder}")

# Path to the CSV file
csv_file = "KT-Questions-S.csv"

# Call the function to generate the webpages
generate_webpages_from_csv(csv_file)
