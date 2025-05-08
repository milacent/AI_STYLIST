from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from problems import problems

app = Flask(__name__)

question_texts = list(problems.keys())
vectorizer = TfidfVectorizer().fit(question_texts)
question_vectors = vectorizer.transform(question_texts)


@app.route('/getrec', methods=['GET'])
def get_recommendation():
    user_problem = request.args.get('data', '').strip().lower()
    if not user_problem:
        return jsonify({"error": "Укажите проблему через параметр ?data=ваша_проблема"}), 400

    # Если пользователь явно ввел "другое", сразу направляем к администратору
    if user_problem in ["другое", "не знаю", "нет похожей проблемы"]:
        response = "Ваш запрос передан администратору. Ожидайте ответа."
        return jsonify({
            "вы ввели": user_problem,
            "похожесть": 0,
            "решение": response
        })

    # Ищем наиболее похожую проблему
    user_vector = vectorizer.transform([user_problem])
    similarities = cosine_similarity(user_vector, question_vectors).flatten()
    max_similarity = max(similarities)
    best_match_index = similarities.argmax()
    best_problem = question_texts[best_match_index]

    # Если похожесть меньше порога или проблема неизвестна
    if max_similarity < 0.3:
        response = "Ваш запрос передан администратору. Ожидайте ответа."
    else:
        response = problems[best_problem]

    return jsonify({
        "вы ввели": user_problem,
        "похоже на": best_problem,
        "решение": response
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
