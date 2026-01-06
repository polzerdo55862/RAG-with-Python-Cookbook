# Cloud Compute Service Level Agreement (SLA)

**Supplier**: SUP1  
**Customer**: Example Customer Inc.  
**Service**: Compute v1.4  
**Version**: 2024-01  
**Effective Date**: 2024-01-01  
**Governing Law**: Germany

## 1. Service Description

The Compute v1.4 service provides virtual compute resources including CPU, memory and temporary storage. Customers can deploy instances, manage workloads and access monitoring tools. The service offers multiple regions and supports varied workloads, though temporary storage is not replicated and should not be used for persistent data.

## 2. Availability and Uptime Commitment

The supplier commits to a **monthly uptime percentage of 99.9 percent**. Downtime refers to intervals of five or more consecutive minutes where operations fail due to service-side issues. Scheduled maintenance and customer-induced issues are excluded.

## 3. Response Times and Incident Handling

Incidents follow a four-level severity model.

- SEV1 receives a response within **15 minutes** with continuous mitigation.
- Lower severities range from 1 to 12 hours depending on impact.

## 4. Maintenance Windows

Routine maintenance requires **72 hours advance notice** and usually occurs Sunday morning. Instances continue running but control-plane operations may be limited.

## 5. Service Credits

- 99.0–99.9 percent uptime → **10 percent credit**
- Below 99.0 percent → **25 percent credit**  
  Credits apply to future invoices.

## 6. Customer Responsibilities

Customers manage OS patches, instance configuration, access control and resource sizing. Backups must be external to avoid data loss.

## 7. Data Protection and Privacy

Customer data follows GDPR. Logs contain only technical metadata unless customers submit personal data.

## 8. Security and Compliance

The platform includes encryption, access logging, multi factor authentication and regular penetration tests. Audit reports (SOC 2, ISO 27001) are available.

## 9. Limitations of Liability

Liability is capped at the previous twelve months of compute fees. Indirect and consequential damages are excluded.

## 10. Termination

Either party may terminate with 30 days notice. Customers must delete resources and remove data.

## 11. Exclusions

This SLA excludes planned maintenance, misconfigurations, external network issues, DDoS attacks, beta features and policy violations.

## 12. Region Specific Terms

EU regions may include additional network operations during maintenance. US regions may operate with reduced redundancy during severe weather conditions.

## 13. Definitions

- **Uptime**: Successful instance operations.
- **Downtime**: Service failure lasting five minutes or more.
- **SEV1 Incident**: Critical issue with no workaround.
- **Service Credit**: Invoice credit based on SLA violation.
