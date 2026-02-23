import os
import base64
import tempfile
from flask import Flask, render_template, request, jsonify
from gradio_client import Client, handle_file

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

GRADIO_SPACE = "Manjushri/Instruct-Pix-2-Pix"


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

    image_file = request.files["image"]
    image_bytes = image_file.read()

    prompt = STYLES[style]

    try:
        # Save uploaded image to temp file for gradio_client
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name

        client = Client(GRADIO_SPACE)
        result_path = client.predict(
            source_img=handle_file(tmp_path),
            instructions=prompt,
            guide=7.5,
            steps=20,
            seed=42,
            api_name="/predict",
        )

        # Clean up temp file
        os.unlink(tmp_path)

        # Read result image and convert to base64 data URI
        with open(result_path, "rb") as f:
            result_bytes = f.read()

        result_b64 = base64.b64encode(result_bytes).decode("utf-8")
        result_url = f"data:image/webp;base64,{result_b64}"

        return jsonify({"url": result_url, "style": style})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
