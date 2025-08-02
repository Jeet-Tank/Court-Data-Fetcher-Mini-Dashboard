from flask import Flask ,render_template,redirect,url_for,session,Response, abort,request, flash
from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired,NumberRange
from flask_bootstrap import Bootstrap4
from case_data import case_types,years
from scraper import fetch_case_data
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer,String,DateTime,Text
import datetime,re,requests,os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key= os.environ.get("SECRET_KEY","demo_secret_key")
bootstrap_style = Bootstrap4(app)
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI","sqlite:///demo_logging.db")


# Create the extension
db = SQLAlchemy(model_class=Base)
# Initialise the app with the extension
db.init_app(app)

class QueryLog(db.Model):
    __tablename__ = "query_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    case_type: Mapped[str] = mapped_column(String[40],nullable=False)
    case_number: Mapped[int] = mapped_column(Integer,nullable=False)
    case_year: Mapped[int] = mapped_column(Integer,nullable=False)
    response_snapshot: Mapped[str] = mapped_column(Text,nullable=False)

with app.app_context():
    db.create_all()

class MyForm(FlaskForm):

    case_type = SelectField(label="Case Type: ", choices=[("","Select")]+case_types,validators=[DataRequired()])
    case_number = IntegerField(label="Case Number:",validators=[DataRequired(),NumberRange(min=0,
                                                                                           message="Please enter a valid case number")])
    year = SelectField(label="Year: ", choices=[("","Select")]+years,validators=[DataRequired()])

    submit = SubmitField(label='Submit')


@app.route("/")
def home():
    case_form = MyForm()
    filtered_data = None
    case_data = session.pop("case_data",None)
    case_number = session.pop("case_number",None)

    if case_data:
        match = re.search(r"\[(.*?)\]", case_data["case_data"][1])
        case_status = match.group(1) if match else "UNKNOWN"

        raw_parties = case_data["case_data"][2]
        parties = re.split(r"\s*vs\.?\s*", raw_parties, flags=re.IGNORECASE)

        if len(parties) == 2:
            petitioner = parties[0].strip()
            respondent = parties[1].strip()
        else:
            petitioner = raw_parties.strip()
            respondent = None

        case_dates = case_data["case_data"][3]
        next_date_match = re.search(r'NEXT DATE:\s*([\d/]+)', case_dates, flags=re.IGNORECASE)
        last_date_match = re.search(r'Last Date:\s*([\d/]+)', case_dates, flags=re.IGNORECASE)
        next_date = next_date_match.group(1) if next_date_match else None
        last_date = last_date_match.group(1) if last_date_match else None

        order_documents = case_data.get("doc_links", [])
        order_dates = case_data.get("doc_dates", [])

        filtered_data = {
            "number":case_number,
            "status":case_status,
            "petitioner":petitioner,
            "respondent":respondent,
            "next_date":next_date,
            "last_date":last_date,
            "order_documents":order_documents,
            "order_dates":order_dates
        }

    return render_template("index.html",case_form=case_form,result = filtered_data)

@app.route("/get_case",methods=["POST"])
def get_case():
    case_form = MyForm()
    if case_form.validate_on_submit():
        result= fetch_case_data(
        case_type = case_form.case_type.data,
        case_number = case_form.case_number.data,
        case_year = case_form.year.data,
        flash=flash)

        if result is None:
            flash("No case data found for the given inputs.", "warning")
            return redirect(url_for("home"))

        response_data , response_html = result
        new_log = QueryLog(
            case_type=case_form.case_type.data,
            case_number=case_form.case_number.data,
            case_year=case_form.year.data,
            response_snapshot = response_html
        )

        db.session.add(new_log)
        db.session.commit()

        session["case_data"]=response_data
        session["case_number"] = case_form.case_number.data

    else:
        for field, errors in case_form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(case_form, field).label.text}: {error}", "warning")
    return redirect(url_for("home"))


@app.route('/download')
def download():
    file_url = request.args.get('file')
    if not file_url:
        abort(400, description="No file URL provided.")

    try:
        r = requests.get(file_url, stream=True)
        r.raise_for_status()

        # Extract filename from URL
        filename = file_url.split("/")[-1] or "downloaded_file.pdf"

        return Response(
            r.iter_content(chunk_size=8192),
            headers={
                "Content-Disposition": f"attachment; filename={filename}.pdf",
                "Content-Type": r.headers.get("Content-Type", "application/octet-stream")
            }
        )
    except Exception as e:
        abort(500, description=str(e))

if __name__ == '__main__':
    app.run()