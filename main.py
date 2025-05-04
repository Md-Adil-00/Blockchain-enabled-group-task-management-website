from flask import Flask, request, jsonify, render_template
import hashlib
import json
from time import time

app = Flask(__name__, static_folder="static", template_folder="templates")

class Block:
    def __init__(self, index, previous_hash, timestamp, task, hash, completed=False):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.task = task
        self.hash = hash
        self.completed = completed

    def __repr__(self):
        return json.dumps(self.__dict__, indent=4)

class Blockchain:
    def __init__(self):
        self.chain = [] 

    def add_task(self, task):
        previous_hash = self.chain[-1].hash if self.chain else "0"
        index = len(self.chain)
        timestamp = time()
        hash = self.calculate_hash(index, previous_hash, timestamp, task)
        new_block = Block(index, previous_hash, timestamp, task, hash, completed=False)
        self.chain.append(new_block)
        return new_block

    def mark_task_complete(self, index):
        if 0 <= index < len(self.chain):
            self.chain[index].completed = True
            return self.chain[index]
        return None

    def calculate_hash(self, index, previous_hash, timestamp, task):
        value = f"{index}{previous_hash}{timestamp}{task}".encode()
        return hashlib.sha256(value).hexdigest()

    def get_chain(self):
        return [block.__dict__ for block in self.chain] if self.chain else []

blockchain = Blockchain()

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(blockchain.get_chain()), 200

@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    if not data or 'task' not in data:
        return jsonify({"message": "Task is required"}), 400

    task = data['task']
    new_block = blockchain.add_task(task)
    return jsonify(new_block.__dict__), 201

@app.route('/tasks/<int:index>', methods=['PUT'])
def update_task(index):
    updated_task = blockchain.mark_task_complete(index)
    if updated_task:
        return jsonify(updated_task.__dict__), 200
    return jsonify({"message": "Task not found"}), 404

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/log')
def task_log():
    return render_template('log.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)
