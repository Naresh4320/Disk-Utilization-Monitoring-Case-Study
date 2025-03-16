
## AWS Cross-Account Disk Utilization Monitoring Solution

### Overview
This solution provides a comprehensive approach to monitoring disk utilization across multiple AWS accounts. It leverages AWS native services to collect, aggregate, visualize, and respond to disk metrics from EC2 instances across three separate AWS accounts.

### Core Components

**1. Data Collection**

*   CloudWatch Agent: Deployed on all EC2 instances using Systems Manager to collect disk utilization metrics.   
*   CloudWatch Metrics: Stores per-account metrics
*   Systems Manager: Manages agent deployment and configuration

**2. Cross-Account Access**

*   IAM Roles: Each source account has a dedicated IAM role that allows the monitoring account to access its CloudWatch metrics
*   Security: Role-based access with least privilege principles

**3. Centralized Monitoring**

*   CloudWatch Cross-Account Observability: Aggregates metrics from all accounts
*   CloudWatch Dashboards: Provides unified view of disk utilization across all accounts
*   QuickSight: Creates advanced visualizations and trend analysis

**4.    Alerting & Remediation**

*   CloudWatch Alarms: Multi-threshold alerts (70%, 85%, 95%)
*   EventBridge: Routes alerts to appropriate destinations
*   SNS: Sends notifications to operations teams
*   Lambda Functions: Executes remediation scripts
*   Systems Manager Automation: Runs standardized remediation workflows

### Security Considerations

**IAM Best Practices**

All IAM roles follow least privilege principle
Cross-account access is restricted to read-only metrics access
Access is conditional on AWS Organizations membership


**Data Protection**

No hardcoded secrets in any component
Sensitive parameters stored in Systems Manager Parameter Store
Logs encrypted at rest using KMS


**Network Security**

All communication uses AWS private endpoints where possible
No direct internet access required for monitoring components


**Monitoring and Audit**

All remediation actions are logged for audit purposes
CloudTrail enabled to track all API calls



###     Implementation Guide
*   **Phase 1:** Setup IAM and Monitoring Infrastructure

    Deploy the IAM cross-account roles to each source account
    Configure CloudWatch Cross-Account Observability in the monitoring account
    Create base CloudWatch dashboards

*   **Phase 2:** Deploy CloudWatch Agent

    Create the CloudWatch Agent configuration in Systems Manager Parameter Store
    Deploy agent to all EC2 instances using the Systems Manager document
    Verify metrics collection

*   **Phase 3:** Configure Alerting and Remediation

    Set up CloudWatch Alarms with multiple thresholds
    Configure EventBridge rules
    Deploy Lambda functions for automated remediation
    Test end-to-end alerting and remediation workflow

*   **Phase 4:** Implement Advanced Analytics

    Set up log archiving to S3
    Configure Athena for log querying
    Create QuickSight dashboards for management reporting

###  Cost Optimization

Use standard resolution metrics (60-second intervals) for most cases
Implement lifecycle policies on S3 to manage log storage costs
Configure CloudWatch Logs retention periods appropriate to requirements
Use alarms and automated remediation to reduce operational costs

### Repository Structure
![alt text](image.png)

###     Conclusion
This solution provides the CTO with a comprehensive system for monitoring disk utilization across all EC2 instances in the enterprise's three AWS accounts. By leveraging AWS native services and following best practices for security and cost optimization, the solution delivers:

1.  Complete visibility into disk usage trends
2.  Early warning system for potential issues
3.  Automated remediation to prevent service disruptions
4.  Historical analysis for capacity planning

The architecture is designed to scale as the enterprise continues to grow, with minimal operational overhead.