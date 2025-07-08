import os
from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd

FILE = 'tasks.xlsx'
if not os.path.exists(FILE):
    df = pd.DataFrame([{'id': 1, 'task': 'Пример задачи', 'status': 'в работе', 'deadline': '2025-07-01'}])
    df.to_excel(FILE, index=False)

app = Flask(__name__)
app.secret_key = 'supersecretkey' 

def load_tasks():
    return pd.read_excel(FILE)

def save_tasks(df):
    df.to_excel(FILE, index=False)

@app.route('/')
def index():
    df = load_tasks()
    return render_template('index.html', tasks=df.to_dict(orient='records'))

@app.route('/add', methods=['POST'])
def add():
    df = load_tasks()
    task = request.form.get('task', '').strip()
    status = request.form.get('status', 'в работе').strip()
    deadline = request.form.get('deadline', '').strip()
    if not task:
        flash('Поле задачи не может быть пустым!')
        return redirect(url_for('index'))
    new_id = int(df['id'].max()) + 1 if not df.empty else 1
    new_row = pd.DataFrame([{'id': new_id, 'task': task, 'status': status, 'deadline': deadline}])
    df = pd.concat([df, new_row], ignore_index=True)
    save_tasks(df)
    flash('Задача добавлена!')
    return redirect(url_for('index'))

@app.route('/edit/<int:task_id>', methods=['POST'])
def edit(task_id):
    df = load_tasks()
    idx = df.index[df['id'] == task_id]
    if not idx.empty:
        i = idx[0]
        task = request.form.get('task', '').strip()
        status = request.form.get('status', '').strip()
        deadline = request.form.get('deadline', '').strip()
        if not task:
            flash('Поле задачи не может быть пустым!')
            return redirect(url_for('index'))
        df.at[i, 'task'] = task
        df.at[i, 'status'] = status
        df.at[i, 'deadline'] = deadline
        save_tasks(df)
        flash('Задача обновлена!')
    else:
        flash('Задача не найдена!')
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete(task_id):
    df = load_tasks()
    if task_id in df['id'].values:
        df = df[df['id'] != task_id]
        save_tasks(df)
        flash('Задача удалена!')
    else:
        flash('Задача не найдена!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)