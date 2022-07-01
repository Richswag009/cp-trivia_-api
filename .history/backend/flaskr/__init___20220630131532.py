import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*": {"origins": '*'}})
    """

    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def available_categories():

        groups = Category.query.order_by(Category.id).all()
        current_category = paginate_questions(request, groups)

        if len(current_category) == 0:
            abort(404)

        # return successful response
        return jsonify({
            'success': True,
            'categories':  {caty.id: caty.type for caty in groups}
        })
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

   # set pagination
    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

    # Get paginated questions
        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    @app.route('/questions')
    def all_questions():

        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        categories = Category.query.order_by(Category.id).all()

    # return error if there are no questions
        if len(current_questions) == 0:
            abort(404)

    # return successful response
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'current_categories': None,
            'categories': {caty.id: caty.type for caty in categories}
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_questions(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)
            question.delete()
            selection = Question.query.order_by(
                Question.id).all()
            current_questions = paginate_questions(
                request, selection)

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'current_total_questions': len(selection)
            })
        except Exception:
            abort(422)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():

        body = request.get_json()
        question = body.get('question')
        answer = body.get('answer')
        category = body.get('category')
        difficulty = body.get('difficulty')
        # search_question = body.get('search_value')
        try:
            if body is None:
                abort(400)
            search = body.get("searchTerm")
            if search:
                try:
                    selection = Question.query.filter(
                        Question.question.ilike('%{}%'.format(search))
                    )
                    current_questions = paginate_questions(
                        request, selection)
                    if len(current_questions) == 0:
                        return {
                            'questions': [{'question': 'Question is not Available'}],
                        }
                    return {
                        "questions": current_questions,
                        "totalQuestions": len(Question.query.all())
                    }
                except Exception as e:
                    return(e)

            if question is None:
                abort(400)

            if answer is None:
                abort(400)

            if difficulty is None:
                abort(400)

            if category is None:
                abort(400)

            else:
                try:
                    question = Question(
                        question=question, answer=answer, difficulty=difficulty, category=category)
                    question.insert()
                    selection = Question.query.order_by(Question.id).all()
                    current_questions = paginate_questions(request, selection)

                    return jsonify({
                        'success': True,
                        'new_question_id': question.id,
                        'questions': current_questions,
                        'totalQuestions': len(Question.query.all())
                    })
                except Exception as e:
                    return(e)
        except Exception as e:
            return(e)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions')
    def question_by_category(category_id):
        try:
            categories = Category.query.filter(
                Category.id == category_id).all()
            if categories is None:
                abort(404)
            category_list = []
            for category in categories:
                category_list.append(category.type)

            selection = Question.query.filter(
                Question.category == category_id).all()
            current_questions = paginate_questions(request, selection)
            return jsonify({
                'success': True,
                'totalQuestions': len(selection),
                'questions': current_questions,
                'categories': category_list[0],
                'current_category': category_id
            })
        except Exception:
            abort(404)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app