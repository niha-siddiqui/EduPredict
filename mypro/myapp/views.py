import datetime

from google.cloud.firestore import Query
from django.contrib import messages
from django.shortcuts import render, redirect
from mypro.firebase_connection import database
firebase_key ="AIzaSyD8qf5ulXocDrn8llaJ-jv_70vve3GrjWc"
import  requests

from mypro.firebase_connection import database

# Create your views here.


def index(r):
    user_email = r.session.get("useremail")  # session se email le lo
    return render(r, "myapp/index.html", {"e": user_email})


def register(r):
    if r.method == "POST":
        a  = r.POST.get("name")
        b  = r.POST.get("email")
        c  = r.POST.get("pswd")
        d  = int(r.POST.get("num"))

        if not a or not b or not c or not d:
            messages.error(r,"All Fields Are Required")
            return redirect("reg")

        if len(c) < 6:
            messages.error(r, "Password Should be Greater than 6")
            return redirect("reg")

        if d < 18:
            messages.error(r, "Age Should be Greater than 17")
            return redirect("reg")

        url=f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={firebase_key}"
        jao = {
            "email" : b,
            "password" : c,
            "returnSecureToken" : True
        }

        resp = requests.post(url,jao)

        if resp.status_code == 200:

            user_Data = resp.json()
            print(user_Data)
            # Email Send
            id = user_Data.get("idToken")

            email_url =f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={firebase_key}"
            email_data = {
                "requestType":"VERIFY_EMAIL",
                "idToken" : id
            }

            email_send = requests.post(email_url , email_data)
            if email_send.status_code == 200:
                database.collection("registered_user").add({
                    "Name" : a,
                    "Email" : b,
                    "Age" : d,
                    "Created_at" : datetime.datetime.utcnow()
                })
                messages.success(r,"User Create Successfully and Email has been sent")
                return redirect("reg")
            else:
                error = resp.json().get("error", {}).get("messages", "Not Found")
                print(error)
                messages.error(r, f"Error : {error}")
                return redirect("reg")
        else:
            error = resp.json().get("error",{}).get("message","Not Found")
            print(error)
            messages.error(r,f"Error : {error}")
            return redirect("reg")
    return render(r,"myapp/register.html")

def login(r):
    if r.method=="POST":
        email = r.POST.get("email")
        pswd = r.POST.get("pswd")

        if not email or not pswd:
            messages.error(r,"All Fields are required")
            return redirect("log")

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_key}"
        data = {
            "email" : email,
            "password" : pswd,
            "returnSecureToken" : True
        }

        res = requests.post(url, data)

        if res.status_code == 200:
            user_Record = res.json()
            r.session["idd"] = user_Record.get("idToken")
            r.session["useremail"] = user_Record.get("email")
            messages.success(r,"Login Sucessfully")
            return redirect("index")

        else:
            error = res.json().get("error",{}).get("message","")
            messages.error(r,f"Error {error}")
            return redirect("log")
    return render(r,"myapp/login.html")

def logout(r):
    r.session.flush()
    return redirect("log")


def ViewData(r):
    data =  database.collection("Contact").order_by("name",direction=Query.ASCENDING).stream()
    contact = []
    for a in data:
       records =  a.to_dict()
       records["id"] = a.id
       contact.append(records)
    return render(r,"myapp/ShowData.html",{"con":contact})


def delete_record(r, id):
    database.collection("Contact").document(id).delete()
    return redirect("showcon")



import os
import pandas as pd
from django.shortcuts import render
from django.conf import settings
from mypro.firebase_connection import database  # Firebase connection
import datetime

# CSV path inside your app
csv_path = os.path.join(settings.BASE_DIR, 'myapp', 'students_dataset.csv')

try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    df = None


def generate_paragraph(responses):
    # Academic behavior
    focus = "You are highly focused while studying." if responses['q1'] in [
        'Never distracted', 'Rarely distracted'
    ] else "You sometimes get distracted but manage to stay on track."

    # Study method
    if responses['q2'] == "Alone":
        study_method = "You prefer studying alone, which helps you concentrate."
    elif responses['q2'] == "With friends":
        study_method = "You enjoy studying with friends and discussing topics together."
    else:
        study_method = "You study both alone and with friends, depending on the task."

    # Problem solving
    problem_solving = (
        "You like to solve problems independently, experimenting until you understand the concept."
        if responses['q6'] == "Try by myself"
        else "You ask for help when needed and use resources wisely to solve problems."
    )

    # Personality
    personality_intro = f"You are {responses.get('q13', 'unique in personality')}."
    learning_style = f"Your preferred learning style is {responses.get('q14', 'adaptable')}."
    study_behavior = f"Your study behavior can be described as {responses.get('q15', 'consistent')}."

    paragraph = (
        f"{personality_intro} {focus} {study_method} "
        f"{problem_solving} {learning_style} {study_behavior}"
    )

    return paragraph


def student_survey(request):
    if request.method == 'POST':
        # Collect responses
        responses = {f'q{i}': request.POST.get(f'q{i}', "") for i in range(1, 13)}

        # Extra personalization fields
        responses['q13'] = "Analytical & Leader"
        responses['q14'] = "Kinesthetic & Reading"
        responses['q15'] = "Focused & Self-motivated"

        # Generate paragraph
        paragraph = generate_paragraph(responses)

        # FINAL VALUES — NO ANALYSIS
        quote = "“The successful warrior is the average man, with laser-like focus.” – Bruce Lee"
        score = 75

        # ---------------- Save to Firestore ----------------
        database.collection("student_survey").add({
            "email": str(request.session.get("useremail", "unknown")),  # User email from session
            "responses": responses,
            "paragraph": paragraph,
            "quote": quote,
            "score": score,
            "created_at": datetime.datetime.utcnow()
        })

        return render(request, 'myapp/survey_result.html', {
            'paragraph': paragraph,
            'quote': quote,
            'score': score,
        })

    return render(request, 'myapp/survey_form.html')


#
# from django.shortcuts import render
# import pandas as pd
# import joblib
# import os
#
# # ---------------------------
# # File paths
# # ---------------------------
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# CSV_PATH = os.path.join(BASE_DIR, "student_data.csv")
# MODEL_PATH = os.path.join(BASE_DIR, "student_model.pkl")
#
# # ---------------------------
# # Field Specializations
# # ---------------------------
# FIELD_SPECIALIZATION = {
#     "Engineering": ["Software Engineer", "AI Specialist", "Robotics Engineer", "Data Scientist", "Electrical Engineer"],
#     "Medical": ["Neurologist", "Gynologist", "Orthologist", "Cardiologist", "Surgeon"],
#     "Arts": ["Graphic Designer", "Animator", "Photographer", "Fashion Designer", "Musician"],
#     "SocialScience": ["Teacher", "Lawyer", "Counselor", "Political Analyst", "Sociologist"]
# }
#
# # ---------------------------
# # Load trained model
# # ---------------------------
# model = joblib.load(MODEL_PATH)
#
# # ---------------------------
# # View Function
# # ---------------------------
# def student_prediction(request):
#     suggestion = None
#
#     if request.method == "POST":
#         # Collect form data
#         form_data = {k: request.POST.get(k, "") for k in [
#             "study_hours","math_marks","english_marks","science_marks","urdu_marks",
#             "biology_marks","computer_marks","arts_marks","interest"
#         ]}
#
#         # Convert numeric fields
#         numeric_cols = ["study_hours","math_marks","english_marks","science_marks","urdu_marks",
#                         "biology_marks","computer_marks","arts_marks"]
#         for col in numeric_cols:
#             try:
#                 form_data[col] = float(form_data[col])
#             except:
#                 form_data[col] = 0
#
#         # Prepare input for model
#         input_df = pd.DataFrame([form_data])
#         input_df = input_df[numeric_cols]
#
#         # Predict final percentage
#         predicted_score = model.predict(input_df)[0]
#
#         # Determine top field and specializations
#         top_field = form_data["interest"]
#         top_specializations = FIELD_SPECIALIZATION.get(top_field, [])[:3]
#
#         # Suggestion dict
#         suggestion = {
#             "predicted_score": round(predicted_score,2),
#             "top_field": top_field,
#             "top_specializations": top_specializations
#         }
#
#         # Append new data to CSV for future retraining
#         new_row = form_data.copy()
#         new_row["final_percentage"] = predicted_ score
#         pd.DataFrame([new_row]).to_csv(CSV_PATH, mode='a', header=False, index=False)
#
#     return render(request, "myapp/studentprediction.html", {"suggestion": suggestion})














import os
import pandas as pd
from django.shortcuts import render
from django.conf import settings
from mypro.firebase_connection import database  # Firebase connection
import datetime

# CSV path inside your app (optional)
csv_path = os.path.join(settings.BASE_DIR, 'myapp', 'student_progress_dataset.csv')
try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    df = None

# Motivational quotes mapping
quotes_mapping = {
    'focus_high': "“The successful warrior is the average man, with laser-like focus.” – Bruce Lee",
    'focus_medium': "“Focus on being productive instead of busy.” – Tim Ferriss",
    'focus_low': "“You don’t have to be great to start, but you have to start to be great.” – Zig Ziglar",
    'study_alone': "“Don’t count the days, make the days count.” – Muhammad Ali",
    'study_group': "“Alone we can do so little; together we can do so much.” – Helen Keller",
    'study_both': "“Adaptability is about the powerful difference between adapting to cope and adapting to win.” – Max McKeown",
    'problem_independent': "“I never teach my pupils; I only attempt to provide the conditions in which they can learn.” – Albert Einstein",
    'problem_help': "“It’s not who you are that holds you back, it’s who you think you’re not.” – Unknown",
    'motivation_high': "“The way to get started is to quit talking and begin doing.” – Walt Disney",
    'motivation_medium': "“Small daily improvements are the key to staggering long-term results.” – Robin Sharma"
}

def generate_paragraph(responses):
    lines = []
    trait_scores = {}

    focus_map = {"Never distracted": 3, "Rarely distracted": 2, "Sometimes distracted": 1, "Often distracted": 0}
    score_focus = focus_map.get(responses.get('q1'), 1)
    if score_focus >= 2:
        lines.append("You are highly focused while studying and rarely get distracted.")
        trait_scores['focus'] = ('focus_high', score_focus)
    elif score_focus == 1:
        lines.append("You have moderate focus; try short study sessions to stay concentrated.")
        trait_scores['focus'] = ('focus_medium', score_focus)
    else:
        lines.append("You often get distracted; consider structured study habits to improve concentration.")
        trait_scores['focus'] = ('focus_low', score_focus)

    study = responses.get('q2')
    if study == 'Alone':
        lines.append("You prefer studying alone, which helps you concentrate better.")
        trait_scores['study'] = ('study_alone', 3)
    elif study == 'With friends':
        lines.append("You enjoy collaborative learning, which boosts understanding through discussion.")
        trait_scores['study'] = ('study_group', 3)
    else:
        lines.append("You adapt your study style depending on the task, which is versatile and effective.")
        trait_scores['study'] = ('study_both', 3)

    problem = responses.get('q4')
    if problem in ["Try by myself", "Practice problems"]:
        lines.append("You solve problems independently, strengthening your critical thinking skills.")
        trait_scores['problem'] = ('problem_independent', 3)
    else:
        lines.append("You ask for help when needed, which shows you know how to collaborate effectively.")
        trait_scores['problem'] = ('problem_help', 2)

    motivation_map = {"Very motivated": 3, "Motivated": 2, "Neutral": 1, "Less motivated": 0}
    score_motivation = motivation_map.get(responses.get('q7'), 1)
    if score_motivation >= 2:
        lines.append("You are highly motivated and committed to achieving your goals.")
        trait_scores['motivation'] = ('motivation_high', score_motivation)
    else:
        lines.append("You have moderate motivation; small daily goals can help you improve steadily.")
        trait_scores['motivation'] = ('motivation_medium', score_motivation)

    personality = f"You are {responses.get('q13', 'analytical & leader')}."
    learning = f"Your preferred learning style is {responses.get('q14', 'kinesthetic & reading')}."
    study_behavior = f"Your study behavior can be described as {responses.get('q15', 'focused & self-motivated')}."
    lines.extend([personality, learning, study_behavior])

    paragraph = " ".join(lines)

    dominant_trait = max(trait_scores.values(), key=lambda x: x[1])[0]
    quote = quotes_mapping.get(dominant_trait, "“Believe you can and you're halfway there.” – Theodore Roosevelt")

    total_score = sum([v[1] for v in trait_scores.values()])
    max_score = len(trait_scores) * 3
    progress_percentage = int((total_score / max_score) * 100)

    return paragraph, quote, progress_percentage, trait_scores


def student_progress_survey(request):
    survey = [
        {"text": "Do you get distracted easily while studying?", "options": ["Never distracted", "Rarely distracted", "Sometimes distracted", "Often distracted"]},
        {"text": "Do you prefer studying alone or with friends?", "options": ["Alone", "With friends", "Both"]},
        {"text": "How often do you complete your homework on time?", "options": ["Always", "Often", "Sometimes", "Rarely", "Never"]},
        {"text": "Do you like solving problems independently?", "options": ["Try by myself", "Practice problems", "Ask for help"]},
        {"text": "Do you review your notes regularly?", "options": ["Always", "Often", "Sometimes", "Rarely"]},
        {"text": "Do you ask for help when stuck in a subject?", "options": ["Always", "Sometimes", "Rarely", "Never"]},
        {"text": "How motivated are you to study daily?", "options": ["Very motivated", "Motivated", "Neutral", "Less motivated"]},
        {"text": "How do you manage stress while studying?", "options": ["Very well", "Well", "Average", "Poorly"]},
        {"text": "Do you participate actively in class?", "options": ["Always", "Often", "Sometimes", "Rarely", "Never"]},
        {"text": "Do you sleep enough before exams?", "options": ["Always", "Often", "Sometimes", "Rarely"]},
        {"text": "How often do you use online learning resources?", "options": ["Daily", "Few times a week", "Rarely", "Never"]},
        {"text": "Do you track your academic progress regularly?", "options": ["Always", "Often", "Sometimes", "Rarely", "Never"]}
    ]

    if request.method == 'POST':
        responses = {f'q{i+1}': request.POST.get(f'q{i+1}') for i in range(len(survey))}
        # Optional extra data for personalization
        responses['q13'] = "You have unique strengths and the potential to grow in every area of learning."
        responses['q14'] = "Your learning style allows you to adapt and explore new ways of understanding concepts."
        responses['q15'] = "Your study habits reflect your dedication, and with consistent effort, you can achieve even more."

        paragraph, quote, progress, trait_scores = generate_paragraph(responses)

        # ---------------- Save to Firestore ----------------
        database.collection("student_progress").add({
            "email": str(request.session.get("useremail", "unknown")),
            "responses": responses,
            "paragraph": paragraph,
            "quote": quote,
            "progress": progress,
            "trait_scores": trait_scores,
            "created_at": datetime.datetime.utcnow()
        })

        return render(request, 'myapp/survey_progress_result.html', {
            'paragraph': paragraph,
            'quote': quote,
            'progress': progress,
            'trait_scores': trait_scores
        })

    return render(request, 'myapp/survey_progress.html', {'survey': survey})










from django.shortcuts import render
import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier

# ---------------- Paths ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "droupout_std.csv")
MODEL_PATH = os.path.join(BASE_DIR, "dropout_model.pkl")

# ---------------- Load dataset & train model ----------------
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    df = pd.read_csv(DATASET_PATH)
    X = df.drop("dropout", axis=1)
    y = df["dropout"]
    model = RandomForestClassifier()
    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)

# ---------------- Suggestions ----------------
SUGGESTIONS = {
    'gpa': 'Focus on weak subjects, complete assignments, join tutoring.',
    'attendance': 'Improve attendance above 80%, manage travel time.',
    'engagement': 'Participate more in class and discussions.',
    'fees_issue': 'Apply for scholarships or financial aid.',
    'family_support': 'Seek guidance from teachers or counselor.',
    'travel_issue': 'Plan travel or seek transport help.'
}

# ---------------- View ----------------
def dropout_form(request):
    if request.method == "POST":
        # Get form inputs
        gpa = float(request.POST.get("gpa"))
        attendance = int(request.POST.get("attendance"))
        engagement = int(request.POST.get("engagement"))
        fees_issue = int(request.POST.get("fees_issue"))
        family_support = int(request.POST.get("family_support"))
        travel_issue = int(request.POST.get("travel_issue"))

        # Predict dropout
        data = [[gpa, attendance, engagement, fees_issue, family_support, travel_issue]]
        pred = model.predict(data)[0]
        prob = model.predict_proba(data)[0][1] * 100

        # Prepare reasons, suggestions, chart_data
        reasons = []
        suggestions = []
        chart_data = {}

        # GPA severity
        gpa_sev = max(0, 4.0 - gpa)/4.0
        if gpa_sev > 0.2:
            reasons.append('Low GPA')
            suggestions.append(SUGGESTIONS['gpa'])
        chart_data['GPA'] = round(gpa_sev, 2)

        # Attendance severity
        att_sev = max(0, 75 - attendance)/75
        if att_sev > 0.2:
            reasons.append('Low Attendance')
            suggestions.append(SUGGESTIONS['attendance'])
        chart_data['Attendance'] = round(att_sev, 2)

        # Engagement severity
        eng_sev = (3 - engagement)/2
        if eng_sev > 0.2:
            reasons.append('Not Active in Class')
            suggestions.append(SUGGESTIONS['engagement'])
        chart_data['Engagement'] = round(eng_sev, 2)

        # Fees issue
        fees_sev = 1 if fees_issue == 1 else 0
        if fees_sev > 0:
            reasons.append('Cannot afford fees')
            suggestions.append(SUGGESTIONS['fees_issue'])
        chart_data['Fees'] = fees_sev

        # Family support
        fam_sev = 1 if family_support == 0 else 0
        if fam_sev > 0:
            reasons.append('Low Family Support')
            suggestions.append(SUGGESTIONS['family_support'])
        chart_data['Family'] = fam_sev

        # Travel severity
        trav_sev = 1 if travel_issue == 1 else 0
        if trav_sev > 0:
            reasons.append('Difficult Travel')
            suggestions.append(SUGGESTIONS['travel_issue'])
        chart_data['Travel'] = trav_sev

        # Convert chart_data to lists for template
        chart_labels = list(chart_data.keys())
        chart_values = list(chart_data.values())
        database.collection("dropout_Record").add({
            "email": str(request.session.get("useremail", "unknown")),
            "dropout_prediction": int(pred),  # convert np.int64 → int
            "reasons": list(map(str, reasons)),  # ensure pure Python list of strings
        })
        return render(request, "myapp/dropout_result.html", {
            "prediction": pred,
            "probability": round(prob, 2),
            "reasons": reasons,
            "suggestions": suggestions,
            "chart_labels": chart_labels,
            "chart_values": chart_values
        })

    # For GET request, render the input form
    return render(request, "myapp/dropout_form.html")

# Add this import at top if not already there



# Add this function
def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        # Validation
        if not name or not email or not phone or not subject or not message:
            messages.error(request, "All fields are required!")
            return redirect("contact")

        # Save to Firebase
        try:
            database.collection("Contact").add({
                "name": name,
                "email": email,
                "phone": phone,
                "subject": subject,
                "message": message,
                "created_at": datetime.datetime.utcnow()
            })
            messages.success(request, "Your message has been sent successfully! We'll get back to you soon.")
            return redirect("contact")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect("contact")

    return render(request, "myapp/contact.html")





from django.shortcuts import render
import pandas as pd
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "student_records_full.csv")
MODEL_FILE = os.path.join(BASE_DIR, "student_model_full.pkl")

FIELD_SPECIALIZATION = {
    "Engineering": ["Software Engineer", "AI Specialist", "Robotics Engineer", "Data Scientist", "Electrical Engineer"],
    "Medical": ["Neurologist", "Gynologist", "Orthologist", "Cardiologist", "Surgeon"],
    "Arts": ["Graphic Designer", "Animator", "Photographer", "Fashion Designer", "Musician"],
    "SocialScience": ["Teacher", "Lawyer", "Counselor", "Political Analyst", "Sociologist"]
}

SUBJECTS = ["Math","English","Science","Urdu","Biology","Computer","Arts"]

model = joblib.load(MODEL_FILE)

from django.shortcuts import render
import pandas as pd
import joblib
import os
import datetime
from mypro.firebase_connection import database  # Firebase connection file

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "student_records_full.csv")
MODEL_FILE = os.path.join(BASE_DIR, "student_model_full.pkl")

FIELD_SPECIALIZATION = {
    "Engineering": ["Software Engineer", "AI Specialist", "Robotics Engineer", "Data Scientist", "Electrical Engineer"],
    "Medical": ["Neurologist", "Gynologist", "Orthologist", "Cardiologist", "Surgeon"],
    "Arts": ["Graphic Designer", "Animator", "Photographer", "Fashion Designer", "Musician"],
    "SocialScience": ["Teacher", "Lawyer", "Counselor", "Political Analyst", "Sociologist"]
}

SUBJECTS = ["Math","English","Science","Urdu","Biology","Computer","Arts"]

model = joblib.load(MODEL_FILE)

def predict_student_full_detailed(request):
    suggestion = None
    class_list = list(range(1,11))  # Classes 1-10
    interest_list = ["Engineering","Medical","Arts","SocialScience"]
    subject_list = SUBJECTS

    if request.method == "POST":
        # Collect all form data
        form = {k: request.POST.get(k, "") for k in [
            "first_name","last_name","age","class",
            "study_hours","math_marks","english_marks","science_marks","urdu_marks",
            "biology_marks","computer_marks","arts_marks","interest",
            "strength_subject","weak_subject","previous_percentage"
        ]}

        # Convert numeric fields
        NUMERIC_FIELDS = ["age","class","study_hours","math_marks","english_marks","science_marks",
                          "urdu_marks","biology_marks","computer_marks","arts_marks","previous_percentage"]
        for f in NUMERIC_FIELDS:
            try:
                form[f] = float(form[f])
            except:
                form[f] = 0

        # Prepare dataframe for model
        input_df = pd.DataFrame([form])
        MODEL_FIELDS = ["study_hours","math_marks","english_marks","science_marks","urdu_marks",
                        "biology_marks","computer_marks","arts_marks"]
        input_df = input_df[MODEL_FIELDS]

        # Predict
        predicted_score = model.predict(input_df)[0]

        # Top field and specializations
        top_field = form["interest"]
        top_specializations = FIELD_SPECIALIZATION.get(top_field, [])[:3]

        # Calculate subject-wise percentage
        subject_marks = {
            "Math": form["math_marks"],
            "English": form["english_marks"],
            "Science": form["science_marks"],
            "Urdu": form["urdu_marks"],
            "Biology": form["biology_marks"],
            "Computer": form["computer_marks"],
            "Arts": form["arts_marks"]
        }
        total_possible = 700  # 7 subjects * 100
        total_obtained = sum(subject_marks.values())
        overall_percentage = (total_obtained / total_possible) * 100

        # Improvement feedback
        prev = form["previous_percentage"]
        if overall_percentage < prev:
            feedback = f"Score decreased from {prev}% to {overall_percentage:.2f}%. Focus on weak areas!"
        else:
            feedback = f"Good! Improved from {prev}% to {overall_percentage:.2f}%."

        # Suggestion dict
        suggestion = {
            "first_name": form["first_name"].capitalize(),
            "last_name": form["last_name"].capitalize(),
            "age": int(form["age"]),
            "class": int(form["class"]),
            "predicted_score": round(predicted_score,2),
            "overall_percentage": round(overall_percentage,2),
            "strength_subject": form["strength_subject"].capitalize(),
            "weak_subject": form["weak_subject"].capitalize(),
            "top_field": top_field,
            "top_specializations": top_specializations,
            "subject_marks": subject_marks,
            "feedback": feedback
        }

        # ----------------- Save to CSV -----------------
        new_record = form.copy()
        new_record["final_percentage"] = predicted_score
        pd.DataFrame([new_record]).to_csv(CSV_FILE, mode='a', header=False, index=False)

        # ----------------- Save to Firebase -----------------
        try:
            database.collection("student_predictions").add({
                "first_name": form["first_name"].capitalize(),
                "last_name": form["last_name"].capitalize(),
                "age": int(form["age"]),
                "class": int(form["class"]),
                "predicted_score": round(predicted_score,2),
                "overall_percentage": round(overall_percentage,2),
                "strength_subject": form["strength_subject"].capitalize(),
                "weak_subject": form["weak_subject"].capitalize(),
                "top_field": top_field,
                "top_specializations": top_specializations,
                "subject_marks": subject_marks,
                "feedback": feedback,
                "email": str(request.session.get("useremail", "unknown")),
                "created_at": datetime.datetime.utcnow()
            })
        except Exception as e:
            print("Firebase save error:", e)

    return render(request, "myapp/student_prediction_full.html", {
        "suggestion": suggestion,
        "class_list": class_list,
        "interest_list": interest_list,
        "subject_list": subject_list
    })


# -------------------- Suggestion Result Page --------------------
from django.shortcuts import render

# Subjects list
subjects = ["English", "Urdu", "Maths", "Physics", "Chemistry",
            "Biology", "Computer", "Accounts", "SST", "Islamiat"]

# -------------------- Suggestion Form Page --------------------
def suggestion(request):
    """
    Display the form to input student details and marks.
    """
    return render(request, "myapp/suggestion.html", {
        "subjects": subjects,
        "marks_range": range(40, 101),  # Marks from 40 to 100
        "class_range": range(6, 13)  # Classes 6 to 12
    })

# -------------------- Suggestion Result Page --------------------
def suggestionresult(request):
    """
    Process submitted form and predict student future, field, careers, and motivation.
    """
    if request.method == "POST":
        student = {}
        student["name"] = request.POST.get("name")
        student["student_class"] = request.POST.get("student_class")
        student["favourite_subject"] = request.POST.get("favourite_subject")
        student["weak_subject"] = request.POST.get("weak_subject")
        student["previous_percentage"] = float(request.POST.get("previous_percentage"))

        # Collect marks, handle "Not in syllabus"
        marks = {}
        for sub in subjects:
            value = request.POST.get(sub)
            if value == "Not in syllabus":
                marks[sub] = None
            else:
                marks[sub] = int(value)

        # Strength & Weakness subjects (exclude None)
        valid_marks = {k: v for k, v in marks.items() if v is not None}
        sorted_marks = sorted(valid_marks.items(), key=lambda x: x[1], reverse=True)
        student["strength"] = dict(sorted_marks[:3])
        student["weakness"] = dict(sorted_marks[-3:])

        # Predicted average score (only syllabus subjects)
        student["predicted_score"] = int(sum(valid_marks.values()) / len(valid_marks)) if valid_marks else 0

        fav = student["favourite_subject"]
        top_subjects = [sub for sub, mark in sorted_marks[:3]]  # Top 3 subjects

        field = ""
        careers = []
        motivation = ""

        # ---------------- NEW: Favourite + Top 3 Strengths Combination Logic ----------------
        # Examples of multiple combinations (approx 40 combinations)
        if fav == "Maths":
            if "Physics" in top_subjects:
                field = "Engineering / Data Science"
                careers = ["AI Engineer", "Robotics Engineer", "Data Scientist", "Mechanical Engineer"]
                motivation = f"You love {fav} and one of your top subjects is Physics. Engineering & Data Science are great options!"
            elif "Biology" in top_subjects:
                field = "Computational Biology / Bioinformatics"
                careers = ["Bioinformatician", "Data Scientist in Biology", "Computational Biologist"]
                motivation = f"You love {fav} and Biology is among your top subjects. Amazing for Computational Biology!"
            elif "Computer" in top_subjects:
                field = "Computer & IT / Analytics"
                careers = ["AI Engineer", "Software Developer", "Data Analyst"]
                motivation = f"Strong {fav} and Computer skills! Perfect for IT & Analytics careers."
            elif "Accounts" in top_subjects:
                field = "Finance & Analytics"
                careers = ["Financial Analyst", "Accountant", "Economist", "Data Analyst"]
                motivation = f"{fav} + Accounts skills are strong. Great for Finance & Analytics."
            else:
                field = "Maths & Science"
                careers = ["Data Analyst", "Statistician", "Researcher"]
                motivation = f"{fav} is your favourite and top subject. Many scientific careers await!"

        elif fav == "Physics":
            if "Maths" in top_subjects:
                field = "Engineering / Research"
                careers = ["Mechanical Engineer", "Civil Engineer", "Data Scientist", "Research Scientist"]
                motivation = f"{fav} + Maths combination suits Engineering & Research."
            elif "Chemistry" in top_subjects:
                field = "Chemical Engineering / Science"
                careers = ["Chemical Engineer", "Lab Researcher", "Materials Scientist"]
                motivation = f"{fav} + Chemistry opens doors to Chemical Engineering & Science."
            elif "Computer" in top_subjects:
                field = "Engineering / IT"
                careers = ["Robotics Engineer", "Software Developer", "AI Engineer"]
                motivation = f"{fav} + Computer opens IT & Engineering opportunities."
            else:
                field = "Physics & Maths"
                careers = ["Researcher", "Technician", "Lab Assistant"]
                motivation = f"{fav} is your favourite. Focus on top strengths to grow in Science & Engineering."

        elif fav == "Biology":
            if "Chemistry" in top_subjects:
                field = "Medical Science / Research"
                careers = ["Doctor", "Pharmacist", "Biotechnologist", "Medical Researcher"]
                motivation = f"{fav} + Chemistry gives strong career options in Medicine & Research."
            elif "Maths" in top_subjects:
                field = "Bioinformatics / Analytics"
                careers = ["Bioinformatician", "Data Scientist in Biology", "Computational Biologist"]
                motivation = f"{fav} + Maths is perfect for Computational Biology & Analytics."
            elif "Computer" in top_subjects:
                field = "Bioinformatics / IT"
                careers = ["Bioinformatician", "Computational Biologist", "Data Scientist in Biology"]
                motivation = f"{fav} + Computer opens opportunities in Bioinformatics & IT."
            else:
                field = "Medical & Biology"
                careers = ["Lab Technician", "Nursing", "Biotechnologist"]
                motivation = f"{fav} is your favourite. Focus on top subjects for medical careers."

        elif fav == "Computer":
            if "Maths" in top_subjects:
                field = "Computer Science / AI"
                careers = ["AI Developer", "Data Scientist", "Software Engineer", "Machine Learning Engineer"]
                motivation = f"{fav} + Maths gives strong IT & AI career prospects."
            elif "Physics" in top_subjects:
                field = "IT & Engineering"
                careers = ["AI Developer", "Software Engineer", "Robotics Engineer"]
                motivation = f"{fav} + Physics skills suit IT & Engineering fields."
            elif "Biology" in top_subjects:
                field = "Bioinformatics / AI"
                careers = ["Bioinformatician", "AI in Healthcare", "Data Scientist"]
                motivation = f"{fav} + Biology gives opportunities in Bioinformatics & AI."
            else:
                field = "Computer & IT"
                careers = ["Software Developer", "AI Engineer", "Data Scientist", "Cyber Security"]
                motivation = f"{fav} is your favourite. Many IT careers await!"

        elif fav == "Accounts":
            if "Maths" in top_subjects:
                field = "Finance / Analytics"
                careers = ["Financial Analyst", "Economist", "Data Analyst"]
                motivation = f"{fav} + Maths is perfect for Finance & Analytics."
            elif "Computer" in top_subjects:
                field = "Accounting & IT"
                careers = ["Accounting Software Specialist", "Financial Analyst", "Auditor"]
                motivation = f"{fav} + Computer opens Accounting & IT opportunities."
            else:
                field = "Commerce / Accounts"
                careers = ["Chartered Accountant (CA)", "ACCA", "B.Com", "Auditor"]
                motivation = f"{fav} is your favourite. Focus on top subjects for commerce careers."

        elif fav == "English":
            if "SST" in top_subjects:
                field = "Arts & Social Sciences"
                careers = ["Journalist", "Lawyer", "Teacher", "Psychologist"]
                motivation = f"Strong {fav} and SST skills are perfect for Arts/Social Sciences."
            elif "Computer" in top_subjects:
                field = "Digital Content / IT"
                careers = ["Content Writer", "Technical Writer", "Web Content Specialist"]
                motivation = f"{fav} + Computer opens doors to Digital Content & IT fields."
            else:
                field = "Language & Arts"
                careers = ["Writer", "Teacher", "Journalist"]
                motivation = f"{fav} is your favourite. Many arts & social careers await!"

        elif fav == "SST":
            if "English" in top_subjects:
                field = "Law / Social Sciences"
                careers = ["Lawyer", "Researcher", "Social Worker", "Teacher"]
                motivation = f"{fav} + English is strong for Law & Social Science careers."
            elif "Computer" in top_subjects:
                field = "IT & Social Sciences"
                careers = ["Data Analyst", "Researcher", "Content Writer"]
                motivation = f"{fav} + Computer is good for IT + Social Sciences roles."
            else:
                field = "Social Studies"
                careers = ["Researcher", "Teacher", "Social Worker"]
                motivation = f"{fav} is your favourite. Focus on top subjects for Social Science careers."

        elif fav == "Chemistry":
            if "Physics" in top_subjects:
                field = "Chemical / Mechanical Engineering"
                careers = ["Chemical Engineer", "Mechanical Engineer", "Materials Scientist"]
                motivation = f"{fav} + Physics suits Engineering & Research."
            elif "Biology" in top_subjects:
                field = "Medical / Pharma Research"
                careers = ["Pharmacist", "Medical Researcher", "Biotechnologist"]
                motivation = f"{fav} + Biology is great for Medicine & Pharma Research."
            else:
                field = "Chemistry & Science"
                careers = ["Lab Technician", "Research Scientist", "Chemist"]
                motivation = f"{fav} is your favourite. Many scientific careers await!"

        elif fav == "Islamiat":
            if "English" in top_subjects:
                field = "Education / Social Studies"
                careers = ["Teacher", "Researcher", "Social Worker"]
                motivation = f"{fav} + English gives opportunities in Education & Social Studies."
            else:
                field = "Religious Studies"
                careers = ["Teacher", "Researcher", "Counselor"]
                motivation = f"{fav} is your favourite. Focus on top subjects for Religious Studies."

        # ---------------- Compare with previous percentage ----------------
        current_percentage = int(sum(valid_marks.values()) / len(valid_marks)) if valid_marks else 0

        if current_percentage >= student["previous_percentage"]:
            student["motivation"] = f"Great job! Your score improved from {student['previous_percentage']}% to {current_percentage}% 🎉"
        else:
            student["motivation"] = f"Your score decreased from {student['previous_percentage']}% to {current_percentage}%. {motivation}"

        student["field"] = field
        student["careers"] = careers

        return render(request, "myapp/suggestionresult.html", {"student": student})






















### Admin ###

import datetime
from django.contrib import messages
from django.shortcuts import render, redirect
from mypro.firebase_connection import database
from google.cloud.firestore import Query
from functools import wraps

# Admin credentials (you can change these)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


# Decorator to check if admin is logged in
def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_admin'):
            messages.error(request, "Please login as admin to access this page")
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)

    return wrapper


# Admin Login
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            request.session['is_admin'] = True
            request.session['admin_username'] = username
            messages.success(request, "Admin login successful!")
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid credentials!")
            return redirect('admin_login')

    return render(request, 'myapp/adminlogin.html')


# Admin Logout
def admin_logout(request):
    request.session.flush()
    messages.success(request, "Logged out successfully!")
    return redirect('admin_login')


# Admin Dashboard
@admin_required
def admin_dashboard(request):
    # Count registered users
    users = list(database.collection("registered_user").stream())
    total_users = len(users)

    # Count student predictions
    predictions = list(database.collection("student_predictions").stream())
    total_predictions = len(predictions)

    # Count surveys
    surveys = list(database.collection("student_survey").stream())
    total_surveys = len(surveys)

    # Count progress surveys
    progress_surveys = list(database.collection("student_progress").stream())
    total_progress = len(progress_surveys)

    # Count dropout predictions
    dropout_records = list(database.collection("dropout_Record").stream())
    total_dropout = len(dropout_records)

    # Count contact messages
    contacts = list(database.collection("Contact").stream())
    total_contacts = len(contacts)

    # Recent activities (last 5)
    recent_users = sorted(users, key=lambda x: x.to_dict().get('Created_at', datetime.datetime.min), reverse=True)[:5]
    recent_contacts = sorted(contacts, key=lambda x: x.to_dict().get('created_at', datetime.datetime.min),
                             reverse=True)[:5]

    context = {
        'total_users': total_users,
        'total_predictions': total_predictions,
        'total_surveys': total_surveys,
        'total_progress': total_progress,
        'total_dropout': total_dropout,
        'total_contacts': total_contacts,
        'recent_users': [u.to_dict() for u in recent_users],
        'recent_contacts': [c.to_dict() for c in recent_contacts],
    }

    return render(request, 'myapp/admindashboard.html', context)


# View All Registered Users
@admin_required
def admin_users(request):
    users_data = database.collection("registered_user").order_by("Created_at", direction=Query.DESCENDING).stream()
    users = []
    for user in users_data:
        user_dict = user.to_dict()
        user_dict['id'] = user.id
        users.append(user_dict)

    return render(request, 'myapp/adminusers.html', {'users': users})


# Delete User
@admin_required
def admin_delete_user(request, user_id):
    database.collection("registered_user").document(user_id).delete()
    messages.success(request, "User deleted successfully!")
    return redirect('admin_users')


# View All Student Predictions
@admin_required
def admin_predictions(request):
    predictions_data = database.collection("student_predictions").order_by("created_at",
                                                                           direction=Query.DESCENDING).stream()
    predictions = []
    for pred in predictions_data:
        pred_dict = pred.to_dict()
        pred_dict['id'] = pred.id
        predictions.append(pred_dict)

    return render(request, 'myapp/adminpredictionsdetail.html', {'predictions': predictions})


# Delete Prediction
@admin_required
def admin_delete_prediction(request, pred_id):
    database.collection("student_predictions").document(pred_id).delete()
    messages.success(request, "Prediction deleted successfully!")
    return redirect('admin_predictions')


# View All Surveys
@admin_required
def admin_surveys(request):
    surveys_data = database.collection("student_survey").order_by("created_at", direction=Query.DESCENDING).stream()
    surveys = []
    for survey in surveys_data:
        survey_dict = survey.to_dict()
        survey_dict['id'] = survey.id
        surveys.append(survey_dict)

    return render(request, 'myapp/adminsurveys.html', {'surveys': surveys})


# Delete Survey
@admin_required
def admin_delete_survey(request, survey_id):
    database.collection("student_survey").document(survey_id).delete()
    messages.success(request, "Survey deleted successfully!")
    return redirect('admin_surveys')


# View All Progress Surveys
@admin_required
def admin_progress(request):
    progress_data = database.collection("student_progress").order_by("created_at", direction=Query.DESCENDING).stream()
    progress_list = []
    for prog in progress_data:
        prog_dict = prog.to_dict()
        prog_dict['id'] = prog.id
        progress_list.append(prog_dict)

    return render(request, 'myapp/adminprogress.html', {'progress_list': progress_list})


# Delete Progress Survey
@admin_required
def admin_delete_progress(request, progress_id):
    database.collection("student_progress").document(progress_id).delete()
    messages.success(request, "Progress survey deleted successfully!")
    return redirect('admin_progress')


# View All Dropout Records
@admin_required
def admin_dropout(request):
    dropout_data = database.collection("dropout_Record").stream()
    dropout_list = []
    for drop in dropout_data:
        drop_dict = drop.to_dict()
        drop_dict['id'] = drop.id
        dropout_list.append(drop_dict)

    return render(request, 'myapp/admindropout.html', {'dropout_list': dropout_list})


# Delete Dropout Record
@admin_required
def admin_delete_dropout(request, dropout_id):
    database.collection("dropout_Record").document(dropout_id).delete()
    messages.success(request, "Dropout record deleted successfully!")
    return redirect('admin_dropout')


# View All Contact Messages
@admin_required
def admin_contacts(request):
    contacts_data = database.collection("Contact").order_by("Record_at", direction=Query.DESCENDING).stream()
    contacts = []

    print(contacts_data)
    for contact in contacts_data:
        contact_dict = contact.to_dict()
        contact_dict['id'] = contact.id
        contacts.append(contact_dict)


    return render(request, 'myapp/admincontacts.html', {'contacts': contacts})


# Delete Contact Message
@admin_required
def admin_delete_contact(request, contact_id):
    database.collection("Contact").document(contact_id).delete()
    messages.success(request, "Contact message deleted successfully!")
    return redirect('admin_contacts')


# View Prediction Details
@admin_required
def admin_prediction_detail(request, pred_id):
    pred_doc = database.collection("student_predictions").document(pred_id).get()
    if pred_doc.exists:
        prediction = pred_doc.to_dict()
        prediction['id'] = pred_doc.id
        return render(request, 'myapp/adminpredictiondetail.html', {'prediction': prediction})
    else:
        messages.error(request, "Prediction not found!")
        return redirect('admin_predictions')


@admin_required
def admin_performance(request):
    """Display all student performance records from Firebase"""
    try:
        performances_data = database.collection("student_predictions").order_by(
            "created_at", direction=Query.DESCENDING
        ).stream()

        performances = []
        for perf in performances_data:
            perf_dict = perf.to_dict()
            perf_dict['id'] = perf.id
            performances.append(perf_dict)

    except Exception as e:
        messages.error(request, f"Error fetching performance records: {str(e)}")
        performances = []

    return render(request, 'myapp/adminperformance.html', {'performances': performances})


@admin_required
def admin_delete_performance(request, perf_id):
    """Delete a performance record from Firebase"""
    try:
        database.collection("student_predictions").document(perf_id).delete()
        messages.success(request, "Performance record deleted successfully!")
    except Exception as e:
        messages.error(request, f"Error deleting record: {str(e)}")

    return redirect('admin_performance')



