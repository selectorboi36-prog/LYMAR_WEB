import os
from datetime import datetime, timezone, timedelta

import base64
from datetime import datetime, timezone, timedelta

from datetime import datetime, timezone, timedelta


from flask import Flask, render_template, request, jsonify, send_file
from google import genai
from PIL import Image


app = Flask(__name__)

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY was not found.")

client = genai.Client(api_key=api_key)


MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite"
]


# =========================
# LYMAR HOME
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# LYMAR STUDY & QUIZ MODE
# =========================

@app.route("/quiz")
def quiz():
    return render_template("quiz.html")


@app.route("/planner")
def planner():
    return render_template("planner.html")


# =========================
# NORMAL LYMAR AI CHAT
# =========================

@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json() or {}

    question = data.get("question", "").strip()

    # Exact Rwanda date and time
    rwanda_time = datetime.now(timezone(timedelta(hours=2)))
    current_date = rwanda_time.strftime("%A, %B %d, %Y")
    current_time = rwanda_time.strftime("%H:%M:%S")

    # Answer date/time questions directly instead of asking Gemini
    question_lower = question.lower()

    if any(term in question_lower for term in [
        "today's date",
        "todays date",
        "today date",
        "current date",
        "what date is it",
        "what day is it",
        "today",
    ]):
        return jsonify({
            "answer": f"Today is {current_date}."
        })

    if any(term in question_lower for term in [
        "current time",
        "what time is it",
        "time now",
        "what is the time",
    ]):
        return jsonify({
            "answer": f"The current time in Rwanda is {current_time}."
        })



    if not question:
        return jsonify({
            "answer": "Please enter a question."
        })

    rwanda_time = datetime.now(timezone(timedelta(hours=2)))
    current_date = rwanda_time.strftime("%A, %B %d, %Y")
    current_time = rwanda_time.strftime("%H:%M:%S")

    prompt = f"""
You are LYMAR, a friendly and intelligent AI school assistant.

You were created by IKUZE AUDOPHEN for:
LYCEE SAINT MARCEL DE RUKARA.

Your job is to help students learn clearly.

IMPORTANT ANSWER STYLE:

1. Write like a helpful teacher having a conversation with a student.
2. Use simple, natural English.
3. Be clear, friendly and easy to understand.
4. Do NOT use Markdown symbols.
5. Do NOT use asterisks such as ** or *.
6. Do NOT use hashtags such as # or ###.
7. Do NOT use LaTeX.
8. Do NOT use dollar signs for mathematical formatting.
9. Do NOT use commands such as \\vec, \\text, \\mathrm, \\frac or similar.
10. Write mathematical formulas in normal plain text.
11. Use simple headings when helpful.
12. Use numbered lists when explaining steps.
13. Keep answers reasonably concise unless the student asks for more detail.
14. For mathematics and science, show the important steps.
15. When appropriate, give a simple example.
16. Answer the student's actual question directly.

CURRENT DATE IN RWANDA: {current_date}
CURRENT TIME IN RWANDA: {current_time}

IMPORTANT: For questions about today's date, current date, current time, day, month, or year, use the CURRENT DATE and CURRENT TIME above. Never guess or invent them.

The student's question is:

{question}
"""

    last_error = None

    for model in MODELS:

        try:

            print("Trying model:", model)

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            print("SUCCESS:", model)

            return jsonify({
                "answer": response.text
            })

        except Exception as error:

            last_error = error

            print("FAILED:", model)
            print("ERROR:", error)

            continue

    print("ALL GEMINI MODELS FAILED:", last_error)

    return jsonify({
        "answer": (
            "LYMAR's AI service is temporarily busy. "
            "Please try again in a few seconds."
        )
    })


# =========================
# LYMAR REASONING MODE
# =========================

@app.route("/reason", methods=["POST"])
def reason():

    data = request.get_json() or {}

    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "answer": "Please enter a problem or question for Reasoning Mode."
        })

    prompt = f"""
You are LYMAR Reasoning Mode, an advanced school problem-solving
assistant created by IKUZE AUDOPHEN for LYCEE SAINT MARCEL DE RUKARA.

Your purpose is to help students understand HOW to solve a problem.

Analyze the student's problem carefully before answering.

Focus especially on:
- Mathematics
- Physics
- Chemistry
- Biology
- ICT and programming
- Logic
- Science problems
- Word problems
- School examination questions

IMPORTANT:

1. Give a clear step-by-step explanation.
2. Explain the important reasoning behind each step.
3. Do not reveal private internal chain-of-thought or hidden reasoning.
4. Give only the useful reasoning needed for the student to understand and learn.
5. Identify the information given in the problem.
6. Identify what the student needs to find.
7. Select an appropriate formula, rule, method, or concept.
8. Apply the method carefully.
9. Show important calculations.
10. Check the result when possible.
11. Give a clear final answer.
12. If there is more than one valid method, mention another method briefly when useful.
13. If the question is ambiguous, explain what information is missing.
14. Never invent information that is not provided.
15. Use simple language suitable for a secondary-school student.
16. Do not use Markdown symbols.
17. Do not use asterisks such as ** or *.
18. Do not use hashtags such as # or ###.
19. Do not use LaTeX.
20. Do not use dollar signs for mathematical formatting.
21. Write mathematical formulas in normal plain text.
22. Use numbered steps.
23. Keep the explanation detailed enough to teach the student, but avoid unnecessary repetition.

Use this structure when appropriate:

Problem
Restate the problem briefly.

Given
List the important information provided.

Find
State what must be found.

Method
Explain the formula, rule, concept, or strategy to use.

Step 1
Show the first important step.

Step 2
Show the next important step.

Step 3
Continue only as necessary.

Check
Verify the answer when possible.

Final Answer
Give the final answer clearly.

Student's problem:

{question}
"""

    last_error = None

    for model in MODELS:

        try:

            print("REASONING: Trying model:", model)

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            print("REASONING: SUCCESS:", model)

            return jsonify({
                "answer": response.text
            })

        except Exception as error:

            last_error = error

            print("REASONING: FAILED:", model)
            print("REASONING ERROR:", error)

            continue

    print("ALL REASONING MODELS FAILED:", last_error)

    return jsonify({
        "answer": (
            "LYMAR Reasoning Mode is temporarily busy. "
            "Please try again in a few seconds."
        )
    })


# =========================
# LYMAR IMAGE UNDERSTANDING
# =========================

@app.route("/analyze_image", methods=["POST"])
def analyze_image():

    if "image" not in request.files:

        return jsonify({
            "answer": "Please upload an image."
        }), 400

    uploaded_file = request.files["image"]

    if uploaded_file.filename == "":

        return jsonify({
            "answer": "Please choose an image."
        }), 400

    try:

        image = Image.open(uploaded_file.stream)

        image.load()

        question = request.form.get(
            "question",
            "Describe this image and explain what it shows."
        ).strip()

        if not question:
            question = "Describe this image and explain what it shows."

        prompt = f"""
You are LYMAR, an intelligent school AI assistant.

You were created by IKUZE AUDOPHEN for:
LYCEE SAINT MARCEL DE RUKARA.

Analyze the image carefully and answer the student's question.

Use simple, natural English.

Do not use Markdown symbols.
Do not use LaTeX.
Do not use asterisks.
Do not use hashtags.

If the image contains a mathematics problem:
Read the problem carefully and solve it step by step.

If the image contains a science diagram:
Identify the important parts and explain them.

If the image contains text:
Read the visible text accurately.

If something is unclear, say so instead of inventing information.

Student's question:

{question}
"""

        last_error = None

        for model in MODELS:

            try:

                print("IMAGE: Trying model:", model)

                response = client.models.generate_content(
                    model=model,
                    contents=[prompt, image]
                )

                print("IMAGE: SUCCESS:", model)

                return jsonify({
                    "answer": response.text
                })

            except Exception as error:

                last_error = error

                print("IMAGE: FAILED:", model)
                print("IMAGE ERROR:", error)

                continue

        print("ALL IMAGE MODELS FAILED:", last_error)

        return jsonify({
            "answer": (
                "LYMAR could not analyze the image right now. "
                "Please try again in a few seconds."
            )
        }), 500

    except Exception as error:

        print("IMAGE PROCESSING ERROR:", error)

        return jsonify({
            "answer": (
                "LYMAR could not open that image. "
                "Please try a JPG, JPEG, PNG or WEBP image."
            )
        }), 400


# =========================
# LYMAR IMAGE GENERATION
# =========================

@app.route("/generate_image", methods=["POST"])
def generate_image():

    data = request.get_json() or {}

    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({
            "error": "Please describe the image you want LYMAR to create."
        }), 400

    try:

        print("IMAGE GENERATION STARTED")

        interaction = client.interactions.create(
            model="gemini-3.1-flash-image",
            input=prompt,
            response_format={
                "type": "image",
                "mime_type": "image/jpeg",
                "aspect_ratio": "16:9",
                "image_size": "1K"
            }
        )

        generated_image = interaction.output_image

        if generated_image:

            os.makedirs("uploads", exist_ok=True)

            image_data = base64.b64decode(
                generated_image.data
            )

            image_path = os.path.join(
                "uploads",
                "lymar_generated.jpg"
            )

            with open(image_path, "wb") as image_file:
                image_file.write(image_data)

            print("IMAGE GENERATION: SUCCESS")

            return jsonify({
                "image": (
                    "data:image/jpeg;base64,"
                    + generated_image.data
                )
            })

        print("IMAGE GENERATION: no image returned")

        return jsonify({
            "error": "LYMAR did not return an image."
        }), 500

    except Exception as error:

        print("IMAGE GENERATION ERROR:")
        print(error)

        return jsonify({
            "error": (
                "LYMAR could not generate the image right now. "
                "Please try again."
            )
        }), 500


# =========================
# START LYMAR
# =========================



# LYMAR SYLLABUS INLINE PDF ROUTE

@app.route("/view_syllabus/<path:filename>")
def view_syllabus(filename):
    syllabus_folder = os.path.join(
        app.root_path,
        "static",
        "syllabuses"
    )

    filepath = os.path.join(
        syllabus_folder,
        filename
    )

    if not os.path.isfile(filepath):
        return "Syllabus not found.", 404

    response = send_file(
        filepath,
        mimetype="application/pdf",
        as_attachment=False
    )

    response.headers["Content-Disposition"] = (
        "inline; filename=\"" + os.path.basename(filepath) + "\""
    )

    response.headers["X-Content-Type-Options"] = "nosniff"

    return response

# END LYMAR SYLLABUS INLINE PDF ROUTE

if __name__ == "__main__":
    app.run(debug=True)
