# Site Reliability Engineer Academy 
## Student: Angelica Salas 

This playbook automates the **FULL** deployment of **ALL** necessary SRE components studied at the IBM SRE Academy.

### Remarks:
- This playbook does not complete the full SRE Academy tool setup from the beginning.
- This playbook assumes the initial installation steps are completed.
- Tested locally on **Windows 10 (WSL2)** and **macOS**.

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
To run this playbook, execute the following command from the `captcha_check/ansible` directory:
`ansible-playbook -i inventory.ini sre_academy_playbook.yaml --ask-become-pass`