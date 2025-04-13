from flask import Flask, request, jsonify, redirect
from collections import defaultdict
from utils import generate_short_code, get_domain

app = Flask(__name__)

# In-memory storage
url_mapping = {}  # short_code -> original_url
url_to_code = {}  # original_url -> short_code
domain_counts = defaultdict(int)  # domain -> count


@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    """API endpoint to shorten URLs"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    original_url = data.get('url')

    if not original_url:
        return jsonify({"error": "URL is required"}), 400

    domain = get_domain(original_url)
    domain_counts[domain] += 1

    # Return existing short code if URL was already shortened
    if original_url in url_to_code:
        short_code = url_to_code[original_url]

    else:
        short_code = generate_short_code(original_url)
        url_mapping[short_code] = original_url
        url_to_code[original_url] = short_code


    return jsonify({
        "short_url": f"/api/redirect/{short_code}"  # Relative path for API consistency
    })




@app.route('/api/redirect/<short_code>', methods=['GET'])
def redirect_to_original(short_code):
    """API endpoint for redirection"""
    if short_code not in url_mapping:
        return jsonify({"error": "Short URL not found"}), 404

    return jsonify({
        "action": "redirect",
        "location": url_mapping[short_code]
    }), 302, {'Location': url_mapping[short_code]}


@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """API endpoint for metrics"""
    sorted_domains = sorted(domain_counts.items(), key=lambda item: item[1], reverse=True)[:3]
    return jsonify({"top_domains": dict(sorted_domains)})


if __name__ == '__main__':
    app.run(debug=True)