from flask import Flask, jsonify
import os
import sys


from groupsGenerator import extract_text_from_pdf

app = Flask(__name__)

@app.route('/analyze-file', methods=['GET'])
def analyze_file():
    try:
        pdf_text = extract_text_from_pdf()
        chunk = pdf_text[:4000]  

        from groupsGenerator import response

        # Return the JSON result
        return jsonify({"result": response['choices'][0]['message']['content']})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)