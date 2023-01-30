from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    
db=SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)



@app.route("/")
def home():
    todo_list = db.session.query(Todo).all()
    return render_template("base.html", todo_list=todo_list)

@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    new_todo = Todo(title=title, complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/update/<int:todo_id>")
def update(todo_id):
    todo = db.session.query(Todo).filter(Todo.id==todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = db.session.query(Todo).filter(Todo.id==todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('home'))



if __name__ == "__main__":
    app.app_context().push()
    db.create_all()
    app.run(debug=True)


# Consideraciones a tener en cuenta:

# 1. db.create_all() por si solo no funciona, hay que hacerlo en el contexto de la app
# por lo tanto, se debe llamar app.app_context().push() antes de db.create_all()
# 2. hay que exportar la variable de entorno "set FLASK_APP=app.py" (windows), o "export FLASK_APP=app.py" (linux)
# 3. la variable de entorno FLASK_ENV será deprecada en la proxima versión, por lo que se debe usar "set FLASK_DEBUG=1" (windows), o "export FLASK_DEBUG=1" (linux)
# 4. para ejecutar la app, se debe usar "flask run" en la terminal
# 5. los métodos PUT y DELETE no están soportados por el navegador, por lo que se debe usar un cliente como Postman para probarlos
# 6. lo ideal sería haber separado la lógica de la app y la del modelo en archivos aparte, pero por simplicidad se dejó todo en el mismo archivo


