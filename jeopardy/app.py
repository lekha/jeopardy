"""Entry point for jeopardy web app."""
from sanic import Sanic
from sanic.response import text


app = Sanic("jeopardy")


@app.route("/health-check")
async def health_check(request):
    """Verify that app is able to respond incoming requests."""
    return text("Look at this healthy server go!")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, workers=1)
