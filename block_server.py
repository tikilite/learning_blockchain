from textwrap import dedent
from flask import Flask, jsonify, request
from uuid import uuid4
import blockchain


# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
mychain = blockchain.Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    # Run the proof of work algorithm to get the next proof
    last_block = mychain.last_block
    last_proof = last_block['proof']
    proof = mychain.proof_of_work(last_proof)

    # Give a reward for finding the proof
    # The sender is '0' to signify that this node has mined a coin
    mychain.new_transaction(sender='0', recipient=node_identifier, amount=1)

    # Forge a new Block by adding it to the chain
    previous_hash = mychain.hash(last_block)
    block = mychain.new_block(proof, previous_hash)

    response ={
        'message': 'New Block forged',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }

    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = mychain.new_transaction(values['sender'], values['recipient'], values['amount'])
    message = 'Transaction will be added to Block', str(index)

    response = {'message': message}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': mychain.chain,
        'length': len(mychain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
  
