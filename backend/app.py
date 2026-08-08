from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from document_processor import process_pdf
from question_parser import parse_questions
from question_bank import get_random_questions

import os


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# =========================================================
# ALLOWED FILE TYPES
# =========================================================

ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template("upload.html")


# =========================================================
# PDF UPLOAD
# =========================================================

@app.route("/upload", methods=["POST"])
def upload_file():

    # -----------------------------------------------------
    # Check document
    # -----------------------------------------------------

    if "document" not in request.files:

        return "No document selected."


    file = request.files["document"]


    if file.filename == "":

        return "No document selected."


    # -----------------------------------------------------
    # Check PDF
    # -----------------------------------------------------

    if not allowed_file(file.filename):

        return "Only PDF files are currently supported."


    # -----------------------------------------------------
    # Secure filename
    # -----------------------------------------------------

    filename = secure_filename(
        file.filename
    )


    # -----------------------------------------------------
    # Upload path
    # -----------------------------------------------------

    upload_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )


    # -----------------------------------------------------
    # Save PDF
    # -----------------------------------------------------

    file.save(upload_path)


    # =====================================================
    # IMAGE STORAGE
    # =====================================================

    images_folder = os.path.join(
        app.config["UPLOAD_FOLDER"],
        "images"
    )


    # Create images folder if necessary

    os.makedirs(
        images_folder,
        exist_ok=True
    )


    # =====================================================
    # PROCESS PDF
    # =====================================================

    pages = process_pdf(
        upload_path,
        images_folder
    )


    # =====================================================
    # EXTRACT QUESTIONS
    # =====================================================

    questions = parse_questions(
        pages
    )


    # =====================================================
    # PRINT TOTAL QUESTION COUNT
    # =====================================================

    print()
    print(
        "TOTAL QUESTIONS DETECTED:",
        len(questions)
    )
    print()


    # =====================================================
    # RANDOM QUESTION SELECTION
    # =====================================================

    # Temporary test value.
    # Later this will come from the user.

    test_questions = get_random_questions(
        questions,
        5
    )


    # =====================================================
    # PRINT RANDOM QUESTIONS IN TERMINAL
    # =====================================================

    print()
    print(
        "======================================"
    )
    print(
        "       RANDOM QUESTIONS"
    )
    print(
        "======================================"
    )
    print()


    for question in test_questions:

        print(
            f"Question {question['id']}:"
        )

        print(
            question["question"]
        )

        print(
            "Options:",
            question["options"]
        )

        print(
            "Image:",
            question["image"]
        )

        print(
            "Original Page:",
            question["page"]
        )

        print(
            "-" * 50
        )


    print()
    print(
        "======================================"
    )
    print()


    # =====================================================
    # BUILD BROWSER OUTPUT
    # =====================================================

    result = f"""
    <!DOCTYPE html>

    <html>

    <head>

        <title>Exam Platform</title>

        <style>

            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                line-height: 1.6;
            }}

            .question {{
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 25px;
            }}

            .option {{
                margin: 8px 0;
            }}

            .question-image {{
                max-width: 600px;
                height: auto;
                margin-top: 15px;
            }}

        </style>

    </head>


    <body>

        <h2>
            Document uploaded successfully!
        </h2>

        <p>
            <strong>File:</strong>
            {filename}
        </p>

        <p>
            <strong>Total questions detected:</strong>
            {len(questions)}
        </p>

        <p>
            <strong>Random questions selected:</strong>
            {len(test_questions)}
        </p>

        <hr>

        <h2>
            Randomly Selected Questions
        </h2>
    """


    # =====================================================
    # NO QUESTIONS
    # =====================================================

    if not test_questions:

        result += """
        <p>
            No questions were detected.
        </p>
        """


    # =====================================================
    # DISPLAY RANDOM QUESTIONS
    # =====================================================

    else:

        for display_number, question in enumerate(
            test_questions,
            start=1
        ):

            safe_question = (
                question["question"]
                .encode(
                    "utf-8",
                    errors="replace"
                )
                .decode("utf-8")
            )


            result += f"""

            <div class="question">

                <h3>
                    Question {display_number}
                </h3>

                <p>
                    {safe_question}
                </p>

                <p>
                    <strong>
                        Source Page:
                    </strong>

                    {question["page"]}
                </p>

            """


            # =================================================
            # DISPLAY OPTIONS
            # =================================================

            if question["options"]:

                result += """

                <p>
                    <strong>
                        Options:
                    </strong>
                </p>

                """


                for option in question["options"]:

                    safe_option = (
                        option["text"]
                        .encode(
                            "utf-8",
                            errors="replace"
                        )
                        .decode("utf-8")
                    )


                    result += f"""

                    <div class="option">

                        {option["label"]}.
                        {safe_option}

                    </div>

                    """


            else:

                result += """

                <p>
                    <em>
                        No options detected.
                    </em>
                </p>

                """


            # =================================================
            # DISPLAY IMAGE / GRAPH
            # =================================================

            if question["image"]:

                result += f"""

                <p>

                    <strong>
                        Associated Figure:
                    </strong>

                </p>

                <img
                    class="question-image"
                    src="/uploaded-images/{question["image"]}"
                >

                """


            # Close question container

            result += """

            </div>

            """


    # =====================================================
    # CLOSE HTML
    # =====================================================

    result += """

    </body>

    </html>

    """


    return result


# =========================================================
# SERVE EXTRACTED IMAGES
# =========================================================

@app.route(
    "/uploaded-images/<filename>"
)
def uploaded_image(filename):

    images_folder = os.path.join(
        app.config["UPLOAD_FOLDER"],
        "images"
    )


    return send_from_directory(
        images_folder,
        filename
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )