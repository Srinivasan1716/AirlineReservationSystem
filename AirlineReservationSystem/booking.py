from flask import render_template, request

def register_routes(app):
    @app.route("/booking")
    def booking():
        destination = request.args.get("destination", "")
        return render_template("booking.html", destination=destination)