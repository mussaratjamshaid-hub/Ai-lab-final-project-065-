from flask import Flask, request, render_template_string

app = Flask(__name__)

template = """
<!DOCTYPE html>
<html>
<head>
    <title>Predict Student Grades</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            background-color: #f0f8ff; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            padding: 20px; 
            color: #333;
        }
        h2, h3 { color: #004080; text-align: center; }
        form { 
            background: #e6f2ff; 
            padding: 20px; 
            border-radius: 10px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            max-width: 600px;
            margin: 20px auto;
        }
        input[type="text"], input[type="number"] {
            width: 95%;
            padding: 8px;
            margin-bottom: 10px;
            border: 1px solid #004080;
            border-radius: 5px;
            display: block;
        }
        button {
            background-color: #004080;
            color: white;
            padding: 10px 15px;
            margin: 5px 5px 15px 0;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover { background-color: #0066cc; }
        hr { border: 1px solid #004080; margin: 15px 0; }
        ul { list-style-type: none; padding-left: 0; }
        li { 
            background: #ffffff; 
            margin-bottom: 10px; 
            padding: 10px; 
            border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .top { color: green; font-weight: bold; background-color: #d4edda; padding: 5px 10px; border-radius: 5px; }
        .fail { color: red; font-weight: bold; background-color: #f8d7da; padding: 5px 10px; border-radius: 5px; }
        .gradeA { color: blue; font-weight: bold; background-color: #cce5ff; padding: 5px 10px; border-radius: 5px; }
        #students div {
            background: #f0f8ff;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 8px;
            border: 1px solid #b3d1ff;
        }
    </style>
    <script>
        function addStudent() {
            const container = document.getElementById("students");
            const div = document.createElement("div");
            div.innerHTML = `
                <hr>
                Roll: <input type="text" name="roll" required><br>
                Attendance (%): <input type="number" name="attendance" required><br>
                Study Time (hrs/week): <input type="number" name="study_time" required><br>
                Test Score: <input type="number" name="test_score" required><br>
            `;
            container.appendChild(div);
        }
    </script>
</head>
<body>
    <h2>Predict Student Grades</h2>
    <form method="POST">
        <div id="students">
            {% for i in range(1) %}
            <div>
                Roll: <input type="text" name="roll" required><br>
                Attendance (%): <input type="number" name="attendance" required><br>
                Study Time (hrs/week): <input type="number" name="study_time" required><br>
                Test Score: <input type="number" name="test_score" required><br>
            </div>
            {% endfor %}
        </div>
        <button type="button" onclick="addStudent()">Add New Student</button>
        <button type="submit">Predict</button>
    </form>

    {% if results %}
    <h2>Predicted Grades:</h2>
    <ul>
        {% for r in results %}
        <li class="{% if r.roll == top_student.roll %}top{% elif r.grade == 'D' %}fail{% elif r.grade == 'A' %}gradeA{% endif %}">
            Roll {{ r.roll }}: Grade {{ r.grade }} - {{ pass_fail(r.grade) }}
        </li>
        {% endfor %}
    </ul>

    <h3>Total Students Submitted: {{ total }}</h3>
    <h3>Average Grade: {{ average }}</h3>
    <h3>Top Student: Roll {{ top_student.roll }} with Grade {{ top_student.grade }}</h3>

    {% if failing_students %}
    <h3>Failing Students:</h3>
    <ul>
        {% for f in failing_students %}
        <li class="fail">Roll {{ f.roll }}: Grade {{ f.grade }}</li>
        {% endfor %}
    </ul>
    {% endif %}

    {% if gradeA_students %}
    <h3>Grade A Students:</h3>
    <ul>
        {% for a in gradeA_students %}
        <li class="gradeA">Roll {{ a.roll }}: Grade {{ a.grade }}</li>
        {% endfor %}
    </ul>
    {% endif %}
    {% endif %}
</body>
</html>
"""

# Python logic remains same
def calculate_grade(attendance, study_time, test_score):
    score = (attendance*0.2) + (study_time*0.3) + (test_score*0.5)
    if score >= 90: return 'A'
    elif score >= 75: return 'B'
    elif score >= 60: return 'C'
    else: return 'D'

def pass_fail(grade):
    return 'Pass' if grade in ['A','B','C'] else 'Fail'

def average_grade(results):
    grade_points = {'A':4,'B':3,'C':2,'D':1}
    total_points = sum(grade_points.get(r['grade'],0) for r in results)
    count = len(results)
    avg_point = total_points/count if count>0 else 0
    for grade, point in sorted(grade_points.items(), reverse=True):
        if avg_point >= point:
            return grade
    return 'N/A'

@app.route('/', methods=['GET','POST'])
def home():
    results,total,average,top_student,failing_students,gradeA_students = [],0,'N/A',{'roll':'N/A','grade':'N/A'},[],[]
    if request.method=='POST':
        rolls = request.form.getlist('roll')
        attendances = request.form.getlist('attendance')
        study_times = request.form.getlist('study_time')
        test_scores = request.form.getlist('test_score')
        for i in range(len(rolls)):
            try:
                att = float(attendances[i])
                st = float(study_times[i])
                ts = float(test_scores[i])
                grade = calculate_grade(att, st, ts)
                results.append({'roll':rolls[i],'grade':grade,'score':(att*0.2+st*0.3+ts*0.5)})
            except:
                results.append({'roll':rolls[i],'grade':'Invalid Input','score':0})
        total = len(results)
        average = average_grade(results)
        top_student = max(results,key=lambda x:x.get('score',0))
        failing_students = [r for r in results if pass_fail(r['grade'])=='Fail']
        gradeA_students = [r for r in results if r['grade']=='A']
    return render_template_string(template,
                                  results=results,
                                  total=total,
                                  average=average,
                                  top_student=top_student,
                                  failing_students=failing_students,
                                  gradeA_students=gradeA_students,
                                  pass_fail=pass_fail)

if __name__=='__main__':
    app.run(debug=True)
