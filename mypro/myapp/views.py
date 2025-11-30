import datetime

from google.cloud.firestore import Query
from django.contrib import messages
from django.shortcuts import render, redirect
from mypro.firebase_connection import database
firebase_key ="AIzaSyCZAFn21FZT4zh5qyN18_KuUH_hdSTg7Ow"
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
        responses = {f'q{i}': request.POST.get(f'q{i}', "") for i in range(1, 13)}

        responses['q13'] = "Analytical & Leader"
        responses['q14'] = "Kinesthetic & Reading"
        responses['q15'] = "Focused & Self-motivated"

        paragraph = generate_paragraph(responses)

        # FINAL VALUES — NO ANALYSIS
        quote = "“The successful warrior is the average man, with laser-like focus.” – Bruce Lee"
        score = 75

        return render(request, 'myapp/survey_result.html', {
            'paragraph': paragraph,
            'quote': quote,
            'score': score,
        })

    return render(request, 'myapp/survey_form.html')






from django.shortcuts import render
import pandas as pd
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "student_model.pkl")
model = joblib.load(MODEL_PATH)

FIELD_SPECIALIZATION = {
    "Engineering": ["Software Engineer", "AI Specialist", "Robotics Engineer", "Data Scientist", "Electrical Engineer"],
    "Medical": ["Neurologist", "Gynologist", "Orthologist", "Cardiologist", "Surgeon"],
    "Arts": ["Graphic Designer", "Animator", "Photographer", "Fashion Designer", "Musician"],
    "SocialScience": ["Teacher", "Lawyer", "Counselor", "Political Analyst", "Sociologist"]
}

def StudentPerformancePrediction(request):
    suggestion = None

    if request.method == "POST":
        # Collect form data
        form_data = {k: request.POST.get(k, 0) for k in [
            "first_name","last_name","gender","age","class","previous_percentage",
            "study_hours","math_marks","english_marks","science_marks","urdu_marks",
            "biology_marks","computer_marks","arts_marks","interest","strength_subject","weak_subject"
        ]}

        # Convert numeric safely
        numeric_cols = ["age","previous_percentage","study_hours","math_marks","english_marks",
                        "science_marks","urdu_marks","biology_marks","computer_marks","arts_marks"]
        for col in numeric_cols:
            form_data[col] = float(form_data[col]) if str(form_data[col]).replace(".", "", 1).isdigit() else 0

        # Create DataFrame for prediction
        input_df = pd.DataFrame([form_data])

        # Predict score
        predicted_score = model.predict(input_df)[0]

        # Map interest to field
        interest_map = {
            "Engineering": "Engineering",
            "Medical": "Medical",
            "Arts": "Arts",
            "SocialScience": "SocialScience"
        }
        top_field = interest_map.get(form_data["interest"], form_data["interest"])

        # Determine top 3 specializations based on marks
        if top_field == "Medical":
            sub_scores = {
                "Neurologist": input_df["science_marks"].values[0]*0.4 + input_df["biology_marks"].values[0]*0.6,
                "Gynologist": input_df["biology_marks"].values[0]*0.7 + input_df["science_marks"].values[0]*0.3,
                "Orthologist": input_df["science_marks"].values[0]*0.5 + input_df["biology_marks"].values[0]*0.5,
                "Cardiologist": input_df["biology_marks"].values[0]*0.6 + input_df["science_marks"].values[0]*0.4,
                "Surgeon": input_df["biology_marks"].values[0]*0.5 + input_df["science_marks"].values[0]*0.5
            }
            top_specializations = sorted(sub_scores, key=sub_scores.get, reverse=True)[:3]

        elif top_field == "Engineering":
            sub_scores = {
                "Software Engineer": input_df["computer_marks"].values[0]*0.7 + input_df["math_marks"].values[0]*0.3,
                "AI Specialist": input_df["computer_marks"].values[0]*0.6 + input_df["math_marks"].values[0]*0.4,
                "Robotics Engineer": input_df["computer_marks"].values[0]*0.5 + input_df["math_marks"].values[0]*0.5,
                "Data Scientist": input_df["math_marks"].values[0]*0.6 + input_df["computer_marks"].values[0]*0.4,
                "Electrical Engineer": input_df["math_marks"].values[0]*0.7 + input_df["science_marks"].values[0]*0.3
            }
            top_specializations = sorted(sub_scores, key=sub_scores.get, reverse=True)[:3]
        else:
            top_specializations = FIELD_SPECIALIZATION.get(top_field, [])[:3]

        # Calculate current percentage
        subjects = ["math_marks","english_marks","science_marks","urdu_marks",
                    "biology_marks","computer_marks","arts_marks"]
        total_marks = sum([form_data[sub] for sub in subjects])
        max_total = len(subjects) * 100  # all subjects out of 100
        current_percentage = (total_marks / max_total) * 100

        # Improvement feedback
        prev = form_data["previous_percentage"]
        if current_percentage < prev:
            improvement_feedback = f"Your score decreased from {prev:.2f}% to {current_percentage:.2f}%. Try to study more and stay focused!"
        else:
            improvement_feedback = f"Great job! Your score improved from {prev:.2f}% to {current_percentage:.2f}%. Keep up the hard work!"

        # Prepare suggestion
        suggestion = {
            "first_name": form_data["first_name"].capitalize(),
            "last_name": form_data["last_name"].capitalize(),
            "gender": form_data["gender"],
            "age": int(form_data["age"]),
            "class": int(form_data["class"]),
            "predicted_score": round(predicted_score, 2),
            "current_percentage": round(current_percentage, 2),
            "strength_subject": form_data["strength_subject"].capitalize(),
            "top_field": top_field,
            "top_specializations": top_specializations,
            "improvement_feedback": improvement_feedback
        }

    return render(request, "myapp/studentprediction.html", {"suggestion": suggestion})











import os
import pandas as pd
from django.shortcuts import render
from django.conf import settings

# CSV path inside your app (optional, if you want to use dataset later)
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

    # Focus scoring
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

    # Study method
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

    # Problem solving
    problem = responses.get('q4')
    if problem in ["Try by myself", "Practice problems"]:
        lines.append("You solve problems independently, strengthening your critical thinking skills.")
        trait_scores['problem'] = ('problem_independent', 3)
    else:
        lines.append("You ask for help when needed, which shows you know how to collaborate effectively.")
        trait_scores['problem'] = ('problem_help', 2)

    # Motivation
    motivation_map = {"Very motivated": 3, "Motivated": 2, "Neutral": 1, "Less motivated": 0}
    score_motivation = motivation_map.get(responses.get('q7'), 1)
    if score_motivation >= 2:
        lines.append("You are highly motivated and committed to achieving your goals.")
        trait_scores['motivation'] = ('motivation_high', score_motivation)
    else:
        lines.append("You have moderate motivation; small daily goals can help you improve steadily.")
        trait_scores['motivation'] = ('motivation_medium', score_motivation)

    # Personality / Learning / Behavior
    personality = f"You are {responses.get('q13', 'analytical & leader')}."
    learning = f"Your preferred learning style is {responses.get('q14', 'kinesthetic & reading')}."
    study_behavior = f"Your study behavior can be described as {responses.get('q15', 'focused & self-motivated')}."
    lines.extend([personality, learning, study_behavior])

    paragraph = " ".join(lines)

    # Determine dominant trait (highest score)
    dominant_trait = max(trait_scores.values(), key=lambda x: x[1])[0]
    quote = quotes_mapping.get(dominant_trait, "“Believe you can and you're halfway there.” – Theodore Roosevelt")

    # Calculate overall progress percentage
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
        responses[
            'q15'] = "Your study habits reflect your dedication, and with consistent effort, you can achieve even more."

        paragraph, quote, progress, trait_scores = generate_paragraph(responses)

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