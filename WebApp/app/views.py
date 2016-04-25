"""
 views.py
"""

from flask import request, session, redirect, render_template, flash, url_for
from app import app
from .sparql import data_queries as dq
from .forms import AddForm, IsoNameForm
import form_to_triple as ft

####################################################################################################
# The homepage I guess. Just renders the index html where the buttons are displayed.
####################################################################################################
@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

####################################################################################################
# For getting the AddForm when requested, and going back to the home page when the form is submitted
# successfully. Calls init_session_vars and creates an AddForm when called.
####################################################################################################
@app.route("/add", methods=["GET", "POST"])
def add():

    if request.method == "GET":
        init_session_vars()

    form = AddForm(session)

    if form.validate_on_submit():
        triple = ft.formToTriple(form)
        #q.writeToBG(triple)
        print triple
        flash("Isolate added")
        return redirect("/index")
    else:
        session["form_error"] = False

    return render_template("addIso.html", title="Add Isolate", form=form)

####################################################################################################
# Calls the query getIsoNames to retrieve, you guessed it, all the names of the isolates in the
# database. Renders the names html which just shows all the names we retrieved. Probably not useful
# and won't be included in the final app, but good for testing and seeing how everything works
# together.
####################################################################################################
@app.route("/names")
def names():

    isos = dq.getIsoNames()
    return render_template("names.html", title="Isolate Names", isos=isos)

####################################################################################################
# Renders the summaryForm when there's a GET request, displays a summary page for an isolate on a
# successful POST request. Retrieves most of the data for an isolate and displays it to the user.
####################################################################################################
@app.route("/getSummary", methods=["GET", "POST"])
def getSummary():

    form = IsoNameForm()

    if form.validate_on_submit():

        iso_title = form.iso_title.data
        return redirect(url_for("summary", iso_title=iso_title))

    return render_template("get_summary.html", title="Isolate Summary", form=form)

@app.route("/summary/<iso_title>")
def summary(iso_title):

    def popVals(my_dict):
        return {x:y for x, y in my_dict.iteritems() if y != "" and y != {}}

    iso_name = dq.getPropVal(iso_title, "hasIsolateName")

    epi_vals, lims_vals, bio_vals = [], [], []

    source = "{} {} {}".format(dq.getPropVal(iso_title, "hasLocale"),
                               dq.getPropVal(iso_title, "hasSampleSource"),
                               dq.getPropVal(iso_title, "hasSampleType"))

    epi_vals.append(source)
    epi_vals.append(dq.getLocation(iso_title))

    lims_vals.append(dq.getPropVal(iso_title, "partOfProject"))
    lims_vals.append(dq.getPropVal(iso_title, "partOfSubProject"))
    lims_vals.append(dq.getPropVal(iso_title, "hasCollectionID"))
    lims_vals.append(dq.getPropVal(iso_title, "hasLDMSid"))
    lims_vals.append(dq.getPropVal(iso_title, "hasNMLid"))

    bio_vals.append(dq.getSpecies(iso_title))

    epi_keys = ("Source", "Location")
    bio_keys = ("Species",)
    lims_keys = ("Project", "Subproject", "Collection ID", "LDMS ID", "NML ID")

    epi_data = popVals(dict(zip(epi_keys, epi_vals)))
    bio_data = popVals(dict(zip(bio_keys, bio_vals)))
    lims_data = popVals(dict(zip(lims_keys, lims_vals)))

    print bio_data

    data = {"EPI Data":epi_data, "Biological Data":bio_data, "LIMS Data":lims_data}

    data = popVals(data)

    title = "Isolate {} Summary".format(iso_name)

    return render_template("summary.html", title=title, data=data)

####################################################################################################
# Just initializes some variables that we need in the session. Used in the AddFom validators mostly.
####################################################################################################
def init_session_vars():

    session["last_animal"] = None
    session["last_sample_type"] = None
    session["form_error"] = False

"""
@app.route("/login", methods = ["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form["username"] != app.config["USERNAME"]:
            error  =  "Invalid username"
        elif request.form["password"] != app.config["PASSWORD"]:
            error = "Invalid password"
        else:
            session["logged_in"] = True
            flash("You were logged in")
            return redirect(url_for("show_entries"))
    return render_template("login.html", error = error)


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    flash("You were logged out")
    return redirect(url_for("show_entries"))
"""


