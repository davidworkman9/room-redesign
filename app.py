import os
import base64
import replicate
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

STYLES = {
    "modern": "modern bathroom, clean lines, marble countertops, frameless glass shower, matte black fixtures, natural light, luxury finishes",
    "industrial": "industrial bathroom, exposed brick, concrete floors, black metal fixtures, edison bulbs, raw materials, urban loft style",
    "minimalist": "minimalist bathroom, white walls, floating vanity, walk-in shower, simple fixtures, clean design, uncluttered space",
    "coastal": "coastal bathroom, blue and white palette, light wood, beadboard, nautical accents, sea glass, airy and bright",
    "vintage": "vintage bathroom, clawfoot tub, hexagonal tile, brass fixtures, wainscoting, classic elegance, period details",
    "scandinavian": "scandinavian bathroom, light wood, white tile, warm minimalism, natural textures, hygge style, clean and cozy",
    "mediterranean": "mediterranean bathroom, terracotta tile, arched mirrors, wrought iron fixtures, warm earth tones, rustic elegance",
    "japanese": "japanese bathroom, soaking tub, natural stone, bamboo accents, zen garden influence, minimalist tranquility, warm wood tones",
}


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

    token = os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        return jsonify({"error": "REPLICATE_API_TOKEN not set"}), 500

    image_file = request.files["image"]
    image_data = base64.b64encode(image_file.read()).decode("utf-8")
    mime = image_file.content_type or "image/jpeg"
    data_uri = f"data:{mime};base64,{image_data}"

    prompt = STYLES[style]

    try:
        output = replicate.run(
            "adirik/interior-design:76604baddc85b1b4616e1c6475eca080da339c8875bd4996705440484a6eac38",
            input={
                "image": data_uri,
                "prompt": prompt,
                "guidance_scale": 15,
                "negative_prompt": "lowres, watermark, banner, logo, text, blurry, ugly, distorted",
                "num_inference_steps": 50,
            },
        )
        # output is typically a URL or list of URLs
        if isinstance(output, list):
            result_url = str(output[0])
        else:
            result_url = str(output)

        return jsonify({"url": result_url, "style": style})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
