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
        body { font-family: Arial, sans-serif; padding: 20px; }
        .problem-item { margin: 10px 0; }
        .problem-button { margin-left: 10px; }
        .solution-block { margin-top: 30px; color: green; font-weight: bold; }
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