# ------------------------------------------------------------
# captcha_check/app.py - Flask application with login + Google reCAPTCHA verification and OpenTelemetry tracing
# ------------------------------------------------------------
# Features:
#  - Hardened Flask application
#   - Secure password hashing
#   - Strong session protection
#   - Login / CAPTCHA bypass prevention
#   - POST-only logout
#   - CSRF protection
#   - OpenTelemetry tracing 
#        - Multi-layered function calls with random delays and error simulation
# ------------------------------------------------------------

# Import necessary libraries for runtime functionality
from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
import os
import random
import time
import json
from dotenv import load_dotenv
from functools import wraps
from datetime import timedelta

# Password security
from werkzeug.security import check_password_hash

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# ------------------------------------------------------------
# OpenTelemetry auto-instrumentation (safe & idempotent)
# ------------------------------------------------------------

# NOTE: instrument() is idempotent and safe to call unconditionally
RequestsInstrumentor().instrument()


# ---------------- Prometheus (metrics) -----------------------
from prometheus_client import Counter, Histogram
from prometheus_flask_exporter import PrometheusMetrics


# ------------------------------------------------------------
# Load environment variables
# ------------------------------------------------------------
load_dotenv()

# ------------------------------------------------------------
# Flask App Initialization
# ------------------------------------------------------------

app = Flask(__name__) # Initialize Flask app
app.secret_key = os.getenv("FLASK_SECRET_KEY") # Set secret key for session management

load_dotenv() # Load environment variables from .env file (confidential keys are stored here, and not in the codebase nor exposed publicly)

# ------------------------------------------------------------
# Secure session configuration
# ------------------------------------------------------------
app.config.update(
    SESSION_COOKIE_HTTPONLY=True, # Prevent JavaScript access to session cookie
    SESSION_COOKIE_SECURE=False,   # ⚠️ MUST be False for local development over HTTP 
    SESSION_COOKIE_SAMESITE="Lax", # Prevent CSRF
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=5)  # Session timeout after 5 minutes of inactivity
)

# ------------------------------------------------------------
# OpenTelemetry Setup (tracing)
# ------------------------------------------------------------

# Define resource attributes for the service
resource = Resource.create({
    "service.name": "captcha-check",
    "service.namespace": "application",
    "service.version": os.getenv("APP_VERSION", "1.0.0"),
    "deployment.environment": os.getenv("DEPLOY_ENV", "dev"),
})

provider = TracerProvider(resource=resource) # Initialize tracer provider with resource attributes

# Configure OTLP exporter to send traces to the OpenTelemetry Collector
span_processor = BatchSpanProcessor(
    OTLPSpanExporter(
        endpoint="otel-collector-service.opentelemetry.svc.cluster.local:4317",
        insecure=True,
    )
)
# Add the span processor to the tracer provider
provider.add_span_processor(span_processor)
trace.set_tracer_provider(provider)

# Create a tracer for this module
tracer = trace.get_tracer(__name__)

# ------------------------------------------------------------
# Flask instrumentation
# ------------------------------------------------------------

# REASON: FlaskInstrumentor instrumentation is idempotent
FlaskInstrumentor().instrument_app(app)

# ------------------------------------------------------------
# Prometheus metrics (/metrics endpoint added automatically) to expose metrics for scraping
# ------------------------------------------------------------
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version=os.getenv("APP_VERSION", "1.0.0"))

# Custom counters
login_attempts_total = Counter(
    "login_attempts_total",
    "Total login form submissions",
    ["service", "country"]
)
login_success_total = Counter(
    "login_success_total",
    "Total successful logins",
    ["service", "country"]
)
login_failures_total = Counter(
    "login_failures_total",
    "Total failed logins",
    ["service", "country", "reason"]
)
captcha_challenges_total = Counter(
    "captcha_challenges_total",
    "Total CAPTCHA challenges",
    ["service"]
)
captcha_success_total = Counter(
    "captcha_success_total",
    "Total CAPTCHA passes",
    ["service"]
)
captcha_failures_total = Counter(
    "captcha_failures_total",
    "Total CAPTCHA failures",
    ["service", "error_code"]
)

# Histograms
login_latency_seconds = Histogram(
    "login_latency_seconds",
    "Server-side login processing latency in seconds",
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)
captcha_latency_seconds = Histogram(
    "captcha_latency_seconds",
    "End-to-end CAPTCHA check latency in seconds (server-side)",
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)
recaptcha_verify_latency_seconds = Histogram(
    "recaptcha_verify_latency_seconds",
    "Outbound latency to Google's siteverify endpoint",
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)

def _prom_exemplar_from_current_span():
    span_ctx = trace.get_current_span().get_span_context()
    if span_ctx and span_ctx.is_valid and span_ctx.trace_flags.sampled:
        from opentelemetry.trace import format_trace_id, format_span_id
        return {
            "trace_id": format_trace_id(span_ctx.trace_id),
            "span_id": format_span_id(span_ctx.span_id),
        }
    return None

# ------------------------------------------------------------
# Google reCAPTCHA configuration
# ------------------------------------------------------------
RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY")
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")

# ------------------------------------------------------------
# User database
# ------------------------------------------------------------
USER_DB = json.loads(os.getenv("USER_DB", "{}"))

# ------------------------------------------------------------
# Authentication decorator
# ------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get("user")
        captcha_ok = session.get("captcha_verified")

        if not user or captcha_ok is not True:
            flash("Authentication required.", "danger")  # >>> CHANGE: Ensure flash before redirect
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function   

# ------------------------------------------------------------
# Helper functions (foo → goo → zoo)
# ------------------------------------------------------------
def zoo(): 
    with tracer.start_as_current_span("zoo") as span:
        delay = random.uniform(0.5, 2.0)
        span.set_attribute("delay.seconds", delay)
        time.sleep(delay)
        return f"Entry to the secure vault network completed in {delay:.2f}s"

def goo(raise_error=False):
    with tracer.start_as_current_span("goo") as span:
        try:
            if raise_error:
                raise ValueError("Security lockout: 5 failed login attempts. Event traced in observability system.")
            result = zoo()
            span.add_event("zoo_called")
            return result
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise

def foo():
    with tracer.start_as_current_span("foo") as span:
        result = goo()
        span.add_event("goo_called")
        return f"Credentials verified → {result}"

# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------
MAX_LOGIN_ATTEMPTS = 5
FINAL_ATTEMPT_LIMIT = 5

# ------------------------------------------------------------
# Session & Security helpers
# ------------------------------------------------------------
def init_security_counters():
    session.setdefault("failed_attempts", 0)
    session.setdefault("final_attempts", 0)
    session.setdefault("vault_access", False)

# ------------------------------------------------------------
# Flask Routes
# ------------------------------------------------------------
@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    init_security_counters()

    if request.method == "POST":
        service = "captcha-check"
        country = request.headers.get("Costa Rica", "unknown")

        login_attempts_total.labels(service=service, country=country).inc(
            exemplar=_prom_exemplar_from_current_span()
        )

        start = time.perf_counter()
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        captcha  = request.form.get("g-recaptcha-response")

        failed = False
        captcha_ok = True
        creds_ok = True

        # ---------------- CAPTCHA ----------------
        captcha_start = time.perf_counter()
        if not captcha:
            captcha_ok = False
            failed = True
            login_failures_total.labels(
                service=service, country=country, reason="missing_captcha"
            ).inc(exemplar=_prom_exemplar_from_current_span())
        else:
            try:
                c_start = time.perf_counter()
                verify_resp = requests.post(
                    "https://www.google.com/recaptcha/api/siteverify",
                    data={
                        "secret": RECAPTCHA_SECRET_KEY,
                        "response": captcha
                    },
                    timeout=5,
                )
                verify_json = verify_resp.json()
            finally:
                recaptcha_verify_latency_seconds.observe(
                    time.perf_counter() - c_start,
                    exemplar=_prom_exemplar_from_current_span()
                )

            captcha_challenges_total.labels(service=service).inc(
                exemplar=_prom_exemplar_from_current_span()
            )

            if not verify_json.get("success"):
                captcha_ok = False
                failed = True
                captcha_failures_total.labels(
                    service=service,
                    error_code=(verify_json.get("error-codes") or ["unknown"])[0]
                ).inc(exemplar=_prom_exemplar_from_current_span())
                login_failures_total.labels(
                    service=service, country=country, reason="captcha_failed"
                ).inc(exemplar=_prom_exemplar_from_current_span())
            else:
                captcha_success_total.labels(service=service).inc(
                    exemplar=_prom_exemplar_from_current_span()
                )

        captcha_latency_seconds.observe(
            time.perf_counter() - captcha_start,
            exemplar=_prom_exemplar_from_current_span()
        )

        # ---------------- CREDENTIALS ----------------
        stored = USER_DB.get(username)
        if not stored or not check_password_hash(stored, password):
            creds_ok = False
            failed = True
            login_failures_total.labels(
                service=service, country=country, reason="invalid_credentials"
            ).inc(exemplar=_prom_exemplar_from_current_span())

        # ---------------- FAILURE COUNT ----------------
        if failed:
            session["failed_attempts"] += 1

            # Flash BEFORE redirect (single redirect, reliable)
            flash(
                f"Failed login attempt {session['failed_attempts']}/{MAX_LOGIN_ATTEMPTS}",
                "danger"
            )

        # ---------------- LOCKOUT ----------------
        if session["failed_attempts"] >= MAX_LOGIN_ATTEMPTS:
            try:
                goo(raise_error=True)
            except Exception as e:
                session["lockout_reason"] = str(e)
                login_latency_seconds.observe(
                    time.perf_counter() - start,
                    exemplar=_prom_exemplar_from_current_span()
                )
                return redirect(url_for("login_failed"))

        # ---------------- SUCCESS ----------------
        if captcha_ok and creds_ok:
            session.clear()
            session.permanent = True
            session["user"] = username
            session["captcha_verified"] = True
            session["failed_attempts"] = 0

            login_success_total.labels(
                service=service, country=country
            ).inc(exemplar=_prom_exemplar_from_current_span())

            login_latency_seconds.observe(
                time.perf_counter() - start,
                exemplar=_prom_exemplar_from_current_span()
            )

            return redirect(url_for("login_passed"))

        # Redirect once, after flashing
        return redirect(url_for("login"))

    # Expose counters to template
    return render_template(
        "login.html",
        site_key=RECAPTCHA_SITE_KEY,
        failed_attempts=session.get("failed_attempts", 0),
        max_attempts=MAX_LOGIN_ATTEMPTS
    )


# Login Passed Route
@app.route("/login_passed")
@login_required
def login_passed():
    operation = foo()
    return render_template("login_passed.html", user=session["user"], operation=operation)

# Login Failed Route
@app.route("/login_failed")
def login_failed():
    # No flashing or redirect chaining here
    lockout_reason = session.get(
        "lockout_reason",
        "Security systems locked due to repeated failures"
    )
    return render_template("login_failed.html", operation=lockout_reason)


# Run Flask App
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)