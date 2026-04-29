# Project: CaptchaCheck — SRE Vault Integrity Lab
 
**IBM Site Reliability Engineer Academy, 2025**  
**Author & Student: Angelica Salas** 
##

"What has keys but can't open locks?"

CaptchaCheck is a gamified, full-stack web application designed to demonstrate core Site Reliability Engineering (SRE) principles through the lens of a "Cyber-Spy" security clearance mission.

The project simulates a secure agent portal where users must pass through behavioral verification (Google reCAPTCHA), cryptographic riddles, and pattern decryption to access a high-security "Safe Lock" combination.

### 🚀 Key Features

* Secure Authentication Flow: Multi-stage login process including Agent ID verification, riddle-based access codes, and Google reCAPTCHA v2 integration.
* SRE Observability: Fully instrumented for monitoring. The application generates "Vault Access Traces" and live telemetry to be scraped by Prometheus and visualized in Grafana.
* Thematic UI/UX: A terminal-style "Neon-Green" interface with simulated boot sequences, scanline effects, and CSS animations that mimic a high-security vault terminal.
* Automated Deployment: Optimized for containerized environments using Docker and Kubernetes (Minikube), with automated traffic generation via CronJobs to simulate real-world user load.

### 🛠 Tech Stack

* Frontend: HTML5, CSS3 (Neon-Cyberpunk UI), Jinja2 Templating.
* Backend: Python (Flask).
* Security: Google reCAPTCHA API.
* Observability: OpenTelemetry (Traces) & Prometheus (Metrics).
* Infrastructure: Docker, Kubernetes (Manifests), and Ansible Playbooks.

### 📁 Application Flow

1. Stage 1: The Briefing (login.html) – User solves a riddle and passes the reCAPTCHA.
2. Stage 2: Credentials (login_passed.html) – A simulated terminal boot sequence verifies Agent credentials.
3. Stage 3: Integrity Challenge (final_test.html) – Pattern recognition and signal identification.
4. Stage 4: The Vault (vault.html) – Successful retrieval of the final encrypted safe combination.

Failure State (login_failed.html) – Security lockdown screen triggered by unauthorized access or failed logic.

--- 

This project automates the **FULL** deployment of **ALL** necessary SRE components studied at the IBM SRE Academy.

### Remarks:
- This playbook does not complete the full SRE Academy tool setup from the beginning.
- This playbook assumes the initial installation steps are completed.
- This playbook was tested locally on a Windows 10 machine with WSL2 Ubuntu environment. MacOs was not tested locally.
- For full SRE Academy tool installation instructions, please refer to the link below.

-------------------------------------------------------------------------

Installation Guide:

https://github.ibm.com/SRE-Academy/sre-academy-training/blob/main/installation.mdtool-installation-guide-for-sre-academy

-------------------------------------------------------------------------

### Features & Components:

**METRICS & LOGGING:**
1. **Prometheus:** Monitoring stack configured to scrape metrics from the CaptchaCheck application.
2. **cAdvisor:** Integration for container-level metrics collection via DaemonSet.
3. **Grafana:** Visualization for Prometheus metrics with pre-configured data sources.

**OBSERVABILITY & TRACES:**

4. **OpenTelemetry & Jaeger:** Collector configured to receive traces and export them to Jaeger for visualization.

**APPLICATION DEPLOYMENT:**

5. **CaptchaCheck Web App:** Deployed in the `application` namespace with Google reCAPTCHA integration.

**TRAFFIC GENERATION:**

6. **CronJob:** Automatically calls the `/login` endpoint every minute to generate observability data.

---

### Instructions: 
To start with the deployment, execute the following command from the `captcha_check/ansible` directory:
`ansible-playbook -i inventory.ini sre_academy_playbook.yaml --ask-become-pass`