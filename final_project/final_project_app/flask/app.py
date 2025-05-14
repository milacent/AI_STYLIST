from flask import Flask, request, render_template_string, redirect
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from problems import problems

app = Flask(__name__)

question_texts = list(problems.keys())
vectorizer = TfidfVectorizer().fit(question_texts)
question_vectors = vectorizer.transform(question_texts)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Чат-бот поддержки</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
            background-color: #161616; /* Dark background */
            color: #fff; /* White text */
        }

        h1 {
            color: #fff; /* White text */
        }

        input[type="text"] {
            width: 400px;
            padding: 10px;
            border: 1px solid #4a90e2; /* Soft blue border */
            border-radius: 5px;
            background-color: #2a2a2a; /* Dark input background */
            color: #fff; /* White text */
            font-size: 16px;
        }

        button[type="submit"] {
            background-color: #4a90e2; /* Soft blue background */
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }

        button[type="submit"]:hover {
            background-color: #93c416; /* Muted green on hover */
        }

        .solution-block {
            margin-top: 30px;
            color: #93c416; /* Muted green text */
            font-weight: bold;
            background-color: #1f1f1f; /* Slightly lighter dark background */
            padding: 15px;
            border-radius: 5px;
        }

        .problem-item {
            margin: 10px 0;
            color: #aaa; /* Light gray text */
        }

        .problem-button {
            margin-left: 10px;
            background-color: #4a90e2; /* Soft blue background */
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
        }

        .problem-button:hover {
            background-color: #93c416; /* Muted green on hover */
        }

        hr {
            border: 0;
            height: 1px;
            background: #4a90e2; /* Soft blue line */
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <h1>Опишите вашу проблему</h1>
    <form method="get" action="/getrec">
        <input type="text" name="data" placeholder="Например: не работает кнопка оплаты" required style="width: 400px;">
        <button type="submit">Отправить</button>
    </form>

    {% if result %}
        <div class="solution-block">
            <h2>Решение:</h2>
            <p>{{ result }}</p>
        </div>
    {% endif %}

    {% if user_input %}
        <hr>
        <div class="problem-actions">
            <h2>Или выберите проблему из списка:</h2>
            <form method="get" action="/getrec">
                {% for prob in problems %}
                    <div class="problem-item">
                        {{ prob }}
                        <button class="problem-button" type="submit" name="data" value="{{ prob }}">Показать решение</button>
                    </div>
                {% endfor %}
            </form>
        </div>
    {% endif %}
</body>
</html>
"""

@app.route('/getrec', methods=['GET'])
def get_recommendation():
    user_problem = request.args.get('data', '').strip().lower()
    if not user_problem:
        return render_template_string(HTML_TEMPLATE)

    if user_problem in ["другое", "не знаю", "нет похожей проблемы"]:
        return render_template_string(HTML_TEMPLATE,
                                      result="Ваш запрос передан администратору. Ожидайте ответа.",
                                      user_input=user_problem,
                                      problems=question_texts)

    user_vector = vectorizer.transform([user_problem])
    similarities = cosine_similarity(user_vector, question_vectors).flatten()
    max_similarity = max(similarities)
    best_match_index = similarities.argmax()
    best_problem = question_texts[best_match_index]

    if max_similarity < 0.3:
        result = "Ваш запрос передан администратору. Ожидайте ответа."
        return render_template_string(HTML_TEMPLATE,
                                      result=result,
                                      user_input=user_problem,
                                      problems=question_texts)
    else:
        result = problems[best_problem]

    return render_template_string(HTML_TEMPLATE,
                                  result=result,
                                  user_input=user_problem,
                                  problems=question_texts)


@app.route('/')
def home():
    return redirect('/getrec')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)