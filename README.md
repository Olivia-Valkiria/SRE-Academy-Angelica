 # Site Reliability Engineer Academy 

## Student: Angelica Salas 

This playbook automates the FULL deployment of ALL necessary SRE components studied at the IBM SRE Academy.

 Remarks:
   - This playbook does not complete the full SRE Academy tool setup from the beginning.
   - This playbook assumes the initial installation steps are completed.
   - This playbook was tested locally on a Windows 10 machine with WSL2 Ubuntu environment. 
      - MacOs was not tested but should work similarly.
   - For full SRE Academy tool installation instructions, please refer to the link below.

 At the end of the playbook execution, it provides URLs to access, reducing toil:
    -  Docker Hub registry for CaptchaCheck application image`
    -  Minikube dashboard to monitor cluster resources
    -  Prometheus UI
    -  Grafana UI
    -  Jaeger UI 
    -  CaptchaCheck Web application  
 
 -------------------------------------------------------------------------

 Installation Guide: 
 https://github.ibm.com/SRE-Academy/sre-academy-training/blob/main/installation.mdtool-installation-guide-for-sre-academy

 -------------------------------------------------------------------------

 ## Playbook features:
   - Detects the operating system (Linux or macOS) and installs required dependencies accordingly 
   - Deployemnt of Minikube (local kubernetes) with dynamic driver selection (Docker or Podman)
   - Deploys Kubernetes manifests for all the following SRE components:

_ _  METRICS & LOGGING: _ _
    
        1. Prometheus monitoring stack. 
         - Prometheus is configured to scrape metrics from the CaptchaCheck application.
         - Prometheus runs as a pod in the 'monitoring' namespace.
         - Prometheus service is exposed via a NodePort service for local access.
         - Pre-configured Prometheus alerting rules for monitoring application health and performance.

       2.cAdvisor integration with Prometheus for container-level metrics collection.
          - cAdvisor to collect container-level metrics for Prometheus scraping and display them in Grafana dashboards
          - cAdvisor runs as a standalone pod, deployed via a DaemonSet to monitor all nodes. 
          - RBAC configuration to allow Prometheus to access cAdvisor metrics across namespaces.

       3. Grafana to visualize metrics from Prometheus (dashboards can be added manually in Grafana UI)
         - Grafana runs as a pod in the 'monitoring' namespace.
         - Grafana service is exposed via a NodePort service for local access.
         - Pre-configured Grafana data source to connect to Prometheus.
         - Sample Grafana dashboards for visualizing CaptchaCheck application metrics, like request rates, error rates, and latency.
        
_ _ OBSERVABILITY & TRACES: _ _     

       4. OpenTelemetry Collector for trace collection & Jaeger for trace visualization
         - OpenTelemetry Collector is configured to receive traces from the CaptchaCheck application and export them to Jaeger.
         - Jaeger runs as a pod in the 'opentelemetry' namespace.
         - Jaeger service is exposed via a NodePort service for local access.
         - Pre-configured Jaeger UI to visualize traces from the CaptchaCheck application. 
         - OpenTelemetry Collector is deployed with a configuration that includes receivers, processors, and exporters suitable for the CaptchaCheck application.
         - OpenTelemetry Collector configuration file (otel-collector-config.yaml) includes the `spanmetrics` processor.
           - This processor converts trace spans into Prometheus-style metrics, which are then scraped by Prometheus.
           - This integration allows for enhanced observability by correlating trace data with metrics in Prometheus and Grafana.

_ _ APPLICATION DEPLOYMENT: _ _

       5. CaptchaCheck web application deployment and service exposure.
         - Google reCAPTCHA integrated login page to demonstrate CAPTCHA functionality.
         - To integrate with reCAPTCHA, domain had to be set to "localhost" in the Google reCAPTCHA admin console.
         - Keys were generated for "localhost" domain and added to the application code.  
         - The CaptchaCheck application is deployed in the 'application' namespace.
         - The application service is exposed via a NodePort service for local access.
         - The application is instrumented with OpenTelemetry SDK to send traces to the OpenTelemetry Collector.
         - The application exposes Prometheus metrics endpoint for scraping.
      
_ _ JOB TO GENERATE TRAFFIC & METRICS: _ _

       6. A CronJob that calls the /login endpoint of the CaptchaCheck application every minute to generate traffic and metrics for monitoring and observability demonstration. 


 -------------------------------------------------------------------------
 Instructions: 

 To run this playbook, run the following command from the 'captcha_check/ansible' directory:

      ansible-playbook -i inventory.ini sre_academy_playbook.yaml --ask-become-pass
 -------------------------------------------------------------------------