import os
import base64
import requests as http_requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

STYLES = {
    "modern": "Transform this room into a modern bathroom with clean lines, marble countertops, frameless glass shower, matte black fixtures, and natural light",
    "industrial": "Transform this room into an industrial bathroom with exposed brick, concrete floors, black metal fixtures, edison bulbs, and raw materials",
    "minimalist": "Transform this room into a minimalist bathroom with white walls, floating vanity, walk-in shower, simple fixtures, and clean uncluttered design",
    "coastal": "Transform this room into a coastal bathroom with blue and white palette, light wood, beadboard, nautical accents, and airy bright feeling",
    "vintage": "Transform this room into a vintage bathroom with clawfoot tub, hexagonal tile, brass fixtures, wainscoting, and classic elegance",
    "scandinavian": "Transform this room into a scandinavian bathroom with light wood, white tile, warm minimalism, natural textures, and cozy hygge style",
    "mediterranean": "Transform this room into a mediterranean bathroom with terracotta tile, arched mirrors, wrought iron fixtures, and warm earth tones",
    "japanese": "Transform this room into a japanese bathroom with soaking tub, natural stone, bamboo accents, zen influence, and warm wood tones",
}

HF_API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-Kontext-dev"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/styles")
def styles():
    return jsonify(list(STYLES.keys()))


@app.route("/redesign", methods=["POST"])
def redesign():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    style = request.form.get("style", "modern")
    if style not in STYLES:
        return jsonify({"error": f"Unknown style: {style}"}), 400

    token = os.environ.get("HF_API_TOKEN")
    if not token:
        return jsonify({"error": "HF_API_TOKEN not set"}), 500

    image_file = request.files["image"]
    image_data = base64.b64encode(image_file.read()).decode("utf-8")

    prompt = STYLES[style]

    try:
        payload = {
            "inputs": image_data,
            "parameters": {
                "prompt": prompt,
                "guidance_scale": 7.5,
                "num_inference_steps": 28,
            },
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        resp = http_requests.post(HF_API_URL, json=payload, headers=headers, timeout=120)

        if resp.status_code != 200:
            error_msg = resp.text
            try:
                error_msg = resp.json().get("error", resp.text)
            except Exception:
                pass
            return jsonify({"error": f"API error ({resp.status_code}): {error_msg}"}), 500

        # Response is raw image bytes - convert to base64 data URI
        result_b64 = base64.b64encode(resp.content).decode("utf-8")
        result_url = f"data:image/png;base64,{result_b64}"

        return jsonify({"url": result_url, "style": style})

    except http_requests.Timeout:
        return jsonify({"error": "Request timed out. The model may be loading - try again in a minute."}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
